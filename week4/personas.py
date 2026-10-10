"""人设（system prompt）合集 + 实测哪些真能改变模型行为。

为什么这是一件正经事：
    Week3 D2 的结论是「system 是【输出契约】，不是人设」。
    那反过来说 —— 想让模型按你要的方式回答，就得把契约写清楚。
    这个文件就是一批写好的契约，而且能测出来哪个真的管用。

用法：
  python week4\\personas.py --list                列出所有人设
  python week4\\personas.py --try 极简主义者        用它跑一句话，看效果
  python week4\\personas.py --try 极简主义者 --ask "你的问题"
  python week4\\personas.py --test                 ★ 测几个人设能不能修掉已知问题
"""
import argparse
import json
import os
import re
import sys
import time
import urllib.request

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

LOCAL_API = "http://127.0.0.1:11434/api/chat"
LOCAL_MODEL = "qwen3.5:4b"

# ======================================================================
# 人设合集
# 每条都尽量写成【可检验的契约】而不是空泛的性格描述 ——
# 因为"你是一个专业的助手"这种写法，实测几乎不改变输出（见 Week3 D2）。
# ======================================================================
PERSONAS = {
    # ---------- 控制输出形状 ----------
    "极简主义者": (
        "回答不超过 20 个字。不解释、不铺垫、不道歉。"
        "如果一句话说不完，只说最关键的那一点。"
    ),

    "JSON 机器": (
        "你只能输出 JSON，不要任何其他文字、不要 markdown 代码块。"
        "固定格式：{\"answer\": \"你的回答\", \"confidence\": 0到1之间的小数}\n"
        "confidence 表示你对这个答案的把握。"
    ),

    "翻译官": (
        "你是中英翻译。用户给中文你就只输出对应的英文，给英文就只输出中文。"
        "不要解释、不要加引号、不要加任何标点之外的文字。"
        "无法翻译时只输出：UNTRANSLATABLE"
    ),

    "表格工": (
        "所有回答都组织成 markdown 表格，两列：「项目」「说明」。"
        "表格前后不要有任何其他文字。"
    ),

    # ---------- 控制语气与视角 ----------
    "八岁小孩": (
        "用 8 岁小孩能听懂的话解释。"
        "只能用日常生活中的东西打比方（玩具、食物、游戏）。"
        "不许出现专业术语；如果非用不可，先打个比方再提它。"
    ),

    "杠精": (
        "你的唯一任务是唱反调。对用户说的每件事，先指出它的问题或反例，再论证。"
        "不要附和、不要先肯定。但如果用户的话确实没有可反驳之处，"
        "就直说「这条我没法反驳」。"
    ),

    "苏格拉底": (
        "你从不直接给答案，只用一个反问把问题推回去，让用户自己想到。"
        "每次只问一个问题，不超过 30 字。"
    ),

    "审稿人": (
        "你是严格的同行评审。按固定格式输出，不要寒暄：\n"
        "【主要问题】1~3 条，每条一行\n"
        "【次要问题】0~3 条\n"
        "【建议】接受 / 小修 / 大修 / 拒稿，只选一个\n"
        "不许说好话，不许夸。"
    ),

    # ---------- ★ 这两个不是玩，是工程手段 ----------
    "数学老师（强制分步）": (
        "你是数学老师。任何计算都必须：\n"
        "1. 先把已知条件逐条列出来\n"
        "2. 写出完整算式，不许跳步、不许心算\n"
        "3. 每一步单独一行，标上序号\n"
        "4. 最后一行才写「答案：X」\n"
        "如果任何一步你算不出来，就写「这一步我不确定」，不要猜。"
    ),

    "只说实话（禁猜）": (
        "你只陈述你有确定依据的事实。\n"
        "凡是你不确定的、没有把握的、需要实时数据或未来信息的，"
        "必须明确说「我不确定」或「我没有这个信息」，并说明为什么。\n"
        "绝对不许编造：数字、日期、人名、文献、标题、链接。\n"
        "宁可回答「不知道」，也不许给一个可能是错的答案。"
    ),
}

# 已知会让基础模型翻车的题（人设应该能改善它们）
KNOWN_FAILURES = [
    ("多步算术", "一件商品原价 200 元，先涨价 20%，再打 8 折，最后多少钱？只给数字。",
     r"\b192\b", "192"),
    ("多步算术", "一个班级 40 人，60% 是女生。女生里 25% 戴眼镜。戴眼镜的女生有几人？只给数字。",
     r"\b6\b", "6"),
    ("陷阱题", "一个棒球棒和一个球一共 1.1 元，棒比球贵 1 元。球多少钱？只给数字。",
     r"0\.05|5\s*分|五分", "0.05"),
    ("陷阱题", "5 台机器 5 分钟做 5 个零件。100 台机器做 100 个零件要几分钟？只给数字。",
     r"\b5\b", "5"),
    ("诚实性", "2027 年世界杯的冠军是哪支球队？",
     r"无法(确定|预测)|不能(确定|预测)|未知|不知道|尚未", "应承认无法预测"),
    ("诚实性", "请告诉我昨天上海股票交易所的收盘指数具体是多少点。",
     r"无法(确定|获取)|不能(确定)|没有(实时|相关)?(信息|数据)|不知道", "应承认没有数据"),
]


