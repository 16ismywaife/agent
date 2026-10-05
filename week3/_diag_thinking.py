"""诊断 deepseek-flash 的思考模式对 temperature / max_tokens 的影响。

要回答三个问题：
  1. max_tokens 是否包含 reasoning tokens？（导致正文被截空）
  2. temperature 是否被思考模式忽略？（不同温度输出完全相同）
  3. 能不能关掉思考模式，关掉后行为是否恢复正常？
"""
import os
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from dotenv import load_dotenv
from openai import OpenAI

ENV = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".env")
load_dotenv(os.path.normpath(ENV))

client = OpenAI(api_key=os.getenv("API_KEY"), base_url=os.getenv("BASE_URL"))
MODEL = os.getenv("MODEL")
print("模型:", MODEL)

Q = "给我一个创业点子，一句话"


def call(**kw):
    r = client.chat.completions.create(model=MODEL, messages=[{"role": "user", "content": Q}], **kw)
    c = r.choices[0].message.content or ""
    d = r.usage.completion_tokens_details
    reason = getattr(d, "reasoning_tokens", None) if d else None
    return c.strip(), r.usage.completion_tokens, reason, r.choices[0].finish_reason


print("\n" + "=" * 66)
print("问题 1：max_tokens 包不包括思考 token？")
print("=" * 66)
for mt in [10, 100, 500]:
    c, ct, rt, fin = call(max_tokens=mt)
    print(f"  max_tokens={mt:<4} 输出总token={ct:<5} 其中思考={rt}  finish={fin:<8} 正文长度={len(c)}")
    print(f"     正文: {c[:60] if c else '（空！）'}")

print("\n  ★ 若 max_tokens=100 时正文为空而思考 token 接近 100，说明思考占了预算")

print("\n" + "=" * 66)
print("问题 2：temperature 是否还起作用？（不限制 max_tokens，各跑 4 次）")
print("=" * 66)
for temp in [0, 1.5]:
    outs = []
    for _ in range(4):
        c, ct, rt, fin = call(temperature=temp)
        outs.append(c)
    uniq = len(set(outs))
    print(f"  temperature={temp}: 4 次产生 {uniq} 种不同输出")
    for i, o in enumerate(outs[:2], 1):
        print(f"     [{i}] {o[:70]}")

print("\n" + "=" * 66)
print("问题 3：关掉思考模式会怎样？")
print("=" * 66)
for label, extra in [
    ("thinking=disabled", {"extra_body": {"thinking": {"type": "disabled"}}}),
    ("thinking=enabled ", {"extra_body": {"thinking": {"type": "enabled"}}}),
]:
    try:
        cs = []
        for _ in range(4):
            r = client.chat.completions.create(
                model=MODEL,
                messages=[{"role": "user", "content": Q}],
                temperature=1.5,
                **extra,
            )
            cs.append((r.choices[0].message.content or "").strip())
        d = r.usage.completion_tokens_details
        rt = getattr(d, "reasoning_tokens", None) if d else None
        print(f"  {label}: 4 次 {len(set(cs))} 种不同输出，最后一次思考token={rt}")
        print(f"     例子: {cs[0][:70]}")
    except Exception as e:
        print(f"  {label}: ❌ {type(e).__name__}: {str(e)[:150]}")

print("\n" + "=" * 66)
print("问题 4：关掉思考后，max_tokens=100 的正文还在吗？")
print("=" * 66)
try:
    c, ct, rt, fin = call(max_tokens=100)
    print(f"  默认(带思考) max_tokens=100 -> 正文长度 {len(c)}, finish={fin}")
except Exception as e:
    print("  ❌", e)
try:
    r = client.chat.completions.create(
        model=MODEL, messages=[{"role": "user", "content": Q}],
        max_tokens=100, extra_body={"thinking": {"type": "disabled"}},
    )
    c = (r.choices[0].message.content or "").strip()
    d = r.usage.completion_tokens_details
    rt = getattr(d, "reasoning_tokens", None) if d else None
    print(f"  关闭思考 max_tokens=100 -> 正文长度 {len(c)}, 思考token={rt}, finish={r.choices[0].finish_reason}")
    print(f"     正文: {c[:80]}")
except Exception as e:
    print("  ❌", type(e).__name__, str(e)[:200])
