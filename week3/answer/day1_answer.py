"""Week3 · D1 —— 参考实现（先自己写，卡住了再对答案）

⚠️ 这不是入口脚本。你要写的是 `week3/day1.py`（骨架版）。
   这个文件只用来在你写完、或写不出来时对照。

你真正要写的只有下面这 5 个函数体（外面全是脚手架，不用管）：
    d1_single      单轮对话
    d2_prompt      有/无 system 角色对比
    d3_multi       多轮对话（自己维护 history）
    d4_structured  response_format 强制 JSON + 正则兜底
    d5_params      temperature / max_tokens 实验

没有 API Key、想先确认代码形状对不对 → 用 mock：
    python _verify\\mock_openai_server.py     （窗口 1）
    python _verify\\verify_handbook_llm.py    （窗口 2）
"""
import argparse
import json
import os
import re
import sys
import time

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from dotenv import load_dotenv

# ---------------------------------------------------------------- 输出小工具
OK = "✅"
BAD = "❌"
WARN = "⚠️"


def head(t):
    print("\n" + "=" * 62)
    print(t)
    print("=" * 62)


def check_env():
    """自检：Key / 地址 / 模型名 / .env 是否安全。"""
    head("第 1 步 · 环境自检")

    ok = True

    # ---------- .env 文件本身 ----------
    env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".env")
    env_path = os.path.normpath(env_path)
    if os.path.exists(env_path):
        print(f"{OK} 找到 .env：{env_path}")

        # 安全检查：.env 绝不能被 git 跟踪。这是最容易出人命的一步。
        try:
            import subprocess
            repo = os.path.dirname(env_path)
            inside = subprocess.run(["git", "rev-parse", "--is-inside-work-tree"],
                                    cwd=repo, capture_output=True, text=True)
            if inside.returncode != 0:
                print(f"{WARN} 这里不是 git 仓库，跳过 .env 忽略检查")
            else:
                r = subprocess.run(["git", "check-ignore", "-q", ".env"],
                                   cwd=repo, capture_output=True)
                if r.returncode == 0:
                    print(f"{OK} .env 已被 .gitignore 排除（安全）")
                else:
                    print(f"{BAD} .env 【没有】被 .gitignore 排除！")
                    print("    危险：一旦 commit，API Key 会进 git 历史，删 commit 也删不干净")
                    print("    解决：在 .gitignore 里加一行 .env，然后 git status 确认看不到它")
                    ok = False
        except FileNotFoundError:
            print(f"{WARN} 没装 git，跳过 .env 忽略检查（请自己确认 .env 没被提交）")
        except Exception as e:
            print(f"{WARN} 跳过 git 检查（{type(e).__name__}）")
    else:
        print(f"{BAD} 没找到 .env：{env_path}")
        print("    解决：copy .env.example .env   然后填上 API_KEY / BASE_URL / MODEL")
        ok = False

    load_dotenv(env_path)

    # ---------- 三个变量 ----------
    api_key = os.getenv("API_KEY")
    base_url = os.getenv("BASE_URL")
    model = os.getenv("MODEL")

    if not api_key:
        print(f"{BAD} API_KEY 是空的")
        print("    常见原因：.env 里写的是 API_KEY=你的密钥（占位符没替换）")
        ok = False
    else:
        # 只显示前后几位，不打印完整密钥
        print(f"{OK} API_KEY 已读到：{api_key[:6]}…{api_key[-4:]}（长度 {len(api_key)}）")
        if api_key != api_key.strip():
            print(f"{BAD} API_KEY 首尾有空格！这会导致 401")
            ok = False

    if not base_url:
        print(f"{BAD} BASE_URL 是空的")
        ok = False
    else:
        print(f"{OK} BASE_URL = {base_url}")
        if not base_url.rstrip("/").endswith("/v1"):
            print(f"{WARN} 国内厂商的兼容接口通常要以 /v1 结尾，检查一下")

    if not model:
        print(f"{BAD} MODEL 是空的")
        ok = False
    else:
        print(f"{OK} MODEL = {model}")

    return ok, api_key, base_url, model


