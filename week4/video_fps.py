"""Week4 · D5/D6 —— 视频 Edge：YOLO 推理 + FPS 基准

★★ 这个文件是【骨架】。标着 TODO 的地方要你自己写。★★

分工（和 week4/agent_calc.py 一样的规矩）：
  · 外面的部分（环境自检 / 抽帧 / 显存查询 / argparse）
    是【脚手架】—— 我写好了，不用动。
  · 下面两个函数体是【你的交付物】—— 必须你自己写。

     d5_detect    单张图推理：取 boxes.xyxy / cls / conf，画框保存
     d6_bench     逐帧跑视频，测平均 FPS / 瞬时 FPS / 总耗时

参考手册：4.16 视频 Edge（有完整解释和逐行注释）
         4.15 YOLO（单张图那段的字段说明）

★ 环境要求：用【AMSP_UOD】那个环境的 Python —— 它是你机器上唯一一个 torch 能用 GPU 的
    & "D:\anaconda\envs\AMSP_UOD\python.exe" week4\video_fps.py --check

  ⚠️ 别用 myenv1（3.13.14）—— 它的 torch 是 2.13.0+cpu，**纯 CPU 跑**，
     FPS 会差十几倍，而且**不报错**，你会安静地测出一个烂数字。
     （2026-10-12 实测：myenv1 → cuda=False / AMSP_UOD → cuda=True + RTX 5060 Laptop）

用法：
  ... video_fps.py --check                    # 只自检，不推理
  ... video_fps.py --grab                     # 从视频抽一帧存本地（当测试图）
  ... video_fps.py --image                    # D5：单张图推理
  ... video_fps.py --video --frames 60        # D6：跑 60 帧测 FPS
"""
import argparse
import os
import subprocess
import sys
import time

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

OK = "✅"
BAD = "❌"
WARN = "⚠️"

# 本机已有的权重（手册 4.15 记过：GitHub 下载经常超时，直接用这个）
WEIGHTS = r"C:\Users\omen\yolov8n.pt"

# 测试素材：从你 E:\video 里的视频抽帧（离线可用，不用联网下样例图）
VIDEO = r"E:\video\110123-1080p.mp4"
FRAME_JPG = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out_edge", "frame.jpg")
OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out_edge")


def head(t):
    print("\n" + "=" * 62)
    print(t)
    print("=" * 62)


def check_env():
    """自检：依赖 / 权重 / 素材 / 显卡。"""
    head("第 1 步 · 环境自检")
    ok = True

    for mod in ("ultralytics", "cv2"):
        try:
            m = __import__(mod)
            ver = getattr(m, "__version__", "?")
            print(f"{OK} {mod} 已安装（{ver}）")
        except ImportError:
            print(f"{BAD} {mod} 没装")
            print(f"    解决：pip install ultralytics opencv-python")
            ok = False

    # ★ 这道闸门最重要：CPU 也能"跑通"，但测出来的 FPS 毫无意义
    try:
        import torch
        print(f"{OK} torch {torch.__version__}")
        if torch.cuda.is_available():
            print(f"{OK} GPU：{torch.cuda.get_device_name(0)}")
        else:
            print(f"{BAD} torch 用不了 GPU（cuda=False）——★ 这个数字不能用来报 FPS")
            print('    解决：换成 D:\\anaconda\\envs\\AMSP_UOD\\python.exe 再跑')
            ok = False
    except ImportError:
        print(f"{BAD} torch 没装")
        ok = False

    if os.path.exists(WEIGHTS):
        size = os.path.getsize(WEIGHTS) / 1024 / 1024
        print(f"{OK} 权重：{WEIGHTS}（{size:.1f} MB）")
    else:
        print(f"{BAD} 找不到权重 {WEIGHTS}")
        ok = False

    if os.path.exists(VIDEO):
        print(f"{OK} 测试视频：{VIDEO}")
    else:
        print(f"{WARN} 找不到测试视频 {VIDEO} —— 改用别的 mp4，或改本文件顶部的 VIDEO")

    try:
        r = subprocess.run(
            ["nvidia-smi", "--query-gpu=name,memory.used,memory.total",
             "--format=csv,noheader"],
            capture_output=True, text=True, timeout=10)
        print(f"{OK} GPU：{r.stdout.strip() or '（无输出）'}")
    except Exception as e:
        print(f"{WARN} 查不到显卡（{type(e).__name__}）—— FPS 照样能测")

    return ok


def gpu_mem_mb():
    """当前显存占用（MB）。查不到就返回 None。"""
    try:
        r = subprocess.run(["nvidia-smi", "--query-gpu=memory.used",
                            "--format=csv,noheader,nounits"],
                           capture_output=True, text=True, timeout=10)
        return int(r.stdout.strip().splitlines()[0])
    except Exception:
        return None


