"""验证 D3 的关键：第 2、3 个问题不带历史时，模型答不上来。

这两个问题里都有人称代词/指代：
  第 2 问「它和 map 有什么区别？」   ← "它" 指谁？
  第 3 问「那什么时候该用哪个？」     ← "哪个" 指什么？
所以如果不带历史，模型没有前提可依，答案必然跑偏。
—— 这就是 D3 自带的"验证机制"：写错了，肉眼就能看出来。
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

Q2 = "它和 map 有什么区别？"
Q3 = "那什么时候该用哪个？"


def ask(messages):
    r = client.chat.completions.create(model=MODEL, messages=messages,
                                       extra_body=THINKING_OFF)
    return (r.choices[0].message.content or "").strip()


print("=" * 70)
print("对照组：把第 2 问【孤立】提问（不带任何历史）")
print("=" * 70)
print(f"问：{Q2}")
print("答：", ask([{"role": "user", "content": Q2}])[:400])

print()
print("=" * 70)
print("对照组：把第 3 问【孤立】提问（不带任何历史）")
print("=" * 70)
print(f"问：{Q3}")
print("答：", ask([{"role": "user", "content": Q3}])[:400])

print()
print("=" * 70)
print("实验组：带历史（第 1 问 + 模型的回答 + 第 2 问）")
print("=" * 70)
history = [{"role": "system", "content": "你是一个耐心的 Python 助教，回答尽量短。"}]
history.append({"role": "user", "content": "什么是列表推导式？"})
a1 = ask(history)
history.append({"role": "assistant", "content": a1})
print("第 1 问答：", a1[:200])
print()
history.append({"role": "user", "content": Q2})
a2 = ask(history)
print(f"问：{Q2}")
print("答：", a2[:400])
print()
print(f"→ 此时发给 API 的 messages 有 {len(history) + 1} 条：")
for m in history + [{"role": "assistant", "content": a2}]:
    print(f"   {m['role']:<10} {str(m['content'])[:46]}")