def build_client(api_key, base_url):
    from openai import OpenAI
    return OpenAI(api_key=api_key, base_url=base_url)


# ---------------------------------------------------------------- 思考模式
# deepseek-flash 默认【开启思考】。实测（见 week3/_diag_thinking.py）发现两件必须知道的事：
#   1. max_tokens 把【思考 token 算在内】。实测 max_tokens=100 时，
#      100 个 token 全被思考吃掉 → 正文是空字符串、finish_reason=length。
#      → 所以 max_tokens 要给够余量（简单任务 500 起步）。
#   2. 思考要花钱（算在 completion_tokens 里），简单任务上纯属浪费。
# 这一周的实验统一关掉思考，让结果干净、便宜、可复现。
THINKING_OFF = {"thinking": {"type": "disabled"}}


def completion(client, model, **kw):
    """统一入口：默认关掉思考模式。

    为什么要包一层：openai SDK 不认 thinking 这个字段，要经 extra_body 透传。
    换厂商后如果对方不认这个字段，去掉 THINKING_OFF 即可 —— 不传就是默认行为。
    """
    extra = dict(kw.pop("extra_body", {}) or {})
    extra.update(THINKING_OFF)
    return client.chat.completions.create(model=model, extra_body=extra, **kw)


def diagnose(e, base_url):
    """把 openai 的异常翻译成「你该去改哪里」。"""
    name = type(e).__name__
    print(f"\n{BAD} 调用失败：{name}")
    print(f"   原始信息：{str(e)[:300]}")

    tips = {
        "AuthenticationError": [
            "API_KEY 不对。检查 .env 里的值有没有多余空格或引号",
            "确认这个 Key 属于 BASE_URL 对应的那家厂商（别把 A 家的 Key 配到 B 家的地址）",
        ],
        "NotFoundError": [
            f"MODEL 名字不对，或者服务地址不对（当前 BASE_URL={base_url}）",
            "★ 网上老教程里的 deepseek-chat / deepseek-reasoner 已失效，现在用 deepseek-flash",
        ],
        "APIConnectionError": [
            f"连不上 {base_url}。检查网络 / 需不需要代理",
            "确认 BASE_URL 没写错，且带了 /v1",
        ],
        "RateLimitError": [
            "被限流或余额不足。等一会儿，或去厂商后台看余额",
        ],
        "BadRequestError": [
            "请求参数不被支持。Week3 最常见的是模型不支持 response_format=json_object",
        ],
    }
    for t in tips.get(name, ["看上面的原始信息，对照手册 6.9 节（LLM / API 类报错表）"]):
        print(f"   → {t}")
    print("\n   环境自检能过、但调用失败，问题基本就在上面这几条里。")


# ---------------------------------------------------------------- D1 单轮
def d1_single(client, model):
    head("D1 · 单轮对话")
    t0 = time.time()
    resp = completion(
        client, model,
        messages=[{"role": "user", "content": "用一句话解释什么是反向传播"}],
    )
    dt = time.time() - t0
    reply = resp.choices[0].message.content
    print("回答：", reply)
    print(f"\n耗时 {dt:.2f}s")
    print("token 用量：", resp.usage)
    print(f"\n{OK} 第一次调用跑通了。这两件事你要能看懂：")
    print("   resp.choices[0].message.content  → 正文")
    print("   resp.usage                       → 花了多少 token（影响成本）")
    return reply


# ---------------------------------------------------------------- D2 prompt
def d2_prompt(client, model):
    head("D2 · Prompt 基础（角色 + few-shot）")
    prompts = {
        "无角色": "把这句话改得更正式：这个方案我觉得不太行",
        "有角色（system）": None,
    }
    r1 = completion(
        client, model,
        messages=[{"role": "user", "content": prompts["无角色"]}],
    )
    print("【无角色】", r1.choices[0].message.content)

    r2 = completion(
        client, model,
        messages=[
            {"role": "system", "content": "你是一名严谨的技术文档编辑，只输出改写后的句子。"},
            {"role": "user", "content": prompts["无角色"]},
        ],
    )
    print("\n【有角色】", r2.choices[0].message.content)
    print(f"\n{OK} 同样的输入，只加了一条 system，输出就变了 —— 这就是 system 的作用")


