"""对比 qwen3.5:4b 开/关思考的耗时和 token。

用 Ollama 原生 API（返回 JSON），比 `ollama run` 的 TUI 干净得多。
★ 这也顺便演示了「同一模型、同一问题，只有思考开关不同」的对照实验
  —— 就是你在 Week3 做过的那个方法论。
"""
import json
import sys
import time
import urllib.request

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

API = "http://127.0.0.1:11434/api/chat"
MODEL = "qwen3.5:4b"
Q = "用一句话解释什么是反向传播"
N = 2


def run(think):
    """think=None 表示不传这个字段（用模型默认）。"""
    body = {"model": MODEL, "messages": [{"role": "user", "content": Q}], "stream": False}
    if think is not None:
        body["think"] = think
    req = urllib.request.Request(
        API, data=json.dumps(body).encode(),
        headers={"Content-Type": "application/json"})
    t0 = time.time()
    with urllib.request.urlopen(req, timeout=600) as r:
        data = json.loads(r.read().decode())
    dt = time.time() - t0
    msg = data.get("message", {})
    return {
        "secs": dt,
        "content_len": len(msg.get("content") or ""),
        "thinking_len": len(msg.get("thinking") or ""),
        "prompt_tokens": data.get("prompt_eval_count"),
        "output_tokens": data.get("eval_count"),
        "eval_duration_s": (data.get("eval_duration") or 0) / 1e9,
        "content": (msg.get("content") or "")[:80],
        "thinking": (msg.get("thinking") or "")[:80],
    }


print("=" * 74)
print(f"同一问题各跑 {N} 次：{Q!r}")
print("=" * 74)

for label, think in [("默认（不传 think）", None), ("think=True", True), ("think=False", False)]:
    print(f"\n--- {label} ---")
    for i in range(N):
        try:
            r = run(think)
            tps = (r["output_tokens"] / r["eval_duration_s"]) if r["eval_duration_s"] else 0
            print(f"  [{i+1}] 总耗时 {r['secs']:6.2f}s | "
                  f"正文 {r['content_len']:4d} 字 | 思考 {r['thinking_len']:5d} 字 | "
                  f"输出 {r['output_tokens']} tok | {tps:5.1f} tok/s")
            if i == 0:
                if r["thinking"]:
                    print(f"       思考开头: {r['thinking']!r}")
                print(f"       正文: {r['content']!r}")
        except Exception as e:
            print(f"  [{i+1}] ❌ {type(e).__name__}: {str(e)[:90]}")

print()
print("=" * 74)
print("判读")
print("=" * 74)
print("""  · think=False  → 没有思考，直接出正文（快、省）
  · think=True   → 先想一大段再答（慢、费）
  · 默认值       → 看它跟哪个一致，就知道这个模型的默认行为

  ★ 对 Week4 的意义：Agent 主循环里每轮都要调一次模型，
    如果每轮都先思考 90 秒，Agent 会慢到没法用。
    → D1/D2 写 Agent 时，要么关思考，要么接受这个延迟。
""")
