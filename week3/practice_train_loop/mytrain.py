"""训练循环填空练习 —— 把 # 【?】 的地方补完整。

规则（重要）：
  1. 不要打开 train.py 对答案，先自己填
  2. 填不出来就【空着】，别猜 —— 空着的地方就是你真实的盲区
  3. 每填完一处就存盘跑一次：python mytrain.py
     ★ 语法错会立刻报出来，这比一次性全填完再调更省时间

已经写好的部分不用改（数据加载、模型定义这些是模板，不考）。
"""
import sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import TensorDataset, DataLoader

# ============================================================
# 下面这段是【给你准备好的模板，不用动】
# 为了不下载 MNIST、几秒就能跑完，这里用合成数据代替。
# 任务：把 784 维的向量分成 10 类（重点看循环，不看效果）。
# ============================================================
torch.manual_seed(0)
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

N_TRAIN, N_TEST, DIM, N_CLS = 4000, 1000, 784, 10
Xtr = torch.randn(N_TRAIN, DIM)
ytr = torch.randint(0, N_CLS, (N_TRAIN,))
Xte = torch.randn(N_TEST, DIM)
yte = torch.randint(0, N_CLS, (N_TEST,))

# 让数据里存在可学的规律：某一类的前 10 个特征略偏大
for c in range(N_CLS):
    Xtr[ytr == c, c * 10:(c + 1) * 10] += 0.4
    Xte[yte == c, c * 10:(c + 1) * 10] += 0.4

train_ld = DataLoader(TensorDataset(Xtr, ytr), batch_size=64, shuffle=True)
test_ld = DataLoader(TensorDataset(Xte, yte), batch_size=256, shuffle=False)


class Net(nn.Module):
    def __init__(self):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(DIM, 128), nn.ReLU(),
            nn.Linear(128, N_CLS),
        )

    def forward(self, x):
        return self.net(x)


model = Net().to(device)
criterion = nn.CrossEntropyLoss()
optimizer = optim.Adam(model.parameters(), lr=1e-3)


# ============================================================
# 评估函数 —— 模板不用动，但里面有两处【?】
# ============================================================
def evaluate():
    # 【? 第 1 处】评估前要把模型切到哪个模式？写一行（就写在这行注释下面）

    correct = total = 0

    # 【? 第 2 处】评估时不需要梯度，用哪个上下文管理器包住下面的循环？
    #             写一行 with 语句（下面的 for 已经缩进好了，你只要补这一行 + 让 for 缩进进去）

    for x, y in test_ld:
        x, y = x.to(device), y.to(device)
        pred = model(x).argmax(dim=1)
        correct += (pred == y).sum().item()
        total += y.size(0)
    return correct / total


# ============================================================
# ★★★ 训练循环 —— 这就是你要填的核心 ★★★
# ============================================================
loss = None
#   ↑ 给你预置的，不用管。它只是让下面的 print 在你还填空时也能跑。

for epoch in range(6):
    # 【? 第 3 处】训练前要把模型切到哪个模式？写一行

    for x, y in train_ld:
        x, y = x.to(device), y.to(device)

        # 【? 第 4 处】下面这 5 步，按正确顺序补齐（每步一行）
        #            写完问自己：「为什么必须是这个顺序？」
        #
        #            提示：想让参数变好 → 需要什么？ → 那个东西又从哪来？
        #                  为什么第一步是"清空"而不是别的？

        # 第 1 步：

        # 第 2 步：

        # 第 3 步：

        # 第 4 步：

        # 第 5 步：

    acc = evaluate()
    loss_txt = "—" if loss is None else f"{loss.item():.4f}"
    #   ↑ "—" 表示"还没有 loss" —— 说明你第 3 步还没填
    print(f"epoch {epoch + 1}  loss={loss_txt}  test_acc={acc:.4f}")
