"""Week3 · D1 —— 跑通第一次 LLM 调用

★★ 这个文件是【骨架】。标着 TODO 的地方要你自己写。★★

分工（重要，别搞错）：
  · 外面的部分（自检 / 报错诊断 / argparse / completion 包装）
    是【脚手架】—— 我写好了，你不用动，也不用理解每一行。
  · 下面 5 个函数体是【你的交付物】—— 必须你自己写。

     d1_single      单轮对话，并把 token 用量打出来
     d2_prompt      同一问题发两次：不带 system / 带 system
     d3_multi       多轮对话，自己维护 history 列表
     d4_structured  response_format 强制 JSON，再用正则兜底
     d5_params      temperature / max_tokens 参数实验

参考手册：4.10 LLM / API 调用（有完整解释和逐行注释）

想对答案 → week3/answer/day1_answer.py
  但先自己写。写不出来再看 —— 卡住的地方就是你的真实盲区。

用法：
  python week3\\day1.py --check      # 只自检，不花钱、不发请求（先跑这个）
  python week3\\day1.py              # D1 单轮对话
  python week3\\day1.py --all        # 填完 5 个函数后跑全部

★ 提示：先只填 d1_single，跑通 `--check` 和默认模式，再往下填。
  一次填 5 个再调，报错会糊在一起。
"""
import argparse
import json
import os
import re
import sys
import time
from idlelib import history

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from dotenv import load_dotenv

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

    env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".env")
    env_path = os.path.normpath(env_path)
    if os.path.exists(env_path):
        print(f"{OK} 找到 .env：{env_path}")

        # 安全检查：.env 绝不能被 git 跟踪。这是最容易出人命的一步。
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
                    print("    危险：一旦 commit，API Key 会进 git 历史，删 commit 也删不干净")
                    print("    解决：在 .gitignore 里加一行 .env，然后 git status 确认看不到它")
                    ok = False
        except FileNotFoundError:
            print(f"{WARN} 没装 git，跳过 .env 忽略检查（请自己确认 .env 没被提交）")
        except Exception as e:
            print(f"{WARN} 跳过 git 检查（{type(e).__name__}）")
    else:
        print(f"{BAD} 没找到 .env：{env_path}")
        print("    解决：copy .env.example .env   然后填上 API_KEY / BASE_URL / MODEL")
        ok = False

    load_dotenv(env_path)

    api_key = os.getenv("API_KEY")
    base_url = os.getenv("BASE_URL")
    model = os.getenv("MODEL")

    if not api_key:
        print(f"{BAD} API_KEY 是空的")
        print("    常见原因：.env 里写的是 API_KEY=你的密钥（占位符没替换）")
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
        if not base_url.rstrip("/").endswith("/v1"):
            print(f"{WARN} 国内厂商的兼容接口通常要以 /v1 结尾，检查一下")

    if not model:
        print(f"{BAD} MODEL 是空的")
        ok = False
    else:
        print(f"{OK} MODEL = {model}")

    return ok, api_key, base_url, model


def build_client(api_key, base_url):
    from openai import OpenAI
    return OpenAI(api_key=api_key, base_url=base_url)


# ---------------------------------------------------------------- 思考模式
# deepseek-flash 默认【开启思考】。实测（见 week3/_diag_thinking.py）发现两件必须知道的事：
#   1. max_tokens 把【思考 token 算在内】。实测 max_tokens=100 时，
#      100 个 token 全被思考吃掉 → 正文是空字符串、finish_reason=length。
#   2. 思考要花钱（算在 completion_tokens 里），简单任务上纯属浪费。
# 这一周的实验统一关掉思考，让结果干净、便宜、可复现。
THINKING_OFF = {"thinking": {"type": "disabled"}}


def completion(client, model, **kw):
    """统一入口：默认关掉思考模式。

    为什么要包一层：openai SDK 不认 thinking 这个字段，要经 extra_body 透传。
    换厂商后如果对方不认这个字段，去掉 THINKING_OFF 即可 —— 不传就是默认行为。
    """
    extra = dict(kw.pop("extra_body", {}) or {})
    extra.update(THINKING_OFF)
    return client.chat.completions.create(model=model, extra_body=extra, **kw)