# ---------------------------------------------------------------- D3 多轮
def d3_multi(client, model, turns=3):
    head("D3 · 多轮对话（历史要自己传）")
    history = [{"role": "system", "content": "你是一个耐心的 Python 助教，回答尽量短。"}]
    questions = ["什么是列表推导式？", "它和 map 有什么区别？", "那什么时候该用哪个？"][:turns]

    for q in questions:
        history.append({"role": "user", "content": q})
        r = completion(client, model, messages=history)
        reply = r.choices[0].message.content
        history.append({"role": "assistant", "content": reply})
        print(f"\n你: {q}")
        print(f"AI: {reply}")

    print(f"\n{OK} 现在 history 里有 {len(history)} 条消息")
    print("   ★ 模型本身没有记忆。「它记得上一句」是因为你把历史全传回去了。")
    print("   ★ 历史会无限增长 —— 这就是 Agent 里的「上下文管理」问题（手册 4.10）")


# ---------------------------------------------------------------- D4 结构化
def d4_structured(client, model):
    head("D4 · 结构化输出 ★ Agent 的地基")
    text = "张小明这次数学考了 88 分，语文 92 分。"
    prompt = (f'从下面的文本中抽取信息，只输出 JSON，不要任何其他文字。\n'
              f'格式：{{"姓名": "", "科目": "", "分数": 0}}\n\n文本：{text}\n')

    print("--- 方式一：response_format 强制 JSON ---")
    raw = None
    try:
        r = completion(
            client, model,
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
        )
        raw = r.choices[0].message.content
        data = json.loads(raw)
        print("解析成功：", data)
        print(f"{OK} 这个模型支持 json_object")
    except Exception as e:
        print(f"{WARN} json_object 不可用（{type(e).__name__}）→ 这不是你的错，换方式二")
        if raw is None:
            r = completion(client, model,
                           messages=[{"role": "user", "content": prompt}])
            raw = r.choices[0].message.content

    print("\n--- 方式二：正则兜底（模型加了多余文字也能救） ---")
    print("原始返回：", (raw or "")[:160])
    m = re.search(r"\{.*\}", raw or "", re.S)
    if m:
        print("正则抠出来：", json.loads(m.group(0)))
        print(f"{OK} 兜底方案有效")
    else:
        print(f"{BAD} 正则也没抠到 JSON —— 这个模型的输出格式需要你调整 prompt")

    print("\n   ★ Tool Calling 本质就是「让模型吐结构化输出」。")
    print("     这一步学不好，第 4 周 Agent 会卡。")


