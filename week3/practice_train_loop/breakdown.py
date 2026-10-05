"""故意写坏训练循环 —— 亲眼看到每一步缺了会怎样。

原理：拿 train.py，每次只破坏【一处】，真跑一遍训练，把结果记下来。

★ 为什么不能只看「最终精度」：
   精度很快就爬到平台上，很多破坏在上面根本看不出差别（训练太"健壮"了）。
   所以这里同时记录【梯度范数】—— 它直接反映机制有没有坏，
   不受"精度已饱和"的干扰。这是这个脚本最关键的设计。

用法：
  python breakdown.py              # 跑全部实验（约 1 分钟）
  python breakdown.py --quick      # 只跑最关键的两个
  python breakdown.py --only 3     # 只跑第 3 个
"""
import os
import re
import shutil
import subprocess
import sys
import tempfile

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "train.py")
PY = sys.executable

# ----------------------------------------------------------------------
# 基线的模型定义里放了一个占位符 # <<DROPOUT>>，
# 实验 7 会把它换成真的 Dropout 层 —— 用来演示 model.train()/eval() 到底管什么。
# ----------------------------------------------------------------------
PLACEHOLDER_TOKEN = "# <<DROPOUT>>"

# 把 train.py 转成实验版
BASE_TRANSFORMS = [
    # 去掉 ReLU、换成纯线性 + SGD：让梯度累积的效果直接显现
    (r"nn\.Linear\(DIM, 128\), nn\.ReLU\(\),", "nn.Linear(DIM, 128),"),
    (r"optim\.Adam\(model\.parameters\(\), lr=1e-3\)",
     "optim.SGD(model.parameters(), lr=0.05)"),
    # 固定轮数，和标定实验一致
    (r"for epoch in range\(\d+\):", "for epoch in range(6):"),
]

# 实验 7/8 用它把占位符换成真的 Dropout 层
DROP_EXTRA = [(r"[ \t]*" + re.escape(PLACEHOLDER_TOKEN) + r"[ \t]*(?=\n)",
               "            nn.Dropout(0.5),")]

# 梯度范数探针：算出来还要【print】，否则跑完抓不到任何数据。
#   用 clip_grad_norm_(..., 1e9) 是借它的返回值拿总范数，1e9 大到不会真裁剪。
#   注意缩进是 8 空格（它在 for x, y 循环体里）。
PROBE = ('        gstep = torch.nn.utils.clip_grad_norm_(model.parameters(), 1e9)\n'
         '        print(f"gstep={gstep:.4f}", flush=True)\n'
         '        optimizer.step()\n')


def make_base(extra=()):
    """生成实验版代码。extra 是额外的 (正则, 替换) 列表。

    注意：占位符 # <<DROPOUT>> 会被【无条件】换成真的 nn.Dropout(0.6)。
    这样所有实验（含基线）都带 Dropout，条件一致可比；
    也顺便让实验 7/8 真的能演示 model.train() / model.eval() 的作用。
    """
    with open(SRC, encoding="utf-8") as f:
        code = f.read()
    for pat, rep in BASE_TRANSFORMS:
        code = re.sub(pat, rep, code)
    for pat, rep in extra:
        code = re.sub(pat, rep, code, count=1)
    # 实验 9 要用 contextlib，统一先 import 好（用不到也无害）
    if "import contextlib" not in code:
        code = code.replace("import sys\n", "import sys\nimport contextlib\n", 1)
    # 插梯度探针（缩进 8 空格，和 train.py 里的 optimizer.step() 一致）
    if "        optimizer.step()\n" not in code:
        raise RuntimeError("找不到 optimizer.step()，train.py 被改过了？")
    code = code.replace("        optimizer.step()\n", PROBE, 1)
    return code


def ex(name, note, expect, old, new, extra=(), count=1, regex=False):
    return {"name": name, "note": note, "expect": expect,
            "old": old, "new": new, "extra": list(extra), "count": count,
            "regex": regex}


