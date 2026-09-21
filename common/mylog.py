"""通用日志器 —— 6 周都能用

用法：
    from common.mylog import get_logger
    log = get_logger("train")
    log.info("开始训练 epoch=1")
    log.error(f"加载失败: {e}")

日志写到 logs/ 目录（已在 .gitignore 里，不会被提交）。
"""
import logging
import os
from datetime import datetime


def get_logger(name="run", log_dir="logs"):
    os.makedirs(log_dir, exist_ok=True)
    path = os.path.join(log_dir, f"{name}_{datetime.now():%Y%m%d}.log")

    lg = logging.getLogger(name)
    lg.setLevel(logging.INFO)

    # 避免重复添加 handler（重复调用时会出现重复日志行）
    if not lg.handlers:
        fmt = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s",
                                datefmt="%H:%M:%S")

        fh = logging.FileHandler(path, encoding="utf-8")
        fh.setFormatter(fmt)

        sh = logging.StreamHandler()
        sh.setFormatter(fmt)

        lg.addHandler(fh)
        lg.addHandler(sh)

    return lg


if __name__ == "__main__":
    log = get_logger("demo")
    log.info("日志器工作正常")
    log.warning("这是一条警告")
    log.error("这是一条错误")
    print("日志已写入 logs/ 目录")
