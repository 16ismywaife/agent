"""查看本地模型的状态：上下文【分配量】和【实际占用量】。

★ 为什么要分开看：
    · ollama ps 的 CONTEXT 列 = 你允许它用多少（上限）
    · API 返回的 prompt_eval_count = 这次请求真的用了多少（实际）
    ollama ps 看不到后者 —— 这个脚本补上。

用法：
  python week4\\ctx_status.py                      # 只看当前状态
  python week4\\ctx_status.py --ask "你的问题"      # 发一条并显示它占了多少上下文
"""
import argparse
import json
import subprocess
import sys
import urllib.request

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

NATIVE = "http://127.0.0.1:11434/api"


def head(t):
    print("\n" + "=" * 64)
    print(t)
    print("=" * 64)


def api(path, payload=None, timeout=600):
    url = f"{NATIVE}{path}"
    if payload is None:
        req = urllib.request.Request(url)
    else:
        req = urllib.request.Request(url, data=json.dumps(payload).encode(),
                                     headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode())


def vram():
    out = subprocess.run(["nvidia-smi", "--query-gpu=memory.used,memory.total",
                          "--format=csv,noheader,nounits"],
                         capture_output=True, text=True, timeout=15)
    p = [int(x) for x in out.stdout.strip().split(",")]
    return p[0], p[1]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ask", default=None, help="发一条消息，显示它占了多少上下文")
    ap.add_argument("--model", default=None)
    args = ap.parse_args()

    # ---------- ① 分配量 ----------
    head("① 已加载的模型（分配量）")
    try:
        ps = api("/ps")
    except Exception as e:
        print(f"  ❌ 连不上 Ollama：{e}")
        print("     → 托盘里找 Ollama 图标，或运行 ollama serve")
        return 2

    models = ps.get("models", [])
    if not models:
        print("  当前没有模型驻留在显存里（空闲了）")
        print("  → 发一次请求就会加载；或 ollama ps 为空是正常的")
        return 0

    for m in models:
        name = m.get("name")
        ctx = m.get("context_length")
        tot = m.get("size", 0)
        v = m.get("size_vram", 0)
        pct = v / tot * 100 if tot else 0
        print(f"  模型        {name}")
        print(f"  上下文上限   {ctx} tokens        ← 这是【允许用多少】")
        print(f"  占用显存     {v/1024**2:.0f} MiB / {tot/1024**2:.0f} MiB")
        print(f"  GPU 占比     {pct:.0f}%   {'✅ 全在显卡' if pct > 99 else '⚠️ 有部分回退到 CPU，会慢很多'}")

    # ---------- ② 显存现状 ----------
    used, total = vram()
    head("② 显卡显存")
    print(f"  已用 {used} MiB / 共 {total} MiB / 空闲 {total - used} MiB")
    if total - used < 1024:
        print("  ⚠️ 空闲不足 1 GB —— 开 Chrome/PyCharm 可能把它挤到 CPU")

    # ---------- ③ 实际占用量 ----------
    head("③ 实际占用量（发一条请求才能量出来）")
    model = args.model or (models[0].get("name") if models else None)
    if not model:
        print("  没有可用的模型")
        return 0

    prompt = args.ask or "请用一句话回答：1+1 等于几？"
    print(f"  模型: {model}")
    print(f"  发送: {prompt!r}")
    print()
    try:
        d = api("/chat", {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "think": False,          # ★ 关思考，否则会白烧 token
            "stream": False,
        })
    except Exception as e:
        print(f"  ❌ {type(e).__name__}: {str(e)[:120]}")
        return 1

    pe = d.get("prompt_eval_count") or 0
    ec = d.get("eval_count") or 0
    ctx = models[0].get("context_length") or 0
    print(f"  prompt 占用     {pe} tokens        ← ★ 这是【实际用了多少】")
    print(f"  本次生成        {ec} tokens")
    if ctx:
        pct_used = pe / ctx * 100
        bar_len = 40
        filled = int(pct_used / 100 * bar_len)
        bar = "█" * filled + "·" * (bar_len - filled)
        print()
        print(f"  上下文占用  [{bar}] {pct_used:.1f}%")
        print(f"              {pe} / {ctx} tokens，还剩 {ctx - pe} tokens")
    print()
    print(f"  回答: {(d.get('message', {}).get('content') or '')[:100]!r}")
    print()
    print("  ★ 每多聊一轮，prompt 占用就会往上涨（历史要全部重发）")
    print("    涨到接近上限时，模型会开始忘记或报错 —— 这就是「上下文管理」问题")
    print("    （和 Week3 D3 那个 prompt_tokens 14 → 796 → 1913 是同一件事）")
    return 0


if __name__ == "__main__":
    sys.exit(main())
