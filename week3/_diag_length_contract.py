"""验证两件事：
  1. prompt_tokens 的算术关系（确认 history 结构真的对）
  2. 对照实验：同一组问题，只改 system 里的长度约束，看输出长度
     这比"改动前后各跑一次"可靠 —— 因为它把随后几轮的历史长度差异
     也一起量进去了（那正是输出契约的连锁效应）
"""
import os
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv(os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".env")))
client = OpenAI(api_key=os.getenv("API_KEY"), base_url=os.getenv("BASE_URL"))
MODEL = os.getenv("MODEL")
THINKING_OFF = {"thinking": {"type": "disabled"}}

QS = ["什么是列表推导式", "它和map有什么区别", "那什么时候用哪个"]


def ask(messages):
    r = client.chat.completions.create(model=MODEL, messages=messages, extra_body=THINKING_OFF)
    return (r.choices[0].message.content or "").strip(), r.usage


# ============ 第 1 部分：算术验证 ============
print("=" * 72)
print("第 1 部分：prompt_tokens 的算术关系")
print("=" * 72)
print()
print("  你的实测（带长度约束）：")
rows = [("轮1", 25, 87, 112), ("轮2", 120, 62, 182), ("轮3", 190, 61, 251)]
print(f"  {'':<6}{'prompt':>8}{'completion':>12}{'total':>8}")
for name, p, c, t in rows:
    ok = (p + c == t)
    print(f"  {name:<6}{p:>8}{c:>12}{t:>8}   prompt+completion==total ? {ok}")

print()
print("  跨轮验证：下一轮的 prompt 应该 ≈ 这一轮的 total + 新问题的 token")
for i in range(len(rows) - 1):
    nxt_p = rows[i + 1][1]
    cur_t = rows[i][3]
    diff = nxt_p - cur_t
    print(f"  轮{i+1} total={cur_t:<5} -> 轮{i+2} prompt={nxt_p:<5} 差 {diff:+d}"
          f"  ← 新问题「{QS[i+1]}」的 token 数")

# ============ 第 2 部分：对照实验 ============
print()
print("=" * 72)
print("第 2 部分：对照实验 —— 只改 system 的长度约束")
print("=" * 72)

SYS_NO = "你是一个耐心的 Python 助手"
SYS_YES = "你是一个耐心的 Python 助手。每次回答控制在 3 句话以内。"

results = {}
for label, sysmsg in [("无长度约束", SYS_NO), ("有长度约束", SYS_YES)]:
    print(f"\n--- {label} ---")
    history = [{"role": "system", "content": sysmsg}]
    comps, prompts = [], []
    for q in QS:
        history.append({"role": "user", "content": q})
        txt, usage = ask(history)
        history.append({"role": "assistant", "content": txt})
        comps.append(usage.completion_tokens)
        prompts.append(usage.prompt_tokens)
    results[label] = (comps, prompts)
    print(f"  completion_tokens 逐轮: {comps}   合计 {sum(comps)}")
    print(f"  prompt_tokens     逐轮: {prompts}   合计 {sum(prompts)}   （末轮 {prompts[-1]}）")
    print(f"  末轮回答长度: {len(txt)} 字")
    print(f"  末轮回答: {txt[:110]}")

print()
print("=" * 72)
print("对比")
print("=" * 72)
(na, pa) = results["无长度约束"]
(yes_a, yes_p) = results["有长度约束"]
print(f"  completion 合计: 无约束 {sum(na)}  vs  有约束 {sum(yes_a)}"
      f"   →  {(1 - sum(yes_a) / sum(na)) * 100:.0f}% 降幅")
print(f"  prompt   末轮  : 无约束 {pa[-1]}  vs  有约束 {yes_p[-1]}"
      f"   →  {(1 - yes_p[-1] / pa[-1]) * 100:.0f}% 降幅")
print()
print("  ★ 注意 prompt 的差别是【连锁效应】：")
print("    第 1 轮 prompt 几乎一样（只差 system 那十几个字），")
print("    但从第 2 轮起，因为上一轮回答短了，历史也短了 → 越往后差得越多。")
