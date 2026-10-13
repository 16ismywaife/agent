"""Week4 · Agent：LLM + 1 个 Tool

★★ 这个文件是【骨架】。标着 TODO 的地方要你自己写。★★

分工（和 week3/day1.py 一样的规矩）：
  · 外面的部分（环境自检 / 报错诊断 / argparse / completion 包装）
    是【脚手架】—— 写好了，不用动。
  · 下面留 TODO 的是【你的交付物】。

按天分工：
  D1（今天）：TOOLS_SPEC（工具说明）+ calculator（工具本体）  ← 只做这两个
  D2（明天）：run_agent（主循环）

用法：
  python week4\\agent_calc.py --sanity    # 只发一次请求，看模型返回什么（不执行工具）
  python week4\\agent_calc.py            # 跑 Agent（D2 之前会提示还没写）
  python week4\\agent_calc.py --check    # 只自检，不发请求

参考手册：4.11 Agent：LLM + 1 个 Tool
想对答案 → week4/answer/agent_calc_answer.py（D2 时提供）
"""
import argparse
import json
import os
import sys
from email import message

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from dotenv import load_dotenv
from datetime import datetime

# ============================================================
# 以下到「你的交付物」为止，全是脚手架，不用改
# ============================================================

OK = "✅"
BAD = "❌"
WARN = "⚠️"


def head(t):
    print("\n" + "=" * 62)
    print(t)
    print("=" * 62)


def check_env():
    """自检：Key / 地址 / 模型名 / .env 是否安全。"""
    head("第 1 步 · 环境自检")

    ok = True
    env_path = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".env"))

    if os.path.exists(env_path):
        print(f"{OK} 找到 .env：{env_path}")
        try:
            import subprocess
            repo = os.path.dirname(env_path)
            inside = subprocess.run(["git", "rev-parse", "--is-inside-work-tree"],
                                    cwd=repo, capture_output=True, text=True)
            if inside.returncode != 0:
                print(f"{WARN} 这里不是 git 仓库，跳过 .env 忽略检查")
            else:
                r = subprocess.run(["git", "check-ignore", "-q", ".env"],
                                   cwd=repo, capture_output=True)
                if r.returncode == 0:
                    print(f"{OK} .env 已被 .gitignore 排除（安全）")
                else:
                    print(f"{BAD} .env 【没有】被 .gitignore 排除！")
                    ok = False
        except Exception as e:
            print(f"{WARN} 跳过 git 检查（{type(e).__name__}）")
    else:
        print(f"{BAD} 没找到 .env：{env_path}")
        ok = False

    load_dotenv(env_path)

    api_key = os.getenv("API_KEY")
    base_url = os.getenv("BASE_URL")
    model = os.getenv("MODEL")

    if not api_key:
        print(f"{BAD} API_KEY 是空的")
        ok = False
    else:
        print(f"{OK} API_KEY 已读到：{api_key[:6]}…{api_key[-4:]}（长度 {len(api_key)}）")
        if api_key != api_key.strip():
            print(f"{BAD} API_KEY 首尾有空格！这会导致 401")
            ok = False

    if not base_url:
        print(f"{BAD} BASE_URL 是空的")
        ok = False
    else:
        print(f"{OK} BASE_URL = {base_url}")

    if not model:
        print(f"{BAD} MODEL 是空的")
        ok = False
    else:
        print(f"{OK} MODEL = {model}")

    return ok, api_key, base_url, model


def build_client(api_key, base_url):
    from openai import OpenAI
    return OpenAI(api_key=api_key, base_url=base_url)


THINKING_OFF = {"thinking": {"type": "disabled"}}


def completion(client, model, **kw):
    """统一入口：默认关掉思考模式（原因见 week3/day1.py 那段注释）。

    ★ 但 Agent 这里有个新问题要想：调工具需要"推理"吗？
      思考开着可能让模型更会选工具，但会吃 token、也可能干扰 tool_calls。
      这个取舍留到 D2 实测。
    """
    extra = dict(kw.pop("extra_body", {}) or {})
    extra.update(THINKING_OFF)
    return client.chat.completions.create(model=model, extra_body=extra, **kw)


def diagnose(e):
    """把异常翻译成「你该去改哪里」。"""
    name = type(e).__name__
    print(f"\n{BAD} 调用失败：{name}")
    print(f"   原始信息：{str(e)[:300]}")
    tips = {
        "AuthenticationError": ["API_KEY 不对，检查 .env"],
        "NotFoundError": ["MODEL 名字不对（deepseek-flash，不是 deepseek-chat）"],
        "APIConnectionError": ["连不上，检查 BASE_URL 和网络"],
        "BadRequestError": [
            "请求参数不被支持。★ Agent 常见原因：这个模型不支持 tools 参数",
            "可以先跑 --sanity 确认 tools 能不能传",
        ],
    }
    for t in tips.get(name, ["看上面的原始信息，对照手册 6.10 节"]):
        print(f"   → {t}")