def diagnose(e, base_url):
    """把 openai 的异常翻译成「你该去改哪里」。"""
    name = type(e).__name__
    print(f"\n{BAD} 调用失败：{name}")
    print(f"   原始信息：{str(e)[:300]}")

    tips = {
        "AuthenticationError": [
            "API_KEY 不对。检查 .env 里的值有没有多余空格或引号",
            "确认这个 Key 属于 BASE_URL 对应的那家厂商（别把 A 家的 Key 配到 B 家的地址）",
        ],
        "NotFoundError": [
            f"MODEL 名字不对，或者服务地址不对（当前 BASE_URL={base_url}）",
            "★ 网上老教程里的 deepseek-chat / deepseek-reasoner 已失效，现在用 deepseek-flash",
        ],
        "APIConnectionError": [
            f"连不上 {base_url}。检查网络 / 需不需要代理",
            "确认 BASE_URL 没写错，且带了 /v1",
        ],
        "RateLimitError": [
            "被限流或余额不足。等一会儿，或去厂商后台看余额",
        ],
        "BadRequestError": [
            "请求参数不被支持。Week3 最常见的是模型不支持 response_format=json_object",
        ],
    }
    for t in tips.get(name, ["看上面的原始信息，对照手册 6.10 节（LLM / API 类报错表）"]):
        print(f"   → {t}")
    print("\n   环境自检能过、但调用失败，问题基本就在上面这几条里。")

def ask(client, model, messages,**kw):
    """通用调用：传什么 messages 就发什么，返回 (正文, usage)。

    为什么要有它：D2~D5 全在做「改一个变量、看输出怎么变」，
    每次都要重复那三行调用代码。抽成一个函数，实验代码才干净。
    """
    r = completion(client, model, messages=messages,**kw)
    return r.choices[0].message.content, r.usage


# ============================================================
# ★★★ 你的交付物：下面 5 个函数体，全部要你自己写 ★★★
# ============================================================


def d1_single(client, model):
    """D1 · 单轮对话。

    要做四件事：
      1. 记开始时间（用 time.time()）
      2. 发一次请求 —— 用上面那个 completion() 包装，别直接调
         client.chat.completions.create（不然你会丢掉关思考的设置）
         · 参数：messages=[{"role": "user", "content": "用一句话解释什么是反向传播"}]
      3. 从返回里取出正文，打印出来
      4. 打印 token 用量，并算出耗时

    返回：正文（字符串）。main() 不检查返回值，但后续函数会用到这个模式。

    提示：返回对象的结构（手册 4.10 有图）
        resp.choices[0].message.content   → 正文
        resp.usage                        → token 用量（含 prompt_tokens / completion_tokens）
    """
    head("D1 · 单轮对话")

    # TODO: 在这里写你的代码（把下面这行删掉）
    t0 = time.time()
    resp=completion(client, model,
                    messages=[{"role":"user","content":"你好"}])
    print(resp.choices[0].message.content)
    print(resp.usage)
    print(f"{time.time() - t0:.2f}s")


def d2_prompt(client, model):
    """D2 · Prompt 基础：对比「有没有 system 角色」。

    要做的：
      1. 定一个待改写的中文句子，例如 "把这句话改得更正式：这个方案我觉得不太行"
      2. 发第一次：messages 里【只有】user
      3. 发第二次：messages 里【先】system（比如「你是一名严谨的技术文档编辑，
         只输出改写后的句子」）【再】user，内容完全相同
      4. 把两次输出分别打印出来，让人一眼看出差别

    为什么要做这个：手册说 system 用来"设定人设"。你要自己验证这句话是不是真的。
    """
    head("D2 · Prompt 基础（角色 + few-shot）")

    t0 = time.time()
    SENT = "把这句话改得更正式：这个方案我觉得不太行"
    SYS = "你是一名严谨的技术文档编辑。把句子改写得更正式（书面、用于工作场合），只输出改写后的句子。"
    N = 5

    print(f"每组各跑 {N} 次。★ 重点不看单条好不好，看这 {N} 次的【一致性】\n")

    print("--- 无 system ---")
    for i in range(N):
        txt, _ = ask(client, model, [{"role": "user", "content": SENT}])
        print(f"[{i + 1}] ({len(txt)}字) {txt}")

    print("\n--- 有 system ---")
    for i in range(N):
        txt, _ = ask(client, model, [{"role": "system", "content": SYS},
                                     {"role": "user", "content": SENT}])
        print(f"[{i + 1}] ({len(txt)}字) {txt}")

    print(f"\n总耗时 {time.time() - t0:.2f}s")