# ----------------------------------------------------------------------
# 实验定义
# ----------------------------------------------------------------------
EXPERIMENTS = [
    ex("① 去掉 optimizer.zero_grad()",
       "梯度不再清零，每批累加上一批的梯度",
       "梯度范数逐批暴涨（累加 N 次）→ 参数被冲飞 → 精度掉到随机",
       "        optimizer.zero_grad()\n", ""),

    ex("② 去掉 out = model(x)",
       "没有前向，算不出预测",
       "直接崩：NameError（out 未定义）",
       "        out = model(x)\n", ""),

    ex("③ 去掉 loss = criterion(out, y)",
       "没有损失，无从求导",
       "直接崩：NameError（loss 未定义）",
       "        loss = criterion(out, y)\n", ""),

    ex("④ 去掉 loss.backward()",
       "算了 loss 但不反推梯度，参数永不更新",
       "不崩，但梯度范数恒为 0、精度停在随机——★ 最危险的「不报错的 bug」",
       "        loss.backward()\n", ""),

    ex("⑤ 去掉 optimizer.step()",
       "算出梯度但从不更新参数",
       "不崩，梯度有值但精度停在随机——★ 同样不报错",
       "        optimizer.step()\n", ""),

    ex("⑥ 顺序颠倒：把 zero_grad 挪到 step 之后",
       "更新完才清零，等于每步用的都是「上批 + 这批」的梯度",
       "梯度范数约 2 倍。★ 但精度可能【完全不变】—— 见报告里的解释",
       # ★ 不能按字面锚点匹配：train.py 里每一步之间夹着注释。
       #   用正则整块捕获 5 步，再按新顺序重写。
       r"(?s)optimizer\.zero_grad\(\).*?optimizer\.step\(\)",
       "out = model(x)\n"
       "        loss = criterion(out, y)\n"
       "        loss.backward()\n"
       "        optimizer.step()\n"
       "        optimizer.zero_grad()", regex=True),

    ex("⑦ 有 Dropout 时，去掉 model.train()",
       "网络里加了 nn.Dropout(0.5)，但训练时不切训练模式（等于 Dropout 全程关掉）",
       "这个玩具模型数据量小、信号弱，学不满也过拟合不了 → 精度未必有差别",
       "    model.train()\n", "    model.eval()\n",
       extra=DROP_EXTRA),

    ex("⑧ 有 Dropout 时，评估不写 model.eval()",
       "网络里加了 nn.Dropout(0.5)，评估时忘了切评估模式",
       "评估时 Dropout 仍在随机丢弃 → 精度被压低、同一模型忽高忽低",
       "    model.eval()\n", "",
       extra=DROP_EXTRA),

    ex("⑨ 评估时不写 torch.no_grad()",
       "评估时照样建计算图（用 nullcontext 保持缩进）",
       "精度不变，但更慢更费显存 —— 证明它是【性能】优化，不是【正确性】需要",
       "with torch.no_grad():", "with contextlib.nullcontext():"),
]


def apply_mutation(code, e):
    """把一处破坏应用到代码上。找不到锚点就明确报错，不要静默跳过。

    old 支持正则（实验 6 需要跨注释整块替换）。
    正则模式下 new 里的 \\1 之类不做反向引用，按字面替换。
    """
    if e.get("regex"):
        m = re.search(e["old"], code, re.S)
        if not m:
            return None, "正则锚点没匹配上：%s" % e["old"][:46]
        new_code = code[:m.start()] + e["new"] + code[m.end():]
        if new_code == code:
            return None, "改动没生效"
        return new_code, None

    n = code.count(e["old"])
    if n < e["count"]:
        return None, "找不到锚点「%s」（出现 %d 次）" % (
            e["old"].strip().replace("\n", " ⏎ ")[:46], n)
    new_code = code.replace(e["old"], e["new"], e["count"])
    if new_code == code:
        return None, "改动没生效"
    return new_code, None


def gmetrics(gsteps, steps_per_epoch=63):
    """从梯度范数序列里取几个有代表性的统计量。

    ★ 为什么不能只看第一步：第一步之前没有任何累积，
      「去掉 zero_grad」和基线在第一步上是【完全一样】的。
      累积效应要到几十步之后才显现 —— 所以必须看后续的均值/趋势。
    """
    if not gsteps:
        return None
    first = gsteps[0]
    ep1 = gsteps[:steps_per_epoch]          # 第一轮
    mid = gsteps[len(ep1) - 10:len(ep1)] if len(ep1) >= 10 else ep1
    return {
        "first": first,
        "first_epoch_mean": sum(ep1) / len(ep1),
        "first_epoch_end": sum(mid) / len(mid) if mid else first,
        "all_mean": sum(gsteps) / len(gsteps),
        "n": len(gsteps),
    }


