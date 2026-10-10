"""Week4 · D3/D4 指标测量：显存 / 加载时间 / TTFT / 吞吐量

这个脚本不发一次普通请求，而是量四件事 —— 正是 D3/D4 要求的产出。

用法：
  python week4\\measure_llm.py --check
      只检查环境和端点，不发请求

  python week4\\measure_llm.py --model qwen3.5:4b
      完整测量（会自动读取 nvidia-smi 的显存，并计时）

前置：Ollama 在跑（安装后会自动启动，托盘有图标）。
     没装 Ollama 也可以测 API —— 见 --backend 参数。
"""
import argparse
import json
import os
import statistics
import subprocess
import sys
import time

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

OK = "✅"
BAD = "❌"
WARN = "⚠️"

# Ollama 的 OpenAI 兼容端点是 /v1
OLLAMA_BASE = "http://127.0.0.1:11434/v1"


def head(t):
    print("\n" + "=" * 66)
    print(t)
    print("=" * 66)


# ---------------------------------------------------------------- 显存
def vram():
    """读 nvidia-smi，返回 (已用MiB, 总MiB, 空闲MiB)。读不到返回 None。"""
    try:
        out = subprocess.run(
            ["nvidia-smi", "--query-gpu=memory.used,memory.total,memory.free",
             "--format=csv,noheader,nounits"],
            capture_output=True, text=True, timeout=15)
        if out.returncode != 0:
            return None
        parts = [int(x.strip()) for x in out.stdout.strip().split(",")]
        return tuple(parts)          # (used, total, free)
    except Exception:
        return None


def show_vram(label):
    v = vram()
    if not v:
        print(f"  {label}: 读不到 nvidia-smi")
        return None
    used, total, free = v
    print(f"  {label}: 已用 {used} MiB / 共 {total} MiB / 空闲 {free} MiB")
    return v


# ---------------------------------------------------------------- 端点检查
def check_endpoint(base_url):
    """确认服务在跑，并列出有哪些模型。"""
    import urllib.request
    import urllib.error

    head("第 1 步 · 检查推理服务")
    root = base_url.rstrip("/").replace("/v1", "")
    try:
        with urllib.request.urlopen(root + "/api/tags", timeout=10) as r:
            data = json.loads(r.read().decode("utf-8"))
        models = [m.get("name") for m in data.get("models", [])]
        print(f"{OK} 服务在跑：{root}")
        if models:
            print(f"{OK} 已下载的模型 {len(models)} 个：")
            for m in models:
                print(f"     - {m}")
        else:
            print(f"{WARN} 还没有下载任何模型。先： ollama pull qwen3.5:4b")
        return True, models
    except Exception as e:
        print(f"{BAD} 连不上 {root}")
        print(f"    {type(e).__name__}: {str(e)[:120]}")
        print(f"    → 检查托盘里有没有 Ollama 图标；或手动启动：ollama serve")
        return False, []


