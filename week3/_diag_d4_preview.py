"""D4 预习实验：结构化输出到底在解决什么，两种方案各自什么行为。

三个对照，同一段文本、同一个抽取任务：
  1. 什么都不加         ← 基线：模型想怎么答就怎么答
  2. + response_format  ← 方案一：API 层强制 JSON
  3. 解析失败会怎样      ← 正则兜底到底在兜什么
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

TEXT = "张小明这次数学考了 88 分，语文 92 分。"
PROMPT = ('从下面的文本中抽取信息，只输出 JSON，不要任何其他文字。\n'
          '格式：{"姓名": "", "科目": "", "分数": 0}\n\n'
          f'文本：{TEXT}\n')


def call(**kw):
    r = client.chat.completions.create(model=MODEL, messages=[{"role": "user", "content": PROMPT}],
                                       extra_body=OFF, **kw)
    return (r.choices[0].message.content or ""), r.usage


def try_parse(raw):
    """两种解析方式都试，返回 (直接json是否成功, 正则兜底是否成功, 结果)"""
    try:
        return True, True, json.loads(raw)
    except Exception:
        pass
    m = re.search(r"\{.*\}", raw, re.S)
    if not m:
        return False, False, None
    try:
        return False, True, json.loads(m.group(0))
    except Exception:
        return False, False, None


print("=" * 74)
print("对照 1：什么都不加（只靠 prompt 里那句「只输出 JSON」）")
print("=" * 74)
raw1, u1 = call()
print("原始返回：")
print(repr(raw1)[:400])
ok1 = try_parse(raw1)
print(f"\n  直接 json.loads 成功: {ok1[0]}")
print(f"  正则兜底成功        : {ok1[1]}")
print(f"  解析结果            : {ok1[2]}")
print(f"  completion_tokens   : {u1.completion_tokens}")

print()
print("=" * 74)
print("对照 2：加 response_format={'type':'json_object'}（API 层强制）")
print("=" * 74)
try:
    raw2, u2 = call(response_format={"type": "json_object"})
    print("原始返回：")
    print(repr(raw2)[:400])
    ok2 = try_parse(raw2)
    print(f"\n  直接 json.loads 成功: {ok2[0]}")
    print(f"  正则兜底成功        : {ok2[1]}")
    print(f"  解析结果            : {ok2[2]}")
    print(f"  completion_tokens   : {u2.completion_tokens}")
except Exception as e:
    print(f"  ❌ {type(e).__name__}: {str(e)[:200]}")

print()
print("=" * 74)
print("对照 3：正则兜底在兜什么 —— 拿「模型加了废话」的假数据演示")
print("=" * 74)
fake_good = '{"姓名": "张小明", "科目": "数学", "分数": 88}'
fake_bad = '好的，我帮你抽取出来了：\n\n```json\n{"姓名": "张小明", "科目": "数学", "分数": 88}\n```\n\n希望有帮助！'
fake_none = '这段文本里提到了张小明，数学考了 88 分。'
for label, text in [("纯 JSON", fake_good), ("JSON 外套了说明文字和代码块", fake_bad), ("完全没有 JSON", fake_none)]:
    d_ok, r_ok, val = try_parse(text)
    print(f"\n  【{label}】")
    print(f"    直接解析: {'✅' if d_ok else '❌'}    正则兜底: {'✅' if r_ok else '❌'}")
    print(f"    结果: {val}")

print()
print("=" * 74)
print("结论")
print("=" * 74)
print("  1. 「只输出 JSON」是【软约束】—— 和 D3 的「3 句话以内」同一类")
print("  2. response_format 是【硬约束】—— 由 API 层保证，模型没有不听的选项")
print("  3. 正则兜底要处理三种情况：纯 JSON / 套了废话 / 没 JSON")
print("     ★ 注意「套了废话」那种：代码块 ```json 里的内容，正则\\{.*\\}也能抠出来")
print("  4. 三种情况里，只有「没 JSON」是真没法救 —— 得让它重试")
