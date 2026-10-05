"""诊断：为什么 pred = model(x).argmax(dim=1) 会报错。"""
import sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
import torch
import torch.nn as nn

torch.manual_seed(0)
x = torch.randn(8, 784)
y = torch.randint(0, 10, (8,))
model = nn.Sequential(nn.Linear(784, 128), nn.ReLU(), nn.Linear(128, 10))

out = model(x)
pred = out.argmax(dim=1)

print("=== 你写的 pred 是什么 ===")
print("  model(x)              shape =", tuple(out.shape), " dtype =", out.dtype)
print("                         ↑ 每个样本的 10 个类别分数（还没选）")
print()
print("  model(x).argmax(dim=1) shape =", tuple(pred.shape), " dtype =", pred.dtype)
print("                         ↑ 只剩一个类别编号，10 个分数被丢掉了")
print()
print("  前 3 个样本的原始分数：")
print("   ", out[:3].detach().numpy().round(2).tolist())
print("  取 argmax 之后：", pred[:3].tolist())
print()

print("=== 为什么 CrossEntropyLoss 不接受它 ===")
crit = nn.CrossEntropyLoss()
print("  CrossEntropyLoss 要求：")
print("    输入 out  : 浮点 logits，shape (批, 类别数)  ← 要【分数】")
print("    目标 y    : Long 标签，shape (批,)            ← 要【编号】")
print()
print("  你现在传的 pred 是 Long 且 shape (批,)，")
print("  它【看起来像标签、位置却是输入】→ 于是报：")
try:
    crit(pred, y)
except Exception as e:
    print("   ", type(e).__name__, "-", e)
print()

print("=== 正确写法 ===")
loss = crit(out, y)
print("  loss = criterion(model(x), y) =", round(loss.item(), 4))
print("          ↑ 传原始分数，不传 argmax 结果")
print()
print("=== 一句话区分 ===")
print("  argmax 只用在【评估准确率】那一步：")
print("     correct += (logits.argmax(dim=1) == y).sum()")
print("  训练时算 loss【绝对不能】先 argmax —— loss 要的是分数，不是编号。")
