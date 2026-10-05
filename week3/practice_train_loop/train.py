"""训练循环 —— 答案版（你的 mytrain.py 填完后跟这个对）

★ 读法：不要只看"写什么"，看每一行上面那句「为什么必须在这里」。
   顺序不是规定，是被因果逼出来的。

     想让参数变好  -> 需要梯度          -> 所以 step 在 backward 后面
     梯度从哪来    -> 从 loss 反推       -> 所以 backward 在算 loss 后面
     loss 需要什么 -> 预测值             -> 所以 model(x) 排最前
     为什么先清零  -> 梯度是【累加】的   -> 所以 zero_grad 必须最先做
"""
import sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import TensorDataset, DataLoader

# ---------- 模板部分：数据 / 模型 / 损失 / 优化器 ----------
# 用合成数据代替 MNIST，几秒就能跑完，重点看循环结构。
torch.manual_seed(0)
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

N_TRAIN, N_TEST, DIM, N_CLS = 4000, 1000, 784, 10
Xtr = torch.randn(N_TRAIN, DIM)
ytr = torch.randint(0, N_CLS, (N_TRAIN,))
Xte = torch.randn(N_TEST, DIM)
yte = torch.randint(0, N_CLS, (N_TEST,))
for c in range(N_CLS):
    Xtr[ytr == c, c * 10:(c + 1) * 10] += 0.4
    Xte[yte == c, c * 10:(c + 1) * 10] += 0.4
#   ↑ 0.4 是标定出来的：信号再强一点，模型一步就学会了，看不出训练过程；
#     再弱一点，精度上不去，也看不出差异。要的就是"学得动但没学满"。

train_ld = DataLoader(TensorDataset(Xtr, ytr), batch_size=64, shuffle=True)
test_ld = DataLoader(TensorDataset(Xte, yte), batch_size=256, shuffle=False)


class Net(nn.Module):
    def __init__(self):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(DIM, 128), nn.ReLU(),
            # <<DROPOUT>>
            #   ↑ 这是给 breakdown.py 用的占位符：实验 7/8 会把它换成真的 nn.Dropout(0.6)，
            #     用来演示 model.train() / model.eval() 到底在管什么。
            #     本模型没有 Dropout / BatchNorm，所以这两个模式开关在这里【看不出差别】——
            #     这不是它们不重要，而是"这个网络用不到"。
            nn.Linear(128, N_CLS),
        )

    def forward(self, x):
        return self.net(x)


model = Net().to(device)
criterion = nn.CrossEntropyLoss()
optimizer = optim.Adam(model.parameters(), lr=1e-3)


# ---------- 评估函数 ----------
def evaluate():
    model.eval()
    #   ↑ 切到【评估模式】。影响 Dropout / BatchNorm —— 它们在训练和评估时行为不同。
    #     ★ 切的是"模式"，不是"要不要梯度"，这两件事是分开的。

    correct = total = 0
    with torch.no_grad():
        #   ↑ 关掉计算图。为了【省显存、加速】，不是为了结果正确。
        #     忘了写不会算错，但会白建一张巨大的图。
        for x, y in test_ld:
            x, y = x.to(device), y.to(device)
            pred = model(x).argmax(dim=1)
            correct += (pred == y).sum().item()
            total += y.size(0)
    return correct / total


# ============================================================
# ★ 训练循环 —— 4 层结构，别只记最里面那层
# ============================================================
for epoch in range(6):
    #   ↑ 第 1 层：外层循环 —— 整个数据集过 6 遍。管"过几遍"。
    #     实验发现：用 SGD 时精度大约在第 4 轮就爬平了，所以 6 轮足够看出趋势。

    model.train()
    #   ↑ 第 2 层：切回【训练模式】。和 evaluate() 里的 model.eval() 配对。
    #     ★ 容易漏：忘了写它，评估模式会"粘"到下一轮训练里。

    for x, y in train_ld:
        #   ↑ 第 3 层：一批一批地取。MNIST(batch=64) 一轮是 938 批。
        x, y = x.to(device), y.to(device)
        #   ↑ 容易漏：数据要搬到和模型同一个设备，否则报设备不一致。

        #   ↓ 第 4 层：★ 你背的 5 步在这里，处理的是【一批】，不是一轮。

        optimizer.zero_grad()
        #   ① 清空上一轮的梯度。
        #      为什么必须最先？因为 backward() 是【累加】不是覆盖。
        #      不清零 = 这轮的梯度 + 上轮的梯度 —— 越跑越偏。

        out = model(x)
        #   ② 前向：算预测。触发 Net.forward()。
        #      为什么在最前？因为后面两步都要用它的结果。

        loss = criterion(out, y)
        #   ③ 算损失：预测和真实差多少。loss 是一个标量（一个数）。
        #      为什么在 backward 前？因为梯度是"loss 对参数的导数"，
        #      没有 loss 就没有可求导的东西。

        loss.backward()
        #   ④ 反向：沿计算图倒着走，一次算出所有参数的梯度，存进 .grad。
        #      为什么在 step 前？因为 step 要读 .grad 才知道往哪走。

        optimizer.step()
        #   ⑤ 更新参数：按 .grad 走一小步。
        #      为什么最后？因为前面四步都是在为"这一步该往哪走"做准备。

    acc = evaluate()
    #   ↑ 每轮结束评估一次。注意它在【内层循环外面】——
    #     评估是"这轮学得咋样"，不是"这批学得咋样"。
    print(f"epoch {epoch + 1}  test_acc={acc:.4f}")
