"""同一批问题，本地 qwen3.5:4b vs 云端 deepseek-flash —— 差距量化。

不只是"哪个更聪明"，而是看【具体差在哪】：
  · 指令遵循（说"只输出 JSON"，它听不听）
  · system 作为输出契约（Week3 D2 的结论在弱模型上还成立吗）
  · 简单推理
"""
import json
import os
import re
import sys
import time
import urllib.request

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from dotenv import load_dotenv
from openai import OpenAI

REPO = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
load_dotenv(os.path.join(REPO, ".env"))

# 本地：走原生 API（因为 /v1 关不掉思考）
LOCAL_API = "http://127.0.0.1:11434/api/chat"
LOCAL_MODEL = "qwen3.5:4b"

# 云端
cloud = OpenAI(api_key=os.getenv("API_KEY"), base_url=os.getenv("BASE_URL"))
CLOUD_MODEL = os.getenv("MODEL")


def ask_local(messages, max_tokens=400):
    body = {"model": LOCAL_MODEL, "messages": messages, "think": False,
            "stream": False, "options": {"num_predict": max_tokens, "temperature": 0}}
    req = urllib.request.Request(LOCAL_API, data=json.dumps(body).encode(),
                                 headers={"Content-Type": "application/json"})
    t0 = time.time()
    d = json.loads(urllib.request.urlopen(req, timeout=600).read().decode())
    return {"text": (d.get("message", {}).get("content") or "").strip(),
            "secs": time.time() - t0, "tok": d.get("eval_count")}


def ask_cloud(messages, max_tokens=400):
    t0 = time.time()
    r = cloud.chat.completions.create(model=CLOUD_MODEL, messages=messages,
                                      max_tokens=max_tokens, temperature=0,
                                      extra_body={"thinking": {"type": "disabled"}})
    return {"text": (r.choices[0].message.content or "").strip(),
            "secs": time.time() - t0, "tok": r.usage.completion_tokens}


def json_ok(t):
    try:
        json.loads(t); return "✅ 直接可解析"
    except Exception:
        pass
    m = re.search(r"\{.*\}", t, re.S)
    if m:
        try:
            json.loads(m.group(0)); return "⚠️ 需正则兜底"
        except Exception:
            return "❌ 有花括号但坏"
    return "❌ 不是 JSON"


TESTS = [
    ("① 指令遵循：只输出 JSON（中文键）",
     [{"role": "user", "content":
       '从文本抽取信息，只输出 JSON 不要其他文字。\n'
       '格式：{"姓名": "", "科目": "", "分数": 0}\n\n'
       '文本：张小明这次数学考了 88 分。'}]),

    ("② system 当输出契约（Week3 D2 的结论）",
     [{"role": "system", "content": "你是一名严谨的技术文档编辑。把句子改写得更正式，只输出改写后的那一句，不要解释、不要给多个选项。"},
      {"role": "user", "content": "把这句话改得更正式：这个方案我觉得不太行"}]),

    ("③ 简单推理",
     [{"role": "user", "content": "一个班级 40 人，60% 是女生。女生里 25% 戴眼镜。戴眼镜的女生有几人？只给答案和算式。"}]),
]

print("=" * 78)
print(f"本地 {LOCAL_MODEL}  vs  云端 {CLOUD_MODEL}")
print("=" * 78)

for title, msgs in TESTS:
    print("\n" + "=" * 78)
    print(title)
    print("=" * 78)
    for label, fn in [("本地 4B", ask_local), ("云端", ask_cloud)]:
        try:
            r = fn(msgs)
            txt = r["text"]
            extra = ""
            if "JSON" in title:
                extra = f"  [{json_ok(txt)}]"
            print(f"\n  --- {label}  ({r['secs']:.2f}s, {r['tok']} tok){extra} ---")
            print(f"  {txt[:340]!r}")
            if "system" in title:
                print(f"      字数 {len(txt)}" + ("  ← ✅ 只给了一句" if len(txt) < 60 else "  ← ⚠️ 超长/给了多个"))
        except Exception as e:
            print(f"\n  --- {label} --- ❌ {type(e).__name__}: {str(e)[:110]}")

print()
print("=" * 78)
print("怎么看这个对比")
print("=" * 78)
print("""  · 如果本地在 ①② 上失败、云端通过 —— 那是【指令遵循能力】的差距，
    不是"模型笨"，是参数量决定的：小模型更难坚持格式约束。
    ★ 这直接验证/推翻 Week3 D2 的结论（system 是输出契约）：
      在大模型上成立，在 4B 上可能不成立 —— 那就说明
      「输出契约的效力取决于模型能力」。
  · ③ 是纯推理，差距应该比 ①② 小（算术对大模型也不难）。
""")
