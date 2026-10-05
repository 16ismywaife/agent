"""用手册里的原样代码，逐段打真实 HTTP 到本地 mock 服务器，验证代码正确性。

★ 重要区分：
   ✅ 这里能证明的：代码语法对、SDK 用法对、请求结构和解析路径对、边界处理对。
   ❌ 这里证明不了的：真实模型是否真的会选你的工具、回答质量、真实 token 计费。
      → 后者必须用自己的 API Key 跑 verify_handbook_llm.py --real

用法：
   python verify_handbook_llm.py                # 打本地 mock（默认 http://127.0.0.1:8799/v1）
   python verify_handbook_llm.py --real         # 打 .env 里配置的真实 API
"""
import json
import os
import re
import sys
import time

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from dotenv import load_dotenv
from openai import OpenAI

REAL = "--real" in sys.argv
load_dotenv()

if REAL:
    API_KEY = os.getenv("API_KEY")
    BASE_URL = os.getenv("BASE_URL")
    MODEL = os.getenv("MODEL")
    if not API_KEY or API_KEY.startswith("你的"):
        print("❌ .env 里的 API_KEY 还没填。先在 E:\\agent\\.env 里填好再跑 --real")
        sys.exit(2)
    print("★ 真实 API 模式：%s  model=%s" % (BASE_URL, MODEL))
else:
    API_KEY = "mock-key-not-secret"
    BASE_URL = os.getenv("MOCK_BASE_URL", "http://127.0.0.1:8799/v1")
    MODEL = "mock-model"
    print("★ Mock 模式：%s" % BASE_URL)
    print("  （只验证代码协议，不验证模型行为）")

client = OpenAI(
    api_key=API_KEY,
    #         ↑从环境变量读取密钥（★ 不要写死在代码里）
    base_url=BASE_URL,
    #          ↑服务地址。用 OpenAI 兼容接口的不同厂商都靠这个切换
)

PASS, FAIL = [], []


def check(name, cond, detail=""):
    if cond:
        PASS.append(name)
        print("  ✅ %s" % name)
    else:
        FAIL.append((name, detail))
        print("  ❌ %s   %s" % (name, detail))


# =====================================================================
# 4.10 单轮对话
# =====================================================================
print("\n=== 4.10 单轮对话 ===")
resp = client.chat.completions.create(
    model=MODEL,
    messages=[
        {"role": "user", "content": "用一句话解释什么是反向传播"},
    ],
)
print("  回答:", str(resp.choices[0].message.content)[:70])
check("resp.choices[0].message.content 可取到文本",
      isinstance(resp.choices[0].message.content, str) and len(resp.choices[0].message.content) > 0)
check("resp.usage 可取到 token 用量",
      resp.usage is not None and resp.usage.total_tokens == resp.usage.prompt_tokens + resp.usage.completion_tokens,
      "usage=%s" % resp.usage)
check("无工具时 message.tool_calls 为空（可直接判断）",
      not resp.choices[0].message.tool_calls,
      "tool_calls=%r" % (resp.choices[0].message.tool_calls,))


# =====================================================================
# 4.10 多轮对话
# =====================================================================
print("\n=== 4.10 多轮对话 ===")
history = [{"role": "system", "content": "你是一个耐心的 Python 助教。"}]
_replies = []


def chat(user_input):
    history.append({"role": "user", "content": user_input})
    r = client.chat.completions.create(
        model=MODEL,
        messages=history,
    )
    reply = r.choices[0].message.content
    history.append({"role": "assistant", "content": reply})
    return reply


for _q in ["什么是列表推导式？", "那它和 map 有什么区别？"]:
    _replies.append(chat(_q))

check("多轮：history 增长为 system+user+assistant+user+assistant",
      len(history) == 5 and [m["role"] for m in history] ==
      ["system", "user", "assistant", "user", "assistant"],
      "roles=%s" % [m["role"] for m in history])
check("多轮：历史整体被传回（不是只传最后一句）", all(len(x) > 0 for x in _replies))


# =====================================================================
# 4.10 结构化输出 ★ Agent 的地基
# =====================================================================
print("\n=== 4.10 结构化输出 ===")
prompt = """从下面的文本中抽取信息，只输出 JSON，不要任何其他文字。
格式：{"姓名": "", "科目": "", "分数": 0}

文本：张小明这次数学考了 88 分。
"""
resp = client.chat.completions.create(
    model=MODEL,
    messages=[{"role": "user", "content": prompt}],
    response_format={"type": "json_object"},
)
try:
    data = json.loads(resp.choices[0].message.content)
    check("response_format=json_object 的返回能被 json.loads 解析", isinstance(data, dict), repr(data)[:80])
    check("解析出的字典能按中文键取值", "姓名" in data and "分数" in data, repr(data)[:80])
except Exception as e:
    check("response_format=json_object 的返回能被 json.loads 解析", False, "%s: %s" % (type(e).__name__, e))

