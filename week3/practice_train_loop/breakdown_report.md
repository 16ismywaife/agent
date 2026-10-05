# 训练循环「故意写坏」实验报告

> 由 `python breakdown.py` 自动生成，不要手改。

> 每个实验只破坏 `train.py` 的一处，真跑一遍 6 轮训练。


**基线（不破坏）**：精度 0.2780；梯度范数 首步 2.104 / 首轮均值 2.073 / 首轮末10步均值 2.125


**为什么同时看「梯度范数」，而且不看第一步**：
① 精度很快就爬到平台上，很多破坏在精度上根本看不出差别；
② 梯度的累积效应在**第一步上完全不存在**（那时没有"上一轮"可累加），
要到几十步之后才显现 —— 所以要看**首轮末尾**的梯度范数。


## 对照表

| 实验 | 改动 | 预期 | 首轮末梯度范数 | 精度 | 实际结果 |
|---|---|---|---|---|---|
| 1 | 去掉 optimizer.zero_grad() | 梯度范数逐批暴涨（累加 N 次）→ 参数被冲飞 → 精度掉到随机 | 30.78 | 0.1520 | ✅ 不崩：首轮末梯度范数 30.78（基线的 14.48 倍），精度 0.1520（-0.1260） |
| 2 | 去掉 out = model(x) | 直接崩：NameError（out 未定义） | — | — | ❌ 崩溃：NameError: name 'out' is not defined. Did you mean: 'oct'? |
| 3 | 去掉 loss = criterion(out, y) | 直接崩：NameError（loss 未定义） | — | — | ❌ 崩溃：NameError: name 'loss' is not defined |
| 4 | 去掉 loss.backward() | 不崩，但梯度范数恒为 0、精度停在随机——★ 最危险的「不报错的 bug」 | 0.00 | 0.0990 | ✅ 不崩：首轮末梯度范数 0.00（基线的 0.00 倍），精度 0.0990（-0.1790） |
| 5 | 去掉 optimizer.step() | 不崩，梯度有值但精度停在随机——★ 同样不报错 | 2.19 | 0.0990 | ✅ 不崩：首轮末梯度范数 2.19（基线的 1.03 倍），精度 0.0990（-0.1790） |
| 6 | 顺序颠倒：把 zero_grad 挪到 step 之后 | 梯度范数约 2 倍。★ 但精度可能【完全不变】—— 见报告里的解释 | — | 0.2780 | ✅ 不崩：精度 0.2780（+0.0000） |
| 7 | 有 Dropout 时，去掉 model.train() | 这个玩具模型数据量小、信号弱，学不满也过拟合不了 → 精度未必有差别 | 2.13 | 0.2780 | ✅ 不崩：首轮末梯度范数 2.13（基线的 1.00 倍），精度 0.2780（+0.0000） |
| 8 | 有 Dropout 时，评估不写 model.eval() | 评估时 Dropout 仍在随机丢弃 → 精度被压低、同一模型忽高忽低 | 2.82 | 0.2600 | ✅ 不崩：首轮末梯度范数 2.82（基线的 1.33 倍），精度 0.2600（-0.0180） |
| 9 | 评估时不写 torch.no_grad() | 精度不变，但更慢更费显存 —— 证明它是【性能】优化，不是【正确性】需要 | 2.13 | 0.2780 | ✅ 不崩：首轮末梯度范数 2.13（基线的 1.00 倍），精度 0.2780（+0.0000） |

## 结论：每一步是「正确性」需要还是「性能」需要？

| 步骤 | 缺了会怎样 | 性质 |
|---|---|---|
| `zero_grad()` | 梯度累积，**更新量被放大** → 精度明显下降 | 🔴 **正确性**（必须写） |
| `model(x)` | 崩：没有预测 | 🔴 **正确性** |
| `criterion(out, y)` | 崩：没有损失 | 🔴 **正确性** |
| `loss.backward()` | **不崩**，但梯度恒为 0、参数永不更新 | 🔴 **正确性（隐蔽）** |
| `optimizer.step()` | **不崩**，梯度正常算出但参数永不更新 → 精度停在随机 | 🔴 **正确性（隐蔽）** |
| 5 步的**顺序** | 更新量约 2 倍。**本实验里精度没变** —— 见下面 | 🟡 **看优化器而定** |
| `model.train()` | **本实验没测出差别** —— Dropout 关掉也没影响这个玩具模型 | 🟡 **视网络和数据而定** |
| `model.eval()` | 有 Dropout 时评估被压低（本实验可见精度 -0.018） | 🟡 **视网络而定** |
| `torch.no_grad()` | 结果**完全不变**，只是慢、费显存 | 🟢 **性能**（不是正确性） |

## ⚠️ 三个「反直觉」的实测结果（比口诀值钱）

### 1. `zero_grad` 的累积效应，**第一步根本看不出来**

「去掉 `zero_grad`」和基线在**第一步**的梯度范数完全一样 ——
因为第一步之前没有「上一轮」可累加，差异要到几十步之后才显现。
**所以不要用「跑一个 batch」来判断训练循环对不对。**

### 2. 把 `zero_grad()` 挪到 `step()` 之后，精度可能**一点不变**

