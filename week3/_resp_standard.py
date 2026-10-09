"""resp 的标准版 —— 不嵌套任何辅助函数，一行行直接写。

这份文件是给你「看清结构」用的，不是给你背的。
它只做一件事：调一次 API，然后把 resp 的每一层都拆开打出来。
"""
import json
import os
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from dotenv import load_dotenv
from openai import OpenAI

# ============================================================
# 第 1 部分：准备 client（标准写法，就这四行）
# ============================================================
load_dotenv()                                    # 把 .env 读进环境变量

client = OpenAI(
    api_key=os.getenv("API_KEY"),                # 从环境变量读，不写死在代码里
    base_url=os.getenv("BASE_URL"),              # 换成别的厂商只改这一个值
)

MODEL = os.getenv("MODEL")                       # 用哪个模型

print("=" * 72)
print("第 1 部分：client 就绪")
print("=" * 72)
print(f"  client   = {type(client).__name__}")
print(f"  MODEL    = {MODEL}")

# ============================================================
# 第 2 部分：调一次 API（标准写法，核心就这几行）
# ============================================================
print()
print("=" * 72)
print("第 2 部分：调一次 API，拿到 resp")
print("=" * 72)

resp = client.chat.completions.create(
    model=MODEL,
    messages=[
        {"role": "user", "content": "用一句话解释什么是反向传播"},
    ],
    # ── 下面是可选参数，用一个加一个 ──
    # temperature=0,                                  # 随机性：要确定性就用 0
    # max_tokens=500,                                 # 输出长度上限
    # response_format={"type": "json_object"},        # 强制输出 JSON
    # extra_body={"thinking": {"type": "disabled"}},  # 关掉思考（厂商私有参数）
)

print(f"  resp 的类型 = {type(resp).__name__}")
print("  ↑ 这不是字典，是 SDK 的对象。但访问方式很像")

# ============================================================
# 第 3 部分：把 resp 一层层拆开
# ============================================================
print()
print("=" * 72)
print("第 3 部分：resp 的每一层长什么样")
print("=" * 72)

print(f"\n  resp.model          = {resp.model!r}")
print(f"  resp.id             = {resp.id!r}")
print("    ↑ 本次请求的唯一编号，报错找客服时用它")

print(f"\n  resp.choices        = 一个列表，长度 {len(resp.choices)}")
print("    ↑ 一般只有 1 个（除非你传了 n=2 之类要多个候选）")

choice = resp.choices[0]
print(f"\n  resp.choices[0]                = 第 0 个候选")
print(f"    .finish_reason               = {choice.finish_reason!r}")
print("      ↑ 为什么停下来：stop / length / tool_calls / content_filter")
print(f"    .index                       = {choice.index}")

msg = choice.message
print(f"\n  ....message                    = 模型这条消息")
print(f"      .role                      = {msg.role!r}")
print(f"      .content                   = {msg.content!r}")
print("        ↑ ★ 正文在这里。但注意：调工具时它是空字符串，不是 None")
print(f"      .tool_calls                = {msg.tool_calls}")
print("        ↑ 要调工具时才有值；这里是 None 说明它直接回答了")
print(f"      .reasoning_content         = {getattr(msg, 'reasoning_content', '（没有这个字段）')!r}")
print("        ↑ 思考过程。★ 本次没关思考（这是默认行为），所以它出现了")
print("          想省钱/要干净结果 → 传 extra_body={'thinking':{'type':'disabled'}}")

print(f"\n  resp.usage                     = token 用量")
u = resp.usage
print(f"    .prompt_tokens                = {u.prompt_tokens}")
print(f"    .completion_tokens            = {u.completion_tokens}")
print(f"    .total_tokens                 = {u.total_tokens}")
print("      ★ 校验：prompt + completion 应该等于 total")
print(f"         {u.prompt_tokens} + {u.completion_tokens} = {u.prompt_tokens + u.completion_tokens}"
      f"  → {'✅ 对得上' if u.prompt_tokens + u.completion_tokens == u.total_tokens else '❌ 对不上'}")

# ============================================================
# 第 4 部分：实际取正文的两种写法
# ============================================================
print()
print("=" * 72)
print("第 4 部分：实际用的时候，取正文就这几种写法")
print("=" * 72)

one_line = resp.choices[0].message.content
print(f"\n  写法 1（一行到底，最常用）：")
print(f"    resp.choices[0].message.content")
print(f"    → {one_line!r}")

print(f"\n  写法 2（拆开，报错好定位）：")
first_choice = resp.choices[0]
message = first_choice.message
text = message.content
print(f"    first_choice = resp.choices[0]")
print(f"    message      = first_choice.message")
print(f"    text         = message.content")
print(f"    → {text!r}")

print(f"\n  写法 3（判空 + 带 fallback，最稳）：")
safe = resp.choices[0].message.content or "（模型没给正文）"
print(f"    resp.choices[0].message.content or '...'")
print(f"    → {safe!r}")
print("    ↑ ★ 加 or 兜底：调工具时 content 是空字符串，直接拿去解析会出问题")

# ============================================================
# 第 5 部分：怎么「看到」整个 resp（调试用）
# ============================================================
print()
print("=" * 72)
print("第 5 部分：调试时怎么把整个 resp 打出来")
print("=" * 72)
print("""
  print(resp)                       ← 只给一行摘要，看不全
  print(resp.model_dump())          ← ★ 转成字典再打印，能看到全部字段
  print(resp.model_dump_json(indent=2))  ← 转成带缩进的 JSON 文本
""")
print("  resp.model_dump() 里 choices[0] 的内容：")
dumped = resp.model_dump()
print("   ", json.dumps(dumped["choices"][0], ensure_ascii=False, indent=4)[:500])
print()
print(f"  usage: {dumped['usage']}")
print()
print("  ★ 记住 model_dump() —— 排查「到底返回了什么」时，比 print(resp) 有用得多")
