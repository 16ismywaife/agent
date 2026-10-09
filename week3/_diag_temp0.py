"""验证：temperature=0 到底有多"确定"？

背景：D3 记录里我写过「temperature=0 时输出仍可能不同（3 种）」，
      但用户两次跑 D5 时 temperature=0 都是「1 种」。
      —— 两种说法对不上，要查清。

方法：
  · 同一句话，temperature=0 连发 10 次，看有几种不同输出
  · 同一句话，temperature=1.5 连发 10 次，作对照
  · max_tokens 给足（避免 D1 那个"空字符串被当成相同"的假象）
"""
import os
import sys
from collections import Counter

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv(os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".env")))
client = OpenAI(api_key=os.getenv("API_KEY"), base_url=os.getenv("BASE_URL"))
MODEL = os.getenv("MODEL")
OFF = {"thinking": {"type": "disabled"}}

Q = "给我一个创业点子，一句话"
N = 10


def run(temp):
    outs = []
    for _ in range(N):
        r = client.chat.completions.create(
            model=MODEL, messages=[{"role": "user", "content": Q}],
            temperature=temp, max_tokens=800, extra_body=OFF)
        outs.append((r.choices[0].message.content or "").strip())
    return outs


for temp in [0, 1.5]:
    outs = run(temp)
    uniq = Counter(outs)
    blank = sum(1 for o in outs if not o)
    print("=" * 72)
    print(f"temperature={temp}   连发 {N} 次")
    print("=" * 72)
    print(f"  不同输出: {len(uniq)} 种    空字符串: {blank} 个")
    for text, cnt in uniq.most_common():
        print(f"    [{cnt} 次] {text[:76]!r}")
    print()

print("=" * 72)
print("判读")
print("=" * 72)
print("""  · temperature=0 若 10 次全相同 → 它确实【高度确定】，D3 那条记录要修正为
    「temperature=0 基本可复现，但不同厂商/模型不保证绝对一致」
  · 若出现 2 种以上 → D3 的说法成立：temperature=0 只是【降低】随机性
  注意：这里只测了一个模型（deepseek-flash），换模型结论可能不同。
""")