# ---------------------------------------------------------------- 测量
def measure(base_url, model, prompt, n_tokens_hint=200):
    """测：加载时间 / TTFT / 吞吐量。返回 dict。"""
    from openai import OpenAI

    client = OpenAI(api_key="ollama", base_url=base_url)   # Ollama 不校验 key

    # ---- 1. 冷加载：第一次请求会包含把模型读进显存的时间 ----
    print(f"\n  [1] 冷启动请求（含模型加载）…")
    t0 = time.time()
    r1 = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": "说一个字"}],
        max_tokens=5,
    )
    cold = time.time() - t0
    print(f"      完成，耗时 {cold:.2f}s（这部分主要是加载模型）")

    # ---- 2. 热请求：模型已在显存里 ----
    print(f"\n  [2] 热请求（模型已加载）…")
    t0 = time.time()
    r2 = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=n_tokens_hint,
    )
    hot_total = time.time() - t0
    out_tokens = r2.usage.completion_tokens if r2.usage else None
    print(f"      耗时 {hot_total:.2f}s，输出 {out_tokens} tokens")
    if out_tokens:
        print(f"      吞吐量 ≈ {out_tokens / hot_total:.1f} tokens/s")

    # ---- 3. TTFT：流式，量首块到达的时间 ----
    print(f"\n  [3] 流式请求，测 TTFT（首 token 延迟）…")
    ttfts = []
    for i in range(3):
        t0 = time.time()
        first = None
        try:
            stream = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=n_tokens_hint,
                stream=True,
            )
            for chunk in stream:
                piece = chunk.choices[0].delta.content if chunk.choices else None
                if piece:
                    first = time.time() - t0
                    break
            # 把流读干净，否则连接不释放
            for _ in stream:
                pass
        except Exception as e:
            print(f"      第 {i+1} 次失败：{type(e).__name__}: {str(e)[:100]}")
            continue
        if first is not None:
            ttfts.append(first)
            print(f"      第 {i+1} 次 TTFT = {first*1000:.0f} ms")

    return {
        "cold_load_s": cold,
        "hot_total_s": hot_total,
        "completion_tokens": out_tokens,
        "throughput_tps": (out_tokens / hot_total) if out_tokens else None,
        "ttft_ms_list": [round(x * 1000) for x in ttfts],
        "ttft_ms_median": round(statistics.median(ttfts) * 1000) if ttfts else None,
        "text_preview": (r2.choices[0].message.content or "")[:60],
    }


def main():
    ap = argparse.ArgumentParser(description="Week4 D3/D4 指标测量")
    ap.add_argument("--model", default="qwen3.5:4b", help="模型名（默认 qwen3.5:4b）")
    ap.add_argument("--base-url", default=OLLAMA_BASE, help=f"端点（默认 {OLLAMA_BASE}）")
    ap.add_argument("--check", action="store_true", help="只检查环境，不发请求")
    ap.add_argument("--prompt", default="用三句话介绍什么是机器学习", help="测试用的问题")
    ap.add_argument("--out", default=None, help="把结果写成 JSON 到这个路径")
    args = ap.parse_args()

    head("环境")
    v0 = show_vram("测量前")
    env_models = os.environ.get("OLLAMA_MODELS")
    default_hint = "（未设，会用默认 %USERPROFILE%\\.ollama\\models）"
    print(f"  OLLAMA_MODELS = {env_models or default_hint}")

    ok, models = check_endpoint(args.base_url)
    if args.check:
        return 0 if ok else 2
    if not ok:
        return 2

    if args.model not in models:
        print(f"\n{WARN} 列表里没有 {args.model}。先下载：")
        print(f"     ollama pull {args.model}")
        return 2

    head(f"第 2 步 · 测量 {args.model}")
    result = measure(args.base_url, args.model, args.prompt)

    head("第 3 步 · 测量后显存")
    v1 = show_vram("测量后")

    head("结果汇总")
    print(f"  模型             {args.model}")
    print(f"  冷启动耗时       {result['cold_load_s']:.2f} s   （含模型加载）")
    print(f"  热请求耗时       {result['hot_total_s']:.2f} s")
    print(f"  输出 token       {result['completion_tokens']}")
    if result["throughput_tps"]:
        print(f"  吞吐量           {result['throughput_tps']:.1f} tokens/s")
    print(f"  TTFT             {result['ttft_ms_list']} ms   中位数 {result['ttft_ms_median']} ms")
    if v0 and v1:
        print(f"  显存占用增量     {v1[0] - v0[0]} MiB   ← ★ 这就是「模型占了多少显存」")
    print(f"  回答开头         {result['text_preview']!r}")
    print()
    print("  ★ TTFT 和吞吐量是两个不同的指标：")
    print("     TTFT     → 用户「感觉快不快」（等第一个字的时间）")
    print("     吞吐量   → 「多久能说完」（每秒吐多少 token）")
    print("     一个模型可能 TTFT 很短但吞吐量低，反过来也有")

    if args.out:
        payload = {"model": args.model, **result,
                   "vram_before_mib": v0[0] if v0 else None,
                   "vram_after_mib": v1[0] if v1 else None,
                   "vram_delta_mib": (v1[0] - v0[0]) if (v0 and v1) else None}
        with open(args.out, "w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)
        print(f"\n  已写入 {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