# ---------------------------------------------------------------- D5 参数
def d5_params(client, model):
    head("D5 · 参数实验（temperature / max_tokens）")

    # ---- max_tokens：★ 先讲这个，因为它是 deepseek-flash 上最容易误解的一个 ----
    print("--- max_tokens 的影响（★ 这里有个坑） ---")
    print("deepseek-flash 默认开启「思考模式」，而 max_tokens 把【思考 token 也算在内】。")
    print("思考没结束预算就没了 → finish_reason=length、正文是空字符串。\n")
    print("★ 注意：下面这几行是【关掉思考】之后跑的（本脚本统一关掉），")
    print("  所以你会看到 reasoning_tokens=None —— 那正说明思考确实没发生。")
    print("  想看『思考吃掉预算』的真实样子 → python week3\\_diag_thinking.py\n")
    print(f"{'max_tokens':>11} | {'思考token':>9} | {'正文长度':>8} | finish_reason")
    print("-" * 62)
    for mt in [50, 100, 500]:
        r = completion(client, model, max_tokens=mt,
                       messages=[{"role": "user", "content": "用三句话介绍什么是机器学习"}])
        c = r.choices[0].message.content or ""
        d = r.usage.completion_tokens_details
        rt = getattr(d, "reasoning_tokens", None) if d else None
        print(f"{mt:>11} | {str(rt):>9} | {len(c):>8} | {r.choices[0].finish_reason}")
        print(f"   正文: {c[:70] if c else '（空！）'}")

    print(f"\n{OK} 两条结论：")
    print("   ① max_tokens 是【思考 + 正文】的总预算。开着思考时给小了 → 正文一个字都没有。")
    print("      做 JSON 输出时尤其危险：预算被吃掉 → 你拿到空字符串 →")
    print("      json.loads('') 报 JSONDecodeError，你会误以为是格式问题。")
    print("   ② 关掉思考后 reasoning_tokens 是 None，【同样的钱买到更多正文】。")

    # 后面的实验关掉思考，排除干扰
    print("\n（下面统一【关掉思考模式】，让结果干净、便宜、可复现）\n")

    # ---- temperature ----
    print("--- temperature 的影响（每个温度跑 4 次，看输出是否变化） ---")
    print("★ 注意：必须给足 max_tokens，否则正文被截成空字符串，")
    print("  4 次\"空\"会被误判成\"输出相同\" —— 这是个很容易踩的测量陷阱。\n")
    print(f"{'temperature':>12} | 4 次的输出")
    print("-" * 62)
    for temp in [0, 0.7, 1.5]:
        outs = []
        for _ in range(4):
            r = completion(client, model, temperature=temp, max_tokens=800,
                           messages=[{"role": "user", "content": "给我一个创业点子，一句话"}])
            outs.append((r.choices[0].message.content or "").strip())
        n_uniq = len(set(outs))
        blank = sum(1 for o in outs if not o)
        note = f"{n_uniq} 种不同"
        if blank:
            note += f"（⚠️ 有 {blank} 次是空的，说明 max_tokens 还是不够）"
        print(f"{temp:>12} | {note}")
        print(f"   例: {outs[0][:66]}")

    print(f"\n{OK} temperature=0 时输出仍可能不同 —— 这很正常：")
    print("   它降低随机性，但不保证 100% 复现（GPU 浮点累加顺序、批处理都会引入差异）。")
    print("   要完全可复现，得配合固定 seed（如果厂商支持）。")
    print("   ★ 实践建议：要 JSON / 要结构化输出 → temperature=0；日常对话 → 0.7 左右")


def main():
    ap = argparse.ArgumentParser(description="Week3 D1 —— 跑通第一次 LLM 调用")
    ap.add_argument("--check", action="store_true", help="只做环境自检，不发请求（不花钱）")
    ap.add_argument("--all", action="store_true", help="跑 D1~D5 全部示例")
    args = ap.parse_args()

    ok, api_key, base_url, model = check_env()
    if not ok:
        print(f"\n{BAD} 自检没过，先把上面的问题解决。")
        print("   不想花钱、想先确认代码对不对 → python _verify\\verify_handbook_llm.py")
        return 2
    print(f"\n{OK} 自检通过")

    if args.check:
        print("\n（--check：只自检，不发请求）")
        return 0

    client = build_client(api_key, base_url)
    print("\n下一步会真的调用 API，会产生少量 token 消耗。")

    try:
        d1_single(client, model)
        if args.all:
            d2_prompt(client, model)
            d3_multi(client, model)
            d4_structured(client, model)
            d5_params(client, model)
    except Exception as e:
        diagnose(e, base_url)
        return 1

    head("完成")
    print(f"{OK} D1 跑通了。")
    if not args.all:
        print("   想看 D2~D5 的完整示例：python week3\\day1.py --all")
    print("\n接下来按手册第 5 章「第 3 周」往下走：")
    print("   D2 Prompt 基础  D3 多轮对话  D4 ★ 结构化输出  D5 参数实验")
    print("\n★ 别忘了：把今天做的事写进 notes/log.md（三行就够）")
    return 0


if __name__ == "__main__":
    sys.exit(main())
