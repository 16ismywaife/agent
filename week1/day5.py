import numpy as np
import pandas as pd

np.random.seed(42)
subjects = ["数学", "语文", "英语"]
rows = []
for i in range(100):
    for s in subjects:
        rows.append({
            "姓名": f"学生{i:03d}",
            "科目": s,
            "分数": int(np.clip(np.random.normal(75, 15), 0, 100)),
        })
df = pd.DataFrame(rows)
df.to_csv("data.csv", index=False, encoding="utf-8-sig")
print("生成完毕:", df.shape)

import pandas as pd
df = pd.read_csv("data.csv")

# 1. 看前 5 行
print(df.head())
# 2. shape / columns / dtypes
print(df.shape,df.columns,df.dtypes)
# 3. 每个科目的平均分（groupby）
print(df.groupby("科目")["分数"].mean())
# 4. 每个科目的 平均/最高/最低/人数（agg）
print(df.groupby("科目")["分数"].agg(["mean","max","min","count"]))
# 5. 数学成绩 > 90 的所有行
print(df[(df["科目"] == "数学") & (df["分数"] > 90)])
# 6. 每个科目的平均分，按分数从高到低排序
print(df.groupby("科目")["分数"].mean().sort_values(ascending=False))
# 7. 有多少个不同的学生（nunique）＋ 一共多少行，比一比
print(df["姓名"].nunique(),len(df))
# 8. 新增一列"是否及格"（分数 >= 60），然后打印及格率
df["是否及格"]=df["分数"]>=60
print("及格率:", df["是否及格"].mean())