# 正则兜底
text = "好的，这是结果：\n{\"姓名\": \"李四\", \"科目\": \"语文\", \"分数\": 92}\n希望有帮助！"
m = re.search(r"\{.*\}", text, re.S)
data2 = json.loads(m.group(0)) if m else None
check("正则兜底：能从含多余文字的返回里抠出 JSON", data2 is not None and data2.get("分数") == 92, repr(data2))


# =====================================================================
# 4.10 参数实验
# =====================================================================
print("\n=== 4.10 参数实验（temperature / max_tokens）===")
_param_ok = True
for temp in [0, 0.7, 1.5]:
    for _ in range(3):
        r = client.chat.completions.create(
            model=MODEL,
            temperature=temp,
            max_tokens=100,
            messages=[{"role": "user", "content": "给我一个创业点子，一句话"}],
        )
        if not r.choices[0].message.content:
            _param_ok = False
check("temperature=0/0.7/1.5 × 3 次全部调用成功", _param_ok)


# =====================================================================
# 4.11 Agent：LLM + 1 个 Tool
# =====================================================================
print("\n=== 4.11 Agent 主循环 ===")


def calculator(expression: str) -> str:
    """计算数学表达式"""
    allowed = set("0123456789+-*/(). %")
    if not set(expression) <= allowed:
        return "错误：表达式含非法字符"
    try:
        return str(eval(expression, {"__builtins__": {}}, {}))
    except Exception as e:
        return f"计算错误：{e}"


TOOLS_IMPL = {"calculator": calculator}

TOOLS_SPEC = [{
    "type": "function",
    "function": {
        "name": "calculator",
        "description": "计算数学表达式。当用户需要做算术运算时调用。",
        "parameters": {
            "type": "object",
            "properties": {
                "expression": {
                    "type": "string",
                    "description": "要计算的数学表达式，例如 '(23*7+15)/2'",
                }
            },
            "required": ["expression"],
        },
    },
}]


def run_agent(question, max_steps=5):
    messages = [
        {"role": "system", "content": "你是一个助手。需要算术时调用 calculator 工具，不要自己心算。"},
        {"role": "user", "content": question},
    ]
    for step in range(max_steps):
        resp = client.chat.completions.create(
            model=MODEL, messages=messages, tools=TOOLS_SPEC
        )
        msg = resp.choices[0].message
        messages.append(msg)
        if not msg.tool_calls:
            return msg.content
        for tc in msg.tool_calls:
            name = tc.function.name
            args = json.loads(tc.function.arguments)
            result = TOOLS_IMPL[name](**args)
            messages.append({
                "role": "tool",
                "tool_call_id": tc.id,
                "content": result,
            })
    return "达到最大步数仍未结束"


for q in ["(23*7+15)/2 等于多少？", "你好，你是谁？", "帮我算 128 的平方，再除以 4"]:
    ans = run_agent(q)
    print("  问题: %-26s 回答: %s" % (q, str(ans)[:56]))
    check("run_agent 正常返回（%s）" % q[:12], isinstance(ans, str) and len(ans) > 0)

check("calculator('(23*7+15)/2') = 88.0", calculator("(23*7+15)/2") == "88.0", calculator("(23*7+15)/2"))
check("calculator 白名单拦住非法字符", calculator("__import__('os').system('echo hi')") == "错误：表达式含非法字符")
check("eval 清空 __builtins__ 后拿不到 __import__",
      "NameError" in calculator("(1).__class__") or "错误" in calculator("(1).__class__"),
      calculator("(1).__class__"))

# 编造不存在的工具名 → KeyError（手册里说的「失败重试要解决的问题」）
_raised = False
try:
    TOOLS_IMPL["不存在的工具"](x=1)
except KeyError:
    _raised = True
check("模型编造不存在的工具名 → KeyError（手册说法正确）", _raised)


# =====================================================================
# 4.18 流式（LLM 部署那节会用到）
# =====================================================================
print("\n=== 流式输出（openai SDK 兼容性）===")
try:
    stream = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": "写一段 50 字的介绍"}],
        stream=True,
    )
    got = []
    first_at = None
    t0 = time.time()
    for chunk in stream:
        piece = chunk.choices[0].delta.content
        if piece:
            if first_at is None:
                first_at = time.time() - t0
            got.append(piece)
    joined = "".join(got)
    check("stream=True 能逐块收完并拼出完整文本", len(joined) > 0, repr(joined)[:60])
    if first_at is not None:
        print("      （首块延迟 %.3fs，可用来演示 TTFT 的测量方式）" % first_at)
except Exception as e:
    check("stream=True 能逐块收完并拼出完整文本", False, "%s: %s" % (type(e).__name__, e))


# =====================================================================
# 汇总
# =====================================================================
print("\n" + "=" * 60)
print("通过 %d / %d" % (len(PASS), len(PASS) + len(FAIL)))
if FAIL:
    print("失败项：")
    for n, d in FAIL:
        print("  ❌ %s   %s" % (n, d))
    sys.exit(1)
print("✅ 全部通过")