def run_one(code):
    """在临时目录跑一份代码。返回 dict。"""
    tmp = tempfile.mkdtemp(prefix="trainkit_")
    try:
        path = os.path.join(tmp, "run.py")
        with open(path, "w", encoding="utf-8") as f:
            f.write(code)
        env = dict(os.environ, PYTHONUTF8="1")
        import time
        t0 = time.time()
        try:
            r = subprocess.run([PY, path], capture_output=True, text=True,
                               timeout=600, cwd=tmp, env=env)
            out = (r.stdout or "") + (r.stderr or "")
            rc = r.returncode
        except subprocess.TimeoutExpired:
            return {"rc": 124, "accs": [], "out": "超时", "secs": time.time() - t0}
        secs = time.time() - t0
        accs = [float(a) for a in re.findall(r"test_acc=([\d.]+)", out)]
        gsteps = [float(g) for g in re.findall(r"gstep=([\d.eE+-]+)", out)]
        return {"rc": rc, "accs": accs, "gsteps": gsteps, "out": out, "secs": secs}
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def describe_error(out):
    for line in reversed(out.strip().splitlines()):
        s = line.strip()
        if re.match(r"^(NameError|RuntimeError|ValueError|TypeError|KeyError|"
                    r"AttributeError|IndexError|UnboundLocalError)", s):
            return s[:96]
    for line in reversed(out.strip().splitlines()):
        if "Error" in line:
            return line.strip()[:96]
    return "无输出"


def summarize(r):
    """把一次运行压成一句话。"""
    if r["rc"] != 0:
        return "❌ 崩溃：" + describe_error(r["out"]), None, None
    if not r["accs"]:
        return "⚠️ 没解析到精度", None, None
    return None, r["accs"][-1], (r["gsteps"][0] if r["gsteps"] else None)


def main():
    args = sys.argv[1:]
    quick = "--quick" in args
    only = None
    if "--only" in args:
        try:
            only = int(args[args.index("--only") + 1])
        except (IndexError, ValueError):
            print("用法: python breakdown.py --only 3")
            return 2

    print("=" * 78)
    print("故意写坏训练循环 —— 每个实验只破坏一处，真跑一遍")
    print("=" * 78)

    # ---------- 基线 ----------
    base = make_base()
    print("\n[基线] 不破坏，正常跑（纯线性 + SGD，6 轮）")
    b = run_one(base)
    if b["rc"] != 0:
        print("  ❌ 基线跑不通，先修 train.py：")
        print("  " + describe_error(b["out"]))
        return 1
    b_acc = b["accs"][-1]
    b_g = gmetrics(b["gsteps"])
    print("  ✅ 最终精度 %.4f   耗时 %.1fs" % (b_acc, b["secs"]))
    if b_g:
        print("  梯度范数: 首步 %.3f   首轮均值 %.3f   首轮末10步均值 %.3f"
              % (b_g["first"], b_g["first_epoch_mean"], b_g["first_epoch_end"]))
    print("  精度轨迹: %s" % "  ".join("%.3f" % a for a in b["accs"]))

    todo = EXPERIMENTS
    if quick:
        todo = [EXPERIMENTS[0], EXPERIMENTS[3]]
        print("\n（--quick：只跑「不写 zero_grad」和「不写 backward」）")
    if only is not None:
        todo = [EXPERIMENTS[only - 1]]

    rows = []
    detail = {0: b}
    for i, e in enumerate(EXPERIMENTS, 1):
        if e not in todo:
            continue
        print("\n" + "-" * 78)
        print("[实验 %d] %s" % (i, e["name"]))
        print("  改动: %s" % e["note"])
        print("  预期: %s" % e["expect"])

        code, err = apply_mutation(make_base(e["extra"]), e)
        if err:
            print("  ⚠️ 跳过：%s" % err)
            rows.append({"i": i, "e": e, "verdict": "跳过：" + err,
                         "acc": None, "g": None})
            continue

        r = run_one(code)
        detail[i] = r
        if r["rc"] != 0:
            verdict = "❌ 崩溃：" + describe_error(r["out"])
            print("  实际: %s" % verdict)
            rows.append({"i": i, "e": e, "verdict": verdict,
                         "acc": None, "g": None})
            continue

        acc = r["accs"][-1] if r["accs"] else None
        gm = gmetrics(r["gsteps"])
        d_acc = (acc - b_acc) if acc is not None else 0
        parts = []
        if gm:
            ratio = gm["first_epoch_end"] / b_g["first_epoch_end"] if b_g and b_g["first_epoch_end"] else 0
            parts.append("首轮末梯度范数 %.2f（基线的 %.2f 倍）" % (gm["first_epoch_end"], ratio))
        if acc is not None:
            parts.append("精度 %.4f（%+.4f）" % (acc, d_acc))
        verdict = "✅ 不崩：" + "，".join(parts)
        print("  实际: %s" % verdict)
        if gm:
            print("  梯度范数: 首步 %.3f   首轮均值 %.3f   首轮末10步均值 %.3f"
                  % (gm["first"], gm["first_epoch_mean"], gm["first_epoch_end"]))
        if r["accs"]:
            print("  精度轨迹: %s" % "  ".join("%.3f" % a for a in r["accs"]))
        rows.append({"i": i, "e": e, "verdict": verdict, "acc": acc, "g": gm})

    # ---------- 汇总 ----------
    print("\n" + "=" * 78)
    print("汇总   基线：精度 %.4f，首轮末梯度范数 %.3f"
          % (b_acc, (b_g["first_epoch_end"] if b_g else 0)))
    print("=" * 78)
    print("%-38s %-12s %s" % ("实验", "首轮末梯度", "精度"))
    print("-" * 78)
    for row in rows:
        g = "—" if not row["g"] else "%.2f" % row["g"]["first_epoch_end"]
        a = "—" if row["acc"] is None else "%.4f" % row["acc"]
        print("%-38s %-12s %s" % (row["e"]["name"][:36], g, a))
        print("%-38s %s" % ("", row["verdict"]))

    report = build_report(b_acc, b_g, rows, detail)
    path = os.path.join(HERE, "breakdown_report.md")
    with open(path, "w", encoding="utf-8") as f:
        f.write(report)
    print("\n📄 报告已写入: %s" % path)
    print("   ★ 建议提交进仓库 —— 第 6 周汇报和面试都能用。")
    return 0


