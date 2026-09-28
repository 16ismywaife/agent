"""学生成绩分析脚本

读 CSV → 统计 → 绘图 → 保存结果。

用法：
    python analyze.py
    python analyze.py --input data.csv --outdir .
"""
import os
import argparse
import pandas as pd
import matplotlib
matplotlib.rcParams["font.sans-serif"] = ["SimHei"]
matplotlib.rcParams["axes.unicode_minus"] = False
import matplotlib.pyplot as plt


def load(path):
    """读 CSV，返回 DataFrame"""
    # TODO: 一行代码
    df=pd.read_csv(path)
    return df



def stats(df):
    """返回各科目的 平均/最高/最低/人数"""
    # TODO: 用 groupby + agg
    s=df.groupby("科目")["分数"].agg(["mean","min","max","count"])
    return s

def plot(df, out_path):
    """画各科平均分柱状图，保存到 out_path"""
    # TODO: 从 day6.py 搬过来
    # 记得：柱子上的数值标签
    fig, ax = plt.subplots(figsize=(12,8))
    s = df.groupby("科目")["分数"].agg(["mean", "min", "max", "count"])
    ax.bar(s.index, s["mean"])
    ax.set_title("各科目平均分")
    ax.set_xlabel("科目")
    ax.set_ylabel("分数")
    for i, v in enumerate(s["mean"]):
        ax.text(i, v + 0.8, f"{v:.1f}", ha="center")
    fig.tight_layout()
    fig.savefig(out_path, dpi=130)



def main():
    """入口：把上面三个串起来"""
    ap = argparse.ArgumentParser(description="学生成绩分析")
    ap.add_argument("--input", default="data.csv", help="输入 CSV 路径")
    ap.add_argument("--outdir", default=".", help="输出目录")
    args = ap.parse_args()
    os.makedirs(args.outdir, exist_ok=True)

    df = load(args.input)

    st = stats(df)
    print(st)
    st.to_csv(os.path.join(args.outdir, "summary.csv"))

    plot(df, os.path.join(args.outdir, "result.png"))

    print("完成")


if __name__ == "__main__":
    main()