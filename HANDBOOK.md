# 自学手册

> 写给「没人问的时候」的自己。
> 覆盖：日常操作 / 知识点与代码 / Bug 速查 / 文件提交
> 维护：**遇到新坑就往里加**，这份文件越用越顺手。

---

## 目录

- [0. 怎么用这份文件](#0-怎么用这份文件)
- [1. 每天要做的四件事](#1-每天要做的四件事)
- [2. 环境速查](#2-环境速查)
- [3. 文件提交方式（Git 完整版）](#3-文件提交方式git-完整版)
- [4. 知识点与代码](#4-知识点与代码)
- [5. 观察期第 5-6 周怎么做](#5-观察期第-5-6-周怎么做)
- [6. Bug 速查表](#6-bug-速查表)
- [7. 卡住时的自救顺序](#7-卡住时的自救顺序)
- [8. 每天的最小检查](#8-每天的最小检查)
- [9. 三个月后回看这三条](#9-三个月后回看这三条)

---

## 0. 怎么用这份文件

**这份文件里的代码分两种，看标记：**

| 标记 | 含义 |
|---|---|
| ✅ **实测** | 我在你这台机器上真跑过，输出正确 |
| ⚠️ **未实测** | 语法标准但我没法跑（比如需要 API Key），**第一次用要自己小心** |

**遇到没写在这里的报错** → 见第 6 节「自救顺序」。

---

## 1. 每天要做的四件事

```
① 写日志（3 行）        notes/log.md
② 跑一遍自己的代码       确认还能跑
③ 提交                  git add / commit / push
④ 记新坑                遇到的 bug 写进第 5 节
```

**第 ① 和第 ③ 是雷打不动的。** 理由见第 3 节末尾。

---

## 2. 环境速查

### 你有三个 Python，别搞混

| 环境 | 路径 | 用途 |
|---|---|---|
| **agent** ← 用这个 | `D:\anaconda\envs\agent\python.exe` | **六周方案 / 项目专用** |
| base | `D:\anaconda\python.exe` | Anaconda 默认 |
| 系统 Python | `D:\PYTHON\python 3.13\python.exe` | 独立安装的 |

### 进环境

```powershell
conda activate agent
```

**提示符变成 `(agent)` 就成功了。**

**如果 `conda activate` 不生效**，用完整路径：

```powershell
D:\anaconda\envs\agent\python.exe 你的脚本.py
```

**装包**（注意用 agent 的 pip）：

```powershell
D:\anaconda\envs\agent\Scripts\pip.exe install 包名
```

### 验证环境对不对

```powershell
D:\anaconda\envs\agent\python.exe -c "import sys; print(sys.executable)"
```

**必须输出 `D:\anaconda\envs\agent\python.exe`。** 输出别的就是没对上。

### 已装的东西

| 包 | 版本 |
|---|---|
| Python | 3.11.16 |
| torch | 2.11.0+cu128 |
| torchvision | 0.26.0+cu128 |
| numpy / pandas / matplotlib | 2.4.6 / 3.0.6 / 3.11.2 |
| **显卡** | RTX 5060 Laptop, 8GB, sm_120, CUDA 12.8 |

### 每个脚本开头都加这两行

```python
import sys
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
```

**不加的话，终端里中文全是乱码。**

---

## 3. 文件提交方式（Git 完整版）

### 3.1 四条主线命令

**先理解这个链条，顺序不能跳：**

```
① 工作区        你在 E:\agent 里编辑的文件
      ↓  git add .
② 暂存区        "我准备把哪些改动打包"
      ↓  git commit -m "说明"
③ 本地仓库      真正的存档（你硬盘上）
      ↓  git push
④ 远程仓库      GitHub（github.com/16ismywaife/agent）
```

**日常就这三条：**

```powershell
cd E:\agent
git add .                                  # ① 把所有改动放进暂存区
git commit -m "week2: MNIST 训练脚本"       # ② 打包成一次提交
git push                                   # ③ 推到 GitHub
```

**关键**：
- 只 `add` 不 `commit` → **没东西可推**
- 只 `commit` 不 `push` → **只在本地，GitHub 看不到**

### 3.2 先看状态（出问题时的第一步）

```powershell
git status
```

**常见输出含义：**

| 输出 | 含义 |
|---|---|
| `nothing to commit, working tree clean` | 干净，没有未提交改动 |
| `Changes not staged for commit` | 改了文件但还没 `add` |
| `Changes to be committed` | 已 `add`，等着 `commit` |
| `Untracked files` | 新文件，git 还不认识它（要 `git add`） |
| `AM 文件名` | A=已暂存新文件，M=暂存后又被改过 |

### 3.3 看历史

```powershell
git log --oneline           # 一行一条
git log --oneline -10       # 最近 10 条
git log --stat              # 带文件改动统计
```

### 3.4 撤销与后悔

| 想干什么 | 命令 | 危险度 |
|---|---|---|
| 撤销某文件的**未暂存**修改 | `git restore 文件` | 低（改动没了） |
| 撤销**暂存**（`add` 之后反悔） | `git restore --staged 文件` | 低 |
| 修改**最后一次**提交的说明 | `git commit --amend -m "新说明"` | 中（**只有没 push 过才能用**） |
| 看某个文件的历史 | `git log --oneline -- 文件` | 无 |
| 看某次提交改了什么 | `git show 提交号` | 无 |

> ⚠️ **`--amend` 只在"还没 push"时安全。** push 过之后再 amend，本地和远端就不一致了。

### 3.5 分支（做实验用）

```powershell
git switch -c feat/新功能      # 建分支并切过去（-c = create）
git switch main                # 切回主线
git merge feat/新功能          # 把分支合并进 main
git branch                     # 看本地分支（* 是当前）
git branch -d feat/新功能      # 删掉已合并的分支
```

**为什么用分支**：不破坏 `main` 的前提下做实验。改坏了，切回 `main` 就恢复了。

**切分支时硬盘上的文件会跟着变**——这是最直观的效果。

**推一个新分支：**

```powershell
git push -u origin feat/新功能
```

### 3.6 `.gitignore`（哪些文件不提交）

**现在的内容：**

```
__pycache__/        Python 缓存
*.pyc
.env                ★ API Key，绝对不能提交
data/               数据集
logs/               程序运行日志
checkpoints/        模型权重
*.pth  *.pt         模型文件
*.csv               数据表（可重新生成）
.idea/              PyCharm 配置
```

**注意：`notes/` 不在忽略列表里** —— **工作日志必须提交**，那是面试素材。

**想确认某个文件有没有被忽略：**

```powershell
git check-ignore -v 文件路径
```

**有输出 = 被忽略了。没输出 = 会提交。**

### 3.7 ⚠️ 千万不要提交的东西

| 文件 | 后果 |
|---|---|
| **`.env`** | **API Key 泄露，会被人扫走盗刷** |
| `*.pth` / `*.pt` | 模型几百 MB，仓库爆掉 |
| `data/` | 数据集可能几个 G |
| `.idea/` | 你的 IDE 配置，别人不需要 |

**已经提交了怎么办（比如 `.env` 泄露）：**

1. **立刻去对应平台把 Key 作废/重新生成**（最重要，删历史没用）
2. 再把文件从 git 里移除：

```powershell
git rm --cached .env
git commit -m "chore: 移除 .env"
git push
```

> ⚠️ **`git rm --cached` 只从"之后的版本"里删掉，历史里还在。**
> 所以**第一步永远是作废 Key**，不是删文件。

### 3.8 提交信息怎么写

**格式**：`<范围>: <做了什么>`

```powershell
git commit -m "week2: MNIST 训练脚本跑通"
git commit -m "week1: day3 函数与类（含边界bug修复）"
git commit -m "fix: analyze.py 的 --outdir 参数崩溃"
```

**为什么重要**：**你的提交历史就是你 2027 年 3 月投简历时的"持续投入"证据。** 一条 `asdf` 和一条 `week2: MNIST 训练脚本跑通`，给人的印象完全不同。

### 3.9 提交的三条铁律

1. **每天至少提交一次** —— 不提交 = 没备份 = 硬盘坏了全没
2. **提交前跑一遍代码** —— 别把跑不通的东西提交上去
3. **提交信息写清楚** —— 三个月后你自己要看懂

---

## 4. 知识点与代码

> 所有 ✅ 标记的代码都在你的 `agent` 环境里实测过。

### 4.1 Python 基础（Week1 D2）

```python
# 变量与类型
n = 10            # int
x = 3.14          # float
s = "hello"       # str
flag = True       # bool
empty = None      # None

# 列表 / 字典
nums = [1, 2, 3]
person = {"name": "张三", "age": 20}

# 条件
if n > 5:
    print("大")
elif n > 0:
    print("小")
else:
    print("非正")

# 循环
for i in range(5):        # 0,1,2,3,4
    print(i)
for item in nums:
    print(item)
while n > 0:
    n -= 1

# 列表推导式
doubled = [x * 2 for x in nums]              # [2,4,6]
passed  = [s for s in scores if s >= 60]

# ★ 字典计数模式（很常用，记住它）
counts = {}
for item in items:
    counts[item] = counts.get(item, 0) + 1
#                     ↑ 取不到就返回 0，这样第一次遇到不会 KeyError
```

### 4.2 函数与类（Week1 D3）

```python
# 函数
def add(a, b, scale=1):        # scale 是默认参数
    """文档字符串：说明这个函数干什么"""
    return (a + b) * scale

add(1, 2)          # 3
add(1, 2, 10)      # 30

# 没有 return 的函数返回 None
def no_return():
    print("hi")
print(no_return())    # None


# 类
class ScoreAnalyzer:
    """分数分析器"""

    def __init__(self, scores):      # 创建对象时自动调用
        self.scores = scores         # 存成"我的属性"

    def count_pass(self, line=60):
        return len([s for s in self.scores if s >= line])

    def pass_rate(self, line=60):
        return self.count_pass(line) / len(self.scores)

    def summary(self, line=60):
        return f"共 {len(self.scores)} 人，及格 {self.count_pass(line)} 人"


if __name__ == "__main__":           # 只在直接运行时执行
    a = ScoreAnalyzer([88, 45, 92, 60, 73, 39, 95])
    print(a.count_pass())    # 5
    print(a.pass_rate())     # 0.714...
    print(a.summary())
```

**三个必须先弄明白的点：**

1. **`self` 就是"这个对象自己"**
   `a.count_pass()` 等价于 `ScoreAnalyzer.count_pass(a)`
2. **`__init__` 在创建对象时自动跑**，不用手动调
3. **属性要写 `self.xxx`**，不写的话函数跑完就没了，其他方法读不到

**`if __name__ == "__main__":` 的作用**：别人 `import` 你的文件时不会自动执行。

### 4.3 NumPy（Week1 D4）✅ 实测

```python
import numpy as np

# 创建
np.array([1, 2, 3])
np.zeros((2, 3))                          # 2行3列全0
np.arange(10)                             # 0~9
np.random.seed(42)                        # 固定随机种子（重要！保证可复现）
a = np.random.randint(0, 100, size=(5, 3))   # 5行3列，【不含100】

# 属性
a.shape      # (5, 3)
a.dtype      # int64
a.ndim       # 2

# 取值
a[0]            # 第0行
a[:, 0]         # 第0列
a[1:3, 0:2]     # 切片

# 聚合（★ axis 是重点）
a.mean()          # 全体平均
a.mean(axis=0)    # 消掉第0维 → 每列一个值
a.mean(axis=1)    # 消掉第1维 → 每行一个值

# 布尔索引
a[a > 80]         # 取出所有 > 80 的
a[a > 80] = 60    # 把所有 > 80 的改成 60
```

**`axis` 的记忆法：`axis` 是"要被消掉的那一维"。**

**验证办法：看输出长度。**
`mean(axis=0)` 出 3 个数，3 就是列数 → 所以是"每列"。

**区间规则：左闭右开。** `randint(0, 100)` 是 0~99，`range(10)` 是 0~9。

### 4.4 Pandas（Week1 D5）✅ 实测

```python
import pandas as pd

# 读 / 写
df = pd.read_csv("data.csv")
df = pd.read_csv("data.csv", encoding="utf-8-sig")   # 有 BOM 时
df = pd.read_csv("data.csv", encoding="gbk")         # 老文件
df.to_csv("out.csv", index=False, encoding="utf-8-sig")

# 看数据（拿到表先做这几件事）
df.head()        # 前5行
df.shape         # (行数, 列数)
df.columns       # 列名
df.dtypes        # 每列类型
df.info()        # 非空数量+类型
df.describe()    # 数值列统计摘要

# 选列
df["分数"]              # → Series（一列）
df[["科目", "分数"]]    # → DataFrame（子表）★ 双括号

# 筛选行
df[df["分数"] > 90]
df[(df["科目"] == "数学") & (df["分数"] > 90)]     # ★ & 不是 and，每个条件要括号

# 统计
df["分数"].mean() / .max() / .min() / .std() / .median()
df["科目"].value_counts()        # 每个值出现几次
df["姓名"].nunique()             # 有多少个不同的值
len(df)                          # 一共多少行

# ★ groupby（数据透视表）
df.groupby("科目")["分数"].mean()
df.groupby("科目")["分数"].agg(["mean", "max", "min", "count"])

# 排序
df.sort_values("分数")
df.sort_values("分数", ascending=False)
df.groupby("科目")["分数"].mean().sort_values(ascending=False)   # ★ 链式调用

# 新增/修改列
df["是否及格"] = df["分数"] >= 60
df["分数"] = df["分数"] + 5
df["等级"] = df["分数"].apply(lambda x: "高" if x >= 90 else "低")

# 透视表 / 分段 / 缺失值
df.pivot_table(index="姓名", columns="科目", values="分数")
pd.crosstab(df["段"], df["科目"])          # 交叉计数（比 pivot_table 简洁）
pd.cut(df["分数"], bins=[0, 59, 79, 100], labels=["<60", "60-79", "80-100"])
df["分数"].isna().sum()
df.dropna(subset=["分数"])
df["分数"].fillna(0)
```

**★ 最重要的一条习惯：**

```python
print(type(x), x.shape, list(x.columns))
```

**链式操作的每一步都插一行这个。** 它能挡掉 90% 的 pandas 错误——因为大部分错误都是"我以为我手里是 A，其实是 B"。

**关键：同一个 groupby，加不加 `agg` 出来的东西完全不同**

```
.mean()      → Series     (3,)      值就是平均值
.agg([...])  → DataFrame  (3, 4)    列名变成 ['mean','min','max','count']
```

**索引是"名字"不是"行号"**：`to_csv(index=False)` 会把索引（比如科目名）丢掉。

### 4.5 Matplotlib（Week1 D6）✅ 实测

```python
import matplotlib
matplotlib.rcParams["font.sans-serif"] = ["SimHei"]     # ★ 中文不乱码
matplotlib.rcParams["axes.unicode_minus"] = False       # ★ 负号正常
import matplotlib.pyplot as plt

# ★ 两层结构
fig, ax = plt.subplots(figsize=(7, 4.5))
#  ↑     ↑
# 画布   坐标系

# fig. 管"整张纸"
fig.tight_layout()              # 调整间距（不加标题会被切掉）
fig.savefig("x.png", dpi=130)   # 保存
figsize=(7, 4.5)                # 画布尺寸（英寸）

# ax. 管"纸上的图"
ax.bar(s.index, s.values, color="#4C78A8")   # 柱状图
ax.plot(x, y, marker="o", label="系列名")     # 折线图
ax.hist(df["分数"], bins=20)                 # 直方图
ax.scatter(x, y)                             # 散点图
ax.set_title("标题")
ax.set_xlabel("X轴名")
ax.set_ylabel("Y轴名")
ax.legend()

# 柱子上标数值
for i, v in enumerate(s.values):
    ax.text(i, v + 0.8, f"{v:.1f}", ha="center")

# pandas 风格（返回的是 ax，不是 fig！）
ax = df.plot(kind="bar", figsize=(7, 4.5), rot=0)
fig = ax.get_figure()
fig.savefig("y.png", dpi=130)
```

**选图原则**：比大小用柱、看趋势用线、看分布用直方、看关系用散点。

**★ 自检：看文件大小**

| 图 | 正常大小 |
|---|---|
| 柱状图 | ~19,000–26,000 bytes |
| 直方图 | ~18,000 bytes |
| **空白图** | **~10,000 bytes** ← 太小就是没画出东西 |

### 4.6 PyTorch：Tensor 与自动求导（Week2）✅ 实测

```python
import torch

# Tensor = NumPy 数组 + 自动求导 + 能上 GPU
a = torch.tensor([1.0, 2.0, 3.0])       # 默认 float32（numpy 默认 float64）
a.to("cuda")                            # 搬到 GPU
torch.from_numpy(np_array)              # numpy -> tensor
a.numpy()                               # tensor -> numpy（要在 CPU 上）

# ★ 自动求导
x = torch.tensor([2.0], requires_grad=True)   # 告诉 torch：盯着这个变量
y = x**2 + 3*x                                # 前向：暗中记录计算图
y.backward()                                  # 反向：算出梯度
print(x.grad)                                 # 7.0  （2x+3 = 7）

# 多变量：一次 backward 同时算出所有梯度
x = torch.tensor([1.0], requires_grad=True)
w = torch.tensor([3.0], requires_grad=True)
b = torch.tensor([2.0], requires_grad=True)
y = w * x + b
y.backward()
# w.grad = 1.0 (=x),  b.grad = 1.0 (=1),  x.grad = 3.0 (=w)

# ★ 陷阱：梯度会【累积】，必须手动清零
for i in range(3):
    y = x**2
    y.backward()          # 第1次 grad=4, 第2次 grad=8, 第3次 grad=12
# 正确做法：
x.grad.zero_()            # 或者训练循环里的 optimizer.zero_grad()
```

**★ 核心练习：用自动求导做梯度下降（拟合 y = 2x + 1）**

```python
import torch

torch.manual_seed(0)
X = torch.linspace(-1, 1, 50).unsqueeze(1)
Y = 2 * X + 1

w = torch.tensor([0.0], requires_grad=True)
b = torch.tensor([0.0], requires_grad=True)
lr = 0.1

for epoch in range(200):
    y_pred = X * w + b
    loss = ((y_pred - Y) ** 2).mean()
    loss.backward()                      # 反向：算出 w.grad / b.grad
    with torch.no_grad():                # 更新时不要建计算图
        w -= lr * w.grad
        b -= lr * b.grad
    w.grad.zero_()                       # 清零，否则梯度累积
    b.grad.zero_()

print(w.item(), b.item())    # 2.0000 1.0000  ← 收敛到真实值
```

**实测结果**：
```
epoch   0  loss=2.387755  w=0.1388  b=0.2000
epoch 100  loss=0.000001  w=1.9986  b=1.0000
epoch 199  loss=0.000000  w=2.0000  b=1.0000
```

**★ "为什么需要反向传播"的答案（考核点名）：**

> 训练就是不断调参数让 Loss 变小。要调参数，得知道**每个参数对 Loss 的影响**——也就是梯度。
> 但模型有几十万到几十亿个参数，**不可能手算**。
> 反向传播用链式法则从 Loss 倒着走一遍计算图，**一次算出所有参数的梯度**。
> **没有它，参数就只能瞎猜**——实测把 `backward()` 删掉跑 200 轮，w 还是 0。

### 4.7 Dataset 与 DataLoader（Week2）✅ 实测

```python
import torch
from torchvision import datasets, transforms
from torch.utils.data import DataLoader

tf = transforms.Compose([
    transforms.ToTensor(),                       # 变成 tensor，并归一化到 [0,1]
    transforms.Normalize((0.1307,), (0.3081,)),  # MNIST 的均值和标准差
])

train_ds = datasets.MNIST("./data", train=True,  download=True, transform=tf)
test_ds  = datasets.MNIST("./data", train=False, download=True, transform=tf)

train_ld = DataLoader(train_ds, batch_size=64,  shuffle=True)    # 训练集要 shuffle
test_ld  = DataLoader(test_ds,  batch_size=256, shuffle=False)   # 测试集不用

x, y = next(iter(train_ld))
print(x.shape, y.shape)     # torch.Size([64,1,28,28]) torch.Size([64])
```

**Dataset 和 DataLoader 的分工**：
- `Dataset` = 一份份数据（"第 i 个样本是什么"）
- `DataLoader` = 把数据打包成 batch、打乱顺序、多进程加载

**★ Windows 上 `num_workers` 大于 0 容易报错，用默认值 0。**

### 4.8 训练循环（Week2）✅ 实测

```python
import torch
import torch.nn as nn
import torch.optim as optim
from torchvision import datasets, transforms
from torch.utils.data import DataLoader

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# ---- 数据 ----
tf = transforms.Compose([transforms.ToTensor(),
                         transforms.Normalize((0.1307,), (0.3081,))])
train_ds = datasets.MNIST("./data", train=True,  download=True, transform=tf)
test_ds  = datasets.MNIST("./data", train=False, download=True, transform=tf)
train_ld = DataLoader(train_ds, batch_size=64,  shuffle=True)
test_ld  = DataLoader(test_ds,  batch_size=256, shuffle=False)

# ---- 模型 ----
class Net(nn.Module):
    def __init__(self):
        super().__init__()
        self.net = nn.Sequential(
            nn.Flatten(),                       # 28x28 -> 784
            nn.Linear(28*28, 128), nn.ReLU(),
            nn.Linear(128, 10),                 # 10 个类别
        )
    def forward(self, x):
        return self.net(x)

model = Net().to(device)
criterion = nn.CrossEntropyLoss()                       # 分类用交叉熵
optimizer = optim.Adam(model.parameters(), lr=1e-3)

# ---- 评估 ----
def evaluate():
    model.eval()                            # ★ 切到评估模式
    correct = total = 0
    with torch.no_grad():                   # ★ 不建计算图，省显存
        for x, y in test_ld:
            x, y = x.to(device), y.to(device)
            pred = model(x).argmax(dim=1)
            correct += (pred == y).sum().item()
            total += y.size(0)
    return correct / total

# ---- ★ 训练循环：记住这 5 步 ----
for epoch in range(3):
    model.train()                           # ★ 切回训练模式
    for x, y in train_ld:
        x, y = x.to(device), y.to(device)
        optimizer.zero_grad()               # ① 清空上轮梯度（不清理会累积）
        out = model(x)                      # ② 前向
        loss = criterion(out, y)            # ③ 算损失
        loss.backward()                     # ④ 反向求梯度
        optimizer.step()                    # ⑤ 更新参数
    print(f"epoch {epoch+1}  loss={loss.item():.4f}  acc={evaluate():.4f}")
```

**实测结果**（3 epoch，每 epoch 只用了 2000 张）：
```
epoch 1  loss=0.5852  test_acc=0.8110
epoch 2  loss=0.1497  test_acc=0.8540
epoch 3  loss=0.4630  test_acc=0.8670
```

**★ 训练循环 5 步必须背下来：**
`zero_grad → forward → loss → backward → step`

### 4.9 保存与加载模型（Week2）✅ 实测

```python
# 保存
torch.save(model.state_dict(), "model.pth")

# 加载（★ 模型结构必须先定义好，且和训练时完全一致）
model2 = Net()
model2.load_state_dict(torch.load("model.pth", map_location="cpu"))
model2.eval()

# 推理
with torch.no_grad():
    pred = model2(x.unsqueeze(0)).argmax().item()
```

**实测**：保存 400 KB，加载后预测正确（预测=7 真实=7）。

**`map_location="cpu"`**：在有 GPU 的机器上存、在没 GPU 的机器上读时要用。

### 4.10 LLM / API 调用（Week3）⚠️ 未实测

**我没有 API Key，跑不了。语法是标准的，但你第一次用要自己小心。**

```python
# 先装：pip install openai python-dotenv

import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()      # 从 .env 文件读环境变量
client = OpenAI(api_key=os.getenv("API_KEY"), base_url=os.getenv("BASE_URL"))

# 单轮
resp = client.chat.completions.create(
    model=os.getenv("MODEL"),
    messages=[{"role": "user", "content": "用一句话解释什么是反向传播"}],
)
print(resp.choices[0].message.content)
print("tokens:", resp.usage)

# 多轮（★ 模型没有记忆，靠把历史全部传回去实现）
history = [{"role": "system", "content": "你是一个耐心的助教。"}]
def chat(user_input):
    history.append({"role": "user", "content": user_input})
    resp = client.chat.completions.create(model=os.getenv("MODEL"), messages=history)
    reply = resp.choices[0].message.content
    history.append({"role": "assistant", "content": reply})
    return reply

# 结构化输出（★ Agent 的地基）
prompt = """从下面文本抽取信息，只输出 JSON，不要其他文字。
格式：{"姓名": "", "分数": 0}
文本：张小明数学考了 88 分。"""
resp = client.chat.completions.create(
    model=os.getenv("MODEL"),
    messages=[{"role": "user", "content": prompt}],
    response_format={"type": "json_object"},     # 支持的话用
)

# 不支持 json_object 时用正则兜底
import re, json
text = resp.choices[0].message.content
m = re.search(r"\{.*\}", text, re.S)
data = json.loads(m.group(0)) if m else None
```

**`.env` 文件长这样：**

```
API_KEY=你的密钥
BASE_URL=https://api.deepseek.com/v1
MODEL=deepseek-chat
```

> ⚠️ **`.env` 必须在 `.gitignore` 里。** 泄露 = 别人拿你的额度。

### 4.11 Agent：LLM + 1 个 Tool（Week4）⚠️ 未实测（需要 API Key）

```python
import os, json
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI(api_key=os.getenv("API_KEY"), base_url=os.getenv("BASE_URL"))
MODEL = os.getenv("MODEL")

# ---- ① 定义工具：真正执行的是这里 ----
def calculator(expression: str) -> str:
    allowed = set("0123456789+-*/(). %")
    if not set(expression) <= allowed:
        return "错误：表达式含非法字符"
    try:
        return str(eval(expression, {"__builtins__": {}}, {}))
    except Exception as e:
        return f"计算错误：{e}"

TOOLS_IMPL = {"calculator": calculator}

# ---- ② 告诉模型有哪些工具 ----
TOOLS_SPEC = [{
    "type": "function",
    "function": {
        "name": "calculator",
        "description": "计算数学表达式。需要算术时调用。",
        "parameters": {
            "type": "object",
            "properties": {"expression": {"type": "string", "description": "数学表达式"}},
            "required": ["expression"],
        },
    },
}]

# ---- ③ Agent 主循环 ----
def run_agent(question, max_steps=5):
    messages = [
        {"role": "system", "content": "需要算术时调用 calculator，不要自己心算。"},
        {"role": "user", "content": question},
    ]
    for step in range(max_steps):
        resp = client.chat.completions.create(
            model=MODEL, messages=messages, tools=TOOLS_SPEC)
        msg = resp.choices[0].message
        messages.append(msg)

        if not msg.tool_calls:               # 模型没要求调工具 → 结束
            return msg.content

        for tc in msg.tool_calls:            # 模型要求调工具 → 【我们】执行
            name = tc.function.name
            args = json.loads(tc.function.arguments)
            result = TOOLS_IMPL[name](**args)      # ← 可能 KeyError（模型编造工具名）
            messages.append({"role": "tool", "tool_call_id": tc.id, "content": result})

    return "达到最大步数"
```

**★ 必须能回答：**

- **模型怎么"决定"调不调工具？** → 靠 `tools` 参数里的工具描述
- **工具是谁执行的？** → **你的代码**，模型只"决定调什么"
- **为什么要 `max_steps`？** → 防止无限循环
- **`tool_call_id` 干什么？** → 把执行结果和模型的请求对应起来
- **模型编造不存在的工具名会怎样？** → `KeyError`。**这就是"失败重试"要解决的**

### 4.12 SQL / 数据库（长期）✅ 实测

```python
import sqlite3

conn = sqlite3.connect("demo.db")
cur = conn.cursor()

# 建表
cur.execute("""
CREATE TABLE IF NOT EXISTS tool_calls (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    tool       TEXT,
    success    INTEGER,
    elapsed_ms REAL,
    ts         TEXT DEFAULT CURRENT_TIMESTAMP
)""")

# 建索引（加快查询）
cur.execute("CREATE INDEX IF NOT EXISTS idx_tool ON tool_calls(tool)")

# 插入
cur.executemany(
    "INSERT INTO tool_calls (tool, success, elapsed_ms) VALUES (?,?,?)",
    [("calculator", 1, 12.3), ("weather", 0, 340.1), ("calculator", 1, 9.8)])
conn.commit()

# 查询
cur.execute("""SELECT tool,
                      COUNT(*) n,
                      ROUND(AVG(success)*100,1) rate,
                      ROUND(AVG(elapsed_ms),1) avg_ms
               FROM tool_calls GROUP BY tool ORDER BY n DESC""")
for row in cur.fetchall():
    print(row)
conn.close()
```

**核心 SQL 语法：**

```sql
SELECT 列 FROM 表 WHERE 条件 ORDER BY 列 DESC LIMIT 10;
SELECT 列, COUNT(*) FROM 表 GROUP BY 列 HAVING COUNT(*) > 5;
SELECT a.*, b.* FROM 表A a JOIN 表B b ON a.id = b.a_id;
```

### 4.13 数据结构与算法（长期，第一优先）

**依据**：技术实习岗 **46.9%** 要求（与 Python 并列第一）。

**力度**：**"熟悉常见数据结构"就够，不用刷 LeetCode 难题。**

| 结构 | 要点 |
|---|---|
| 数组 | 随机访问 O(1)，插入删除 O(n) |
| 链表 | 插入删除 O(1)，访问 O(n) |
| 栈 | 后进先出（LIFO） |
| 队列 | 先进先出（FIFO） |
| 哈希表 | 查找 O(1)（Python 的 `dict` 就是） |
| 排序 | 冒泡 O(n²)、快排/归并 O(n log n) |

**刷题节奏**：LeetCode 简单 + 部分中等，**60–100 题**，每题能讲清思路。

---

### 4.14 Linux 常用命令（Week2，培养方案要求）

**你没有 Linux 机器，但命令要认识**——迟早会在服务器/容器里遇到。

**在 Windows 上练习：用 Git Bash**（开始菜单搜 `Git Bash`），大部分命令通用。

```bash
pwd              # 我在哪个目录
ls -la           # 列出所有文件（含隐藏）
cd /path         # 切换目录
cd ..            # 上一级
mkdir demo       # 建目录
cp a b           # 复制
mv a b           # 移动 / 重命名
rm file          # 删文件
rm -rf demo/     # 删目录（★ 危险，想清楚再敲）
cat file.txt     # 看文件内容
head -n 20 f     # 看前 20 行
tail -n 20 f     # 看后 20 行
grep "error" log.txt        # 搜内容
grep -r "def " .            # 递归搜
find . -name "*.py"         # 找文件
chmod +x run.sh             # 加执行权限
ps aux | grep python        # 看进程
top                         # 看资源占用
nvidia-smi                  # 看显卡
```

**管道与重定向：**

```bash
python train.py > log.txt 2>&1    # 输出存文件（含报错）
cat log.txt | grep "acc"          # 只看含 acc 的行
```

**和 Windows 的区别：**

| | PowerShell | Linux / Git Bash |
|---|---|---|
| 路径分隔符 | `\` | `/` |
| 家目录 | `$env:USERPROFILE` | `~`（**bash 里会展开**） |
| 盘符 | `E:\agent` | `/e/agent` |
| 删目录 | `Remove-Item -Recurse` | `rm -rf` |

> ⚠️ **`~` 的区别**：Linux/Git Bash 里会展开；**PowerShell 里传给外部程序时不展开**（你踩过这个坑）。

### 4.15 YOLO / 计算机视觉（Week3 备选分支）✅ 实测

**Week3 是二选一：① YOLO 视觉 ② 大模型。你选了②，但①也记一下。**

```bash
pip install ultralytics opencv-python
```

```python
import numpy as np
import cv2
from ultralytics import YOLO

# 加载模型（第一次会自动下载权重；下载超时就指定本地路径）
model = YOLO("yolov8n.pt")
# model = YOLO(r"C:\Users\omen\yolov8n.pt")     # 用本机已有的

img = cv2.imread("test.jpg")
results = model(img, verbose=False)
r = results[0]

print(f"检测到 {len(r.boxes)} 个框")
print(f"坐标:   {r.boxes.xyxy}")     # 形状 (N, 4)
print(f"类别:   {r.boxes.cls}")      # 形状 (N,)
print(f"置信度: {r.boxes.conf}")     # 形状 (N,)

annotated = r.plot()                 # 返回 BGR 图像，形状同输入
cv2.imwrite("out.jpg", annotated)
```

**实测结果**（用本机 `C:\Users\omen\yolov8n.pt`）：
```
模型加载   0.07s
单张推理   1308ms
r.boxes.xyxy 形状  (0, 4)
r.plot() 返回      (480, 640, 3)
```

> **权重下载经常超时**（GitHub）。本机已有可直接用：
> `C:\Users\omen\yolov8n.pt`、`D:\dsh\YOLO-Starfish-repo\weights\yolov8n.pt`

### 4.16 视频 Edge（Week4 三方向之一）✅ 实测

**关键指标是 FPS**（能不能实时处理）。

```python
import cv2, time
from ultralytics import YOLO

model = YOLO("yolov8n.pt")
cap = cv2.VideoCapture("test.mp4")     # 或 0 用摄像头

fps_list = []
frames = 0
t_start = time.time()

while True:
    ok, frame = cap.read()
    if not ok:
        break
    t0 = time.time()
    results = model(frame, verbose=False)
    fps_list.append(1.0 / (time.time() - t0))

    frames += 1
    cv2.imwrite(f"out/frame_{frames:05d}.jpg", results[0].plot())
    if frames >= 200:                   # 只跑 200 帧做测试
        break

cap.release()
print(f"处理 {frames} 帧, 平均 {sum(fps_list)/len(fps_list):.1f} FPS")
print(f"总耗时 {time.time()-t_start:.1f}s")
```

**实测**（60 帧随机噪声）：
```
平均 FPS: 12.4
总耗时:   13.0s
保存的帧: 3 个
```

**为什么 FPS 是关键指标**：视频通常 25–30 FPS。**处理速度低于它就跟不上实时**，会丢帧或延迟累积。

**要记录的**：帧数、平均 FPS、总耗时、显存占用（`nvidia-smi`）。

### 4.17 LLM 部署（Week4 三方向之一）⚠️ 未实测

**目标**：跑起来一个开源 LLM，**记录显存占用和推理速度**。

**选项 A：Ollama**（最简单）

```bash
ollama pull qwen2.5:1.5b
ollama run qwen2.5:1.5b
```

**选项 B：vLLM**（接近工业用法，需要 NVIDIA 显卡）

```bash
pip install vllm
python -m vllm.entrypoints.openai.api_server --model Qwen/Qwen2.5-1.5B-Instruct
```

**要记录的指标：**

| 指标 | 怎么测 | 单位 |
|---|---|---|
| 显存占用 | `nvidia-smi` | MB |
| 加载时间 | `time` | 秒 |
| **首 token 延迟（TTFT）** | 代码计时 | 毫秒 |
| **生成速度** | 输出 token 数 / 耗时 | tokens/s |

```python
import time
t0 = time.time()
r = client.chat.completions.create(model="本地模型名",
        messages=[{"role": "user", "content": "写一段 200 字的介绍"}])
t1 = time.time()
n_out = r.usage.completion_tokens
print(f"耗时 {t1-t0:.2f}s, 输出 {n_out} tokens, 速度 {n_out/(t1-t0):.1f} tokens/s")
```

> **没有显卡 / 下载不下来**：用 API 替代，但**指标要换**——记录"不同 max_tokens 的耗时"或"并发请求的延迟"。
> **重点是"记录指标"这个动作**，不是非要本地跑。

**TTFT 和吞吐量的区别**：
- **TTFT**（Time To First Token）= 用户等多久看到第一个字 → 影响"感觉快不快"
- **吞吐量**（tokens/s）= 生成多快 → 影响"多久说完"

### 4.18 RAG / 知识库（Week5 可选项）⚠️ 未实测

**核心流程：**

```
文档 → 解析 → 切块(Chunk) → 向量化(Embedding) → 存进向量库
                                                    ↓
用户问题 → 向量化 → 检索(Top-k) → [重排 Rerank] → 拼进 Prompt → LLM 回答
```

**要比较的参数**（Week5 的"对比实验"）：Chunk 大小、Embedding 模型、Top-k、是否 Rerank。

**文档点名的关键问题：**

> **什么时候 RAG 真正有用，什么时候反而给 Agent 提供错误信息？**

**这就是它和"调包"的区别**——RAG 会检索到不相关片段，然后 LLM 基于错误信息自信地胡说。**这个失败模式值得专门记录。**

---

## 5. 观察期第 5-6 周怎么做

> 前 4 周是学技术，第 5-6 周是**把技术变成"能拿出去的东西"**。

### 5.1 第 5 周：选方向 + 完成一个小模块

**可选项（选一个）：**

| 选项 | 难度 | 产出 |
|---|---|---|
| **Agent 调用日志** | ★ | 日志记录 + 统计脚本 |
| **数据库 Tool** | ★★ | 可被 Agent 调用的数据库查询工具 |
| **任务评价脚本** | ★★ | 自动评分脚本 |
| **PDF 解析 Tool** | ★★ | 文档解析工具 |
| **简单 RAG** | ★★★ | 检索服务 |

**推荐：Agent 调用日志 或 数据库 Tool**——门槛低、产出明确，数据库那个顺带补了 SQL。

**考核标准（文档原文）：**
- 模块能**独立运行**
- **输入输出明确**
- **代码可复现**
- **能说明该模块在整体项目中的作用**

**做法：先写"接口契约"，再写代码。**

```markdown
# 模块：Agent 调用日志
## 输入
- Agent 每次运行的 trace（工具名、参数、结果、耗时、成功/失败）
## 输出
- logs/agent_run_YYYYMMDD.jsonl   每行一条记录
- 一个统计函数：成功率、平均调用次数、平均耗时
## 依赖
- 无外部服务；只用标准库
## 入口
- python logger.py --input trace.json --summary
```

**写完契约先给别人看一眼确认边界**——避免做偏。

### 5.2 第 6 周：正式考核

**要交四样东西（文档原文）：**

| 材料 | 要求 |
|---|---|
| 1. 可运行 Demo | **必须现场运行，不能只展示截图或 PPT** |
| 2. Git 代码仓库 | 代码能运行；能说明主要目录、入口程序、依赖环境 |
| 3. 5 页以内汇报 | 回答四问 |
| 4. 1 页个人总结 | 最感兴趣的方向、每周可投入时间、是否愿意长期参与 |

**5 页汇报的结构：**

**第 1 页 · 我做了什么**
- 6 周产出清单（每周一行）

**第 2 页 · 系统怎么运行**
- 一张架构图（手画拍照也行）
- 入口命令
- 关键目录说明

**第 3-4 页 · 遇到什么问题、怎么解决** ← **直接抄 `notes/log.md`**
- 挑 3–4 个最有代表性的
- 每个写成：现象 → 排查过程 → 根因 → 解法

**第 5 页 · 还有什么没完成**
- **诚实写。** 文档说"重点考察是否真正做过、是否能解释"
- **写清没做完什么不扣分，假装做完才扣分**

**Demo 准备清单：**
- [ ] **在考核用的机器上，提前跑一遍**
- [ ] 准备好演示数据（不要现场下载模型/数据集）
- [ ] 准备"现场跑挂了怎么解释"的预案
- [ ] 确认 Git 仓库干净（没有 `.env`、没有大文件）

---

## 6. Bug 速查表

### 6.1 ★ 你实际踩过的（最有价值）

| 报错 / 现象 | 根因 | 解法 |
|---|---|---|
| `SyntaxError: invalid non-printable character U+00A0` | 从网页复制代码带了**不换行空格** | 手敲，或全文替换 U+00A0 为普通空格 |
| 终端中文全是乱码 | Python 按 GBK 输出，控制台是 UTF-8 | 脚本开头 `sys.stdout.reconfigure(encoding="utf-8")` |
| `ax.bar=(x, y)` 不报错但图是空白 | **写成了赋值不是调用**，把方法覆盖成了元组 | 去掉等号：`ax.bar(x, y)` |
| 加 `color=` 报语法错误 | 因为上面那行是赋值，`color=` 跑到元组里了 | 先修掉等号 |
| `fig.savefig("out_path")` 存成怪名字 | **变量加了引号变成字面字符串** | 去掉引号：`fig.savefig(out_path)` |
| `else` 返回 `None`（嵌套函数） | 函数里又 `def` 了一个同名函数，外层什么都没干 | 删掉外层，只留一个 |
| `Column not found: 分数` | `st` 已经是 `.agg()` 的结果，**没有"分数"这一列** | 用原 `df`，或 `st["mean"]` |
| `TypeError: unsupported format string passed to numpy.ndarray` | `s.values` 是**二维**的，遍历出来是整行 | `enumerate(s["mean"])` 或把 `s` 变成 Series |
| `summary.csv` 里科目名不见了 | `to_csv(index=False)` **把索引丢了** | 去掉 `index=False` |
| `OSError: Cannot save file into a non-existent directory` | `--outdir` 传了不存在的目录 | `os.makedirs(args.outdir, exist_ok=True)` |
| `ssh-keygen` 报 `No such file or directory` | **PowerShell 里 `~` 不展开**，传给了外部程序 | 用 `$env:USERPROFILE\.ssh\...` |
| `git remote` 里字面写着"你的用户名" | 复制模板时没替换占位符 | `git remote set-url origin 正确地址` |
| `Enter passphrase for key ...` | 私钥设了密码短语 | 输入（**屏幕不显示字符是正常的**），或新生成一把不带密码的 |

### 6.2 环境类

| 报错 | 根因 | 解法 |
|---|---|---|
| `conda: command not found` | 安装没勾 PATH | 重装勾选，或手动加 PATH |
| `ModuleNotFoundError: No module named 'xxx'` | 没装 / 装错环境 | `conda activate agent` 后再 `pip install` |
| pip 装完还是 import 不到 | IDE 的解释器不对 | PyCharm: `File→Settings→Python Interpreter` |
| `ImportError: DLL load failed` | 缺 VC++ 运行库 | 装 Microsoft Visual C++ Redistributable |
| 装 torch 后 `CUDA 可用: False` | 装成了 CPU 版 | 重装，**必须带 `--index-url .../whl/cu128`** |

### 6.3 Python 类

| 报错 | 根因 | 解法 |
|---|---|---|
| `IndentationError` | Tab 和空格混用 | 统一 4 个空格 |
| `NameError: name 'x' is not defined` | 变量名拼错 / 用了没定义的 | 检查拼写和作用域 |
| `KeyError: 'xxx'` | 字典/DataFrame 里没这个键 | `print(list(d.keys()))` 或 `df.columns` |
| `IndexError: list index out of range` | 索引越界 | 检查长度，记住是**左闭右开** |
| `TypeError: can only concatenate str to str` | 字符串拼了数字 | `str(n)` 或 f-string `f"{n}"` |
| `FileNotFoundError` | 路径不对 | 用绝对路径，或先 `os.path.exists()` |
| `UnicodeDecodeError` | 编码不对 | 试 `encoding="utf-8-sig"` / `"gbk"` |
| `NoneType has no attribute` | 函数没 return，拿到的是 None | 检查有没有漏 `return` |

### 6.4 Pandas 类

| 报错 | 根因 | 解法 |
|---|---|---|
| `KeyError: '列名'` | 列名写错 / 已经聚合过 | `print(df.columns.tolist())` |
| `ValueError: The truth value of a Series...` | 用了 `and` / `or` | 改成 `&` / `\|`，每个条件加括号 |
| 多出一列 `Unnamed: 0` | `to_csv` 没加 `index=False` | 加上（但如果索引是"名字"，**别加**） |
| Excel 打开中文乱码 | 没加编码 | `encoding="utf-8-sig"` |
| `SettingWithCopyWarning` | 改的是筛选结果的副本 | `df = df.copy()` |
| `Column not found` | 拿聚合结果再去分组 | 检查这一步手里到底是 df 还是聚合结果 |

### 6.5 Matplotlib 类

| 现象 | 根因 | 解法 |
|---|---|---|
| 中文变方块 + `Glyph missing` | 字体没设 | 那三行 rcParams |
| 保存出来是空白 | `savefig` 在 `plt.show()` 之后 | 调到 show 之前 |
| `'tuple' object is not callable` | `ax.bar = (...)` 写成了赋值 | 去掉等号 |
| 图很小 / 文件很小 | 其实什么都没画 | **看文件大小**（<12KB 就是空的） |
| 标题被切掉 | 没调 `tight_layout()` | `fig.tight_layout()` |

### 6.6 PyTorch 类

| 报错 | 根因 | 解法 |
|---|---|---|
| `RuntimeError: expected scalar type Long but found Float` | 标签类型不对 | 标签用 `.long()` |
| `RuntimeError: CUDA out of memory` | 显存不够 | 减小 `batch_size` |
| `mat1 and mat2 shapes cannot be multiplied` | 维度对不上 | `print(x.shape)` 逐层查 |
| loss 不下降 | 学习率不对 | 试 `1e-2` ~ `1e-5` |
| 准确率一直是 10%（10分类） | 模型没学到 | 检查标签、loss 用对没 |
| `DataLoader` 卡死 | Windows 下 `num_workers>0` | 改成 `num_workers=0` |
| 梯度越跑越大 | **忘了 `zero_grad()`** | 在 `backward()` 前清零 |
| 加载模型报 `Missing key(s)` | 模型结构和训练时不一致 | 结构必须完全相同 |

### 6.7 Git 类

| 报错 | 根因 | 解法 |
|---|---|---|
| `Please tell me who you are` | 没配身份 | `git config --global user.name/user.email` |
| `Permission denied (publickey)` | 公钥没绑 / 用错钥匙 | 检查 `~/.ssh/config` 和 GitHub 上的公钥 |
| `Repository not found` | 用户名或仓库名写错 | `git remote -v` 检查 |
| `src refspec main does not match any` | 还没有 commit | 先 `git add` + `git commit` |
| `remote origin already exists` | 重复添加 | `git remote set-url origin 新地址` |
| `failed to push some refs` | 远端有本地没有的提交 | `git pull --rebase origin main` 再 push |
| `LF will be replaced by CRLF` | Windows 换行符警告 | **无害，忽略** |
| `fatal: not a git repository` | 不在仓库目录里 | `cd E:\agent` |

### 6.8 Windows / PowerShell 类

| 现象 | 根因 | 解法 |
|---|---|---|
| `~` 在命令里不生效 | **PowerShell 不给外部程序展开 `~`** | 用 `$env:USERPROFILE`，或改用 Git Bash |
| 命令退出码 1 但其实成功了 | PowerShell 把 stderr 输出当错误 | 看实际输出内容，别只看退出码 |
| `ssh -T git@github.com` 退出码 1 | **这是正常的**，成功也是 1 | 看输出有没有 `Hi 用户名!` |
| 中文命令输出乱码 | 控制台代码页 | `chcp 65001` |

---

## 7. 卡住时的自救顺序

**按顺序做，别跳：**

```
1. 读报错最后一行        ← 最关键的信息在这里，不是最上面那堆
2. 用 type() / print() 看变量到底是什么
   print(type(x), x.shape if hasattr(x,'shape') else x)
3. 查本文件第 5 节
4. 报错原文搜一遍（去掉路径和内存地址）
5. 问 AI（把完整报错 + 你的代码贴进去）
6. 卡 2 小时以上 → 跳过这个点，先做别的
```

### 时间规则

| 卡住时长 | 做什么 |
|---|---|
| 30 分钟 | 自己查（本文件 + 搜索 + 官方文档） |
| 2 小时 | 问 AI |
| 半天 | 问同学 / 问师兄 |
| 一天 | 先放着，做别的部分，回头再看 |

**★ 最重要的一条：不要在一个点上耗一整天。**

---

## 8. 每天的最小检查

```powershell
cd E:\agent
git status                                    # 有没有没提交的
git add .
git commit -m "..."
git push
```

```python
# 跑一遍今天的脚本，确认还能跑
```

**然后在 `notes/log.md` 里写三行：**

```markdown
## MM-DD
- 做了：
- 卡了：
- 解了：
```

---

## 9. 三个月后回看这三条

1. **面试必问「你遇到最难的问题是什么，怎么解决的」** → 答案在 `notes/log.md`
2. **简历要有东西可写** → 靠 `week1/` ~ `week6/` 的产出
3. **"持续投入"要有证据** → 靠 `git log` 的提交历史

**这三样都只能靠"每天做一点"攒出来，没有捷径。**

---

*最后更新：2026-09-28*