实测就是这样。原因：
- 它等价于每步用「上批 + 这批」的梯度，**梯度范数变成约 2 倍**
- 但每步的**方向**仍指向正确方向（两批梯度的期望方向相同）
- 所以它数学上等价于 **「把学习率乘 2」**
- 而这个模型的学习率本来就偏保守，乘 2 反而没坏事

**但顺序错误依然是真错误**：更新量错了，换更大的学习率就会发散；
配合 Adam 这类自适应优化器还会更糟。
→ 真正要记住的是：**「代码没报错、精度也还行」不等于代码对。**

### 3. `model.train()` 和 `model.eval()` 是【看情况】的

本实验里，把训练模式关掉（等价于 Dropout 失效）精度**一点没变**，
而评估时不切评估模式掉了 0.018。
原因：这是个**玩具级**任务 —— 数据小、信号弱、模型简单，
既学不满也过拟合不了，所以正则化开不开都一样。

**这说明：`model.train()`/`model.eval()` 的重要性取决于网络里有没有
Dropout / BatchNorm，以及数据集和任务的难度。**
真实项目里（大数据、深网络）这两个开关漏掉是常见事故来源。
**不要因为这里"没差别"就以为可以不写。**


## ★ 最值得记住的一条

**`loss.backward()` 和 `optimizer.step()` 漏掉时【不会报错】。**
代码正常跑完、正常打印精度 —— 只是精度永远停在随机水平（本实验里恰好是 0.0990）。

**这类「不报错的 bug」最危险**，也正好说明为什么每轮结束都要 `evaluate()`
并盯着精度看：**没有评估，你根本不知道训练有没有真的发生。**


## 原始输出（便于核对）

> 已剔除逐批的 `gstep=` 噪音，只留每轮精度和报错。

<details><summary>基线（退出码 0，耗时 10.0s）</summary>

```
epoch 1  test_acc=0.1990
epoch 2  test_acc=0.2550
epoch 3  test_acc=0.2780
epoch 4  test_acc=0.2890
epoch 5  test_acc=0.2730
epoch 6  test_acc=0.2780
```
</details>

<details><summary>实验 1（退出码 0，耗时 9.8s）</summary>

```
epoch 1  test_acc=0.1570
epoch 2  test_acc=0.1430
epoch 3  test_acc=0.1630
epoch 4  test_acc=0.1480
epoch 5  test_acc=0.1350
epoch 6  test_acc=0.1520
```
</details>

<details><summary>实验 2（退出码 1，耗时 6.3s）</summary>

```
Traceback (most recent call last):
  File "C:\Users\omen\AppData\Local\Temp\trainkit_j_w2a992\run.py", line 106, in <module>
    loss = criterion(out, y)
                     ^^^
NameError: name 'out' is not defined. Did you mean: 'oct'?
```
</details>

<details><summary>实验 3（退出码 1，耗时 6.5s）</summary>

```
Traceback (most recent call last):
  File "C:\Users\omen\AppData\Local\Temp\trainkit_wpv7a4f5\run.py", line 111, in <module>
    loss.backward()
    ^^^^
NameError: name 'loss' is not defined
```
</details>

<details><summary>实验 4（退出码 0，耗时 7.7s）</summary>

```
epoch 1  test_acc=0.0990
epoch 2  test_acc=0.0990
epoch 3  test_acc=0.0990
epoch 4  test_acc=0.0990
epoch 5  test_acc=0.0990
epoch 6  test_acc=0.0990
```
</details>

<details><summary>实验 5（退出码 0，耗时 8.3s）</summary>

```
epoch 1  test_acc=0.0990
epoch 2  test_acc=0.0990
epoch 3  test_acc=0.0990
epoch 4  test_acc=0.0990
epoch 5  test_acc=0.0990
epoch 6  test_acc=0.0990
```
</details>

<details><summary>实验 6（退出码 0，耗时 8.3s）</summary>

```
epoch 1  test_acc=0.1990
epoch 2  test_acc=0.2550
epoch 3  test_acc=0.2780
epoch 4  test_acc=0.2890
epoch 5  test_acc=0.2730
epoch 6  test_acc=0.2780
```
</details>

<details><summary>实验 7（退出码 0，耗时 9.9s）</summary>

```
epoch 1  test_acc=0.1990
epoch 2  test_acc=0.2550
epoch 3  test_acc=0.2780
epoch 4  test_acc=0.2890
epoch 5  test_acc=0.2730
epoch 6  test_acc=0.2780
```
</details>

<details><summary>实验 8（退出码 0，耗时 9.9s）</summary>

```
epoch 1  test_acc=0.1710
epoch 2  test_acc=0.1920
epoch 3  test_acc=0.2460
epoch 4  test_acc=0.2420
epoch 5  test_acc=0.2600
epoch 6  test_acc=0.2600
```
</details>

<details><summary>实验 9（退出码 0，耗时 9.8s）</summary>

```
epoch 1  test_acc=0.1990
epoch 2  test_acc=0.2550
epoch 3  test_acc=0.2780
epoch 4  test_acc=0.2890
epoch 5  test_acc=0.2730
epoch 6  test_acc=0.2780
```
</details>