def d3_multi(client, model, turns=3):
    """D3 · 多轮对话：自己维护 history 列表。

    ★ 这一段的核心认知：模型本身没有记忆。
      「它记得上一句」是因为你把历史【全部】传回去了。

    要做的：
      1. 建一个 history 列表，第一条是 system（例如「你是一个耐心的 Python 助教，
         回答尽量短」）
      2. 依次问这 3 个问题（这样第 2、3 个问题在语义上依赖前文，
         如果历史没传对，模型会答不上来）：
           "什么是列表推导式？"
           "它和 map 有什么区别？"
           "那什么时候该用哪个？"
      3. 每一轮：
           · 把 user 那条 append 进 history
           · 把【整个 history】传给 API
           · 把模型的回复也 append 进 history（否则下一轮它就"忘了"）
      4. 最后打印 history 的长度，并说明它就是上下文管理问题的来源

    最容易忘的一步：把模型回复 append 回 history。漏了的话，
    模型下一轮看不到自己说过什么，多轮就变成单轮了。
    """
    head("D3 · 多轮对话（历史要自己传）")

    # TODO: 在这里写你的代码
    history=[{"role":"system","content":"你是一个耐心的 Python 助手。每次回答控制在 3 句话以内。"}]
    questions=["什么是列表推导式","它和map有什么区别","那什么时候用哪个"]

    for q in questions:
        history.append({"role":"user","content":q})
        txt,usage=ask(client, model, history)
        history.append({"role":"assistant","content":txt})
        print(f"question:{q},reply:{txt},usage:{usage}")
        print(len(history))


def d4_structured(client, model):
    """D4 · 结构化输出 ★ Agent 的地基（本周最重要的一段）

    要做的两套方案：
      方案一：response_format={"type": "json_object"} 强制模型输出合法 JSON
              · prompt 里明确说"只输出 JSON，不要其他文字"，并给出格式
              · 文本可以用："张小明这次数学考了 88 分，语文 92 分。"
              · 拿到返回后用 json.loads() 解析
              · ★ 用 try/except 包住：不是所有模型都支持这个参数
      方案二：正则兜底 —— 模型在 JSON 前后加了说明文字时用这个救
              · re.search(r"\\{.*\\}", 文本, re.S) 把 JSON 抠出来
              · 注意 re.S 让 . 能匹配换行

    打印时把「原始返回」也打出来 —— 你要亲眼看到模型到底吐了什么。

    ★ 为什么这段最重要：Tool Calling 本质就是「让模型吐结构化输出」。
      这一步没搞明白，Week4 的 Agent 会卡住。
    """
    head("D4 · 结构化输出 ★ Agent 的地基")

    # TODO: 在这里写你的代码
    text="张小明这次数学考了 88 分，语文 92 分。"
    prompt=(f'从下面的文本中抽取信息，只输出 JSON，不要任何其他文字。\n'
              f'格式：{{"姓名": "", "科目": "", "分数": 0}}\n\n文本：{text}\n')
    txt=None
    try:
        txt,usage=ask(client,model, [{"role":"user","content":prompt}], response_format={"type":"json_object"})
        print(f"reply:{txt},usage:{usage}")
    except Exception as e:
        print("不支持 response_format：", e)

    print("原始返回:", repr(txt))  # ← 缩进回到函数层
    m = re.search(r"\{.*\}", txt or "", re.S)  # ← txt 可能是 None
    if m:
        print("兜底解析成功：", json.loads(m.group(0)))
    else:
        print("正则也没抠到 —— 只能重试或改 prompt")



