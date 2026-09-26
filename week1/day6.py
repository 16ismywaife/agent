import pandas as pd
import matplotlib
matplotlib.rcParams["font.sans-serif"] = ["SimHei"]
matplotlib.rcParams["axes.unicode_minus"] = False
import matplotlib.pyplot as plt

df = pd.read_csv("data.csv")

# 1. 每个科目的平均分 → 柱状图，带标题和轴标签，柱子上标数值
fig,ax=plt.subplots(figsize=(7,4.5))
s=df.groupby("科目")["分数"].mean()
ax.bar(s.index,s.values)
ax.set_title("各科目平均分")
ax.set_xlabel("科目")
ax.set_ylabel("平均分")
fig.tight_layout()
for i, v in enumerate(s.values):
    ax.text(i, v + 0.8, f"{v:.1f}", ha="center")
fig.tight_layout()
fig.savefig("avg_by_subject.png", dpi=130)
#    存成 week1/avg_by_subject.png
# 2. 全体分数的分布 → 直方图（bins=20）
#    存成 week1/score_dist.png
fig,ax=plt.subplots(figsize=(7,4.5))
ax.set_title("全体分数的分布")
ax.set_xlabel("idk")
ax.set_ylabel("scores")
ax.hist(df["分数"], bins=20)
fig.tight_layout()
fig.savefig("hist_by_subject.png", dpi=130)
# 3.（加分）各科目 × 各分数段的人数 → 分组柱状图
df["段"] = pd.cut(df["分数"], bins=[0, 59, 79, 100], labels=["<60", "60-79", "80-100"])
pv = pd.crosstab(df["段"], df["科目"])

ax = pv.plot(kind="bar", figsize=(7.5, 4.5), rot=0)
ax.set_title("各科目 × 各分数段人数")
ax.set_xlabel("分数段")
ax.set_ylabel("人数")
ax.legend(title="科目")
fig = ax.get_figure()
fig.tight_layout()
fig.savefig("grouped.png", dpi=130)
plt.close(fig)