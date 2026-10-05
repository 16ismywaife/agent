# Week2 · Git、Linux 与深度学习基础

MNIST 手写数字分类。完整链路：**自动求导 → 数据加载 → 训练 → 保存模型 → 加载推理**。

---

## 依赖

```
Python 3.11
torch 2.11.0+cu128
torchvision 0.26.0+cu128
```

安装（显卡是 RTX 5060，必须用 CUDA 12.8 的构建，否则会用 CPU 跑）：

```bash
pip install torch==2.11.0 torchvision==0.26.0 --index-url https://download.pytorch.org/whl/cu128
```

验证：

```python
import torch
print(torch.__version__)          # 2.11.0+cu128
print(torch.cuda.is_available())  # True
print(torch.cuda.get_device_name(0))  # NVIDIA GeForce RTX 5060 Laptop GPU
```

---

## 文件说明

| 文件 | 作用 |
|---|---|
| `tensor & 自动求导.py` | **练习**：自动求导基础 + 用梯度下降拟合 `y = 2x + 1` |
| `dataset & dataloader.py` | **练习**：Dataset / DataLoader 用法 |
| **`LOOP.py`** | **入口程序**：训练 MNIST 并保存模型 |
| `loadtest.py` | 加载模型 → 推理一张图 → 对比预测和真实 |
| `model.pth` | 训练好的模型参数（约 400 KB，**不进 git**） |
| `data/` | MNIST 数据集（约 60 MB，**不进 git**） |

> **`model.pth` 和 `data/` 都被 `.gitignore` 排除。**
> 这是有意的：**不提交数据，提交生成数据的代码。**
> 别人拿到仓库后，按下面「怎么跑」执行一遍就能重建它们。

---

## 怎么跑

```bash
# 1. 训练（第一次会自动下载 MNIST 数据集，约 18 秒）
python LOOP.py

# 2. 加载模型并推理
python loadtest.py
```

**期望输出：**

`LOOP.py`（实测，RTX 5060 全量 60000 张 × 3 epoch 约 **110 秒**）：
```
cuda
Epoch 1: test Accuracy: 0.9592
Epoch 2: test Accuracy: 0.9707
Epoch 3: test Accuracy: 0.9736
模型已保存: model.pth
```

`loadtest.py`：
```
pred: 7, label: 7
```

**`pred` 和 `label` 一样就说明模型保存和加载都成功。**

---

## 输出

| 输出 | 说明 |
|---|---|
| `model.pth` | 模型参数（`state_dict`），约 **400 KB** |
| 终端 | 每轮的测试准确率；加载后的预测结果 |

---

## 代码结构

### `LOOP.py`（入口程序）

```python
class Net(nn.Module):          # 模型定义
    def __init__(self):        # 结构：Flatten → Linear(784,128) → ReLU → Linear(128,10)
    def forward(self, x):      # 前向计算

def evaluate():                # 在测试集上算准确率

for epoch in range(3):         # ★ 训练循环（5 步）
    model.train()
    for x, y in train_loader:
        optimizer.zero_grad()  # ① 清空上轮梯度
        pred = model(x)        # ② 前向
        loss = criterion(pred, y)  # ③ 算损失
        loss.backward()        # ④ 反向求梯度
        optimizer.step()       # ⑤ 更新参数

torch.save(model.state_dict(), "model.pth")   # 保存参数
```

### `loadtest.py`

**关键点：必须重新定义 `Net` 类，而且和训练时一模一样。**

因为 `state_dict()` **只保存参数，不保存结构** —— 加载时要先有结构，再把参数灌进去。

```python
model = Net()                                    # ① 先建结构
model.load_state_dict(torch.load("model.pth"))   # ② 再灌参数
model.eval()                                     # ③ 切评估模式
```

---

## 关键概念

### 训练集 / 测试集 / 验证集

| | 作用 | 能不能用来调参数 |
|---|---|---|
| **训练集** | 更新模型参数 | ✅ 只能用它 |
| **验证集** | 调超参数（学习率、层数等） | ❌ 不更新参数，但会**间接影响选择** |
| **测试集** | 最终评估模型好坏 | ❌ **绝对不能碰** |

**为什么不能拿测试集训练**：那样模型会"见过考题"，测出来的分数是虚高的，**不能反映真实能力**。就像考试前把答案背了，考 100 分也不代表学会了。

本项目用了 60000 张训练 + 10000 张测试。

### Loss 是什么

**Loss（损失）= 模型预测和真实答案差多少。**

本项目用 `nn.CrossEntropyLoss()`（交叉熵），分类任务的标准损失函数。

- **loss 越小 = 预测越接近真实**
- 训练就是**不断调参数让 loss 变小**
- **它内部已经包含 softmax**，所以模型最后一层不要再写 softmax

### 为什么需要反向传播

> 训练就是不断调参数让 Loss 变小。要调参数，就得知道**每个参数对 Loss 的影响有多大**——也就是梯度。
>
> 但模型有几十万到几十亿个参数，**不可能手算每个参数的导数**。
>
> 反向传播用链式法则，**从 Loss 倒着走一遍计算图，一次就同时算出所有参数的梯度**。
>
> **没有它，参数就只能瞎猜。**

**实测证据**（`tensor & 自动求导.py` 那个练习）：

| 做法 | 200 轮后的结果 |
|---|---|
| 有 `loss.backward()` | `w=2.0000, b=1.0000`（正确收敛） |
| **删掉 `loss.backward()`** | **`w=0.0000, b=0.0000`（参数一点没动）** |

### 梯度会累积

```python
x = torch.tensor([2.0], requires_grad=True)
for i in range(3):
    y = x**2
    y.backward()
    print(x.grad)
# 第1次: 4.0    正确
# 第2次: 8.0    ← 变成 8 了！
# 第3次: 12.0   ← 又加了 4
```

**`backward()` 是累加梯度，不是覆盖。** 所以每次都要 `optimizer.zero_grad()` 清零。

**这就是训练循环第 ① 步存在的原因。**

---

## 已知限制

- **网络是简单全连接**，没用卷积（CNN）。**实测准确率 97.36%**；换成 CNN 能到 99%+
- **只用 3 个 epoch**，没有调学习率、没有数据增强
- **没有验证集**，只有训练/测试划分
- **训练耗时约 110 秒**（RTX 5060，全量 60000 张 × 3 epoch）
- **`model.pth` 不进 git**，换机器演示时要重新训练（约 2 分钟）
- 文件名带空格和 `&`，命令行里需要加引号（如 `python "dataset & dataloader.py"`）

---

## 过程中踩过的坑

记录在仓库根目录的 `HANDBOOK.md` 第 6 章，主要有：

| 现象 | 根因 |
|---|---|
| `RuntimeError: a Tensor with 784 elements cannot be converted to Scalar` | 括号位置错了：`model(x.argmax())` 应该是 `model(x).argmax()` |
| 梯度越跑越大 | 忘了 `optimizer.zero_grad()` |
| 参数完全不更新 | 忘了 `loss.backward()` |
| 测试集也 `shuffle=True` | 测试集不需要打乱 |