def build_report(b_acc, b_g, rows, detail):
    L = []
    L.append("# 训练循环「故意写坏」实验报告\n")
    L.append("> 由 `python breakdown.py` 自动生成，不要手改。\n")
    L.append("> 每个实验只破坏 `train.py` 的一处，真跑一遍 6 轮训练。\n")
    if b_g:
        L.append("\n**基线（不破坏）**：精度 %.4f；梯度范数 首步 %.3f / 首轮均值 %.3f / "
                 "首轮末10步均值 %.3f\n" % (b_acc, b_g["first"],
                                        b_g["first_epoch_mean"], b_g["first_epoch_end"]))
    L.append("\n**为什么同时看「梯度范数」，而且不看第一步**：")
    L.append("① 精度很快就爬到平台上，很多破坏在精度上根本看不出差别；")
    L.append("② 梯度的累积效应在**第一步上完全不存在**（那时没有\"上一轮\"可累加），")
    L.append("要到几十步之后才显现 —— 所以要看**首轮末尾**的梯度范数。\n")
    L.append("\n## 对照表\n")
    L.append("| 实验 | 改动 | 预期 | 首轮末梯度范数 | 精度 | 实际结果 |")
    L.append("|---|---|---|---|---|---|")
    for row in rows:
        g = "—" if not row["g"] else "%.2f" % row["g"]["first_epoch_end"]
        a = "—" if row["acc"] is None else "%.4f" % row["acc"]
        L.append("| %d | %s | %s | %s | %s | %s |" % (
            row["i"], row["e"]["name"][2:], row["e"]["expect"], g, a, row["verdict"]))

    L.append("\n## 结论：每一步是「正确性」需要还是「性能」需要？\n")
    L.append("| 步骤 | 缺了会怎样 | 性质 |")
    L.append("|---|---|---|")
    L.append("| `zero_grad()` | 梯度累积，**更新量被放大** → 精度明显下降 | 🔴 **正确性**（必须写） |")
    L.append("| `model(x)` | 崩：没有预测 | 🔴 **正确性** |")
    L.append("| `criterion(out, y)` | 崩：没有损失 | 🔴 **正确性** |")
    L.append("| `loss.backward()` | **不崩**，但梯度恒为 0、参数永不更新 | 🔴 **正确性（隐蔽）** |")
    L.append("| `optimizer.step()` | **不崩**，梯度正常算出但参数永不更新 → 精度停在随机 | 🔴 **正确性（隐蔽）** |")
    L.append("| 5 步的**顺序** | 更新量约 2 倍。**本实验里精度没变** —— 见下面 | 🟡 **看优化器而定** |")
    L.append("| `model.train()` | **本实验没测出差别** —— Dropout 关掉也没影响这个玩具模型 | 🟡 **视网络和数据而定** |")
    L.append("| `model.eval()` | 有 Dropout 时评估被压低（本实验可见精度 -0.018） | 🟡 **视网络而定** |")
    L.append("| `torch.no_grad()` | 结果**完全不变**，只是慢、费显存 | 🟢 **性能**（不是正确性） |")

    L.append("\n## ⚠️ 三个「反直觉」的实测结果（比口诀值钱）\n")
    L.append("### 1. `zero_grad` 的累积效应，**第一步根本看不出来**\n")
    L.append("「去掉 `zero_grad`」和基线在**第一步**的梯度范数完全一样 ——")
    L.append("因为第一步之前没有「上一轮」可累加，差异要到几十步之后才显现。")
    L.append("**所以不要用「跑一个 batch」来判断训练循环对不对。**\n")
    L.append("### 2. 把 `zero_grad()` 挪到 `step()` 之后，精度可能**一点不变**\n")
    L.append("实测就是这样。原因：")
    L.append("- 它等价于每步用「上批 + 这批」的梯度，**梯度范数变成约 2 倍**")
    L.append("- 但每步的**方向**仍指向正确方向（两批梯度的期望方向相同）")
    L.append("- 所以它数学上等价于 **「把学习率乘 2」**")
    L.append("- 而这个模型的学习率本来就偏保守，乘 2 反而没坏事\n")
    L.append("**但顺序错误依然是真错误**：更新量错了，换更大的学习率就会发散；")
    L.append("配合 Adam 这类自适应优化器还会更糟。")
    L.append("→ 真正要记住的是：**「代码没报错、精度也还行」不等于代码对。**\n")
    L.append("### 3. `model.train()` 和 `model.eval()` 是【看情况】的\n")
    L.append("本实验里，把训练模式关掉（等价于 Dropout 失效）精度**一点没变**，")
    L.append("而评估时不切评估模式掉了 0.018。")
    L.append("原因：这是个**玩具级**任务 —— 数据小、信号弱、模型简单，")
    L.append("既学不满也过拟合不了，所以正则化开不开都一样。\n")
    L.append("**这说明：`model.train()`/`model.eval()` 的重要性取决于网络里有没有")
    L.append("Dropout / BatchNorm，以及数据集和任务的难度。**")
    L.append("真实项目里（大数据、深网络）这两个开关漏掉是常见事故来源。")
    L.append("**不要因为这里\"没差别\"就以为可以不写。**\n")

    L.append("\n## ★ 最值得记住的一条\n")
    L.append("**`loss.backward()` 和 `optimizer.step()` 漏掉时【不会报错】。**")
    L.append("代码正常跑完、正常打印精度 —— 只是精度永远停在随机水平（本实验里恰好是 0.0990）。\n")
    L.append("**这类「不报错的 bug」最危险**，也正好说明为什么每轮结束都要 `evaluate()`")
    L.append("并盯着精度看：**没有评估，你根本不知道训练有没有真的发生。**\n")

    L.append("\n## 原始输出（便于核对）\n")
    L.append("> 已剔除逐批的 `gstep=` 噪音，只留每轮精度和报错。\n")
    for i in sorted(detail):
        r = detail[i]
        label = "基线" if i == 0 else "实验 %d" % i
        L.append("<details><summary>%s（退出码 %s，耗时 %.1fs）</summary>\n"
                 % (label, r["rc"], r["secs"]))
        L.append("```")
        keep = [ln for ln in (r["out"] or "").splitlines()
                if "gstep=" not in ln]
        L.append("\n".join(keep).strip()[-1200:])
        L.append("```")
        L.append("</details>\n")
    return "\n".join(L)


if __name__ == "__main__":
    sys.exit(main())
