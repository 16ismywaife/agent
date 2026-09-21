"""第 1 周 D1：环境验证
确认 conda 环境、Python 版本、关键库都正常。
"""
import sys
import numpy as np
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt

# 终端中文不乱码
# Windows 下 Python 默认按 GBK 输出，而控制台是 UTF-8，两边对不上就变乱码。
# 这一行强制按 UTF-8 输出。加 hasattr 判断是为了兼容输出被重定向的情况。
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

print("=" * 40)
print("Python :", sys.version.split()[0])
print("解释器 :", sys.executable)
print("numpy  :", np.__version__)
print("pandas :", pd.__version__)
print("matplot:", matplotlib.__version__)
print("=" * 40)

# 中文显示（Windows 用 SimHei）
matplotlib.rcParams["font.sans-serif"] = ["SimHei"]
matplotlib.rcParams["axes.unicode_minus"] = False

# 造一点数据跑通全流程
df = pd.DataFrame({
    "科目": ["数学", "语文", "英语", "物理"],
    "分数": [88, 76, 92, 81],
})
print(df)
print("平均分:", round(df["分数"].mean(), 2))

# 画图并保存
fig, ax = plt.subplots(figsize=(6, 4))
ax.bar(df["科目"], df["分数"], color="#4C78A8")
ax.set_title("各科目分数")
ax.set_ylabel("分数")
fig.tight_layout()
fig.savefig("test.png", dpi=120)
print("图片已保存: test.png")