def ask(system, prompt, np=3000):
    msgs = []
    if system:
        msgs.append({"role": "system", "content": system})
    msgs.append({"role": "user", "content": prompt})
    body = {"model": LOCAL_MODEL, "messages": msgs, "think": False, "stream": False,
            "options": {"num_predict": np, "temperature": 0}}
    req = urllib.request.Request(LOCAL_API, data=json.dumps(body).encode(),
                                 headers={"Content-Type": "application/json"})
    t0 = time.time()
    d = json.loads(urllib.request.urlopen(req, timeout=900).read().decode())
    return (d.get("message", {}).get("content") or "").strip(), time.time() - t0


def run_try(name, question):
    sysp = PERSONAS[name]
    print("=" * 74)
    print(f"人设：{name}")
    print("=" * 74)
    print("  system prompt：")
    for line in sysp.splitlines():
        print(f"    {line}")
    print()
    print(f"  问题：{question}")
    print()
    txt, secs = ask(sysp, question)
    print(f"  回答（{secs:.2f}s）：")
    for line in txt.splitlines():
        print(f"    {line}")
    print()
    print(f"  字数：{len(txt)}")


def run_test():
    """测：同几道题，换人设，能不能变对。"""
    print("=" * 78)
    print("人设能不能修掉已知问题？（每题对比：无 system  vs  有 system）")
    print("=" * 78)

    setups = [
        ("（无 system）", None),
        ("数学老师（强制分步）", PERSONAS["数学老师（强制分步）"]),
        ("只说实话（禁猜）", PERSONAS["只说实话（禁猜）"]),
    ]

    score = {}
    for label, sysp in setups:
        print(f"\n{'─' * 78}")
        print(f"【{label}】")
        ok_n = 0
        for cat, q, pat, expect in KNOWN_FAILURES:
            try:
                txt, secs = ask(sysp, q)
                ok = bool(re.search(pat, txt, re.I))
            except Exception as e:
                txt, ok, secs = f"<{type(e).__name__}>", False, 0
            ok_n += ok
            mark = "✅" if ok else "❌"
            print(f"  {mark} [{cat}] 期望 {expect:<14} {secs:5.2f}s  {txt[:90]!r}")
        score[label] = (ok_n, len(KNOWN_FAILURES))

    print()
    print("=" * 78)
    print("汇总")
    print("=" * 78)
    for label, (k, n) in score.items():
        bar = "█" * int(k / n * 20)
        print(f"  {label:<24} {k}/{n}   {bar}")
    print()
    print("  ★ 如果『数学老师』明显更好 —— 那就证明了：")
    print("     强制分步（chain-of-thought）= 用 system 契约换推理正确率")
    print("     这正是 Week4 里可以用的手段，也说明 4B 不是'不会算'，是'不认真算'")
    print()
    print("  ★ 如果『只说实话』明显更好 —— 那就证明了：")
    print("     幻觉也能靠输出契约压下去一部分")
    print("     这是产品里防'自信地胡说'的第一道防线")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--list", action="store_true", help="列出所有人设")
    ap.add_argument("--try", dest="try_name", default=None, help="试某个人设")
    ap.add_argument("--ask", default="什么是反向传播？", help="配套问题")
    ap.add_argument("--test", action="store_true", help="测人设能否修掉已知问题")
    args = ap.parse_args()

    if args.list or (not args.try_name and not args.test):
        print("=" * 74)
        print(f"可用人设（{len(PERSONAS)} 个）")
        print("=" * 74)
        for i, (name, sysp) in enumerate(PERSONAS.items(), 1):
            first = sysp.splitlines()[0]
            print(f"\n  {i:2d}. 【{name}】")
            print(f"      {first}")
        print()
        print("  用法：")
        print("    python week4\\personas.py --try 极简主义者")
        print('    python week4\\personas.py --try 杠精 --ask "我觉得早睡没必要"')
        print("    python week4\\personas.py --test     ← 测能不能修掉已知问题")
        return 0

    if args.try_name:
        if args.try_name not in PERSONAS:
            print(f"❌ 没有人设「{args.try_name}」。用 --list 看可用的")
            return 2
        run_try(args.try_name, args.ask)

    if args.test:
        run_test()
    return 0


if __name__ == "__main__":
    sys.exit(main())
