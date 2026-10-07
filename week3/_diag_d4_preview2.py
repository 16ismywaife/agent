"""D4 预习（第二轮）：找一个"软约束会失效"的真实场景。

上一轮发现：prompt 里写了「只输出 JSON」，软约束就够了，加不加 response_format 一样。
所以关键问题是：什么情况下软约束不够？

候选原因：
  · prompt 措辞含糊（没明确说"只输出 JSON"）
  · 任务本身有"想解释"的冲动（比如要判断、要分析）
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

CASES = [
    ("① 措辞含糊（没说'只输出 JSON'）",
     '从下面的文本中抽取信息，用 JSON 格式给我。\n\n文本：张小明这次数学考了 88 分，语文 92 分。'),
    ("② 有'想解释'的冲动（要判断）",
     '判断下面这句话是正面还是负面评价，并用 JSON 给出结果。\n\n句子：这个方案我觉得不太行。'),
    ("③ 措辞明确 + 无解释冲动（对照）",
     '从下面的文本中抽取信息，只输出 JSON，不要任何其他文字。\n'
     '格式：{"姓名": "", "科目": "", "分数": 0}\n\n文本：张小明这次数学考了 88 分。'),
]


def call(prompt, **kw):
    r = client.chat.completions.create(model=MODEL,
                                       messages=[{"role": "user", "content": prompt}],
                                       extra_body=OFF, **kw)
    return (r.choices[0].message.content or "").strip(), r.usage


def status(raw):
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
    return "❌ 完全没有 JSON"


for label, prompt in CASES:
    print("=" * 74)
    print(label)
    print("=" * 74)
    for mode, kw in [("软约束（只靠 prompt）", {}),
                     ("硬约束（response_format）", {"response_format": {"type": "json_object"}})]:
        try:
            raw, u = call(prompt, **kw)
            print(f"\n  【{mode}】completion={u.completion_tokens}  {status(raw)}")
            print(f"    {raw[:220]}")
        except Exception as e:
            print(f"\n  【{mode}】❌ {type(e).__name__}: {str(e)[:150]}")
    print()
