"""实测：本地模型在不同上下文长度下占多少显存。

为什么不能只靠算：KV cache 的实际分配还取决于
  · 精度（f16 / q8_0 / q4_0）
  · flash attention 开不开
  · Ollama 自己的显存规划（会预留）
所以直接量。

★ 这就是 Week4 D3 要交付的「显存占用」数据。
"""
import json
import subprocess
import sys
import time
import urllib.request

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

API = "http://127.0.0.1:11434/api"
MODEL = "qwen3.5:4b"


def vram_used():
    out = subprocess.run(
        ["nvidia-smi", "--query-gpu=memory.used", "--format=csv,noheader,nounits"],
        capture_output=True, text=True, timeout=15)
    return int(out.stdout.strip())


def unload():
    """让 Ollama 把模型从显存卸掉（keep_alive=0）。"""
    try:
        req = urllib.request.Request(
            f"{API}/generate",
            data=json.dumps({"model": MODEL, "keep_alive": 0}).encode(),
            headers={"Content-Type": "application/json"})
        urllib.request.urlopen(req, timeout=60).read()
    except Exception:
        pass
    time.sleep(3)


def chat_num_ctx(n):
    """带指定 num_ctx 发一次极短请求，把模型按这个上下文加载进来。"""
    body = {
        "model": MODEL,
        "messages": [{"role": "user", "content": "hi"}],
        "stream": False,
        "think": False,
        "options": {"num_ctx": n, "num_predict": 1},
    }
    req = urllib.request.Request(f"{API}/chat", data=json.dumps(body).encode(),
                                headers={"Content-Type": "application/json"})
    t0 = time.time()
    urllib.request.urlopen(req, timeout=600).read()
    return time.time() - t0


print("=" * 74)
print("实测：不同 num_ctx 下的显存占用")
print("=" * 74)

unload()
base = vram_used()
print(f"\n  基线（模型未加载）: {base} MiB\n")
print(f"  {'num_ctx':>9} {'加载后显存':>12} {'模型+KV 占用':>14} {'KV 部分(减权重)':>16} {'耗时':>8}  能否加载")
print("  " + "-" * 76)

# 权重部分（4B + 多模态投影层）大致是固定的，先用 4096 那一档反推
weight_mib = None
results = []
for n in [2048, 4096, 8192, 16384, 32768, 65536]:
    unload()
    try:
        secs = chat_num_ctx(n)
        used = vram_used()
        delta = used - base
        if n == 4096:
            weight_mib = delta     # 记下来当"权重底座"
        kv = (delta - weight_mib) if (weight_mib is not None and n != 4096) else (0 if n == 4096 else None)
        kv_s = f"{kv:>13} MiB" if kv is not None else f"{'—':>13}"
        print(f"  {n:>9} {used:>9} MiB {delta:>11} MiB {kv_s:>16} {secs:>7.1f}s  ✅")
        results.append((n, used, delta, secs))
    except Exception as e:
        print(f"  {n:>9} {'—':>12} {'—':>14} {'—':>16} {'—':>8}  ❌ {type(e).__name__}: {str(e)[:40]}")

print()
print("  ★ 判读：")
print("     · 「模型+KV 占用」是总数；减去权重底座就是 KV cache 的增量")
print("     · 看哪一档开始逼近 8151 MiB 总显存 —— 那就是你的上限")
print("     · 如果某一档加载失败或退回 CPU，说明放不下")
print()
print("  注：Ollama 的 /api/ps 能看模型实际跑在 GPU 还是 CPU 上")
