"""复现：content 写成 "prompt"（带引号）为什么报「Prompt must contain the word 'json'」。"""
import os
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv(os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".env")))
client = OpenAI(api_key=os.getenv("API_KEY"), base_url=os.getenv("BASE_URL"))
MODEL = os.getenv("MODEL")
OFF = {"thinking": {"type": "disabled"}}

text = "张小明这次数学考了 88 分，语文 92 分。"
prompt = (f'从下面的文本中抽取信息，只输出 JSON，不要任何其他文字。\n'
          f'格式：{{"姓名": "", "科目": "", "分数": 0}}\n\n文本：{text}\n')

print("=" * 72)
print("先看两个「东西」分别是什么")
print("=" * 72)
print(f"  prompt   变量 → {prompt!r}")
print(f"  \"prompt\" 字面量 → {'prompt'!r}")
print()
print("  ★ 差在一对引号：加了引号就不是变量了，是四个字母的【字符串】")

print()
print("=" * 72)
print("用真实 API 各发一次，看结果")
print("=" * 72)

for label, content in [('❌ content: "prompt"（带引号）', "prompt"),
                       ("✅ content: prompt（变量）", prompt)]:
    print(f"\n--- {label} ---")
    print(f"    实际发出的 content = {content!r}")
    try:
        r = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": content}],
            response_format={"type": "json_object"},
            extra_body=OFF,
        )
        out = (r.choices[0].message.content or "").strip()
        print(f"    ✅ 成功，返回: {out[:110]}")
    except Exception as e:
        msg = str(e)
        # 只留关键那句
        if "Prompt must contain" in msg:
            print(f"    ❌ 400: Prompt must contain the word 'json' in some form...")
            print(f"       ← 因为你发过去的正文就是 'prompt' 这四个字母")
        else:
            print(f"    ❌ {type(e).__name__}: {msg[:180]}")
