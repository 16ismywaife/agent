"""第 1 周 D1：环境验证
确认 conda 环境、Python 版本、关键库都正常。
"""
import sys
import numpy as np
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt

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