# 工作日志

> **每天 3 行，几十秒。** 格式就这么简单，别加负担。
>
> 为什么值得写：2027 年 3 月面试时，面试官一定会问「你遇到过什么问题、怎么解决的」。
> 那个答案只能从这里来。第 6 周汇报第 3 页也是同一份材料。
>
> 写法：直接往下加，不用管格式好看。

---

## 09-21（Day 1 · 环境）

- **做了**：建 conda 环境（Python 3.11）、配 PyCharm、建 git 仓库 + `.gitignore`、写 `day1.py` 跑通
- **卡了**：PyCharm 项目根目录开成了 `week1`，导致 Git 面板看不到整个仓库
- **解了**：`File → Open` 重新打开 `E:\agent`

- **还卡了**：终端里中文全是乱码
- **解了**：脚本里加 `sys.stdout.reconfigure(encoding="utf-8")`

---

## 09-22（Day 2 · Python 基础）

- **做了**：三道题——数及格人数、字典分桶统计、列表推导式
- **卡了**：第 2 题说"用字典统计各分数段人数"，我以为字典是题目给的输入，找不到
- **解了**：想通了字典是自己**造出来的输出**，用 `counts[b] = counts.get(b, 0) + 1` 计数

---

## 09-23（Day 3 · 函数与类）

- **做了**：`get_bucket()` / `pass_rate()` 两个函数 + `ScoreAnalyzer` 类（5 个方法）
- **卡了 1**：`elif 60 <= s < 79` —— 79 分被判成了 `>=80`
- **解了 1**：改成 `60 <= s < 80`。**测试数据里没有 79/80，所以一直没暴露**——补了边界测试

- **卡了 2**：`summary()` 里又写了一个 `def summary`，返回 `None`
- **解了 2**：嵌套函数——外层只定义不调用，什么都不做。删掉外层

- **卡了 3**：`summary` 用了 `print` 而不是 `return`
- **解了 3**：改成 `return`

---

## 09-25（Day 4 · NumPy）

- **做了**：矩阵创建 / shape / 三种聚合 / `axis=0,1` / 布尔索引 / 布尔赋值
- **卡了**：没有。`axis` 一次就对了
- **记一下**：验证 `axis` 的办法是**看输出长度**——`mean(axis=0)` 出 3 个数就是"每科目"

---

## 09-25（Day 5 · Pandas）

- **做了**：生成 300 行测试数据、`groupby`、`agg`、条件筛选、排序、`nunique`
- **卡了 1**：第 6 题报 `KeyError: 科目`——我写的是 `df.sort_values(df.groupby(...).mean())`，**排的是 300 行的大表，不是 groupby 的结果**
- **解了 1**：改成链式调用 `df.groupby("科目")["分数"].mean().sort_values(ascending=False)`

- **卡了 2**：第 8 题只建了列，忘了打印
- **解了 2**：加上 `print(df["是否及格"].mean())`——**布尔列的均值就是比例**，这个技巧记住了

---

## 09-26（Day 6 · Matplotlib）

- **做了**：柱状图、直方图、分组柱状图（用 `pd.crosstab`），三张图都保存了
- **卡了 1**：`ax.bar=(s.index, s.values,)` 多了个等号——**这是赋值不是调用**，把 matplotlib 的方法覆盖成了元组
- **现象**：脚本退出码 0、图片也生成了，**但图是空白的**
- **解了 1**：去掉等号。**学到：图片文件太小（10KB vs 正常 20KB）说明没画出东西**

- **卡了 2**：加了 `color="#4C78A8"` 报语法错误
- **解了 2**：因为前面是赋值，`color=` 跑到元组里去了。**`关键字=值` 只能在函数调用的括号里写**

---

## 09-29 ~ 10-02（Week2 · Git 远程与分支）

- **做了**：生成 GitHub 专用密钥 `id_ed25519_github` → 配 `~/.ssh/config` → 建仓库 → `git push`；练了分支（`switch -c` / `merge` / `branch -d`）
- **卡了 1**：`ssh-keygen -f ~/.ssh/id_ed25519_github` 报 `Saving key "~/.ssh/id_ed25519_github" failed: No such file or directory`
- **解了 1**：**PowerShell 里 `~` 不会展开**（它只在自己人写的 cmdlet 里展开）。ssh-keygen 是外部程序，原样收到 `~`，就把它当成文件夹名了。改用 `"$env:USERPROFILE\.ssh\id_ed25519_github"`
- **卡了 2**：`git remote add origin git@github.com:你的用户名/agent.git` —— **占位符「你的用户名」被我原样贴上去了**
- **现象**：`git push` 报 `Repository not found`，`git remote -v` 里字面就是「你的用户名」
- **解了 2**：`git remote set-url origin git@github.com:16ismywaife/agent.git`（用户名是 `16ismywaife`，不是 `cheggs` —— `cheggs` 只是 git 的 `user.name`）。**学到：文档里的占位符必须先替换，`git remote -v` 是查这个的第一步**
- **记一下**：原来的 `id_ed25519` 没动 —— 实验室服务器还在用它，新建的是 GitHub 专用钥匙

---

## 10-01 ~ 10-02（Week2 · Tensor 与自动求导）

- **做了**：`x.grad` 手算对账；**用自动求导做梯度下降拟合 `y = 2x + 1`** → 200 轮后 `w=2.0000, b=1.0000`
- **卡了**：验证「为什么需要反向传播」时删掉 `loss.backward()`，但循环里还留着 `w.grad.zero_()`，报错
- **解了**：`backward()` 和 `zero_()` 要一起删 —— **没有 `backward()` 就没有 `.grad`，`zero_()` 自然没得清**
- **★ 这个反证很值钱**：删掉 `backward()` 后 `w` 一直是 `0.0000` —— **参数一点没动**。比任何解释都能说明反向传播在干什么
- **记一下**：梯度是**累加**不是覆盖，所以 `zero_grad()` 必须每轮都调

