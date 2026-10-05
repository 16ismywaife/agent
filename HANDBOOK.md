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
- [5. 6 周逐日任务表](#5-6-周逐日任务表)
- [6. Bug 速查表](#6-bug-速查表)
- [7. 卡住时的自救顺序](#7-卡住时的自救顺序)
- [8. 每天的最小检查](#8-每天的最小检查)
- [9. 三个月后回看这三条](#9-三个月后回看这三条)

---

## 0. 怎么用这份文件

**这份文件里的代码分三种，看标记：**

| 标记 | 含义 |
|---|---|
| ✅ **实测** | 我在你这台机器上真跑过，输出正确 |
| ◐ **协议已验** | 代码本身真跑过（请求结构、返回解析、边界处理都对），但**当时没有 API Key**，没打过真实模型。第一次用真实 Key 时留意返回内容 |
| ⚠️ **未实测** | 语法标准但完全没跑过（缺硬件/依赖），**第一次用要自己小心** |

> **◐ 是怎么验的**：我起了一个**本地 OpenAI 兼容 mock 服务器**，用**真实的 `openai` SDK**打真实 HTTP，
> 检查了请求头、`tools` 结构、`tool_call_id` 配对、`response_format`、`temperature`、`stream` 分块——
> **协议层是对的**。
> **但它证明不了「真实模型会不会选你的工具」「回答质量如何」** —— 那必须用你自己的 Key 跑一次。
> 仓库根目录有现成的验证脚本，填完 `.env` 直接跑：
> ```powershell
> python verify_handbook_llm.py --real
> ```

**遇到没写在这里的报错** → 见第 7 节「自救顺序」。

---

## 1. 每天要做的四件事

```
① 写日志（3 行）        notes/log.md
② 跑一遍自己的代码       确认还能跑
③ 提交                  git add / commit / push
④ 记新坑                遇到的 bug 写进第 6 节
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

> **这一章的读法**：
> 1. 每段代码 **逐行都有注释**（`#` 后面就是那行在干什么）
> 2. 代码后面有 **「关键字逐个说」表格**，解释每个写法的作用和为什么这么写
> 3. 看标记：✅ **实跑过** ／ ◐ **协议已验、模型没验**（LLM/Agent 那几节，含义见第 0 节）／ ⚠️ **没跑过**
> 4. 标记为 ◐ 的节，都配了现成的验证脚本 —— `_verify/README.md`

### 4.1 Python 基础 ✅ 实测

```python
# ---------- 变量与类型 ----------
n = 10              # 整数 int
x = 3.14            # 小数 float
s = "hello"         # 字符串 str（单双引号都行）
flag = True         # 布尔 bool（注意首字母大写）
empty = None        # 空值 None（不是 0，也不是 ""）

# 查看一个变量是什么类型
print(type(n))      # <class 'int'>

# ---------- 列表 list：有序、可改 ----------
nums = [1, 2, 3]           # 方括号
nums.append(4)             # 末尾加一个 → [1,2,3,4]
nums[0]                    # 取第 0 个 → 1（★ 从 0 开始数）
nums[-1]                   # 取最后一个 → 4（负数 = 从后往前）
len(nums)                  # 有几个元素 → 4
nums[1:3]                  # 切片：第1个到第2个（★ 左闭右开，不含 3）

# ---------- 字典 dict：键值对 ----------
person = {"name": "张三", "age": 20}    # 大括号 + 冒号
person["name"]                          # 用键取值 → "张三"
person["city"] = "广州"                  # 新增一项
person.get("height", 0)                 # ★ 取不到就返回 0（不报错）
person.keys()                           # 所有键
person.values()                         # 所有值

# ---------- 条件 ----------
score = 75
if score >= 90:                 # 冒号结尾，下面是缩进的代码块
    print("优秀")
elif score >= 60:               # ★ 走到这里说明 score < 90 已经成立
    print("及格")
else:
    print("不及格")

# ---------- 循环 ----------
for i in range(5):              # range(5) = 0,1,2,3,4（★ 不含 5）
    print(i)

for item in nums:               # 直接遍历列表的元素
    print(item)

while score > 0:                # 条件为真就一直循环
    score -= 1                  # ★ -= 是 score = score - 1 的简写
    if score == 50:
        break                   # 立刻跳出整个循环
    if score == 70:
        continue                # 跳过本次剩余部分，进入下一次

# ---------- 列表推导式：一行生成新列表 ----------
doubled = [x * 2 for x in nums]                    # 每个元素乘 2
passed  = [s for s in scores if s >= 60]           # ★ 只保留 >= 60 的

# ---------- ★ 字典计数模式（最常用的套路之一）----------
items = ["苹果", "香蕉", "苹果", "橘子", "香蕉", "苹果"]
counts = {}                                  # 先造一个空字典装结果
for item in items:                           # 逐个遍历
    counts[item] = counts.get(item, 0) + 1   # 取旧值（没有就当 0）+1 存回去
print(counts)                                # {'苹果': 3, '香蕉': 2, '橘子': 1}
```

**关键字逐个说**

| 写法 | 作用 | 为什么 / 注意 |
|---|---|---|
| `# 注释` | 给人看的说明 | Python 会忽略 `#` 后面的内容 |
| `type(x)` | 查一个变量是什么类型 | 调试最常用的工具 |
| `[1, 2, 3]` | 列表（有序、可改） | 用 `[]` 创建 |
| `{"键": "值"}` | 字典（键值对） | 用 `{}` 创建，靠"键"取值不靠位置 |
| `nums[0]` | 按下标取元素 | **从 0 开始**，不是 1 |
| `nums[-1]` | 取最后一个 | 负数从右往左数 |
| `nums[1:3]` | 切片 | **左闭右开**：含 1，不含 3 |
| `.append(x)` | 往列表末尾加一个 | 会**修改原列表**，不返回新列表 |
| `.get(键, 默认值)` | 取字典的值 | **取不到就返回默认值，不报错**（所以计数要用它） |
| `if / elif / else` | 条件分支 | **从上往下判，命中就停**，所以 `elif` 不用重复写前面的条件 |
| `range(5)` | 生成 0~4 | **不含 5**（左闭右开） |
| `for x in 列表` | 遍历 | 直接拿元素，不用管下标 |
| `while 条件` | 条件循环 | 条件为假时退出 |
| `break` | 跳出整个循环 | |
| `continue` | 跳过本次，进入下一次 | |
| `+= / -=` | 加等于 / 减等于 | `a += 1` 就是 `a = a + 1` |
| `[表达式 for x in 列表 if 条件]` | 列表推导式 | 一行干完"遍历+筛选+变换" |

**三个最容易错的点**

1. **下标从 0 开始**，`nums[0]` 是第一个
2. **切片是左闭右开**，`nums[1:3]` 只取 1 和 2
3. **`counts[item]` 直接取会 KeyError**，必须先 `.get(item, 0)`

---

### 4.2 函数与类 ✅ 实测

```python
# ================= 函数 =================

def add(a, b, scale=1):
    #   ↑函数名  ↑参数  ↑带默认值的参数（不传就用 1）
    """文档字符串：一句话说明这个函数干什么"""
    result = (a + b) * scale     # 函数体（缩进 4 空格）
    return result                # ★ 把结果交出去

print(add(1, 2))        # 3     只用前两个参数
print(add(1, 2, 10))    # 30    scale 传了 10
print(add(b=2, a=1))    # 3     ★ 关键字参数，顺序可以打乱


def no_return():
    print("做了点事")
    # 没有 return

print(no_return())      # 打印"做了点事"后，再打印 None
# ★ 没写 return 的函数，返回 None


# ================= 类 =================

class ScoreAnalyzer:
    #   ↑类名（习惯首字母大写）
    """分数分析器"""

    def __init__(self, scores):
        #   ↑构造方法：创建对象时【自动】被调用，不用手动调
        #        ↑self 是"这个对象自己"
        self.scores = scores
        #   ↑把传进来的分数【存成自己的属性】
        #    不加 self. 的话，函数跑完 scores 就没了，别的方法读不到

    def count_pass(self, line=60):
        #   ↑每个方法的第一个参数都必须是 self
        passed = [s for s in self.scores if s >= line]
        #               ↑用 self. 读自己的属性
        return len(passed)                  # 返回人数

    def pass_rate(self, line=60):
        return self.count_pass(line) / len(self.scores)
        #      ↑在方法里调用自己的另一个方法

    def summary(self, line=60):
        return f"共 {len(self.scores)} 人，及格 {self.count_pass(line)} 人"
        #      ↑f-string：字符串前面加 f，{} 里可以直接放变量或表达式


# ================= 入口 =================

if __name__ == "__main__":
    #   ↑只有"直接运行这个文件"时才成立；被别人 import 时不执行
    a = ScoreAnalyzer([88, 45, 92, 60, 73, 39, 95])
    #   ↑创建对象，这一刻 __init__ 自动跑，scores 被存进 self.scores
    print(a.count_pass())    # 5    ★ 不传 line，用默认值 60
    print(a.pass_rate())     # 0.714...
    print(a.summary())
    #     ↑a.count_pass() 等价于 ScoreAnalyzer.count_pass(a)
    #      只是 Python 帮你把 a 当第一个参数自动传进去了
```

**关键字逐个说**

| 写法 | 作用 | 为什么 / 注意 |
|---|---|---|
| `def 名字(参数):` | 定义函数 | 冒号 + 缩进是函数体 |
| `return x` | 把结果交出去并结束函数 | **不写 return 就返回 `None`** |
| `"""文档"""` | 文档字符串 | `help(函数名)` 能读出来 |
| `参数=默认值` | 默认参数 | 不传就用默认值；**默认参数要放在普通参数后面** |
| `f"{变量}"` | 格式化字符串 | 字符串前加 `f`，`{}` 里放变量或表达式 |
| `class 名字:` | 定义类 | 类名习惯首字母大写 |
| `__init__` | 构造方法 | **创建对象时自动调用**，用来初始化属性 |
| `self` | 指"这个对象自己" | 方法第一个参数必须是它；**名字可以改但别改** |
| `self.属性` | 存/读对象自己的属性 | 不加 `self.` 的话，其他方法读不到 |
| `对象.方法()` | 调用方法 | `a.count_pass()` 等价于 `ScoreAnalyzer.count_pass(a)` |
| `if __name__ == "__main__":` | 入口判断 | 直接运行时执行；被 `import` 时不执行 |

**三个必须先弄明白的点**

1. **`self` 就是"这个对象自己"**
   `a.count_pass()` → Python 自动翻译成 `ScoreAnalyzer.count_pass(a)`

2. **`__init__` 在创建对象那一刻自动跑**
   `a = ScoreAnalyzer([...])` 这一行的瞬间，`scores` 就被存进了 `self.scores`

3. **属性必须写 `self.`**
   ```python
   def __init__(self, scores):
       scores = scores          # ❌ 只是给局部变量赋值，出了函数就没了
       self.scores = scores     # ✅ 存成对象的属性，别的方法能读到
   ```

**⚠️ 两个常见坑**

- **函数里又 `def` 一个同名函数** → 外层什么都不做，返回 `None`（你踩过）
- **方法忘了写 `self`** → 调用时 `TypeError: missing 1 required positional argument`

---

### 4.3 NumPy ✅ 实测

```python
import numpy as np                              # 惯例缩写为 np

# ---------- 创建 ----------
a = np.array([1, 2, 3])                         # 从列表创建
np.zeros((2, 3))                                # 2行3列，全是 0
np.arange(10)                                   # 0~9（★ 不含 10）
np.random.seed(42)                              # ★ 固定随机种子
b = np.random.randint(0, 100, size=(5, 3))      # 5行3列随机整数（★ 不含 100）

# ---------- 属性 ----------
b.shape        # (5, 3)     形状（几行几列）
b.dtype        # int64      元素类型
b.ndim         # 2          维度数

# ---------- 取值 ----------
b[0]           # 第 0 行（一整行）
b[:, 0]        # 第 0 列（★ 冒号表示"所有行"）
b[1:3, 0:2]    # 第1~2行 × 第0~1列（左闭右开）

# ---------- 聚合 ----------
b.mean()          # 全体平均
b.max()           # 全体最大
b.std()           # 标准差
b.sum()           # 求和
b.mean(axis=0)    # ★ 消掉第0维 → 每列一个值（长度 = 列数 3）
b.mean(axis=1)    # ★ 消掉第1维 → 每行一个值（长度 = 行数 5）

# ---------- 布尔索引 ----------
b[b > 80]         # 取出【所有】> 80 的元素，返回一维数组
b[b > 80] = 60    # 把所有 > 80 的元素改成 60（原地修改）
(b > 80).sum()    # 有多少个 > 80（True 当 1）

# ---------- 整体运算（不用写循环）----------
c = np.array([1, 2, 3])
c * 2             # [2, 4, 6]        每个元素乘 2
c + 10            # [11, 12, 13]     每个元素加 10
d = np.array([10, 20, 30])
c + d             # [11, 22, 33]     对应位置相加（这叫"逐元素运算"）
```

**关键字逐个说**

| 写法 | 作用 | 为什么 / 注意 |
|---|---|---|
| `np.array([...])` | 从列表创建数组 | |
| `np.zeros((行, 列))` | 全 0 数组 | **参数是元组**，`(2,3)` 是 2行3列 |
| `np.arange(10)` | 等差序列 | **左闭右开**，`arange(10)` = 0~9 |
| `np.random.seed(42)` | 固定随机种子 | **保证每次生成一样的数据**（可复现的关键） |
| `np.random.randint(a, b, size=)` | 随机整数 | **左闭右开**，`randint(0,100)` = 0~99 |
| `.shape` | 形状 | `(5, 3)` = 5行3列；**注意是属性，不加括号** |
| `.dtype` | 元素类型 | `int64` / `float32` |
| `b[:, 0]` | 取第 0 列 | `:` 表示那一维全要 |
| `.mean()` / `.max()` / `.sum()` | 聚合 | **不带参数 = 全体** |
| `axis=0` | 消掉第 0 维 | **每列一个值**（输出长度 = 列数） |
| `axis=1` | 消掉第 1 维 | **每行一个值**（输出长度 = 行数） |
| `b[b > 80]` | 布尔索引 | 返回**一维**数组，不是原来的形状 |
| `b[b > 80] = 60` | 布尔赋值 | 原地修改，把所有满足条件的改掉 |

**★ 唯一会让你卡住的概念：`axis`**

**记住这一句就够：`axis` 是"要被消掉的那一维"。**

```
b 的形状是 (5, 3)：5 行学生，3 列科目

b.mean(axis=0)  →  消掉第 0 维（5 个学生）→ 剩 (3,)  →  每个科目一个值
b.mean(axis=1)  →  消掉第 1 维（3 个科目）→ 剩 (5,)  →  每个学生一个值
```

**验证办法：看输出长度。**
`mean(axis=0)` 出 3 个数 → 3 是列数 → 所以是"每列"。

**别死记"0 是行 1 是列"**——那个说法在三维数组上会崩。

**⚠️ 两个注意**

1. **`np.random.randint(0, 100)` 不含 100**（左闭右开）；要含 100 得写 `randint(0, 101)`
2. **NumPy 的切片是"视图"不是"拷贝"**，改了切片会影响原数组

---

### 4.4 Pandas ✅ 实测

#### 读 / 写

```python
import pandas as pd

df = pd.read_csv("data.csv")
#   ↑把 CSV 读成 DataFrame（一张二维表）

df = pd.read_csv("data.csv", encoding="utf-8-sig")
#                              ↑有 BOM 头时用这个
df = pd.read_csv("data.csv", encoding="gbk")
#                              ↑老文件常常是 GBK

df.to_csv("out.csv", index=False, encoding="utf-8-sig")
#                    ↑不写行号    ↑中文 Excel 打开不乱码
```

| 写法 | 作用 | 注意 |
|---|---|---|
| `pd.read_csv(路径)` | 读 CSV 成 DataFrame | 报编码错就试 `utf-8-sig` → `gbk` |
| `df.to_csv(路径, index=False)` | 存成 CSV | **`index=False` 很关键**（否则多一列行号） |
| `encoding="utf-8-sig"` | 带 BOM 的 UTF-8 | **中文用 Excel 打开不乱码** |

> ⚠️ **但如果索引是"名字"（比如科目名），就别加 `index=False`**——会把名字丢掉。

#### 看数据（拿到表先做这几件事）

```python
df.head()       # 前 5 行
df.head(10)     # 前 10 行
df.tail(3)      # 后 3 行

df.shape        # (300, 3)  300行3列（★ 属性，不加括号）
df.columns      # 列名列表
df.dtypes       # 每列的类型

df.info()       # 每列的非空数量 + 类型（查缺失值用）
df.describe()   # 数值列的统计摘要（mean/std/min/25%/50%/75%/max）
```

| 写法 | 作用 |
|---|---|
| `.head(n)` | 看前 n 行（默认 5） |
| `.shape` | `(行数, 列数)`，**是属性不是方法** |
| `.columns` | 列名，报 `KeyError` 时先 `print(df.columns.tolist())` |
| `.info()` | 列类型 + 非空个数 |
| `.describe()` | 数值列统计摘要 |

#### 选列 / 选行

```python
df["分数"]                # 取一列 → 返回 Series（一维）
df[["科目", "分数"]]       # 取多列 → 返回 DataFrame（二维）★ 双括号！

df[df["分数"] > 90]                                   # 分数 > 90 的行
df[df["科目"] == "数学"]                               # 科目是数学的行
df[(df["科目"] == "数学") & (df["分数"] > 90)]          # ★ 两个条件
#  ↑每个条件都要括号    ↑用 & 不是 and
df[(df["科目"] == "数学") | (df["科目"] == "语文")]      # 或条件用 |

df.iloc[0]        # 第 0 行（按位置）
df.iloc[0:5]      # 前 5 行
```

**★ 三种括号的区别（最容易混）**

| 写法 | 返回 | 含义 |
|---|---|---|
| `df["分数"]` | Series | 取**一列** |
| `df[["分数"]]` | DataFrame | 取**一个子表**（只含这一列） |
| `df[df["分数"] > 90]` | DataFrame | 取**满足条件的行** |

**★ 筛选的三个铁律**

1. 用 **`&`（与）/ `|`（或）**，不是 `and` / `or`
2. **每个条件都要自己加括号**：`(df["a"] > 1) & (df["b"] < 2)`
3. **`==` 是比较，`=` 是赋值**（`df["科目"] = "数学"` 会把整列改掉！）

#### 统计

```python
df["分数"].mean()        # 平均
df["分数"].max()         # 最大
df["分数"].min()         # 最小
df["分数"].std()         # 标准差
df["分数"].median()      # 中位数
df["分数"].count()       # 非空个数

df["科目"].value_counts()      # 每个值出现几次（默认按次数从多到少排）
df["姓名"].nunique()           # 有多少个【不同】的值
len(df)                        # 一共多少行
```

**`nunique()` 和 `len()` 的区别（重要）**

```python
df["姓名"].nunique()    # 100  ← 有多少个学生
len(df)                 # 300  ← 一共多少条记录（100 学生 × 3 科）
```

#### ★ groupby（数据透视表）—— 最值钱的部分

```python
df.groupby("科目")["分数"].mean()
#  ↑按"科目"分组      ↑对"分数"这一列    ↑算平均值
#  读法：按科目分组，然后算分数的平均

df.groupby("科目")["分数"].agg(["mean", "max", "min", "count"])
#                                    ↑一次算多个统计

df.groupby(["科目", "段"])["分数"].mean()      # 按多列分组

df.groupby("科目")["分数"].mean().sort_values(ascending=False)
#                                  ↑对结果排序（链式调用）
```

| 写法 | 作用 |
|---|---|
| `.groupby("列")` | 按这列的值分组 |
| `["列"]` | 对哪一列做统计 |
| `.mean()` / `.sum()` | 算单个统计 |
| `.agg([...])` | **一次算多个**，传列表 |

**★ 关键：加不加 `agg`，出来的东西完全不同**（这是你踩过的坑）

```python
a = df.groupby("科目")["分数"].mean()                       # Series  (3,)
b = df.groupby("科目")["分数"].agg(["mean","max","min","count"])  # DataFrame (3,4)

a 的"值"就是平均值，没有列名
b 的列名是 ['mean','max','min','count'] —— 【没有"分数"这一列】
```

**所以 `b["分数"]` 会报 `Column not found`** —— `b` 已经是聚合结果，不能再按"分数"分组。

#### 索引（index）是"名字"，不是"行号"

```python
df[df["分数"] > 90]        # 索引变成 [3, 6, 20, 31]（★ 有空洞，不是 0,1,2,3）
df.sort_values("分数")      # 索引乱序（★ Pandas 不会自动重排）
```

| 写法 | 作用 |
|---|---|
| `.reset_index(drop=True)` | 丢掉旧索引，重新编号 0,1,2... |
| `.set_index("姓名")` | 把某一列变成索引 |
| `.loc[标签]` | 按**标签**取 |
| `.iloc[位置]` | 按**位置**取 |

> **`value_counts()` 的结果里，索引是"值"，数据才是"次数"** —— 很多人在这里取错。

#### 排序 / 新增列 / 其他

```python
df.sort_values("分数")                       # 按分数升序
df.sort_values("分数", ascending=False)       # 降序
df.sort_values(["科目", "分数"])              # 先按科目，再按分数

df["是否及格"] = df["分数"] >= 60              # 新增一列（布尔）
df["分数"] = df["分数"] + 5                   # 整列 +5
df["等级"] = df["分数"].apply(lambda x: "高" if x >= 90 else "低")
#                              ↑对每个元素应用一个函数

pd.crosstab(df["段"], df["科目"])              # 交叉计数（比 pivot_table 简洁）
df.pivot_table(index="姓名", columns="科目", values="分数")   # 透视表
pd.cut(df["分数"], bins=[0,59,79,100], labels=["<60","60-79","80-100"])
#        ↑把连续值切成几段

df["分数"].isna().sum()          # 有多少个缺失
df.dropna(subset=["分数"])        # 删掉分数缺失的行
df["分数"].fillna(0)             # 用 0 填
df["是否及格"].mean()             # ★ 布尔列的均值 = 比例（True 当 1）
```

**★ 最重要的一条习惯**

```python
print(type(x), x.shape, list(x.columns))
```

**链式操作每写一步就插一行这个。** 它能挡掉 90% 的 Pandas 错误——因为大部分错误都是"我以为我手里是 A，其实是 B"。

---

### 4.5 Matplotlib ✅ 实测

```python
import matplotlib
matplotlib.rcParams["font.sans-serif"] = ["SimHei"]
#   ↑全局设置中文字体，不加的话中文会变方块
matplotlib.rcParams["axes.unicode_minus"] = False
#   ↑让负号正常显示

import matplotlib.pyplot as plt

# ---------- 两层结构 ----------
fig, ax = plt.subplots(figsize=(7, 4.5))
#  ↑     ↑                     ↑画布大小（宽7英寸 高4.5英寸）
# 画布  坐标系

# ---------- fig. 管"整张纸" ----------
fig.tight_layout()                  # 自动调整间距（不加标题会被切掉）
fig.savefig("result.png", dpi=130)  # 保存（dpi 越大越清晰）
#   ↑注意：不加引号！加了引号就变成存成"叫 result.png 这个名字的字符串"了

# ---------- ax. 管"纸上的图" ----------
s = df.groupby("科目")["分数"].mean()

ax.bar(s.index, s.values, color="#4C78A8")
#  ↑画柱状图  ↑x轴数据  ↑y轴数据   ↑颜色（十六进制）
ax.plot(x, y, marker="o", markersize=3, label="系列名")   # 折线图
ax.hist(df["分数"], bins=20, edgecolor="white")           # 直方图，bins=切几段
ax.scatter(x, y)                                          # 散点图

ax.set_title("各科目平均分")     # 图标题
ax.set_xlabel("科目")            # x 轴名字
ax.set_ylabel("平均分")          # y 轴名字
ax.legend()                      # 显示图例（要有 label 才有东西显示）

# ---------- 柱子上标数值 ----------
for i, v in enumerate(s.values):
    #      ↑i是序号  ↑v是数值
    ax.text(i, v + 0.8, f"{v:.1f}", ha="center")
    #  ↑x位置 ↑y位置(比柱子高一点) ↑显示的文字  ↑水平居中

# ---------- 第二种写法：pandas 风格 ----------
ax2 = s.plot(kind="bar", figsize=(7, 4.5), rot=0, title="标题")
#   ↑★ 注意返回的是 ax，不是 fig
fig2 = ax2.get_figure()          # 所以要这样把 fig 拿回来
fig2.savefig("out.png", dpi=130)
```

**关键字逐个说**

| 写法 | 作用 | 为什么 / 注意 |
|---|---|---|
| `rcParams["font.sans-serif"]` | 设置中文字体 | **不加中文变方块** |
| `rcParams["axes.unicode_minus"]` | 负号显示 | 设 `False` 让负号正常 |
| `plt.subplots()` | 创建画布 + 坐标系 | 返回 `(fig, ax)` 两个东西 |
| `figsize=(7, 4.5)` | 画布尺寸 | 单位是**英寸** |
| **`fig.`** 开头 | 管**整张纸** | `savefig` / `tight_layout` / `figsize` |
| **`ax.`** 开头 | 管**纸上的图** | `bar` / `plot` / `set_title` / `legend` |
| `ax.bar(x, y)` | 柱状图 | **函数调用，不是赋值**（写 `=` 就不报错但图空白） |
| `ax.hist(数据, bins=20)` | 直方图 | `bins` = 把数据切成几段 |
| `ax.plot(x, y, marker="o")` | 折线图 | `marker` = 数据点的形状 |
| `ax.text(x, y, 文字)` | 在图上写字 | 用来标数值 |
| `ha="center"` | 水平对齐 | `ha` = horizontal alignment |
| `fig.savefig(变量)` | 保存 | **变量不能加引号** |
| `dpi=130` | 分辨率 | 默认 100 有点糊 |
| `fig.tight_layout()` | 自动调间距 | 不加标题会被切掉 |
| `ax.get_figure()` | 从 ax 拿回 fig | **pandas 的 `.plot()` 只返回 ax** |

**★ 记忆规则：`fig.` 管"纸"，`ax.` 管"纸上的图"**

**★ 自检：看文件大小**

| 图 | 正常大小 |
|---|---|
| 柱状图 | ~19,000–26,000 bytes |
| 直方图 | ~18,000 bytes |
| **空白图** | **~10,000 bytes** ← 太小就是没画出东西 |

**生成图片后 `ls` 看一眼大小** —— 你 Day 6 那个 `ax.bar=(...)` 的 bug 就是这么发现的（文件只有 10KB）。

**选图原则**：比大小用柱、看趋势用线、看分布用直方、看关系用散点。

---

### 4.6 PyTorch：Tensor 与自动求导（Week2）✅ 实测

#### Tensor 是什么

```python
import torch                                    # 导入 PyTorch

# ---------- 创建 ----------
a = torch.tensor([1.0, 2.0, 3.0])
#   ↑注意：torch 默认 float32，numpy 默认 float64，精度不一样
b = torch.zeros(2, 3)                           # 2行3列全 0（不用写元组）
c = torch.linspace(-1, 1, 50)
#   ↑在 -1 到 1 之间均匀取 50 个点 → 形状 (50,)
c.unsqueeze(1)
#   ↑在第 1 维插入一个维度 → 形状从 (50,) 变成 (50, 1)
#    ★ 为什么需要：矩阵运算要求两个操作数形状能对上

# ---------- 和 NumPy 互转 ----------
import numpy as np
np_arr = np.array([1.0, 2.0])
t = torch.from_numpy(np_arr)                    # numpy → tensor（共享内存）
back = t.numpy()                                # tensor → numpy（必须先在 CPU 上）

# ---------- 搬运到 GPU ----------
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
#                       ↑有显卡就用显卡，没有就用 CPU（这句是标准写法）
t = t.to(device)                                # 把张量搬到 GPU
```

**关键字逐个说**

| 写法 | 作用 | 为什么 / 注意 |
|---|---|---|
| `torch.tensor([...])` | 创建张量 | 默认 `float32`（numpy 是 `float64`） |
| `torch.zeros(2, 3)` | 全 0 张量 | **不用写元组**，直接逗号分隔 |
| `torch.linspace(a, b, n)` | 等差序列 | 含首尾，n 是**个数**不是步长 |
| `.unsqueeze(dim)` | 插入一个维度 | `(50,)` → `(50,1)`；矩阵运算常用 |
| `.to(device)` | 搬到指定设备 | `"cuda"` 或 `"cpu"` |
| `torch.cuda.is_available()` | 显卡能不能用 | 返回 `True`/`False` |
| `torch.from_numpy(x)` | numpy → tensor | **共享内存**，改一个另一个也变 |
| `.numpy()` | tensor → numpy | 必须在 CPU 上，GPU 上会报错 |

#### ★ 自动求导（这一节是核心）

```python
x = torch.tensor([2.0], requires_grad=True)
#                            ↑★ 这句在说："PyTorch，请盯着 x，
#                              凡是它参与的运算都帮我记下来"
y = x**2 + 3*x
#   ↑前向：算出 y。同时 PyTorch 在【暗中】画了一张计算图
y.backward()
#   ↑反向：沿着计算图倒着走一遍，用链式法则算出所有梯度
print(x.grad)
#        ↑梯度存在 .grad 里 → 7.0
#          手算验证：y = x²+3x 的导数是 2x+3，x=2 时 = 2*2+3 = 7 ✅
```

**多变量：一次 `backward()` 同时算出所有梯度**

```python
x = torch.tensor([1.0], requires_grad=True)
w = torch.tensor([3.0], requires_grad=True)
b = torch.tensor([2.0], requires_grad=True)

y = w * x + b            # y = 3*1 + 2 = 5
y.backward()             # ★ 一次调用，三个梯度全出来了

print(w.grad)   # 1.0  （dy/dw = x = 1）
print(b.grad)   # 1.0  （dy/db = 1）
print(x.grad)   # 3.0  （dy/dx = w = 3）
```

> **"一次算出所有梯度"就是反向传播不可替代的原因。** 模型有几十万到几十亿个参数，你不可能手算。

#### ★ 陷阱：梯度会累积

```python
x = torch.tensor([2.0], requires_grad=True)

for i in range(3):
    y = x**2
    y.backward()
    print(x.grad)
#   第1次: 4.0    （2x = 4，对的）
#   第2次: 8.0    ← 变成 8 了！
#   第3次: 12.0   ← 又加了 4
```

**`backward()` 是"累加"梯度，不是"覆盖"。**

**所以每次反向传播前必须清零：**

```python
x.grad.zero_()
#      ↑末尾的下划线表示"原地修改"（PyTorch 的命名惯例）
#   训练循环里对应的是 optimizer.zero_grad()
```

**这就是为什么每个训练循环开头都有 `optimizer.zero_grad()`。**

#### ★ 完整例子：用自动求导做梯度下降

```python
import torch

torch.manual_seed(0)                     # 固定随机种子（保证可复现）

# ---------- 1. 造数据：真实规律是 y = 2x + 1 ----------
X = torch.linspace(-1, 1, 50).unsqueeze(1)    # 50 个点，形状 (50,1)
Y = 2 * X + 1                                 # 真实答案

# ---------- 2. 从【错误】的初值开始（假装不知道 w=2, b=1）----------
w = torch.tensor([0.0], requires_grad=True)   # 可训练参数，要梯度
b = torch.tensor([0.0], requires_grad=True)
lr = 0.1                                      # 学习率：每次调多大一步

# ---------- 3. 训练 ----------
for epoch in range(200):
    y_pred = X * w + b                        # ① 前向：模型预测
    loss = ((y_pred - Y) ** 2).mean()         # ② 算 Loss（均方误差 MSE）
    #        ↑预测与真实的差   ↑平方    ↑求平均
    loss.backward()                           # ③ 反向：算出 w.grad / b.grad

    with torch.no_grad():
        #   ↑★ 这句里的运算【不建计算图】
        #     因为"更新参数"不是模型运算，不需要梯度
        #     不写的话计算图会越堆越大，吃爆显存
        w -= lr * w.grad                      # ④ 沿梯度反方向走一小步
        b -= lr * b.grad
        #   ↑负号：梯度指向"loss 变大"的方向，所以要往反方向走

    w.grad.zero_()                            # ⑤ 清空梯度（不清理会累积！）
    b.grad.zero_()

    if epoch % 50 == 0:
        print(f"epoch {epoch:3d}  loss={loss.item():.6f}  w={w.item():.4f}  b={b.item():.4f}")
        #              ↑:3d 表示占3位     ↑.6f 表示6位小数  ↑.item() 取出标量值

print(f"最终: w={w.item():.4f} (目标 2), b={b.item():.4f} (目标 1)")
```

**实测结果：**

```
epoch   0  loss=2.387755  w=0.1388  b=0.2000
epoch  50  loss=0.001045  w=1.9489  b=1.0000
epoch 100  loss=0.000001  w=1.9986  b=1.0000
epoch 150  loss=0.000000  w=2.0000  b=1.0000
epoch 199  loss=0.000000  w=2.0000  b=1.0000

最终: w=2.0000 (目标 2), b=1.0000 (目标 1)
```

**从 w=0 收敛到 w=2.0000。这五行就是训练的全部。**

#### ★ 反证：不用反向传播会怎样

**我把 `loss.backward()` 删掉，其他不动，跑了 200 轮：**

```
200 轮后 w=0.0000, b=0.0000, loss=2.3878    ← 参数一点没动
```

**为什么？** 没有 `backward()` 就没有梯度。`w -= lr * w.grad` 里 `w.grad` 是空的——**你根本不知道 w 该往哪个方向调、调多少。**

#### ★ "为什么需要反向传播"的答案（考核点名）

> 训练就是不断调参数让 Loss 变小。要调参数，就得知道**每个参数对 Loss 的影响有多大**——也就是梯度。
>
> 但模型可能有几十万到几十亿个参数，**不可能手算每个参数的导数**。
>
> 反向传播用链式法则，**从 Loss 倒着走一遍计算图，一次就同时算出所有参数的梯度**。上面那个例子里，一次 `backward()` 同时得到了 `w.grad` 和 `b.grad`。
>
> **没有它，参数就只能瞎猜**——实测去掉 `backward()`，跑 200 轮参数还是 0。

**关键字逐个说（PyTorch 自动求导）**

| 写法 | 作用 | 为什么 / 注意 |
|---|---|---|
| `requires_grad=True` | 告诉 PyTorch 盯住这个变量 | 只有它才需要算梯度 |
| `.backward()` | 反向传播，算梯度 | **梯度存在 `.grad` 里** |
| `.grad` | 读梯度 | 累加值，不是覆盖值 |
| `.grad.zero_()` | 清空梯度 | **末尾下划线 = 原地修改**；不清会累积 |
| `torch.no_grad()` | 这个块里不建计算图 | 更新参数时用，省显存 |
| `.item()` | 从单元素张量取出 Python 数值 | `print` 时更干净 |
| `torch.manual_seed(n)` | 固定随机种子 | 保证结果可复现 |
| `f"{x:.4f}"` | 格式化 | `.4f` = 保留 4 位小数 |

#### 输出结果怎么读懂

```
epoch   0  loss=2.387755  w=0.1388
#        ↑第0轮  ↑误差还很大  ↑参数刚开始动

epoch 199  loss=0.000000  w=2.0000
#          ↑误差几乎为0   ↑参数到位了
```

- **loss 越来越小** = 模型在学会
- **w 越来越接近 2** = 参数在往正确答案走
- **两者必须同时收敛** —— 如果 loss 降了但参数乱跑，说明有问题

---

### 4.7 Dataset 与 DataLoader（Week2）✅ 实测

```python
import torch
from torchvision import datasets, transforms
from torch.utils.data import DataLoader

# ---------- 1. 定义"怎么处理每张图" ----------
tf = transforms.Compose([
    #   ↑把多个变换串起来（按顺序执行）
    transforms.ToTensor(),
    #   ↑把 PIL 图片变成 Tensor，同时把像素值从 [0,255] 归一化到 [0,1]
    transforms.Normalize((0.1307,), (0.3081,)),
    #   ↑标准化：减去均值再除以标准差
    #    ★ 这两个数是 MNIST 数据集的全局均值和标准差，是【算出来的常量】
    #    为什么：让数据分布接近 0 均值 1 方差，训练更稳
])

# ---------- 2. 加载数据集 ----------
train_ds = datasets.MNIST("./data", train=True, download=True, transform=tf)
#                             ↑存哪  ↑要训练集  ↑本地没有就下载  ↑用上面的变换
test_ds  = datasets.MNIST("./data", train=False, download=True, transform=tf)
#                                        ↑测试集

print(len(train_ds), len(test_ds))    # 60000 10000

# ---------- 3. 包成 DataLoader ----------
train_ld = DataLoader(train_ds, batch_size=64, shuffle=True)
#                                ↑每批64张   ↑每个 epoch 打乱顺序
test_ld  = DataLoader(test_ds,  batch_size=256, shuffle=False)
#                                                  ↑测试集不用打乱

# ---------- 4. 取一批看看 ----------
x, y = next(iter(train_ld))
#      ↑把 DataLoader 变成迭代器，取第一个元素
print(x.shape)    # torch.Size([64, 1, 28, 28])
#                        ↑批大小 ↑通道数(灰度=1) ↑高 ↑宽
print(y.shape)    # torch.Size([64])   64 个标签
print(y[:5])      # tensor([5, 0, 4, 1, 9])   ← 前 5 张图是什么数字
```

**关键字逐个说**

| 写法 | 作用 | 为什么 / 注意 |
|---|---|---|
| `transforms.Compose([...])` | 把多个变换串起来 | 按列表顺序依次执行 |
| `transforms.ToTensor()` | 图片 → Tensor | 顺便把 [0,255] 压到 [0,1] |
| `transforms.Normalize(mean, std)` | 标准化 | 让分布接近 0均值1方差，训练更稳 |
| `datasets.MNIST(路径, train=, download=, transform=)` | 加载 MNIST | `train=True` 训练集 |
| `DataLoader(ds, batch_size=, shuffle=)` | 打包成批 | **训练集 shuffle=True，测试集 False** |
| `next(iter(loader))` | 取第一个 batch | 调试时常用 |
| `x.shape` | `[批大小, 通道, 高, 宽]` | MNIST 是 `[64, 1, 28, 28]` |

**Dataset 和 DataLoader 的分工**

| | 负责什么 |
|---|---|
| **Dataset** | "第 i 个样本是什么"（一份份数据） |
| **DataLoader** | 打包成 batch、打乱顺序、多进程加载 |

**为什么要分批（batch）而不是一次全上**

1. 一次 6 万张显存放不下
2. 小批量更新参数更稳（相当于带噪声的梯度下降，不容易卡在局部最优）

**★ 两个注意**

- **Windows 上 `num_workers` 大于 0 容易卡死** → 用默认值 0
- **`shuffle=True` 只在训练集用** —— 测试集打乱没有意义

---

### 4.8 训练循环（Week2）✅ 实测

**★ 这是整个 Week2 最重要的代码。看懂它 = 会训练模型。**

```python
import torch
import torch.nn as nn                # nn = neural network，放网络层和损失函数
import torch.optim as optim          # optim = optimizer，放优化器
from torchvision import datasets, transforms
from torch.utils.data import DataLoader

# ---------- 0. 选设备 ----------
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print("用:", device)

# ---------- 1. 数据 ----------
tf = transforms.Compose([transforms.ToTensor(),
                         transforms.Normalize((0.1307,), (0.3081,))])
train_ds = datasets.MNIST("./data", train=True,  download=True, transform=tf)
test_ds  = datasets.MNIST("./data", train=False, download=True, transform=tf)
train_ld = DataLoader(train_ds, batch_size=64,  shuffle=True)
test_ld  = DataLoader(test_ds,  batch_size=256, shuffle=False)

# ---------- 2. 定义模型 ----------
class Net(nn.Module):
    #        ↑★ 所有 PyTorch 模型都必须继承 nn.Module
    def __init__(self):
        super().__init__()
        #   ↑★ 必须先调父类的初始化（固定写法，别漏）
        self.net = nn.Sequential(
            #   ↑把层按顺序串起来，数据依次流过
            nn.Flatten(),
            #   ↑把 (批,1,28,28) 压平成 (批, 784)
            nn.Linear(28*28, 128), nn.ReLU(),
            #   ↑全连接层：784 个输入 → 128 个输出
            #                         ↑激活函数：把负数变 0，引入非线性
            #                           ★ 不加它，多层网络等价于一层
            nn.Linear(128, 10),
            #   ↑128 → 10（10 个数字类别，输出 10 个分数）
        )

    def forward(self, x):
        #   ↑★ 名字必须叫 forward，PyTorch 会在 model(x) 时自动调它
        return self.net(x)

model = Net().to(device)             # 创建模型并搬到 GPU

# ---------- 3. 损失函数 + 优化器 ----------
criterion = nn.CrossEntropyLoss()
#           ↑分类任务的标准损失函数
#            它内部已经包含 softmax，所以模型最后一层【不要】再写 softmax

optimizer = optim.Adam(model.parameters(), lr=1e-3)
#                    ↑Adam 优化器   ↑要优化的所有参数  ↑学习率 0.001
#                     ↑ 比 SGD 收敛快，是默认首选

# ---------- 4. 评估函数 ----------
def evaluate():
    model.eval()
    #   ↑★ 切到【评估模式】
    #     影响 Dropout 和 BatchNorm 的行为（训练和测试时不一样）
    correct = total = 0
    with torch.no_grad():
        #   ↑★ 评估时不需要梯度，关掉省显存、加速
        for x, y in test_ld:
            x, y = x.to(device), y.to(device)     # 数据也要搬到 GPU
            pred = model(x).argmax(dim=1)
            #                        ↑沿第1维取最大值的【下标】
            #                         输出是 10 个分数，取最大的那个就是预测类别
            correct += (pred == y).sum().item()
            #                    ↑逐元素比较，得到 True/False
            #                          ↑True 的个数  ↑转成 Python 数字
            total += y.size(0)                    # y 有多少个（=批大小）
    return correct / total                        # 正确率

# ---------- 5. ★★ 训练循环（记住这 5 步）----------
for epoch in range(3):               # 整个数据集过 3 遍
    model.train()
    #   ↑★ 切回【训练模式】
    for x, y in train_ld:            # 一个 batch 一个 batch 地处理
        x, y = x.to(device), y.to(device)

        optimizer.zero_grad()        # ① 清空上一轮的梯度（★ 不清会累积）
        out = model(x)               # ② 前向：算出预测
        loss = criterion(out, y)     # ③ 算损失：预测和真实差多少
        loss.backward()              # ④ 反向：算出每个参数的梯度
        optimizer.step()             # ⑤ 更新参数：按梯度走一小步

    acc = evaluate()                 # 每轮结束评估一次
    print(f"epoch {epoch+1}  loss={loss.item():.4f}  test_acc={acc:.4f}")
```

**实测结果**（3 epoch，每轮只用了 2000 张）：

```
epoch 1  loss=0.5852  test_acc=0.8110
epoch 2  loss=0.1497  test_acc=0.8540
epoch 3  loss=0.4630  test_acc=0.8670
```

**★ 训练循环：不要只背那 5 步**（这是最容易记不住的地方）

**先说一个常见误解：手册里有两个东西都叫「训练循环」，别搞混。**

| 叫法 | 是什么 | 代码 |
|---|---|---|
| **外层循环** | 「过几遍」 | `for epoch in range(3):` |
| **内层 5 步** | 「一批数据怎么学」 | `zero_grad → ... → step` |

**你要背的那 5 步是内层，而且它处理的是「一批（batch）」不是「一轮（epoch）」。**
MNIST 用 batch=64 时，**一轮要跑 938 次那 5 步**。

**完整结构是 4 层套嵌，5 步只占最里面一层：**

```
第 1 层  for epoch in range(3):          过几遍
第 2 层      model.train()                切回训练模式
第 3 层      for x, y in train_ld:       一批一批地取
第 4 层          optimizer.zero_grad()    ← 5 步在这里
                 out = model(x)
                 loss = criterion(out, y)
                 loss.backward()
                 optimizer.step()
             acc = evaluate()             这轮学得咋样
```

**只背第 4 层的 5 个零件，却要拿它拼整台机器 —— 所以一紧张就乱序。**

**那 5 步的顺序不是规定，是被因果逼出来的：**

| 追问 | 答案 → 必然推出下一步 |
|---|---|
| 想让参数变好，需要什么？ | 需要梯度 → 所以 **`step()` 必须排在 `backward()` 后面** |
| 梯度从哪来？ | 从 loss 反推 → 所以 **`backward()` 排在算 loss 后面** |
| loss 需要什么？ | 需要预测值 → 所以 **`model(x)` 排最前** |
| 为什么第一步是"清零"？ | 因为梯度**累加** → **不清零 = 旧梯度 + 新梯度**，所以必须最先做 |

**一句总纲：`zero → forward → loss → backward → step` 就是
「打扫 → 做饭 → 尝味 → 找问题 → 改进」。你不能先改进再尝味。**

**记不住就去做这两个练习**（`week3/practice_train_loop/`）：

| 文件 | 干什么 |
|---|---|
| `mytrain.py` | **填空**：只留 `# 【?】`，你从零写出来。空着也跑得起来（精度会停在 10%，正好说明没填=没学到） |
| `breakdown.py` | **故意写坏**：自动逐个破坏，真跑一遍，给你一张「缺了会怎样」的对照表 |

**实测出来的三个反直觉结论**（`breakdown_report.md`，比口诀值钱）：

1. **`zero_grad` 的累积效应，第一步看不出来** —— 因为第一步之前没有"上一轮"可累加。**所以别用「跑一个 batch」判断循环对不对。**
2. **把 `zero_grad` 挪到 `step` 之后，精度可能一点不变** —— 它等价于「学习率乘 2」。**「没报错、精度也还行」不等于代码对。**
3. **漏掉 `backward()` 或 `step()` 不会报错** —— 代码正常跑完、正常打印，只是精度永远停在随机（本实验是 0.0990）。**必须靠每轮的 `evaluate()` 才能发现。**

**5 步口诀（记住结构之后，这个才有意义）**：

```
① optimizer.zero_grad()     清空上轮梯度
② out = model(x)            前向：算预测
③ loss = criterion(out, y)  算损失
④ loss.backward()           反向：算梯度
⑤ optimizer.step()          更新参数
```

**记忆口诀：清零 → 前向 → 损失 → 反向 → 更新**

**关键字逐个说**

| 写法 | 作用 | 为什么 / 注意 |
|---|---|---|
| `nn.Module` | 所有模型的父类 | `class Net(nn.Module)` |
| `super().__init__()` | 初始化父类 | **固定写法，别漏** |
| `nn.Sequential(...)` | 按顺序串联各层 | 数据依次流过 |
| `nn.Flatten()` | 压平 | `(批,1,28,28)` → `(批,784)` |
| `nn.Linear(入, 出)` | 全连接层 | 输入维度必须和上一层对上 |
| `nn.ReLU()` | 激活函数 | **不加它，多层等于一层** |
| `forward(self, x)` | 前向计算 | 名字必须叫 `forward` |
| `model(x)` | 触发 `forward` | PyTorch 自动调，不用写 `model.forward(x)` |
| `nn.CrossEntropyLoss()` | 分类损失 | **内部含 softmax**，模型最后别再加 |
| `optim.Adam(params, lr=)` | 优化器 | `lr` 学习率；Adam 比 SGD 收敛快 |
| `lr=1e-3` | 学习率 | `1e-3` = 0.001（科学计数法） |
| `model.train()` | 训练模式 | Dropout/BatchNorm 按训练时行为 |
| `model.eval()` | 评估模式 | **评估前必须切，否则结果不准** |
| `torch.no_grad()` | 不建计算图 | 评估/更新时用，省显存 |
| `.argmax(dim=1)` | 取最大值的下标 | 10 个分数 → 预测的类别 |
| `.item()` | 张量 → Python 数值 | |
| `.size(0)` | 第 0 维的长度 | 即批大小 |

**⚠️ 常见问题排查**

| 现象 | 可能原因 |
|---|---|
| loss 不下降 | 学习率太大/太小（试 `1e-2` ~ `1e-5`） |
| 准确率一直 10% | 标签错了 / loss 用错 / 模型没学到 |
| `CUDA out of memory` | 减小 `batch_size` |
| 准确率忽高忽低 | 忘了 `model.eval()` |
| 第二轮结果异常 | 忘了 `zero_grad()` |

---

### 4.9 保存与加载模型（Week2）✅ 实测

```python
# ---------- 保存 ----------
torch.save(model.state_dict(), "model.pth")
#          ↑★ 只保存【参数】，不保存模型结构
#            state_dict() 是一个字典：{层名: 参数张量}

# ---------- 加载 ----------
model2 = Net()
#        ↑★ 必须先把模型结构定义好，而且要和训练时【完全一致】
model2.load_state_dict(torch.load("model.pth", map_location="cpu"))
#                                              ↑★ 强制加载到 CPU
#                                                有显卡存、没显卡读时必用
model2.eval()
#       ↑★ 加载后一定要切评估模式

# ---------- 推理 ----------
x, y = test_ds[0]                    # 取一张测试图
with torch.no_grad():                # 不需要梯度
    pred = model2(x.unsqueeze(0)).argmax().item()
    #             ↑★ 加一个批次维度
    #               单张图是 (1,28,28)，模型要的是 (批,1,28,28)
print(f"预测={pred}  真实={y}")
```

**实测**：保存 400 KB，加载后预测正确（预测=7 真实=7）。

**关键字逐个说**

| 写法 | 作用 | 为什么 / 注意 |
|---|---|---|
| `torch.save(obj, 路径)` | 保存 | 存整个模型也可以，但**推荐只存 `state_dict()`** |
| `model.state_dict()` | 参数字典 | `{层名: 张量}`，不含结构 |
| `torch.load(路径)` | 读回来 | |
| `map_location="cpu"` | 强制加载到 CPU | 跨设备时**必须加** |
| `model.load_state_dict(...)` | 把参数灌进模型 | **结构必须先定义且完全一致** |
| `.unsqueeze(0)` | 在最前面插入一维 | 单张图 `(1,28,28)` → `(1,1,28,28)` |

**为什么推荐只存 `state_dict()` 而不是整个模型**

| | 存 state_dict | 存整个模型 |
|---|---|---|
| 文件大小 | 小 | 大 |
| 跨代码版本 | ✅ 结构改了也能读参数 | ❌ 结构改了就读不了 |
| 安全性 | ✅ | ⚠️ 反序列化整个对象有风险 |

**⚠️ 常见坑**

```
RuntimeError: Error(s) in loading state_dict: Missing key(s)...
```
→ **模型结构和训练时不一致。** 检查 `__init__` 里的层是否一模一样。

---

### 4.10 LLM / API 调用（Week3）◐ 协议已验

> **这一段是「协议已验」，不是「模型已验」。**
> 我用**真实的 `openai` SDK** + 本地 mock 服务器真跑了一遍：请求头、`messages` 结构、
> `response_format`、`temperature`、`stream` 分块、`resp.usage` **全部正确**。
> **但没打过真实模型**（当时没有 API Key），所以「模型答得怎么样」这一层你要自己看。
>
> 第一次拿到 Key 后，先跑一次这个（不花钱的 mock + 你的一次真实调用）：
> ```powershell
> python _verify\verify_handbook_llm.py --real
> ```

#### 环境准备

```bash
pip install openai python-dotenv
#           ↑调用大模型的官方库  ↑从 .env 文件读环境变量
```

**`.env` 文件（放在项目目录，绝不要提交）：**

```
API_KEY=你的密钥
BASE_URL=https://api.deepseek.com/v1
MODEL=deepseek-flash
```

> ⚠️ **`deepseek-chat` 这个名字已经失效了**（网上老教程还在写它），现在用会直接 404。
> DeepSeek 当前的模型名：`deepseek-flash`（便宜快，支持 JSON + Tool Calls，**Week3/4 用这个**）、
> `deepseek-v4-pro`（更强更贵）。
>
> **`BASE_URL` 的 `/v1`**：官方文档写的是 `https://api.deepseek.com`（不带 `/v1`），
> 两种都能用。**带上 `/v1` 的好处是换成别的厂商时写法一致**，所以这里统一带 `/v1`。
>
> ⚠️ **`.env` 必须在 `.gitignore` 里。** 泄露 = 别人拿你的额度盗刷。
> 提交前先 `git status` 确认看不到它。
>
> **别手打 Key** —— 多一个空格就是 401，而且报错不会告诉你"你多打了空格"。
> 用 `python week3\_set_key.py`：输入时不显示、不进命令历史。

#### ★★ 思考模式：`deepseek-flash` 上最容易咬人的一个坑

**`deepseek-flash` 默认【开启思考模式】。** 这会带来两个后果，实测确认（`week3/_diag_thinking.py`）：

**① `max_tokens` 把【思考 token 算在内】。** 思考没结束预算就没了：

| `max_tokens` | 总输出 token | 其中思考 | 正文长度 | `finish_reason` |
|---|---|---|---|---|
| 10 | 10 | 10 | **0（空！）** | `length` |
| 100 | 100 | 100 | **0（空！）** | `length` |
| 500 | 122 | 98 | 39 ✅ | `stop` |

**这个坑特别阴**：做结构化输出时，预算被思考吃掉 → 你拿到**空字符串** →
`json.loads("")` 报 `JSONDecodeError` → **你会以为是 JSON 格式问题，去改 prompt**，
而真正的原因是 `max_tokens` 太小。**找错方向能卡一整天。**

**② 思考要花钱**（算在 `completion_tokens` 里），简单任务上纯属浪费。

**解决办法：关掉思考。** 用 `extra_body` 透传（openai SDK 不认这个字段）：

```python
resp = client.chat.completions.create(
    model=os.getenv("MODEL"),
    messages=[{"role": "user", "content": "..."}],
    extra_body={"thinking": {"type": "disabled"}},   # ★ 关掉思考
    #          ↑ openai SDK 不认厂商私有字段，要用 extra_body 透传
)
```

关掉后 `reasoning_tokens` 变成 `None`，**同样的钱买到更多正文**。
Week3 的实验统一关掉；到 Week4 做 Agent 时，**遇到需要多步推理的难题可以再开回来**。

> **参考**：DeepSeek 官方文档的调用示例里带的 `"thinking": {"type": "enabled"}` +
> `"reasoning_effort": "high"` 就是这个开关。它是**厂商私有参数**，
> 换厂商（通义/智谱/硅基流动）后大概率不认，去掉即可。

#### 单轮对话

```python
import os
from dotenv import load_dotenv          # 读 .env 文件的库
from openai import OpenAI

load_dotenv()
#   ↑把 .env 里的变量加载进环境变量，之后可以用 os.getenv 读

client = OpenAI(
    api_key=os.getenv("API_KEY"),
    #         ↑从环境变量读取密钥（★ 不要写死在代码里）
    base_url=os.getenv("BASE_URL"),
    #          ↑服务地址。用 OpenAI 兼容接口的不同厂商都靠这个切换
)

resp = client.chat.completions.create(
    #      ↑创建一次对话补全
    model=os.getenv("MODEL"),
    #      ↑用哪个模型
    messages=[
        #  ↑★ 对话历史，是一个列表，每个元素是一条消息
        {"role": "user", "content": "用一句话解释什么是反向传播"},
        #  ↑role 有四种：system（定义输出契约）/ user（你说）/ assistant（模型说）/ tool（工具返回）
    ],
)
print(resp.choices[0].message.content)
#          ↑choices 是候选列表      ↑第0个  ↑消息对象  ↑正文
print("tokens:", resp.usage)
#                    ↑本次用掉的 token 数（影响成本）
```

**关键字逐个说**

| 写法 | 作用 | 为什么 / 注意 |
|---|---|---|
| `load_dotenv()` | 读 `.env` 到环境变量 | 必须在使用 `os.getenv` 之前调 |
| `os.getenv("X")` | 读环境变量 | **密钥不写死在代码里**，这是安全底线 |
| `base_url=` | 服务地址 | 换厂商只改这个，代码不用动 |
| `messages=[...]` | 对话历史 | **列表顺序 = 对话顺序** |
| `{"role": "system"}` | **定义"输出契约"**（见下方 ★） | 放最前面。**它约束的是输出形状，不只是语气** |
| `{"role": "user"}` | 用户输入 | |
| `{"role": "assistant"}` | 模型回复 | 多轮时要手动塞回历史 |
| `{"role": "tool"}` | 工具返回结果 | Agent 用 |
| `resp.choices[0]` | 第一个候选结果 | 一般只有 1 个 |
| `resp.usage` | token 用量 | 算成本用 |

#### 多轮对话

```python
history = [{"role": "system", "content": "你是一个耐心的 Python 助教。"}]
#   ↑★ 用一个列表保存全部历史

def chat(user_input):
    history.append({"role": "user", "content": user_input})
    #   ↑先把用户这轮加进去

    resp = client.chat.completions.create(
        model=os.getenv("MODEL"),
        messages=history,
        #        ↑★ 把【全部历史】传回去
    )
    reply = resp.choices[0].message.content
    history.append({"role": "assistant", "content": reply})
    #   ↑再把模型回复也加进去，下一轮才能"记得"
    return reply

while True:
    q = input("你: ")
    if q in ("exit", "quit"):
        break
    print("AI:", chat(q))
```

**★ 关键认知：模型本身没有记忆。**

**它看起来"记得"上一句，是因为你把历史全传回去了。** 每一次请求都是独立的。

**这个"历史无限增长"的问题，就是 Agent 领域说的「上下文管理」。**

| 问题 | 后果 |
|---|---|
| 历史越来越长 | token 变多，成本上升 |
| 超过模型上下文上限 | 直接报错 |
| 太长的上下文 | 模型注意力被稀释，效果下降 |

**常见处理**：只保留最近 N 轮、把旧对话总结成一段、丢弃无关内容。

#### ★★ system 不是"设定人设"，是"定义输出契约"（实测）

网上教程都说 system 用来"设定人设"。**实测下来这个说法不准确。**
完整实验见 `week3/prompt_compare.md`，这里只放结论和数据。

**实验**：同一个待改写句子，对比「有没有 system」，各跑 5 次。

拆开那条 system：

```
你是一名严谨的技术文档编辑。              ← 身份。影响最小
把句子改写得更正式（书面、用于工作场合），
只输出改写后的句子。                       ← ★ 决定性的半句
```

**真正起作用的是「只输出改写后的句子」这个约束，不是那个身份。**

| 指标 | 无 system | 有 system |
|---|---|---|
| 输出字数范围 | 14 ~ **477** | 18 ~ 30 |
| **变异系数 CV**（越小越稳定） | **1.83** | **0.22** |
| 给了"菜单"（多个选项 + 解释） | 1 / 5 | 0 / 5 |

**没有 system 时**，模型把 `"把这句话改得更正式：…"` 理解成
**"帮我想想有哪些更正式的说法"** → 给一堆选项。

**有 system 时**，任务被收窄成 **"给出那一句改写"** → 只给一句。

**为什么这比"语气"重要得多** —— 这是**能不能写代码**的问题：

```python
reply = ask(...)      # 无 system：这次 "该方案尚不可行。"
                      #            下次 "**1. 标准职场版**\n> …\n**要点总结**…"
# 下一行没法写 —— 不知道拿到的是什么结构
```

**当你要把模型输出接进程序时（Week4 Agent），一致性比单条质量重要。**
**所以 D2 和 D4「结构化输出」是同一件事的两面：都在给输出"定形"。**

> **自己动手验证**：`python week3\day1.py --only 2`（`d2_prompt` 里就是这个实验）
>
> **★ 做这类对比实验的铁律**：**n≥5，看分布，不看单条。**
> 这个实验我们先用 n=1 得出了**相反**的结论，加到 n=5 才推翻。
> **样本太少时，随机性会被当成变量的效果。**

#### 结构化输出 ★ Agent 的地基

```python
prompt = """从下面的文本中抽取信息，只输出 JSON，不要任何其他文字。
格式：{"姓名": "", "科目": "", "分数": 0}

文本：张小明这次数学考了 88 分。
"""
#  ↑三引号可以写多行字符串

resp = client.chat.completions.create(
    model=os.getenv("MODEL"),
    messages=[{"role": "user", "content": prompt}],
    response_format={"type": "json_object"},
    #                ↑★ 强制模型输出合法 JSON（不是所有模型都支持）
)

import json
data = json.loads(resp.choices[0].message.content)
#           ↑把 JSON 字符串解析成 Python 字典
print(data["姓名"], data["分数"])
```

**不支持 `json_object` 时用正则兜底：**

```python
import re, json
text = resp.choices[0].message.content
m = re.search(r"\{.*\}", text, re.S)
#            ↑匹配从 { 到 } 的内容
#                          ↑re.S 让 . 也能匹配换行
data = json.loads(m.group(0)) if m else None
#                    ↑group(0) 是整个匹配结果；m 为 None 时给 None
```

**为什么这一步重要**

> **Tool Calling 本质就是"让模型吐结构化输出"。**
> 模型不是直接执行函数，而是返回一个结构化的"调用请求"。**这一步学不好，第 4 周 Agent 会卡。**

**关键字逐个说**

| 写法 | 作用 | 注意 |
|---|---|---|
| `response_format={"type":"json_object"}` | 强制输出 JSON | 不是所有模型支持 |
| `json.loads(文本)` | JSON 字符串 → Python 字典 | **模型可能加解释文字导致失败** |
| `re.search(r"\{.*\}", text, re.S)` | 从文本里抠出 JSON | `re.S` 让 `.` 匹配换行 |
| `m.group(0)` | 匹配到的整段文字 | |

#### 参数实验

```python
for temp in [0, 0.7, 1.5]:
    for _ in range(3):
        #        ↑下划线表示"这个变量我不用"，只是循环 3 次
        r = client.chat.completions.create(
            model=os.getenv("MODEL"),
            temperature=temp,
            #           ↑★ 随机性
            #             0   = 每次都一样（要确定性、要 JSON 时用）
            #             0.7 = 有变化但合理（日常对话）
            #             1.5 = 很随机（创意写作）
            max_tokens=100,
            #           ↑最多生成多少 token（防止话太长）
            messages=[{"role": "user", "content": "给我一个创业点子，一句话"}],
        )
```

**关键字逐个说**

| 参数 | 作用 | 什么时候用 |
|---|---|---|
| `temperature` | 随机性（0~2） | 要 JSON/确定性 → 0；创意 → 1+ |
| `max_tokens` | 输出长度上限 | 防止生成过长；**★ 思考模式下它把思考 token 也算在内，给小了正文会是空的** |
| `top_p` | 另一种采样控制 | 一般只调 `temperature` 就够 |
| `extra_body={"thinking":{"type":"disabled"}}` | 关掉思考模式（厂商私有） | **省 token、结果更干净。Week3 建议一直关着** |

> **实测**：`temperature=0` 时输出**仍然可能不同** —— 它降低随机性，但不保证 100% 复现
> （GPU 浮点累加顺序、批处理都会引入差异）。要完全可复现得配合固定 seed（看厂商是否支持）。
> **别因为"跑了 3 次不完全一样"就以为自己写错了。**

---

### 4.11 Agent：LLM + 1 个 Tool（Week4）◐ 协议已验

> **协议层已真跑通**：`tools` 结构、`tool_call_id` 配对、`json.loads(tc.function.arguments)`、
> `**args` 展开、白名单校验、`eval` 清空 `__builtins__` 的防护 —— **17 项断言全过**（见 `_verify/`）。
> **没验的**：真实模型会不会真的选这个工具、会不会编造工具名。
> **这两件事正是你要亲眼看的**，跑 `python _verify\verify_handbook_llm.py --real` 看输出。

#### ★ 先理解原理（比代码重要）

```
1. 你问模型一个问题
2. 你同时告诉它："你有这些工具可用"（工具名、作用、参数格式）
3. 模型判断"这问题需要调工具"，返回一个【结构化的调用请求】
4. 【你的代码】去执行那个工具，拿到结果
5. 你把结果再发给模型
6. 模型基于结果生成最终回答
```

**★ 最关键的一句：模型自己不执行任何东西。它只"决定调什么"，真正执行的是你的代码。**

#### 完整代码

```python
import os, json
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI(api_key=os.getenv("API_KEY"), base_url=os.getenv("BASE_URL"))
MODEL = os.getenv("MODEL")

# ================= ① 定义工具：真正执行的是这里 =================
def calculator(expression: str) -> str:
    #              ↑参数类型提示  ↑返回类型提示（只是提示，Python 不强制）
    """计算数学表达式"""
    allowed = set("0123456789+-*/(). %")
    #   ↑允许出现的字符集合
    if not set(expression) <= allowed:
        #  ↑★ 安全校验：表达式里只能有这些字符
        #    `<=` 用在集合上是"子集"判断
        return "错误：表达式含非法字符"
    try:
        return str(eval(expression, {"__builtins__": {}}, {}))
        #          ↑eval 把字符串当代码算
        #                         ↑★ 关键安全设置：清空内置函数
        #                           防止有人输入 __import__('os').system('rm -rf /')
        #                                          ↑空的全局/局部命名空间
    except Exception as e:
        #       ↑捕获所有异常，别让工具崩掉整个 Agent
        return f"计算错误：{e}"

TOOLS_IMPL = {"calculator": calculator}
#   ↑把"工具名 → 函数"的对应关系存起来，后面按名字调

# ================= ② 告诉模型有哪些工具 =================
TOOLS_SPEC = [{
    "type": "function",
    "function": {
        "name": "calculator",
        "description": "计算数学表达式。当用户需要做算术运算时调用。",
        #              ↑★ 这段描述非常关键 —— 模型就是靠它判断"什么时候该用"
        "parameters": {
            "type": "object",
            "properties": {
                "expression": {
                    "type": "string",
                    "description": "要计算的数学表达式，例如 '(23*7+15)/2'",
                }
            },
            "required": ["expression"],
            #  ↑哪些参数是必填的
        },
    },
}]

# ================= ③ Agent 主循环 =================
def run_agent(question, max_steps=5):
    #                          ↑★ 最大步数，防止无限循环
    messages = [
        {"role": "system", "content": "你是一个助手。需要算术时调用 calculator 工具，不要自己心算。"},
        {"role": "user", "content": question},
    ]

    for step in range(max_steps):
        resp = client.chat.completions.create(
            model=MODEL, messages=messages, tools=TOOLS_SPEC
            #                                ↑★ 把工具说明传给模型
        )
        msg = resp.choices[0].message
        messages.append(msg)
        #   ↑把模型的回复（可能是工具请求）也加进历史

        if not msg.tool_calls:
            #  ↑★ 模型没有要求调工具 → 说明它要直接回答
            return msg.content

        for tc in msg.tool_calls:
            #        ↑tool_call 对象
            name = tc.function.name
            args = json.loads(tc.function.arguments)
            #                    ↑★ 注意：arguments 是【JSON 字符串】，要解析
            result = TOOLS_IMPL[name](**args)
            #                       ↑按名字找函数
            #                              ↑** 把字典展开成关键字参数
            #                                {"expression":"1+1"} → calculator(expression="1+1")
            messages.append({
                "role": "tool",
                "tool_call_id": tc.id,
                #              ↑★ 把结果和模型的请求对应起来
                #                模型可能一次要调多个工具，靠 id 区分
                "content": result,
            })

    return "达到最大步数仍未结束"
```

**测试：**

```python
for q in ["(23*7+15)/2 等于多少？", "你好，你是谁？", "帮我算 128 的平方，再除以 4"]:
    print("问题:", q)
    print("回答:", run_agent(q))
```

#### ★ 你必须能回答的五个问题

| 问题 | 答案 |
|---|---|
| **模型怎么"决定"调不调工具？** | 靠 `tools` 参数里的**工具描述**，所以 `description` 要写清楚 |
| **工具是谁执行的？** | **你的代码**（`TOOLS_IMPL[name](**args)`），模型只"决定调什么" |
| **为什么要 `max_steps`？** | 防止模型反复调工具停不下来（无限循环） |
| **`tool_call_id` 干什么？** | 把执行结果和模型的请求**对应起来**（可能一次调多个） |
| **模型编造不存在的工具名会怎样？** | `KeyError` —— **这就是"失败重试"要解决的问题** |

#### 关键字逐个说

| 写法 | 作用 | 注意 |
|---|---|---|
| `def f(x: str) -> str:` | 类型提示 | **只是提示，Python 不强制检查** |
| `set(a) <= set(b)` | 集合的"子集"判断 | 用来做白名单校验 |
| `eval(表达式, 全局, 局部)` | 把字符串当代码算 | **必须清空 `__builtins__`**，否则是安全漏洞 |
| `try / except` | 捕获异常 | 工具执行失败不要崩掉整个 Agent |
| `TOOLS_IMPL = {"名": 函数}` | 名字→函数的映射 | 按名字调用 |
| `"description": "..."` | 工具说明 | **模型靠它决定何时调用**，要写清楚 |
| `tools=TOOLS_SPEC` | 把工具传给模型 | |
| `msg.tool_calls` | 模型的工具请求 | 为空说明它要直接回答 |
| `json.loads(tc.function.arguments)` | 解析参数 | **arguments 是 JSON 字符串** |
| `func(**字典)` | 把字典展开成关键字参数 | `**{"a":1}` → `func(a=1)` |
| `"role": "tool"` | 工具返回结果 | 必须带 `tool_call_id` |
| `max_steps` | 最大循环数 | 防死循环 |

---

### 4.12 SQL / 数据库（长期）✅ 实测

```python
import sqlite3
#       ↑Python 标准库自带，不用装

conn = sqlite3.connect("demo.db")
#      ↑连接数据库（文件不存在会自动创建）
cur = conn.cursor()
#     ↑游标：用来执行 SQL 语句

# ---------- 建表 ----------
cur.execute("""
CREATE TABLE IF NOT EXISTS tool_calls (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    tool       TEXT,
    success    INTEGER,
    elapsed_ms REAL,
    ts         TEXT DEFAULT CURRENT_TIMESTAMP
)""")
#   ↑IF NOT EXISTS = 表已存在就不报错
#    ↑主键，自增                    ↑默认值：当前时间

# ---------- 建索引（加快查询）----------
cur.execute("CREATE INDEX IF NOT EXISTS idx_tool ON tool_calls(tool)")
#                                   ↑在 tool 这列上建索引

# ---------- 插入 ----------
cur.executemany(
    #   ↑插入多行（单行用 execute）
    "INSERT INTO tool_calls (tool, success, elapsed_ms) VALUES (?,?,?)",
    #                                                        ↑★ 占位符，防 SQL 注入
    [("calculator", 1, 12.3),
     ("weather", 0, 340.1),
     ("calculator", 1, 9.8)])
conn.commit()
#    ↑★ 必须提交，否则改动不生效

# ---------- 查询 ----------
cur.execute("""
    SELECT tool,                            -- 选哪些列
           COUNT(*) AS n,                   -- 计数，起个别名叫 n
           ROUND(AVG(success)*100, 1) rate, -- 成功率
           ROUND(AVG(elapsed_ms), 1) avg_ms -- 平均耗时
    FROM tool_calls                         -- 从哪张表
    GROUP BY tool                           -- 按 tool 分组
    ORDER BY n DESC                         -- 按数量降序
""")
for row in cur.fetchall():
    #        ↑取出所有结果（每行是一个元组）
    print(row)

conn.close()
#    ↑用完关闭
```

**核心 SQL 语法**

```sql
SELECT 列1, 列2 FROM 表 WHERE 条件 ORDER BY 列 DESC LIMIT 10;
--     ↑选什么      ↑从哪   ↑筛什么      ↑排序       ↑只取10条

SELECT 列, COUNT(*) FROM 表 GROUP BY 列 HAVING COUNT(*) > 5;
--                              ↑按这列分组          ↑分组【后】再筛

SELECT a.*, b.* FROM 表A a JOIN 表B b ON a.id = b.a_id;
--                          ↑起别名  ↑关联   ↑关联条件
```

**关键字逐个说**

| 写法 | 作用 | 注意 |
|---|---|---|
| `sqlite3.connect(文件)` | 连接数据库 | 文件不存在会自动建 |
| `.cursor()` | 创建游标 | 执行 SQL 靠它 |
| `CREATE TABLE IF NOT EXISTS` | 建表 | 已存在不报错 |
| `PRIMARY KEY AUTOINCREMENT` | 主键自增 | 每行唯一编号 |
| `CREATE INDEX` | 建索引 | **加快查询**，但会占空间 |
| `execute` / `executemany` | 执行单条 / 多条 | |
| `?` | 占位符 | **防 SQL 注入，永远别用字符串拼接** |
| `.commit()` | 提交 | **不提交改动不生效** |
| `.fetchall()` | 取所有结果 | |
| `GROUP BY` | 分组 | 配合聚合函数用 |
| `HAVING` | 分组后筛选 | **`WHERE` 是分组前，`HAVING` 是分组后** |
| `JOIN ... ON` | 关联两张表 | |
| `ROUND(x, n)` | 保留 n 位小数 | |
| `AS` | 起别名 | |

**为什么这个值得学**

技术实习岗 **15.6%** 要求 SQL。而且你第 5 周如果选「数据库 Tool」，正好用得上——**一次做完，既交了作业又补了技能。**

---

### 4.13 数据结构与算法（长期，第一优先）

**依据**：技术实习岗 **46.9%** 要求（与 Python 并列第一）。

**力度**：**"熟悉常见数据结构"就够，不用刷 LeetCode 难题。**

| 结构 | 要点 | Python 里对应 |
|---|---|---|
| 数组 | 随机访问 O(1)，插入删除 O(n) | `list` |
| 链表 | 插入删除 O(1)，访问 O(n) | 手写类 |
| 栈 | 后进先出 LIFO | `list` 的 `append`/`pop` |
| 队列 | 先进先出 FIFO | `collections.deque` |
| 哈希表 | 查找 O(1) | `dict` |
| 排序 | 冒泡 O(n²)；快排/归并 O(n log n) | `sorted()` |

**复杂度速记**

```
O(1)     常数 —— 和数量无关（查字典）
O(log n) 对数 —— 二分查找
O(n)     线性 —— 遍历一遍
O(n²)   平方 —— 两层循环（冒泡排序）
```

**刷题节奏**：LeetCode 简单 + 部分中等，**60–100 题**，每题能讲清思路。

**★ 比刷题量重要的一件事**：每道题问自己"**为什么这么解**"，而不是"**记住这个写法**"。

---

### 4.14 Linux 常用命令（Week2，培养方案要求）

**你没有 Linux 机器，但命令要认识**——迟早会在服务器/容器里遇到。

**在 Windows 上练习：用 Git Bash**（开始菜单搜 `Git Bash`），大部分命令通用。

```bash
pwd                    # print working directory：我在哪个目录
ls -la                 # list：列出文件；-l 详细信息，-a 含隐藏文件
cd /path/to/dir        # change directory：切换目录
cd ..                  # 回上一级
cd ~                   # 回家目录（★ bash 里 ~ 会展开）
mkdir demo             # make directory：建目录
cp a.txt b.txt         # copy：复制
cp -r dir1 dir2        # -r 递归复制整个目录
mv a.txt b.txt         # move：移动 / 重命名
rm file.txt            # remove：删文件
rm -rf demo/           # -r 递归，-f 强制（★ 危险，想清楚再敲）
cat file.txt           # 打印整个文件
head -n 20 f.txt       # 看前 20 行
tail -n 20 f.txt       # 看后 20 行
tail -f log.txt        # 实时跟踪文件新增内容（看日志用）
grep "error" log.txt   # 在文件里搜内容
grep -r "def " .       # -r 递归搜整个目录
find . -name "*.py"    # 按名字找文件
chmod +x run.sh        # change mode：加执行权限
ps aux | grep python   # 看正在跑的进程
top                    # 实时看资源占用（q 退出）
nvidia-smi             # 看显卡状态
```

**管道与重定向（很实用）**

```bash
python train.py > log.txt 2>&1
#               ↑把标准输出写入文件
#                          ↑2>&1 把错误输出也一起写进去（★ 常用）
cat log.txt | grep "acc"
#           ↑管道：把左边的输出当作右边的输入
```

**和 Windows 的区别**

| | PowerShell | Linux / Git Bash |
|---|---|---|
| 路径分隔符 | `\` | `/` |
| 家目录 | `$env:USERPROFILE` | `~`（**bash 里会展开**） |
| 盘符 | `E:\agent` | `/e/agent` |
| 删目录 | `Remove-Item -Recurse` | `rm -rf` |
| 看文件 | `Get-Content` | `cat` |
| 搜内容 | `Select-String` | `grep` |

> ⚠️ **`~` 的区别（你踩过）**：Git Bash / Linux 里 `~` 会展开成家目录；**PowerShell 里传给外部程序时不会展开**，会被当成字面字符。

**关键字逐个说**

| 命令/符号 | 作用 |
|---|---|
| `pwd` / `ls` / `cd` | 看位置 / 列文件 / 切目录 |
| `-l` `-a` `-r` `-f` | 参数：详细 / 含隐藏 / 递归 / 强制 |
| `>` | 输出重定向（覆盖） |
| `>>` | 输出重定向（追加） |
| `2>&1` | 把错误输出也合并进标准输出 |
| `\|` | 管道：左边输出 → 右边输入 |
| `rm -rf` | **危险命令**，删目录不确认 |

---

### 4.15 YOLO / 计算机视觉（Week3 备选分支）✅ 实测

```bash
pip install ultralytics opencv-python
#           ↑YOLO 的官方库      ↑OpenCV，图像处理
```

```python
import numpy as np
import cv2
from ultralytics import YOLO

# ---------- 加载模型 ----------
model = YOLO("yolov8n.pt")
#            ↑n = nano，最小的版本，速度最快、精度最低
#              越大越准越慢：n < s < m < l < x
# model = YOLO(r"C:\Users\omen\yolov8n.pt")   # 用本机已有的，避免下载超时

# ---------- 单张图片推理 ----------
img = cv2.imread("test.jpg")
#     ↑读图片，返回 numpy 数组，形状 (高, 宽, 3)，通道顺序是 BGR（★不是 RGB）

results = model(img, verbose=False)
#                ↑verbose=False 关掉进度输出

r = results[0]
#   ↑results 是一个列表；单张图取第 0 个

print(f"检测到 {len(r.boxes)} 个框")
print(f"坐标:   {r.boxes.xyxy}")     # 形状 (N, 4)：左上角x,y 右下角x,y
print(f"类别:   {r.boxes.cls}")      # 形状 (N,)：类别编号
print(f"置信度: {r.boxes.conf}")     # 形状 (N,)：0~1，越高越确定

# ---------- 画框并保存 ----------
annotated = r.plot()
#           ↑在原图上画好框和标签，返回 BGR 图像，形状和输入一样
cv2.imwrite("out.jpg", annotated)
#          ↑保存图片
```

**实测结果**（用本机 `C:\Users\omen\yolov8n.pt`）：

```
模型加载   0.07s
单张推理   1308ms
r.boxes.xyxy 形状  (0, 4)
r.plot() 返回      (480, 640, 3)
```

> **权重下载经常超时**（GitHub 国内访问不稳）。本机已有可直接用：
> `C:\Users\omen\yolov8n.pt`、`D:\dsh\YOLO-Starfish-repo\weights\yolov8n.pt`

**关键字逐个说**

| 写法 | 作用 | 注意 |
|---|---|---|
| `YOLO("yolov8n.pt")` | 加载模型 | `n`=nano 最小最快；首次会自动下载 |
| `model(img)` | 推理 | 返回 `Results` 列表 |
| `results[0]` | 取第一张的结果 | 传多张图时是多个 |
| `r.boxes` | 检测框对象 | |
| `r.boxes.xyxy` | 框坐标 | 形状 `(N,4)`，**N 可能是 0**（没检测到） |
| `r.boxes.cls` | 类别编号 | 数字，要查 `model.names` 才知道是什么 |
| `r.boxes.conf` | 置信度 | 0~1 |
| `r.plot()` | 画框后的图 | 返回 BGR numpy 数组 |
| `cv2.imread` / `imwrite` | 读/写图 | **通道顺序是 BGR，不是 RGB** |

---

### 4.16 视频 Edge（Week4 三方向之一）✅ 实测

**关键指标是 FPS**（能不能实时处理）。

```python
import cv2, time
from ultralytics import YOLO

model = YOLO("yolov8n.pt")

cap = cv2.VideoCapture("test.mp4")
#     ↑打开视频文件；改成 0 就是用摄像头

fps_list = []                    # 存每一帧的 FPS
frames = 0                       # 已处理帧数
t_start = time.time()            # 开始时间

while True:
    ok, frame = cap.read()
    #  ↑是否读到了  ↑这一帧的图像
    if not ok:                   # 视频读完了
        break

    t0 = time.time()
    results = model(frame, verbose=False)
    fps_list.append(1.0 / (time.time() - t0))
    #                 ↑用"1 除以这一帧耗时"算瞬时 FPS

    frames += 1
    cv2.imwrite(f"out/frame_{frames:05d}.jpg", results[0].plot())
    #                              ↑:05d 补零到 5 位 → frame_00001.jpg
    if frames >= 200:            # 只跑 200 帧做测试
        break

cap.release()
#   ↑释放视频资源（用完要放）

print(f"处理 {frames} 帧, 平均 {sum(fps_list)/len(fps_list):.1f} FPS")
print(f"总耗时 {time.time()-t_start:.1f}s")
```

**实测结果**（60 帧随机噪声）：

```
平均 FPS: 12.4
总耗时:   13.0s
保存的帧: 3 个
```

**★ 为什么 FPS 是关键指标**

**视频通常是 25–30 FPS。处理速度低于它就跟不上实时** —— 会丢帧，或者延迟越积越多。

| 场景 | 要求 |
|---|---|
| 离线分析视频 | FPS 无所谓，慢慢跑 |
| 实时监控 | **必须 ≥ 视频帧率** |
| 边缘设备（如 Jetson） | 算力有限，要优化模型大小 |

**要记录的**：帧数、平均 FPS、总耗时、显存占用（`nvidia-smi`）。

**关键字逐个说**

| 写法 | 作用 | 注意 |
|---|---|---|
| `cv2.VideoCapture(路径或0)` | 打开视频/摄像头 | `0` = 默认摄像头 |
| `cap.read()` | 读下一帧 | 返回 `(是否成功, 帧)` |
| `cap.release()` | 释放资源 | 用完要放 |
| `1.0 / 耗时` | 算瞬时 FPS | 单位：帧/秒 |
| `f"{n:05d}"` | 补零格式化 | `1` → `00001` |
| `time.time()` | 当前时间戳（秒） | 相减得耗时 |

---

### 4.17 LLM 部署（Week4 三方向之一）◐ 指标代码已验 / 本地推理未验

**目标**：跑起来一个开源 LLM，**记录显存占用和推理速度**。

> **状态拆开说**：
> - ✅ **`r.usage.completion_tokens` 和下面那段计时代码：已验证能跑通**（走 4.10 的同一套协议）
> - ✅ **`nvidia-smi` 看显存：你这台机器有 RTX 5060，可以直接用**（4.15 节已经用过）
> - ⚠️ **Ollama / vLLM 本身没跑过** —— 需要下载模型（几个 GB），当时没做
>
> **注意**：这一段即使不装 Ollama 也能交差。手册下面写了替代方案——
> **重点是「记录指标」这个动作，不是非要本地部署。**

**选项 A：Ollama**（最简单，适合入门）

```bash
ollama pull qwen2.5:1.5b
#            ↑模型名:参数量；1.5b = 15 亿参数，8G 显存够用
ollama run qwen2.5:1.5b
```

**选项 B：vLLM**（接近工业用法，需要 NVIDIA 显卡）

```bash
pip install vllm
python -m vllm.entrypoints.openai.api_server --model Qwen/Qwen2.5-1.5B-Instruct
#      ↑以模块方式运行 vLLM          ↑启动 OpenAI 兼容的 API 服务
#      启动后就是一个本地 API，用法和 4.10 一样，只是 base_url 换成 localhost
```

**★ 要记录的四个指标**

| 指标 | 怎么测 | 单位 | 说明 |
|---|---|---|---|
| **显存占用** | `nvidia-smi` | MB | 加载前 vs 加载后对比 |
| 加载时间 | 计时 | 秒 | 从启动到能响应 |
| **首 token 延迟（TTFT）** | 代码计时 | 毫秒 | 用户等多久看到第一个字 |
| **生成速度** | 输出 token 数 / 耗时 | tokens/s | 说完全部要多久 |

```python
import time
t0 = time.time()
r = client.chat.completions.create(
    model="本地模型名",
    messages=[{"role": "user", "content": "写一段 200 字的介绍"}])
t1 = time.time()

n_out = r.usage.completion_tokens
#        ↑这次实际生成了多少 token
print(f"耗时 {t1-t0:.2f}s, 输出 {n_out} tokens, 速度 {n_out/(t1-t0):.1f} tokens/s")
```

**★ TTFT 和吞吐量的区别（重要）**

| | 含义 | 影响什么 |
|---|---|---|
| **TTFT** | 从发出请求到收到**第一个** token 的时间 | 用户"感觉快不快" |
| **吞吐量** | 每秒生成多少 token | "多久能说完" |

**一个模型可能 TTFT 很短但吞吐量低**（第一个字很快，但后面吐得很慢），反过来也有。

> **没有显卡 / 下载不下来怎么办**：用 API 替代，但**指标要换**——记录"不同 `max_tokens` 的耗时"或"并发请求的延迟"。
> **重点是"记录指标"这个动作**，不是非要本地跑。

**关键字逐个说**

| 写法 | 作用 |
|---|---|
| `ollama pull` / `run` | 下载模型 / 运行模型 |
| `python -m vllm.entrypoints...` | 以模块方式启动服务 |
| `--model 模型名` | 指定用哪个模型 |
| `r.usage.completion_tokens` | 本次输出的 token 数 |
| `n_out / 耗时` | 算吞吐量（tokens/s） |

---

### 4.18 RAG / 知识库（Week5 可选项）⚠️ 未实测

> **这一节没有可跑的代码块**（只有流程图和表格），所以没有「实测」可言。
> ⚠️ 的真正含义是：**「Embedding + 向量检索」这条链路我没在这台机器上跑过**（需要 API Key 或本地向量库）。
>
> **但有个好消息**：RAG 的**骨架部分不用 API Key 也能练**——切块、Top-k 检索、拼 Prompt 这三步，
> 用 `difflib` 或简单的词频匹配就能做出一个能跑的版本（**检索质量差，但流程一样**）。
> 等第 5 周真要做的时候，把「向量检索」换成真实 Embedding 即可，**其余代码不用动**。
> 这一节真正的价值在下面那张「失败模式」表 —— 那就是 Week5 对比实验要回答的问题。

**核心流程**

```
文档 → 解析 → 切块(Chunk) → 向量化(Embedding) → 存进向量库
                                                    ↓
用户问题 → 向量化 → 检索(Top-k) → [重排 Rerank] → 拼进 Prompt → LLM 回答
```

**每一步在干什么**

| 步骤 | 做什么 | 为什么 |
|---|---|---|
| **解析** | PDF/Word → 纯文本 | 模型只认文本 |
| **切块** | 长文档切成小段 | 太长塞不进上下文；太短丢信息 |
| **向量化** | 每段文本 → 一串数字（向量） | 让"意思相近"变成"距离相近" |
| **向量库** | 存这些向量 | 支持快速找"最相近的" |
| **检索** | 拿问题去找最相近的 Top-k 段 | 这就是 RAG 的核心动作 |
| **重排** | 对检索结果再排一次序 | 提升精度（可选） |
| **拼 Prompt** | 把检索到的内容塞进提示词 | 让模型"看着资料回答" |

**要比较的参数（这就是 Week5 的"对比实验"）**

| 变量 | 试什么 |
|---|---|
| Chunk 大小 | 200 / 500 / 1000 字符 |
| Embedding 模型 | 不同模型的效果差异 |
| Top-k | 取 3 段 / 5 段 / 10 段 |
| 是否 Rerank | 开 / 关 |

**★ 文档点名的关键问题**

> **什么时候 RAG 真正有用，什么时候反而给 Agent 提供错误信息？**

**这就是它和"调包"的区别。**

RAG 会检索到**不相关的片段**，然后 LLM 基于错误信息**自信地胡说**——这比"模型说不知道"更危险。

**值得专门记录的失败模式：**

| 失败模式 | 表现 |
|---|---|
| 检索不到 | 知识库里没有，模型开始编 |
| 检索错了 | 找到相似但无关的内容，答案跑偏 |
| 片段被截断 | 关键信息在切块边界上丢了 |
| 多段冲突 | 检索到互相矛盾的内容，模型随机选一个 |

**这一节的价值不在"会调 RAG"，而在"知道它什么时候会错"。**

---

## 5. 6 周逐日任务表

> 这是"今天该干什么"的直接答案。每天四件事：**学什么 → 做什么 → 产出什么 → 怎么自查**。
> 卡住时先查第 6 章 Bug 表，再走第 7 章自救流程。

**总览**

| 周 | 主题 | 本周交付物 | 状态 |
|---|---|---|---|
| 1 | Python 与开发环境 | `week1/analyze.py` | ✅ 已完成 |
| 2 | Git、Linux 与深度学习基础 | `week2/` MNIST 训练脚本 | ✅ 已完成（97.36%） |
| 3 | 现代 AI 模型体验 | `week3/` LLM 调用脚本 | ⬜ 未开始 |
| 4 | 三个方向体验 | `week4/` Agent + 部署 + Edge | ⬜ 未开始 |
| 5 | 选方向 + 小模块 | `week5/` 独立模块 | ⬜ 未开始 |
| 6 | 正式考核 | Demo + 仓库 + 5页汇报 + 1页总结 | ⬜ 未开始 |

**每天的固定动作（不管哪天）：**

```
开始前    git pull                    # 拉最新（有远端更新时）
结束时    git add . && git commit -m "..." && git push
结束时    notes/log.md 写 3 行
```

---

### 第 1 周 · Python 与开发环境

> **文档要求**：Python 基础、函数、类；NumPy、Pandas、Matplotlib；Conda、VS Code
> **实践任务**：读 CSV → 统计 → 绘图 → 保存结果
> **考核重点**：能独立创建环境、安装库、运行程序，**并处理简单报错**
> **交付物**：`week1/analyze.py`

**状态：✅ 已完成**

#### D1 · 环境搭建
- **学**：Conda 环境、IDE 解释器、Git 初始化（→ 第 2 章）
- **做**：建 `agent` 环境（Python 3.11）→ 装 numpy/pandas/matplotlib → 建仓库 + `.gitignore` → 写脚本跑通
- **产出**：`week1/day1.py`
- **自查**：能从零建环境；第一次 commit 成功

#### D2 · Python 基础
- **学**：变量/类型、if/elif/else、for/while、列表、字典、列表推导式（→ 4.1）
- **做**：三道题 —— 数及格人数、**字典分段统计**、列表推导式取及格
- **产出**：`week1/day2.py`
- **自查**：能说清 `counts[k] = counts.get(k, 0) + 1` 为什么不会 KeyError

#### D3 · 函数与类
- **学**：`def` / 参数 / 默认参数 / `return`；`class` / `__init__` / `self`；`if __name__ == "__main__"`（→ 4.2）
- **做**：把 D2 的 if/elif 抽成 `get_bucket()`；写 `pass_rate()`；写 `ScoreAnalyzer` 类（4 个方法）
- **产出**：`week1/day3.py`
- **自查**：**`self` 是什么**；`__init__` 什么时候被调用；属性为什么要写 `self.`
- **⚠️ 常见坑**：`elif 60 <= s < 79` 把 79 漏了；函数里嵌套定义同名函数返回 None

#### D4 · NumPy
- **学**：`np.array`/`random`/`arange`、`shape`/`dtype`、切片、聚合、**`axis`**、布尔索引（→ 4.3）
- **做**：造 5×3 成绩矩阵；算全体/每列/每行平均、每行最高；取 `>90`；把 `<60` 改成 60
- **产出**：`week1/day4.py`
- **自查**：**`axis` 是"要被消掉的那一维"**；用输出长度验证

#### D5 · Pandas
- **学**：`read_csv`/`to_csv`、`head`/`info`/`describe`、选列选行、`groupby`/`agg`、`sort_values`、`value_counts`/`nunique`（→ 4.4）
- **做**：先生成 `data.csv`（100 学生 × 3 科，固定 seed）；再做 8 道题
- **产出**：`week1/day5.py` + `week1/data.csv`
- **自查**：`groupby` 在干什么；**每一步 `print(type(x), x.shape)`**
- **⚠️ 常见坑**：多条件要用 `&` 且每个条件加括号

#### D6 · Matplotlib
- **学**：`fig, ax = plt.subplots()` 两层结构；`fig.` vs `ax.`；柱/折/直方/散点；中文三行；`savefig`（→ 4.5）
- **做**：画各科平均分柱状图（柱上标数值）+ 分数分布直方图 + 分组柱状图
- **产出**：`week1/*.png` 三张
- **自查**：**生成图片后看文件大小**（<12KB = 空白图）
- **⚠️ 常见坑**：`ax.bar=(...)` 多了等号 → 不报错但图空白

#### D7 · 整合成本周交付物
- **做**：把 D5+D6 重构成 `analyze.py`（`load`/`stats`/`plot`/`main` 四个函数）；加 `argparse`；写 `README.md`
- **产出**：`week1/analyze.py` + `README.md` + `make_data.py` + `result.png` + `summary.csv`
- **自查**：**复制到别的目录还能跑**（可复现）；**`--input` 和 `--outdir` 都能用**
- **⚠️ 常见坑**：`savefig("out_path")` 加了引号；`to_csv(index=False)` 丢了科目名；没 `os.makedirs`

---

### 第 2 周 · Git、Linux 与深度学习基础

> **文档要求**：Linux 常用命令；Git 及 GitHub/GitLab 基本使用；PyTorch、Tensor、Dataset、DataLoader；训练与测试流程
> **实践任务**：MNIST 或 CIFAR 分类 —— **训练模型、保存和加载模型、输出 Accuracy**
> **考核重点**：**"不能只运行别人代码"**；能解释**训练集、测试集、Loss、为什么需要反向传播**
> **交付物**：`week2/` 训练脚本 + 日志

**状态：✅ 已完成**（交付物：`week2/LOOP.py` + `loadtest.py` + `README.md`，实测准确率 **97.36%**）

#### D1 · Git 远程 ✅ 已完成
- **学**：SSH 密钥、`git remote`、`push`/`pull`、`.gitignore`（→ 第 3 章）
- **做**：生成 GitHub 专用密钥 → 配 `~/.ssh/config` → 网页建仓库 → 绑公钥 → `git push`
- **产出**：GitHub 上的仓库
- **自查**：`git ls-remote origin` 能列出 refs
- **⚠️ 常见坑**：**PowerShell 里 `~` 不展开**；私钥有密码短语；remote 里占位符没替换

#### D2 · Git 分支 ✅ 已完成
- **学**：`switch -c` / `merge` / `branch -d`（→ 3.5）
- **做**：建 `feat/xxx` 分支 → 加一个功能 → 提交 → **切回 main 看文件变回去** → 合并 → 删分支
- **产出**：合并进 main 的一次提交
- **自查**：**切分支时硬盘上的文件会跟着变**；合并完记得删本地和远端分支

#### D3 · Linux 常用命令 ✅ 已完成
- **学**：`pwd`/`ls`/`cd`/`cp`/`mv`/`rm`/`cat`/`grep`/`find`/`chmod`/`ps`；管道与重定向（→ 4.14）
- **做**：**在 Git Bash 里**把每个命令敲一遍；练习 `python x.py > log.txt 2>&1`
- **产出**：命令笔记已并入手册 4.14 节
- **自查**：能说清 `~` 在 bash 和 PowerShell 里的区别；知道 `rm -rf` 为什么危险

#### D4 · PyTorch Tensor 与自动求导 ✅ 已完成
- **学**：Tensor 与 NumPy 的关系；`requires_grad`；计算图；`backward()`；`.grad`；**梯度累积**（→ 4.6）
- **做**：`x.grad` 手算对账；多变量求导；**用自动求导做梯度下降拟合 `y = 2x + 1`**
- **产出**：`week2/day4.py`，`w` 收敛到 **2.0000**
- **自查**：**用自己话讲"为什么需要反向传播"**（考核点名）
- **⚠️ 常见坑**：忘了 `zero_grad()` → 梯度累积

#### D5 · Dataset 与 DataLoader ✅ 已完成
- **学**：`Dataset` vs `DataLoader` 的分工；`batch_size`；`shuffle`（→ 4.7）
- **做**：加载 MNIST；取一个 batch 看 shape；对比 shuffle 开/关
- **产出**：`week2/dataset & dataloader.py`
- **自查**：为什么**训练集要 shuffle、测试集不用**？
- **⚠️ 常见坑**：Windows 上 `num_workers > 0` 会卡死

#### D6 · MNIST 训练循环 ✅ 已完成
- **学**：**训练循环 5 步**：`zero_grad → forward → loss → backward → step`；`model.train()`/`eval()`；`torch.no_grad()`（→ 4.8）
- **做**：完整训练 3 个 epoch；每轮记录 loss 和 test_acc
- **产出**：`week2/LOOP.py`，**实测准确率 97.36%**（RTX 5060 / 60000 张 / 110 秒）
- **自查**：
  - [ ] 能说出**4 层结构**（epoch 循环 / `train()` / batch 循环 / 5 步），不只是背 5 步
  - [ ] 能说出 5 步**为什么是这个顺序**（因果逼出来的，不是规定）
  - [ ] 能说出 `eval()` 和 `train()` 分别管什么
  - [ ] 记不牢 → 做 `week3/practice_train_loop/` 的两个练习
- **⚠️ 常见坑**：loss 不下降（学习率）；显存不够（减 batch_size）；**漏 `backward()`/`step()` 不报错但白训**

#### D7 · 保存/加载模型 + 整理交付物 ✅ 已完成
- **学**：`torch.save(state_dict)` / `load_state_dict`；`map_location`（→ 4.9）
- **做**：保存模型 → 新建脚本加载 → 推理一张图；整理 `week2/README.md`
- **产出**：`week2/loadtest.py` + `model.pth` + `README.md`
- **自查**：
  - [ ] 能解释**训练集/测试集/验证集**分别干什么
  - [ ] 能解释 **Loss** 是什么、为什么能衡量好坏
  - [ ] 能解释**为什么需要反向传播**
  - [ ] 能说清**你改了哪几行、结果怎么变**（证明不是只跑别人的代码）

---

### 第 3 周 · 现代 AI 模型体验（大模型分支）

> **文档要求**：二选一 ①视觉 YOLO ②大模型（本地小模型或 LLM API）
> **你的选择**：**② 大模型**
> **实践任务**：Prompt、多轮对话、结构化输出
> **考核重点**：能改变输入和参数、保存结果，并**解释模型的输入与输出**
> **交付物**：`week3/` LLM 调用脚本 + 参数实验记录

**状态：⬜ 未开始**（`week3/day1.py` 已备好 —— 是「环境自检 + D1~D5 示例」的一体脚本）

> **开跑前先做两件事**（`week3/practice_train_loop/`）：
> 1. 训练循环还记不牢 → 先做 `mytrain.py` 填空，再跑 `breakdown.py` 看"缺了会怎样"
> 2. 确认代码层面没问题 → `python _verify\verify_handbook_llm.py`（不花钱，不需要 Key）
>
> 然后 `copy .env.example .env` 填三个值，再 `python week3\day1.py --check` 自检。
>
> **进度**：D1 ✅（单轮调用）　D2 ✅（Prompt 对比，见 `prompt_compare.md`）　D3~D5 ⬜

> ⚠️ **`ROADMAP-5months.md` 顶部有更正标记** —— 那份长期计划是按**大厂**标准排的，
> 而你的第一份实习目标是**中小厂**（两者要求差别很大）。
> **六周期间不用管它**，等观察期跑完再重排。**别照它执行。**

#### D1 · 跑通第一次调用
- **学**：API 基本用法；`.env` 管理密钥（→ 4.10）
- **做**：选一个 OpenAI 兼容服务 → 写 `.env` → **确认 `.env` 在 `.gitignore` 里** → 跑通一次对话
- **产出**：`week3/day1.py`（**已备好**，直接跑）+ `.env`
- **自查**：
  - [ ] `git status` 里**看不到 `.env`**
  - [ ] `python week3\day1.py --check` 五项自检全过
- **⚠️ 关键**：密钥泄露 = 被盗刷。先确认 `.gitignore` 再加文件
- **★ 省事提示**：`day1.py` 内置了 401 / 404 / 连接失败的中文诊断。报错时它会直接告诉你**该去改哪个变量**，不用自己猜

#### D2 · Prompt 基础
- **学**：system 角色设定、明确指令、**少样本示例（few-shot）**、思维链
- **做**：同一问题做 3 组对比（有/无 system、有/无示例、直接问/先分析）
- **产出**：`week3/prompt_compare.md`（3 组对比记录）
- **自查**：能说出 few-shot 为什么有效

#### D3 · 多轮对话
- **学**：**模型没有记忆**，多轮靠把 `messages` 历史全部传回去
- **做**：写一个命令行聊天循环；观察 `messages` 怎么增长
- **产出**：`week3/llm_chat.py`
- **自查**：能说出**历史无限增长会导致什么问题**（token 变多、成本上升、超上下文限制）

#### D4 · 结构化输出 ★ Agent 的地基
- **学**：让模型输出 JSON；`response_format`；正则兜底
- **做**：从一段文本抽取信息成 JSON；故意触发一次解析失败并处理
- **产出**：`week3/llm_json.py`
- **自查**：**能稳定拿到可解析的 JSON**；知道模型会加解释文字导致 `json.loads` 失败
- **为什么重要**：**Tool Calling 本质就是"让模型吐结构化输出"**，D4 学不好第 4 周会卡

#### D5 · 参数实验
- **学**：`temperature` / `max_tokens` / `top_p`
- **做**：固定 prompt，改参数跑多次，记录差异到 CSV
- **产出**：`week3/param_exp.csv`
- **自查**：`temperature=0` 适合什么场景（要确定性、要 JSON）

#### D6 · 保存与整理
- **做**：所有脚本整理进 `week3/`；每个都能独立跑；写 README
- **产出**：`week3/README.md`
- **自查**：换台机器按 README 能跑起来

#### D7 · 收尾自查
- **自查**：
  - [ ] 能改变输入和参数，并**说出输出为什么变**
  - [ ] 能解释这个模型的**输入是什么、输出是什么**
  - [ ] 结果**都保存下来了**（不是只在终端看一眼）

---

### 第 4 周 · 三个方向体验

> **文档要求**：所有学生均体验 **Agent、LLM 部署、视频 Edge** 三个方向
> **考核重点**：能独立运行三个最小示例，理解每个方向的**基本工作链路与关键指标**
> **交付物**：`week4/` 三个可运行示例

> **文档说这周只是"体验"。别人走流程，你把它做扎实——第 5 周的模块、第 6 周的 Demo，本质都是这个的放大版。**

#### D1 · Agent 原理 + 定义工具
- **学**：Tool Calling 的流程（→ 4.11）；**模型只"决定调什么"，执行的是你的代码**
- **做**：定义 `calculator` 工具；写好 `TOOLS_SPEC`（工具说明）
- **产出**：`week4/agent_calc.py` 的工具定义部分
- **自查**：能说清**模型怎么"知道"有哪些工具可调**

#### D2 · Agent 主循环跑通 ★ 本周重点
- **做**：实现 `run_agent()` 主循环；跑通"需要算术的问题"和"闲聊问题"两种
- **产出**：完整的 `week4/agent_calc.py`
- **自查**：
  - [ ] 模型要求调工具时，**我的代码**去执行
  - [ ] `tool_call_id` 把结果和请求对应起来
  - [ ] 为什么要 `max_steps`（防无限循环）
  - [ ] **模型编造不存在的工具名会怎样**（KeyError → 这就是"失败重试"要解决的）
- **⚠️ 常见坑**：模型返回的 `arguments` 是 JSON 字符串，要 `json.loads`

#### D3 · LLM 部署（一）：跑起来
- **学**：Ollama / vLLM（→ 4.17）
- **做**：跑起来一个开源小模型；用 `nvidia-smi` 记录**显存占用**和加载时间
- **产出**：`week4/llm_serve.md`（显存 + 加载时间记录）
- **自查**：模型能响应；记录了数字
- **没有显卡/下载不动**：用 API 替代，但**指标要换**（不同 `max_tokens` 的耗时）

#### D4 · LLM 部署（二）：测指标
- **学**：**TTFT**（首 token 延迟）vs **吞吐量**（tokens/s）
- **做**：写计时脚本，测 TTFT 和生成速度
- **产出**：`week4/bench.py` + 指标记录
- **自查**：能说清 TTFT 和吞吐量的区别（一个影响"感觉快不快"，一个影响"多久说完"）

#### D5 · 视频 Edge（一）：YOLO 跑通
- **学**：`ultralytics` 用法（→ 4.15）
- **做**：加载模型 → 单张图片推理 → 取 `boxes.xyxy`/`cls`/`conf` → `r.plot()` 保存
- **产出**：`week4/video_fps.py` 的推理部分
- **自查**：能说出 `r.boxes.xyxy` 的形状是 `(N, 4)`
- **⚠️ 常见坑**：**权重下载超时**（GitHub）。本机已有 `C:\Users\omen\yolov8n.pt`，直接用

#### D6 · 视频 Edge（二）：测 FPS
- **做**：逐帧循环 + 计时；处理 200 帧；记录平均 FPS 和总耗时
- **产出**：FPS 记录
- **自查**：**为什么 FPS 是关键指标**（视频 25-30 FPS，跟不上就丢帧）
- **实测参考**：60 帧随机噪声 → 平均 12.4 FPS

#### D7 · 三个示例整合
- **做**：三个示例放进同一仓库，各自能独立运行；写 README
- **产出**：`week4/README.md`
- **自查**：
  - [ ] 三个示例**都能独立跑起来**
  - [ ] 能说出每个方向的**关键指标**（Agent=调用成功率；部署=显存/速度；Edge=FPS）
  - [ ] **能讲清 Agent 里"LLM 怎么决定调用工具"**

---

### 第 5 周 · 选方向 + 完成小模块

> **文档要求**：根据兴趣选择方向，进入真实项目，**只承担边界清晰的小模块**
> **考核重点**：模块能独立运行；输入输出明确；**代码可复现**；**能说明该模块在整体项目中的作用**
> **交付物**：`week5/` 一个可复现的独立模块

#### D1 · 定模块 + 写接口契约
- **选模块**（优先级从高到低）：
  - **推荐首选**：Agent 调用日志（门槛最低、产出明确、是方向 3 评测可观测的核心）
  - **次选**：数据库 Tool（顺带补 SQL）
  - 其他：任务评价脚本 / PDF 解析 Tool / 简单 RAG
- **做**：写接口契约（输入 / 输出 / 依赖 / 入口），**给别人看一眼确认边界**
- **产出**：`week5/接口契约.md`
- **自查**：能一句话说清"输入是什么、输出是什么"
- **⚠️ 关键**：契约没确认就写代码 → 容易做偏，返工

#### D2 · 实现（一）
- **做**：搭骨架，跑通"最小可用版本"（能读到输入、能写出输出）
- **产出**：能跑的第一版
- **自查**：**边做边 commit**，不要攒到最后

#### D3 · 实现（二）
- **做**：补完核心逻辑
- **产出**：功能完整版
- **自查**：自己拿几组数据试，边界情况（空输入、错误输入）会不会崩

#### D4 · 实现（三）+ 加统计
- **做**：补统计/汇总功能；处理异常情况
- **产出**：带统计的完整版
- **自查**：失败了会怎样（有没有错误提示，还是静默出错）

#### D5 · 可复现性测试 ★ 文档点名
- **做**（三种测试，全做）：
  1. **换环境跑**：新建 conda 环境，只按 README 装依赖
  2. **换目录跑**：把代码拷到别处
  3. **让别人跑**：同学只看 README，不看代码
- **产出**：一份"可复现性测试记录"
- **自查**：**这步经常暴露真问题**（路径写死、依赖没记录、少传文件）

#### D6 · 写 README
- **做**：依赖 / 怎么跑 / 输入输出 / **在整体项目中的作用**
- **产出**：`week5/README.md`
- **自查**：**"在整体项目中的作用"必须写**（文档考核重点点名）

#### D7 · 收尾自查
- **自查**：
  - [ ] 模块能**独立运行**（不依赖没提交的文件）
  - [ ] **输入输出明确**（写进 README）
  - [ ] **代码可复现**（别人按 README 能跑）
  - [ ] **我能说明它在整体项目中的作用**

---

### 第 6 周 · 正式考核

> **文档要求**：现场展示可运行 Demo、Git 代码仓库、5 页以内汇报、1 页个人总结
> **考核重点**：**是否真正做过、是否能解释、代码是否可运行**、是否具备后续持续参与能力
> **交付物**：四样材料

#### D1 · Demo 准备（一）
- **做**：把要演示的流程跑顺；**在考核用的机器上提前跑一遍**
- **产出**：能在目标机器上跑通的 Demo
- **自查**：代码能跑、数据齐、依赖都装了
- **⚠️ 常见坑**：不要现场下载模型/数据集（网络可能不通）

#### D2 · Demo 准备（二）
- **做**：准备演示脚本/命令清单；准备**"现场跑挂了怎么解释"的预案**
- **产出**：`week6/demo步骤.md`
- **自查**：别人按你的步骤能复现

#### D3 · 写 5 页汇报
- **结构**（严格 5 页以内）：
  - 第 1 页：我做了什么（6 周产出清单）
  - 第 2 页：系统怎么运行（架构图 + 入口命令 + 目录说明）
  - **第 3-4 页：遇到什么问题、怎么解决** ← **直接抄 `notes/log.md`**，挑 3-4 个
  - 第 5 页：还有什么没完成（**诚实写**）
- **产出**：`week6/汇报.md` 或 ppt
- **自查**：每个问题都写成"现象 → 排查 → 根因 → 解法"

#### D4 · 写 1 页个人总结
- **要回答三点**：
  - 最感兴趣的方向（为什么）
  - **每周预计可投入时间**（★ 这是筛选维度，诚实写）
  - 是否愿意长期参与
- **产出**：`week6/个人总结.md`
- **自查**：想清楚再写，这三个问题会影响分流

#### D5 · 演练（一）
- **做**：找人听你讲一遍，限时
- **自查**：**重点练"解释"部分**（文档反复强调"是否能解释"）

#### D6 · 演练（二）+ 仓库检查
- **做**：
  - 再演练一遍
  - 检查 Git 仓库：`git log --oneline` 看提交历史够不够
  - **确认没有 `.env`、没有大文件**
  - 查历史里有没有误提交的密钥：`git log --all --full-history -- .env`
- **产出**：干净的仓库
- **自查**：README 能让陌生人跑起来

#### D7 · 正式考核
- **做**：现场演示 + 汇报 + 交材料
- **心态**：
  - **"还有什么没完成"诚实写，不扣分；假装做完才扣分**
  - 被问倒了就说"这个我还没搞清，我回去查" —— 比瞎编好

---

### 观察期之后（第 7 周起）→ 完整版见 `ROADMAP-5months.md`

**先说清楚为什么要单独一份文件**：

观察期只有 6 周，但**你的 deadline 是 2027 年 3 月**（暑期实习招聘季开启）。
**准备期是 2026.10 → 2027.02，约 5 个月。这 6 周只是第 1 个月。**

所以完整路线图单独放在 **`ROADMAP-5months.md`**（用你自己的对标数据算的，不是通用建议）。
这里只留最关键的几条，防止你在手册里看不到方向。

#### ★ 两条最反直觉的结论

**① Agent 是差异化，不是入场券。**

| 项 | 对标出现率（n=32 大厂技术实习岗） | 你的状态 |
|---|---|---|
| **数据结构与算法** | **46.9%**（与 Python 并列第一） | ❌ **完全没碰** |
| 大模型 / LLM | 28.1% | ⏳ 第 3 周学 |
| **Agent / 智能体** | **18.8%** | ⏳ 第 4 周学 |

> **光会 Agent 拿不到 offer；不会 DSA，一半的岗位直接没戏。**
>
> **所以：DSA 不能"等观察期结束再开始"。** 从第 3 周起，每周 3 道题 ——
> 强度小到不会挤垮观察期，但能让你多出 4 周。
> → 手册 4.13 节有 DSA 的范围说明（"熟悉常见数据结构"就够，不用刷难题）

**② 投递不要等 3 月 —— 学期中实习是一条独立的路。**

你之前发现过：「学期中到不了岗（有课）」。**这条对，但它只讲了一半：**

```
到岗窗口：寒假 4 周 ← 能去！      暑假 8 周 ← 能去
          学期中 4-5 天/周 ← 去不了（有课）
投递窗口：任何时候都能投
```

**中小厂招实习的逻辑（你自己的调研原话）**：

> 大厂是**筛未来的正式员工**，看学校、看潜力。
> 中小厂是**要人来干活**，所以看：**你能不能每周到岗、交给你的活你能不能做完。**

**推论：对中小厂，「你能到岗」的权重高于「你学校好不好」。**
而你在黄埔住 —— 琶洲实验室（黄埔科学城）有 **300-500 元/日、明确本科可投** 的后端实习岗。

> **投递可以现在就开始**，目标广州本地、寒假能到岗的岗位。
> 哪怕小厂、哪怕只干 4 周 —— **"有一段真实实习"和"没有"，在 3 月的简历上是两个世界。**
> ⚠️ 前提：先得**有能写进简历的东西**（见下面第 3 条）。

#### ③ 285 小时怎么分（按每周 15 小时 × 19 周算）

| 项 | 小时 | 交付物 |
|---|---|---|
| **数据结构与算法** | 100 | 常见结构能独立实现 + 约 80~100 题 |
| **一个能讲 15 分钟的项目** | 90 | 有 README、讲得出"为什么这么设计" |
| Python 工程 + 真的用 AI 工具 | 40 | 见 `ROADMAP-5months.md` 阶段 3 |
| SQL | 25 | 能建表、查询、加索引 |
| 简历 + 投递准备 | 30 | **简历初稿硬 deadline：2027.02 中** |

**DSA + 项目 = 67%。这两样是 offer 的主体，其他都是配菜。**

#### 从今天起，只加一件事

**观察期继续按第 5 章走，同时每周加 3 道 DSA 题，记进 `notes/dsa.md`。**

**别的都别加。** 完整的 5 个月安排、每月检查点、三种失败方式，都在 `ROADMAP-5months.md`。

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
| `RuntimeError: a Tensor with 784 elements cannot be converted to Scalar` | **括号位置错了**：`argmax` 作用在输入图像上，而不是模型输出上 | `model(x.unsqueeze(0)).argmax(dim=1).item()` —— 右括号要在 `x` 后面就闭合 |

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
| `a Tensor with N elements cannot be converted to Scalar` | 括号位置错，`argmax`/`item` 被套进了 `model()` 里 | 写成 `out = model(x); pred = out.argmax(dim=1).item()` |
| `RuntimeError: element 0 of tensors does not require grad` | 调了 `backward()` 但计算图已断（或删了 `requires_grad`） | 检查 `requires_grad=True`；`backward()` 和 `zero_()` 要配套 |

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
| **`意外的标记"PS"` / `UnexpectedToken`** | **把提示符一起复制进终端了**。`PS E:\agent>` 是终端自己显示的，不是命令的一部分 | 只复制命令本身，从 `python` / `git` 这类词开始 |
| 命令退出码 1 但其实成功了 | PowerShell 把 stderr 输出当错误 | 看实际输出内容，别只看退出码 |
| `ssh -T git@github.com` 退出码 1 | **这是正常的**，成功也是 1 | 看输出有没有 `Hi 用户名!` |
| 中文命令输出乱码 | 控制台代码页 | `chcp 65001` |

### 6.9 看提示符就知道哪里错了

终端最左边那串东西不是命令，是**状态显示**：

```
(agent)  PS  E:\agent>
   ↑      ↑      ↑
 哪个环境  什么shell  当前目录
```

| 看到 | 意思 | 怎么办 |
|---|---|---|
| `(agent)` | ✅ 环境对 | — |
| `(base)` / 没有括号 | ❌ 环境不对 | `conda activate agent` |
| `E:\agent>` | ✅ 目录对 | — |
| `C:\Users\omen>` | ❌ 目录不对 | `cd E:\agent` |

**两个最常见的粘贴事故：**

1. **把提示符一起复制了** → `意外的标记"PS"`。只复制从命令第一个词开始的部分。
2. **文档里的占位符没替换** → 例如 `git remote add origin git@github.com:你的用户名/agent.git`
   里的 `你的用户名`。`git remote -v` 能查出这个。

### 6.10 LLM / API 类（Week3 起会用到）

**先记住一句话**：API 报错里**最有用的是 `status_code` 和 `body` 里的 `message`**，
不要只看 Python 抛出来的那句话。

**在代码里这样看：**

```python
from openai import APIError, AuthenticationError, RateLimitError, APIConnectionError

try:
    resp = client.chat.completions.create(model=..., messages=[...])
except AuthenticationError as e:
    #          ↑401：Key 错了 / 没读到
    print("Key 有问题：", e)
except RateLimitError as e:
    #          ↑429：太频繁 / 没额度
    print("被限流或余额不足：", e)
except APIConnectionError as e:
    #          ↑连不上：base_url 写错 / 没网 / 需要代理
    print("连不上服务器：", e)
except APIError as e:
    #          ↑其他：看 status_code
    print("API 报错", e.status_code, e.message)
```

| 报错 / 现象 | 根因 | 解法 |
|---|---|---|
| `AuthenticationError` (401) | Key 没读到 / 填错 / 多了空格 | `print(repr(os.getenv("API_KEY")))` 看**真实值**；`load_dotenv()` 要在 `os.getenv` **之前** |
| `APIConnectionError` | `base_url` 写错 / 少了 `/v1` / 网络不通 | 打印 `os.getenv("BASE_URL")`；国内厂商**大多要带 `/v1`** |
| `NotFoundError` (404) | 模型名写错，**或用了已失效的老模型名** | 模型名要一字不差。★ `deepseek-chat` / `deepseek-reasoner` **已失效**，现在用 `deepseek-flash` |
| `RateLimitError` (429) | 请求太密 / 余额为 0 | 加 `time.sleep()`；去后台看余额 |
| `BadRequestError` (400) `response_format` | 该模型**不支持** `json_object` | 去掉这个参数，用正则兜底（手册 4.10） |
| 模型答非所问 / 不调工具 | `description` 写得太含糊 | 手册 4.11：**模型就是靠描述判断该不该调**，把「什么时候用」写进去 |
| 报错 `KeyError: '工具名'` | **模型编造了不存在的工具名** | 调之前先 `if name not in TOOLS_IMPL: 返回错误提示`（手册 4.11 五个问题之一） |
| `content` 是 `None` 但没报错 | 这一轮模型要**调工具**，正文就是空的 | 判断 `if msg.tool_calls:`，别直接 `print(msg.content)` |
| `json.loads(...)` 报 `JSONDecodeError` | ①模型在 JSON 前后加了说明文字 ②**`max_tokens` 太小，正文是空字符串** | 先 `print(repr(raw))` 确认是哪种：空字符串 → 加大 `max_tokens` 或关掉思考；有文字 → 用正则兜底 |
| JSON 输出「被截断」/ 正文是空的 | **`max_tokens` 把思考 token 算在内**，预算被思考吃光 | 关掉思考（`extra_body={"thinking":{"type":"disabled"}}`）或把 `max_tokens` 调到 500+ |
| `.env` 被提交上去了 | 忘了 `.gitignore` | 见 3.7 节：**Key 一旦进了 git 历史，删 commit 也删不干净**——立刻去厂商后台吊销重发 |
| 账单突然变多 | 历史无限增长 / 没设 `max_tokens` | 手册 4.10「上下文管理」：只留最近 N 轮 |

> **`.env` 的四个自检**（每次动完配置跑一遍）：
> ```powershell
> cd E:\agent
> Test-Path .env                      # True 说明文件在
> git check-ignore -v .env            # 必须输出一行（说明被忽略）；没输出 = 危险
> git status --short                  # 确认列表里【没有】.env
> ```

---

## 7. 卡住时的自救顺序

**按顺序做，别跳：**

```
1. 读报错最后一行        ← 最关键的信息在这里，不是最上面那堆
2. 用 type() / print() 看变量到底是什么
   print(type(x), x.shape if hasattr(x,'shape') else x)
3. 查本文件第 6 节
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

### ★ 怎么分清「没提交」和「被故意忽略」

**这两个是完全不同的状态，但 `git status` 只显示前一个**，所以很容易误判成"我有东西没提交"。

| 状态 | 例子 | `git status` 里 | 该做什么 |
|---|---|---|---|
| **没提交** | 你新写的脚本 | `??`（新文件）或 `M`（改过） | **要提交** |
| **被故意忽略** | `.env`、`data.csv`、`model.pth` | **完全不显示** | **正常，别管** |

**一条命令看清全部**（`--ignored` 会把被忽略的也列出来）：

```powershell
git status --short --ignored
```

输出里 `!!` 开头的就是**被故意忽略**的：

```
 M HANDBOOK.md              ← 改过，要提交
?? week4/new.py             ← 新文件，要提交
!! .env                     ← 被忽略（正常，密钥不该提交）
!! week2/model.pth          ← 被忽略（正常，大文件）
```

**两条确认命令：**

```powershell
# 1. 我对不对得上远端？（两个都是 0 就是同步了）
git fetch origin
git rev-list --count origin/main..HEAD     # 本地领先几个
git rev-list --count HEAD..origin/main     # 本地落后几个

# 2. 某个文件为什么没出现在 status 里？
git check-ignore -v week1/data.csv
#  → 输出 ".gitignore:29:*.csv  week1/data.csv"
#     读法：被 .gitignore 的 *.csv 规则挡住了（行号会变，不用记）
#     这是【有意的】，不是忘了提交
#  → 没有任何输出 = 它没被忽略，那它应该出现在 status 里
```

**为什么有些东西被故意排除**（这不是忘了）：

| 文件 | 为什么排除 | 那别人怎么跑起来？ |
|---|---|---|
| `.env` | **密钥，泄露会被盗刷** | 从 `.env.example` 复制一份填自己的 |
| `week2/model.pth` | 400 KB 二进制，换机器能重训 | 跑 `LOOP.py` 重新训练（约 2 分钟） |
| `week1/data.csv` / `summary.csv` | 数据不该进 git（`*.csv`） | 跑 `make_data.py` 重新生成 |
| `week2/data/` | MNIST 约 60 MB | 脚本里 `download=True` 会自动下 |

> **原则：提交「生成数据的代码」，不提交「数据本身」。**
> 这样仓库小、别人 clone 下来按 README 跑一遍就能重建。
>
> ⚠️ **一个副作用要知道**：`*.csv` 被全局忽略了，所以**你以后如果写了该提交的 csv**（比如一个小的配置表），
> 它会静默不进 git。发现"文件明明在却提交不上"时，用上面的 `git check-ignore -v` 查。
> 真要强制提交：`git add -f 文件名`（**别对 `.env` 用这个**）。

---

## 9. 三个月后回看这三条

1. **面试必问「你遇到最难的问题是什么，怎么解决的」** → 答案在 `notes/log.md`
2. **简历要有东西可写** → 靠 `week1/` ~ `week6/` 的产出
3. **"持续投入"要有证据** → 靠 `git log` 的提交历史

**这三样都只能靠"每天做一点"攒出来，没有捷径。**

---

*最后更新：2026-09-28*