# ============================================================
# ★★★ 你的交付物 ★★★
# ============================================================


# ---------------------------------------------------------------- D1 第一件
def calculator(expression: str) -> str:
    """计算数学表达式。★ 这是【真正执行】的地方 —— 模型不执行任何东西。

    要做三件事：
      1. 白名单校验：expression 里只允许出现
         数字 0-9 和这些符号： + - * / ( ) . 空格 和 %
         （用集合的子集判断：set(expression) <= allowed）
         → 不合法就 return 一个错误说明（不要抛异常）
      2. 用 eval() 计算，但【必须】清空内置函数：
         eval(expression, {"__builtins__": {}}, {})
         → 不清空的话，别人输入 __import__('os').system('rm -rf /') 就完了
      3. 用 try/except 包住，把结果转成字符串返回
         → ★ 工具执行失败不要让整个 Agent 崩掉，返回错误文本让模型知道

    返回：结果的字符串形式，或错误说明
    """
    # TODO: 在这里写你的代码
    allowed=set("0123456789+-*/(). %")
    if not set(expression) <= allowed:
        return "错误，含未知字符"
    try:
        return str(eval(expression, {"__builtins__": {}}, {}))
    except Exception as e:
        return f"计算错误{e}"

def get_time()->str:
    return datetime.now().astimezone().isoformat()


# ---------------------------------------------------------------- D1 第二件
# 名字 → 函数 的映射，后面 run_agent 靠它按名字找到函数
TOOLS_IMPL = {
    # TODO: 把 calculator 注册进来
    #       提示：{"calculator": calculator}
    "calculator": calculator,
    "get_time":get_time
}

# ★ 工具描述：告诉模型「有哪些工具可用、什么时候该用」
#   模型就是靠这份描述决定调不调工具的 —— 所以 description 要写清楚
TOOLS_SPEC = [
    # TODO: 按下面的结构写（这是 OpenAI function-calling 的标准格式）
    {"type":"function",
     "function":{
         "name":"calculator",
         "description":"计算数学表达式。当用户需要做算术运算时调用。",
         "parameters":{
             "type":"object",
             "properties":{
                 "expression":{
                     "type":"string",
                     "description":"要计算的数学表达式，例如 '(23*7+15)/2'",
                 }
             },
             "required":["expression"],
         },
     },
     },
    {"type":"function",
     "function":{
         "name":"get_time",
         "description":"获取当前时间，当用户询问你当前时间时调用",
         "parameters":{
             "type":"object",
             "properties":{},
             "required": [],

         },
     },
     },
]


# ---------------------------------------------------------------- D2 主循环
def run_agent(client, model, question, max_steps=5):
    """D2 ★ 本周重点 · Agent 主循环。

    要做的事（手册 4.11 有完整代码和逐行注释）：
      1. 先建 messages，两条：
           {"role": "system", "content": "……需要算术时调用 calculator，不要自己心算"}
           ↑ ★ 为什么 system 里要加这句？你的工具 description 只管"我是什么"，
             这句管"你必须用它、别自己算" —— 少了它模型会选择硬算
           {"role": "user", "content": question}
      2. for step in range(max_steps):        ← ★ 为什么要这个上限？（自查第 3 条）
      3. 循环里发请求：走 completion(...)，参数带 tools=TOOLS_SPEC
      4. 取 msg = r.choices[0].message，★ 先把它 append 进 messages
           （不 append 的话，下一轮模型不知道"我刚才已经要调工具了"）
      5. ★ 出口：msg 没有 tool_calls（空列表或 None）→ 它要直接回答 → return msg.content
      6. 否则遍历 msg.tool_calls，对每个 tc：
           name   = tc.function.name
           args   = json.loads(tc.function.arguments)   ← ★ 字符串 → 字典
           result = TOOLS_IMPL[name](**args)            ← ★ 真正执行的是【你的代码】
           messages.append({"role": "tool",
                            "tool_call_id": tc.id,       ← ★ 就是它把"结果"和"请求"对上号
                            "content": result})
      7. 循环跑满 max_steps 还没 return → 说明出问题了。
           返回一句说明（★ 不要静默返回 None —— 那会让调用方以为模型没说话）

    返回：最终回答的字符串。

    三个坑（手册点名 + D1 你亲手踩过的）：
      · tc.function.arguments 是【JSON 字符串】。不 json.loads 就直接下标 → 报错
      · TOOLS_IMPL 的值必须是【函数对象】—— D1 你这里踩过（"get_time" 加了引号变字符串）
      · 模型可能编一个【不存在的工具名】→ TOOLS_IMPL[name] 抛 KeyError
        ★ 想清楚：让它崩，还是接住、回一句"没有这个工具"给模型？
          这就是 Week5「失败重试」的种子问题 —— D2 先想，不用做

    要能回答（手册 D2 自查 4 条 + 培养方案 5 问）：
      ① 模型怎么知道有哪些工具可用？   ② 工具是谁执行的？
      ③ 为什么要 max_steps？            ④ tool_call_id 干什么的？
      ⑤ 模型编造一个不存在的工具名会怎样？
    """
    messages=[{"role":"system","content":"需要算术时调用 calculator；需要当前日期/时间时调用 get_time。都不要自己编。"},
              {"role":"user","content":question}
              ]
    for step in range(max_steps):
        r=completion(client,model,messages=messages,tools=TOOLS_SPEC)
        msg=r.choices[0].message
        messages.append(msg)

        if not msg.tool_calls:
            return msg.content

        for tc in msg.tool_calls:
            args=json.loads(tc.function.arguments)
            result=TOOLS_IMPL[tc.function.name](**args)
            messages.append({"role": "tool", "tool_call_id": tc.id, "content": result})

    return "达到最大步数还未结束"