---

## 10-02（Week2 · Dataset 与 DataLoader）

- **做了**：加载 MNIST（60000 / 10000）、取 batch 看 shape `[32, 1, 28, 28]`、对比 shuffle
- **卡了**：以为 `DataLoader` 和 `Dataset` 是同一层的东西
- **解了**：**`Dataset` 管「一条数据怎么取」，`DataLoader` 管「怎么攒成一批、要不要打乱」** —— 两层分工
- **记一下**：**测试集不用 `shuffle`**（顺序固定结果才可复现）；Windows 上 `num_workers > 0` 会卡死

---

## 10-05（Week2 · MNIST 训练循环 + 保存/加载模型）★ 本周交付物

- **做了**：`LOOP.py` 全量训练 3 个 epoch → **准确率 97.36%**（RTX 5060，60000 张，110 秒）；`torch.save(state_dict)` 存模型 → `loadtest.py` 加载推理，`pred: 7, label: 7` 一致
- **卡了**：`loadtest.py` 报 `RuntimeError: a Tensor with 784 elements cannot be converted to Scalar`
- **根因**：**括号位置错了**。我写的是
  ```python
  pred = model(x.unsqueeze(0).argmax(dim=1).item())   # ❌ 全在 model() 里面
  ```
  `argmax` 跑在**输入图像**上（在 784 个像素里找最大值），而不是在**模型输出**上。所以 `model()` 收到了一个数字，`item()` 又想把 784 个元素的张量变成标量
- **解了**：
  ```python
  pred = model(x.unsqueeze(0)).argmax(dim=1).item()   # ✅ argmax 在外面，对输出做
  ```
- **★ 学到**：**`model(x)` 的右括号在哪结束，决定了后面所有操作作用在谁身上。** 拆成两行就不会错：
  ```python
  out  = model(x.unsqueeze(0))     # 先拿输出（形状 [1, 10]）
  pred = out.argmax(dim=1).item()  # 再在输出上取类别
  ```
- **记一下**：`state_dict()` **只存参数不存结构**，所以加载时 `Net` 类必须和训练时一模一样，先建结构再灌参数

---

## 10-06（Week3 · D1 跑通第一次 LLM 调用）

> **这一条要分清哪些是我自己做的** —— 考核标准是「不能只运行别人代码」，
> 混着记等于自欺欺人。下面标了出处。
> 这一天一开始 AI 把整套脚本都替我写完了，我提出质疑，之后改成
> **骨架 + 我填核心**（`week3/day1.py` 里 5 个函数体留 TODO 自己写）。

- **做了**：配 `.env`（DeepSeek）→ `day1.py --check` 五项自检全过 → D1~D5 跑通
  - （脚手架、报错诊断：AI 提供；**5 个核心函数体：待我自己填**）
- **卡了 1（我自己写的代码，我自己改对的）**：`mytrain.py` 第 2 步我写成 `pred = model(x).argmax(dim=1)`，报
  `RuntimeError: Expected floating point type for target with class probabilities, got Long`
- **解了 1**：`CrossEntropyLoss` 要的是**浮点分数** `(批,10)`，`argmax` 把它压成了 Long `(批,)`。改成 `pred = model(x)` 后 loss 2.12→0.19，精度 0.0950→0.2510。
  **★ 这和 Week2 那次报错是同一个根因：`argmax` 下得太早。** 记住一条规则就够了 —— **`argmax` 只用于算准确率那一步，算 loss 时绝对不能加。**
- **卡了 2**：跑 D5 时 `max_tokens=10` / `100` 返回的正文**全是空字符串**，`finish_reason=length`
- **解了 2**：`deepseek-flash` **默认开启思考模式**，而 **`max_tokens` 把思考 token 也算在内** —— 思考没结束预算就没了，正文一个字都吐不出来。
  **★ 这个坑最阴的地方**：做 JSON 输出时预算被吃掉 → 拿到空字符串 → `json.loads("")` 报 `JSONDecodeError` → **你会以为是自己 JSON 格式写错，去改 prompt，方向全错。**
  解决：`extra_body={"thinking": {"type": "disabled"}}` 关掉思考（SDK 不认这个字段，必须用 `extra_body` 透传）。关掉后 `reasoning_tokens` 变 `None`，**同样的钱买到更多正文**。
- **卡了 3（这个更值得记：错的是【测量方法】，不是模型）**：一开始把 temperature 实验写成 `max_tokens=60`，结果 3 次输出全是空字符串，被统计成「全部相同」，差点得出「temperature 不起作用」的**错误结论**
- **解了 3**：把 `max_tokens` 提到 800 后重测 —— `temperature=0.7` / `1.5` 各 4 次**都产生 4 种不同输出**，**temperature 完全正常**。
  **★ 学到：「三次都一样」和「三次都是空的」，在代码里长得一模一样。** 必须先 `print(repr(输出))` 看清内容再下判断。
  **★ 附带发现**：`temperature=0` 时输出**仍可能不同**（3 种）—— 它只是降低随机性，不保证 100% 复现。
- **记一下**：`deepseek-chat` 这个模型名**已失效**（网上老教程还在写），现在用会 404。当前是 `deepseek-flash` / `deepseek-v4-pro`
- **我自己的反思**：AI 一开始把 5 个函数全写好了，我差点直接收下。**读得懂 ≠ 写得出来。** 以后默认要骨架，不要成品 —— 尤其 Week4 的 Agent。

---

<!--
往下加新的一天。三行就够：

## MM-DD（Day X · 主题）

- **做了**：
- **卡了**：
- **解了**：

-->
