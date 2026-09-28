# 学生成绩分析

读入成绩 CSV，输出各科目统计和图表。

第 1 周交付物。从生成数据到出图、出统计表，全流程可复现。

---

## 依赖

- Python 3.11
- pandas
- matplotlib
- numpy（生成数据用）

安装：

```bash
pip install pandas matplotlib numpy
```

---

## 文件说明

| 文件 | 作用 |
|---|---|
| **`make_data.py`** | 生成测试数据 `data.csv`（固定随机种子） |
| **`analyze.py`** | **入口程序**。执行统计分析 + 绘图 |
| `data.csv` | 输入数据：100 个学生 × 3 个科目 = 300 行 |
| `summary.csv` | 输出：各科目统计表 |
| `result.png` | 输出：各科平均分柱状图 |
| `day1.py` ~ `day7.py` | 第 1 周每天的练习脚本（保留作过程记录） |

> `data.csv` 不提交到 git（`.gitignore` 里忽略了 `*.csv`）。
> 这是有意的：**不提交数据，提交生成数据的脚本**——脚本固定了种子，跑一遍就能得到一模一样的数据。

---

## 怎么跑

### 完整流程（从零开始）

```bash
python make_data.py      # 1. 生成数据 data.csv
python analyze.py        # 2. 分析并输出 result.png + summary.csv
```

### 常用参数

```bash
# 默认：读 data.csv，结果输出到当前目录
python analyze.py

# 指定输入文件
python analyze.py --input 别的数据.csv

# 指定输出目录（目录不存在会自动创建）
python analyze.py --outdir out

# 组合使用
python analyze.py --input data.csv --outdir out
```

| 参数 | 默认值 | 说明 |
|---|---|---|
| `--input` | `data.csv` | 输入 CSV 路径 |
| `--outdir` | `.`（当前目录） | 输出目录，不存在会自动创建 |

---

## 输出

### `summary.csv`

各科目的平均分、最低分、最高分、人数：

```
科目,mean,min,max,count
数学,75.74,45,100,100
英语,74.83,35,100,100
语文,71.62,26,100,100
```

### `result.png`

各科目平均分柱状图，柱顶标注具体数值。

---

## 代码结构

`analyze.py` 分成四个函数，每个只做一件事：

| 函数 | 职责 |
|---|---|
| `load(path)` | 读 CSV，返回 DataFrame |
| `stats(df)` | 按科目分组统计，返回汇总表 |
| `plot(df, out_path)` | 画各科平均分柱状图并保存 |
| `main()` | 解析参数，把上面三个串起来 |

这样拆分的好处：改统计逻辑只动 `stats()`，换图表只动 `plot()`，互不影响。

---

## 数据说明

`make_data.py` 用 `np.random.seed(42)` 固定了随机种子，生成规则：

- 100 个学生，每人 3 个科目（数学 / 语文 / 英语）
- 分数服从正态分布 `N(75, 15)`，再截断到 `[0, 100]`
- 共 300 行

**因为种子固定，任何人跑 `make_data.py` 都会得到完全相同的 `data.csv`。**

---

## 已知限制

- 只处理这一种数据格式（列必须为 `姓名` / `科目` / `分数`）
- 只画平均分柱状图，不支持其他图表类型
- 没有处理缺失值
