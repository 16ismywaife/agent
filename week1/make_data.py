"""生成测试数据 data.csv

固定了随机种子（42），所以每次生成的数据完全一样——这是"可复现"的前提。

用法：
    python make_data.py
"""
import sys

# 终端中文不乱码
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

import numpy as np
import pandas as pd

np.random.seed(42)

subjects = ["数学", "语文", "英语"]
rows = []
for i in range(100):                       # 100 个学生
    for s in subjects:                     # 每人 3 科
        rows.append({
            "姓名": f"学生{i:03d}",
            "科目": s,
            "分数": int(np.clip(np.random.normal(75, 15), 0, 100)),
        })

df = pd.DataFrame(rows)
df.to_csv("data.csv", index=False, encoding="utf-8-sig")

print("生成完毕:", df.shape)
print(df.head(3).to_string(index=False))