# ============================================================
# 下面是工具函数和入口，不用改
# ============================================================


def sanity(client, model):
    """D1 用：只发一次请求，把模型的原始返回摊开给你看。

    ★ 这个函数【不执行】任何工具 —— 只为让你看清"模型要调工具时返回什么"。
    """
    head("D1 · 只发一次请求，看模型返回什么")
    question = "帮我算一下 (23*7+15)/2 等于多少"
    print(f"  问题：{question}")
    print(f"  工具描述：{'已定义' if TOOLS_SPEC else '❌ TOOLS_SPEC 还是空的'}")
    print()

    if not TOOLS_SPEC:
        print(f"{WARN} 你还没写 TOOLS_SPEC —— 先做 D1 那两件（calculator + TOOLS_SPEC）")
        return

    try:
        r = completion(
            client, model,
            messages=[{"role": "user", "content": question}],
            tools=TOOLS_SPEC,
        )
    except Exception as e:
        diagnose(e)
        return

    msg = r.choices[0].message
    print(f"  finish_reason = {r.choices[0].finish_reason!r}")
    print(f"  msg.content   = {msg.content!r}")
    print("    ↑ ★ 注意：要调工具时这里是空字符串，不是回答")
    print(f"  msg.tool_calls= {msg.tool_calls if not msg.tool_calls else f'{len(msg.tool_calls)} 个'}")
    print()

    if msg.tool_calls:
        for tc in msg.tool_calls:
            print(f"  模型要求调：{tc.function.name}")
            print(f"    参数（★ 是一串 JSON 文本，不是字典）：{tc.function.arguments!r}")
            args = json.loads(tc.function.arguments)
            print(f"    json.loads 之后：{args}")
            print()
            print("  ★ 到这里为止，模型只做了'决定调什么'。")
            print("    真正执行的是【你的代码】—— D2 写 run_agent 就是干这个。")
            print()
            print("  你可以手动试一下你的工具执行得对不对：")
            try:
                result = TOOLS_IMPL[tc.function.name](**args)
                print(f"    {tc.function.name}(**{args}) = {result!r}")
            except NotImplementedError as e:
                print(f"    {WARN} {e}")
            except KeyError:
                print(f"    {BAD} TOOLS_IMPL 里没有 '{tc.function.name}' —— 你注册了吗？")
    else:
        print(f"{WARN} 模型没要求调工具 —— 可能是 TOOLS_SPEC 的 description 写得太含糊")
        print("     它直接回答了，说明它觉得不需要用工具")


def main():
    ap = argparse.ArgumentParser(description="Week4 · Agent：LLM + 1 个 Tool")
    ap.add_argument("--check", action="store_true", help="只自检，不发请求")
    ap.add_argument("--sanity", action="store_true", help="只发一次请求，看模型返回什么（不执行工具）")
    args = ap.parse_args()

    ok, api_key, base_url, model = check_env()
    if not ok:
        print(f"\n{BAD} 自检没过，先把上面的问题解决。")
        return 2
    print(f"\n{OK} 自检通过")

    if args.check:
        print("\n（--check：只自检，不发请求）")
        return 0

    client = build_client(api_key, base_url)
    print("\n下一步会真的调用 API，会产生少量 token 消耗。")

    try:
        if args.sanity:
            sanity(client, model)
        else:
            head("跑 Agent")
            print(run_agent(client, model, "帮我算一下 (23*7+15)/2 等于多少"))
            print()
            print(run_agent(client, model, "今天几号？"))
            print(run_agent(client, model, "你好，你是谁？"))
    except NotImplementedError as e:
        print(f"\n{WARN} {e}")
        print("   → D1：先写 calculator 和 TOOLS_SPEC，然后跑 --sanity")
        print("   → D2：再写 run_agent")
        return 3
    except Exception as e:
        diagnose(e)
        return 1

    head("完成")
    return 0


if __name__ == "__main__":
    sys.exit(main())
