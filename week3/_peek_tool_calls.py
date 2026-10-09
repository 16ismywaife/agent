"""Week4 预告：tool_calls 到底长什么样 —— 用真实 API 看一次。

目的：把"难度会不会飙升"变成可测量的东西。
     不是讲原理，是把【真实结构】打出来。
"""
import json
import os
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv(os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".env")))
client = OpenAI(api_key=os.getenv("API_KEY"), base_url=os.getenv("BASE_URL"))
MODEL = os.getenv("MODEL")
OFF = {"thinking": {"type": "disabled"}}

# 工具定义：就是你 Week3 学的「结构化输出」，只不过这次是描述【你能做什么】
TOOL = {
    "type": "function",
    "function": {
        "name": "calculator",
        "description": "计算数学表达式。当用户需要做算术运算时调用。",
        "parameters": {
            "type": "object",
            "properties": {
                "expression": {"type": "string", "description": "数学表达式，例如 '(23*7+15)/2'"}
            },
            "required": ["expression"],
        },
    },
}

Q = "帮我算一下 (23*7+15)/2 等于多少"

print("=" * 76)
print("第 1 步：把工具说明 + 问题发过去，看模型回什么")
print("=" * 76)
r = client.chat.completions.create(
    model=MODEL,
    messages=[{"role": "user", "content": Q}],
    tools=[TOOL],
    extra_body=OFF,
)
msg = r.choices[0].message

print(f"  finish_reason = {r.choices[0].finish_reason!r}")
print(f"  msg.content   = {msg.content!r}          ← ★ 空字符串！（话说一半改去要工具了）")
print(f"  msg.tool_calls 有 {len(msg.tool_calls)} 个")
print()
print("  tool_calls[0] 的完整结构：")
tc = msg.tool_calls[0]
print(f"    tc.id                  = {tc.id!r}")
print(f"    tc.type                = {tc.type!r}")
print(f"    tc.function.name       = {tc.function.name!r}")
print(f"    tc.function.arguments  = {tc.function.arguments!r}   ← ★ 是【字符串】不是字典")
print()
print("  ★ 关键：arguments 是一串 JSON 文本，要用 json.loads 转成字典：")
args = json.loads(tc.function.arguments)
print(f"    json.loads(...)        = {args}   (type={type(args).__name__})")
print(f"    于是可以调用：calculator(**{args})")

print()
print("=" * 76)
print("第 2 步：假设我们执行了工具，把结果发回去，看它怎么收尾")
print("=" * 76)
# 真正执行（就是 Week3 学的那个白名单 + eval）
allowed = set("0123456789+-*/(). %")
expr = args["expression"]
result = str(eval(expr, {"__builtins__": {}}, {})) if set(expr) <= allowed else "非法字符"
print(f"  我们自己执行：{expr} = {result}")

messages = [
    {"role": "user", "content": Q},
    msg,                                        # ★ 把模型那条（含 tool_calls）原样加回历史
    {"role": "tool", "tool_call_id": tc.id, "content": result},   # ★ 必须带 tool_call_id
]
r2 = client.chat.completions.create(model=MODEL, messages=messages, tools=[TOOL], extra_body=OFF)
msg2 = r2.choices[0].message
print(f"  finish_reason = {r2.choices[0].finish_reason!r}")
print(f"  msg.content   = {msg2.content!r}")
print(f"  msg.tool_calls= {msg2.tool_calls}          ← None/空 = 它不再要工具了")
print()
print("  → 此时发给 API 的 messages 有 %d 条：" % len(messages))
for m in messages:
    role = m.get("role") if isinstance(m, dict) else m.role
    if isinstance(m, dict):
        extra = " +tool_call_id" if m.get("role") == "tool" else ""
        print(f"     {role:<10}{extra}")
    else:
        print(f"     {role:<10}+tool_calls（模型要调工具的请求）")

print()
print("=" * 76)
print("第 3 步：如果模型编造一个不存在的工具名会怎样")
print("=" * 76)
print("  （不实测，因为要伪造返回。但结论明确：）")
print("    TOOLS_IMPL[模型给的名字]  →  KeyError")
print("    这就是手册 4.11 五个问题里那条「失败重试要解决的问题」")

print()
print("=" * 76)
print("对照：这和你 Week3 做的有什么不同")
print("=" * 76)
print("""  相同：请求结构、messages 列表、response_format 那套「让模型吐结构化输出」
  不同：多了一个 tools 参数；返回里多一个 tool_calls 字段
        正文变成空字符串（话说一半改去要工具了）—— 别急着 print 正文
        finish_reason 从 stop 变成 tool_calls
        ★ 多了一个「循环」：要工具 → 执行 → 发回 → 再问 → 直到它不要工具
""")
