"""D4 的核心对照：为什么需要「正则兜底」？

同一段【措辞含糊】的 prompt，各跑一次：
  软约束（不加 response_format）  vs  硬约束（加 response_format）

重点看「原始返回」——不是看模型答得好不好，是看它【包了什么外壳】。
"""
import json
import os
import re
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv(os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".env")))
client = OpenAI(api_key=os.getenv("API_KEY"), base_url=os.getenv("BASE_URL"))
MODEL = os.getenv("MODEL")
OFF = {"thinking": {"type": "disabled"}}

# ★ 故意用【含糊】的措辞（只说"用 JSON 格式给我"，没说"只输出 JSON"）
text = "张小明这次数学考了 88 分，语文 92 分。"
VAGUE = f'从下面的文本中抽取信息，用 JSON 格式给我。\n\n文本：{text}'

# 你 D4 里那种【明确】的措辞（对照组）
EXPLICIT = (f'从下面的文本中抽取信息，只输出 JSON，不要任何其他文字。\n'
            f'格式：{{"姓名": "", "科目": "", "分数": 0}}\n\n文本：{text}\n')


def call(prompt, use_format, n=3):
    outs = []
    for _ in range(n):
        kw = {"response_format": {"type": "json_object"}} if use_format else {}
        r = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": prompt}],
            extra_body=OFF, **kw)
        outs.append((r.choices[0].message.content or "").strip())
    return outs


def parse_status(raw):
    """这个返回，能不能被程序吃掉？"""
    try:
        json.loads(raw)
        return "✅ 直接可解析"
    except Exception:
        pass
    m = re.search(r"\{.*\}", raw, re.S)
    if m:
        try:
            json.loads(m.group(0))
            return "⚠️ 需正则兜底"
        except Exception:
            return "❌ 有花括号但解析失败"
    return "❌ 没有 JSON"


print("=" * 74)
print("【含糊措辞】" + repr(VAGUE))
print("=" * 74)

for label, use in [("软约束（不加 response_format）", False),
                   ("硬约束（加 response_format）", True)]:
    outs = call(VAGUE, use)
    print(f"\n--- {label} ---")
    for i, raw in enumerate(outs, 1):
        print(f"  [{i}] {parse_status(raw)}   长度 {len(raw)}")
        print(f"      {raw[:130]!r}")
    n_bad = sum(1 for r in outs if not parse_status(r).startswith("✅"))
    print(f"  → 3 次里有 {n_bad} 次不能被程序直接吃掉")

print()
print("=" * 74)
print("【明确措辞 + 无格式要求】—— 对照，看是不是措辞的功劳")
print("=" * 74)
outs = call(EXPLICIT, False)
for i, raw in enumerate(outs, 1):
    print(f"  [{i}] {parse_status(raw)}   长度 {len(raw)}")
    print(f"      {raw[:100]!r}")

print()
print("=" * 74)
print("结论")
print("=" * 74)
print("""  1. 软约束最典型的失败【不是"不输出 JSON"】，而是
     "输出 JSON 但套了一层 markdown 代码块 ```json ... ```"
     → 这时候 json.loads() 直接报错，而模型觉得自己答得挺好
  2. 正则兜底存在的唯一理由：把代码块和说明文字扒掉，只留花括号那段
  3. 但也救不了全部：如果模型压根没输出花括号 → 只能重试或改 prompt
  4. 硬约束（response_format）从 API 层保证 → 没有这些问题

  ★ 所以 D4 的"两套方案"不是冗余：
     方案一是首选（能用就用），方案二是【降级】路线（模型不支持时兜住）
""")
