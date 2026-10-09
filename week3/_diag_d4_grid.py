"""补齐 D4 的实验数据：你这句明确措辞，在【软约束】下是什么样。

目的：把「措辞」和「约束」这两个因素拆开，做成 2x2 对照。
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

text = "张小明这次数学考了 88 分，语文 92 分。"

# 你这句：措辞明确（"只输出 JSON"）+ 给了格式
EXPLICIT = (f'从下面的文本中抽取信息，只输出 JSON，不要任何其他文字。\n'
            f'格式：{{"姓名": "", "科目": "", "分数": 0}}\n\n文本：{text}\n')

# 我对照实验那句：措辞含糊
VAGUE = f'从下面的文本中抽取信息，用 JSON 格式给我。\n\n文本：{text}'

N = 5


def run(prompt, use_format):
    outs = []
    for _ in range(N):
        kw = {"response_format": {"type": "json_object"}} if use_format else {}
        r = client.chat.completions.create(
            model=MODEL, messages=[{"role": "user", "content": prompt}],
            extra_body=OFF, **kw)
        outs.append((r.choices[0].message.content or "").strip())
    return outs


def status(raw):
    try:
        json.loads(raw)
        return "直接可解析"
    except Exception:
        pass
    m = re.search(r"\{.*\}", raw, re.S)
    if m:
        try:
            json.loads(m.group(0))
            return "需正则兜底"
        except Exception:
            return "有花括号但失败"
    return "没有JSON"


print("=" * 78)
print(f"2x2 对照（每组各跑 {N} 次）")
print("=" * 78)
grid = {}
for plabel, prompt in [("明确措辞", EXPLICIT), ("含糊措辞", VAGUE)]:
    for clabel, use in [("软约束", False), ("硬约束", True)]:
        outs = run(prompt, use)
        st = [status(o) for o in outs]
        ok = sum(1 for s in st if s == "直接可解析")
        wrapped = sum(1 for s in st if s == "需正则兜底")
        lens = [len(o) for o in outs]
        grid[(plabel, clabel)] = (ok, wrapped, lens)
        print(f"\n【{plabel} + {clabel}】")
        print(f"  直接可解析 {ok}/{N}    需兜底 {wrapped}/{N}")
        print(f"  长度分布 {lens}")
        for s, o in zip(st, outs):
            print(f"    {s:<12} {o[:95]!r}")

print()
print("=" * 78)
print("汇总表（写进 docs 用）")
print("=" * 78)
print(f"  {'':<10}{'软约束':<22}{'硬约束'}")
for plabel in ["明确措辞", "含糊措辞"]:
    row = f"  {plabel:<10}"
    for clabel in ["软约束", "硬约束"]:
        ok, wrapped, lens = grid[(plabel, clabel)]
        row += f"{ok}/{N} 直接可解析{'':<8}"
    print(row)
print()
print("  长度中位数：")
for plabel in ["明确措辞", "含糊措辞"]:
    line = f"  {plabel:<10}"
    for clabel in ["软约束", "硬约束"]:
        lens = sorted(grid[(plabel, clabel)][2])
        line += f"{lens[len(lens)//2]:<22}"
    print(line)