def d5_params(client, model):
    """D5 · 参数实验：temperature / max_tokens

    两个实验都要做，而且都要【打印出让人能下结论的表格】。

    实验一：temperature
      · 试 [0, 0.7, 1.5] 三个值
      · 每个值重复请求 4 次（同一个问题，例如"给我一个创业点子，一句话"）
      · 统计这 4 次里有几种【不同】的输出，打印出来
      · 你要能回答：temperature 到底改变了什么？

      ⚠️ 这里有个坑，你要自己撞一次才算学会：
         如果你把 max_tokens 设小了（比如 60），正文可能被截成【空字符串】，
         于是 4 次"空"会被统计成"输出相同" —— 你会得出
         「temperature 不起作用」这个【错误结论】。
         所以：max_tokens 给足（比如 800），并且打印内容本身，
         别只看统计数字。

    实验二：max_tokens
      · 试 [50, 100, 500] 三个值，问同一个问题（例如"用三句话介绍什么是机器学习"）
      · 对每个值打印：返回的正文字符数、finish_reason
      · finish_reason 的取值含义：stop = 正常说完；length = 被 max_tokens 截断
      · 你要能回答：为什么设小了会拿到【空】正文？（提示：想想思考模式）

    参考手册 4.10「参数实验」那一节。
    """
    head("D5 · 参数实验（temperature / max_tokens）")

    # TODO: 在这里写你的代码
    raise NotImplementedError("d5_params 还没写")


# ============================================================
# 下面是入口，不用改
# ============================================================


def main():
    ap = argparse.ArgumentParser(description="Week3 D1 —— 跑通第一次 LLM 调用")
    ap.add_argument("--check", action="store_true", help="只做环境自检，不发请求（不花钱）")
    ap.add_argument("--all", action="store_true", help="跑 D1~D5 全部示例")
    ap.add_argument("--only", type=int, metavar="N",
                    help="只跑第 N 天（1~5）。写一天时用这个，不会撞到还没写的函数")
    args = ap.parse_args()

    ok, api_key, base_url, model = check_env()
    if not ok:
        print(f"\n{BAD} 自检没过，先把上面的问题解决。")
        print("   不想花钱、想先确认代码对不对 → python _verify\\verify_handbook_llm.py")
        return 2
    print(f"\n{OK} 自检通过")

    if args.check:
        print("\n（--check：只自检，不发请求）")
        return 0

    client = build_client(api_key, base_url)
    print("\n下一步会真的调用 API，会产生少量 token 消耗。")

    # 把「第 N 天」映射到函数。--only 用它挑一个跑，方便逐天写。
    days = {1: d1_single, 2: d2_prompt, 3: d3_multi, 4: d4_structured, 5: d5_params}

    try:
        if args.only is not None:
            if args.only not in days:
                print(f"{BAD} --only 只能是 1~5，你给的是 {args.only}")
                return 2
            days[args.only](client, model)
        else:
            d1_single(client, model)
            if args.all:
                for n in (2, 3, 4, 5):
                    days[n](client, model)
    except NotImplementedError as e:
        print(f"\n{WARN} {e}")
        print("   → 打开 week3\\day1.py，找到这个函数，把 TODO 那段写掉。")
        print("   → 卡住了看 week3\\answer\\day1_answer.py，或者问。")
        return 3
    except Exception as e:
        diagnose(e, base_url)
        return 1

    head("完成")
    print(f"{OK} 跑完了。")
    if args.only is None and not args.all:
        print("   逐天写代码时建议用 --only，例如： python week3\\day1.py --only 2")
        print("   D2~D5 全跑：                    python week3\\day1.py --all")
    print("\n接下来按手册第 5 章「第 3 周」往下走：")
    print("   D2 Prompt 基础  D3 多轮对话  D4 ★ 结构化输出  D5 参数实验")
    print("\n★ 别忘了：把今天做的事写进 notes/log.md（三行就够）")
    return 0


if __name__ == "__main__":
    sys.exit(main())