def grab_frame(video=VIDEO, out=FRAME_JPG, frame_no=100):
    """从视频里抽一帧存成 jpg —— 当 D5 的测试图用（离线，不用联网下图）。"""
    import cv2
    os.makedirs(os.path.dirname(out), exist_ok=True)
    cap = cv2.VideoCapture(video)
    if not cap.isOpened():
        print(f"{BAD} 打不开视频：{video}")
        return None
    cap.set(cv2.CAP_PROP_POS_FRAMES, frame_no)
    #                            ↑跳到第 100 帧，避开片头黑屏
    ok, frame = cap.read()
    cap.release()
    if not ok:
        print(f"{BAD} 第 {frame_no} 帧读不到")
        return None
    cv2.imwrite(out, frame)
    print(f"{OK} 抽帧成功：{out}  形状 {frame.shape}")
    return out


# ============================================================
# ★★★ 你的交付物 ★★★
# ============================================================


def d5_detect(image_path, weights=WEIGHTS):
    """D5 · 单张图推理。

    要做的事（手册 4.15）：
      1. 加载模型：model = YOLO(weights)
      2. 读图：cv2.imread(image_path)   ← ★ 通道顺序是 BGR
      3. 推理：results = model(img, verbose=False)，取 r = results[0]
      4. 打印三样（★ 这就是"能解释"的地方）：
           r.boxes.xyxy   形状 (N, 4)：左上x, 左上y, 右下x, 右下y
           r.boxes.cls    形状 (N,)：类别编号
           r.boxes.conf   形状 (N,)：置信度
      5. ★ 把类别编号翻译成名字：用 model.names
           （编号是数字，光看数字你根本不知道检测到了什么）
      6. 画框保存：cv2.imwrite(out_path, r.plot())
      7. 打印 N（检测到几个框）和保存路径

    返回：检测到的框数 N。

    提示：
      · r.boxes.xyxy 形状是 (0, 4) 是正常的 —— 说明这张图没有它认识的物体
      · 想只看置信度高的框，可以用 model(img, conf=0.5)
    """
    raise NotImplementedError("d5_detect 还没写（D5 的任务）")


def d6_bench(video_path=VIDEO, max_frames=60, weights=WEIGHTS):
    """D6 · 逐帧测 FPS —— 这个方向的关键指标。

    要做的事（手册 4.16）：
      1. cv2.VideoCapture(video_path) 打开视频
      2. 循环读帧：ok, frame = cap.read()，ok 为 False 就 break
      3. ★ 每帧单独计时：t0 = time.time() → model(frame) → 记 1/(time.time()-t0)
      4. 数够 max_frames 帧就停（跑整个视频太慢）
      5. 循环里每帧存一张画框图？（★ 想想：60 帧存 60 张图有意思吗？还是只存第 1 张？）
      6. 跑完 cap.release()
      7. 打印：
           处理帧数 / 平均 FPS / 总耗时 / 瞬时 FPS 的最小值和最大值 / 显存占用
      8. 返回平均 FPS

    要能回答两个问题（D7 自查会问）：
      · 平均 12 FPS 意味着什么？（视频是 25–30 FPS）
      · 为什么"瞬时 FPS 的波动"也值得看，不能只看平均？

    提示：
      · 第一帧通常特别慢（模型要先加载/预热），想想要不要把它算进平均
      · 显存用上面的 gpu_mem_mb() 拿
    """
    raise NotImplementedError("d6_bench 还没写（D6 的任务）")


# ============================================================
# 下面是入口，不用改
# ============================================================


def main():
    ap = argparse.ArgumentParser(description="Week4 · 视频 Edge：YOLO 推理 + FPS")
    ap.add_argument("--check", action="store_true", help="只自检")
    ap.add_argument("--grab", action="store_true", help="从视频抽一帧当测试图")
    ap.add_argument("--image", action="store_true", help="D5：单张图推理")
    ap.add_argument("--video", action="store_true", help="D6：测 FPS")
    ap.add_argument("--frames", type=int, default=60, help="--video 跑多少帧（默认 60）")
    args = ap.parse_args()

    if args.grab:
        grab_frame()
        return 0

    ok = check_env()
    if not ok:
        print(f"\n{BAD} 自检没过，先解决上面的问题（多半就是 pip install 那一步）")
        return 2

    if args.check:
        print("\n（--check：只自检，不推理）")
        return 0

    os.makedirs(OUT_DIR, exist_ok=True)

    try:
        if args.image:
            if not os.path.exists(FRAME_JPG):
                print(f"{WARN} 还没有测试图，先跑：--grab")
                return 2
            d5_detect(FRAME_JPG)
        elif args.video:
            d6_bench(VIDEO, args.frames)
        else:
            print("选一个：--grab / --image / --video / --check")
    except NotImplementedError as e:
        print(f"\n{WARN} {e}")
        print("   → D5：先写 d5_detect，跑 --image")
        print("   → D6：再写 d6_bench，跑 --video")
        return 3
    except Exception as e:
        print(f"\n{BAD} 出错了：{type(e).__name__}: {e}")
        return 1

    head("完成")
    return 0


if __name__ == "__main__":
    sys.exit(main())
