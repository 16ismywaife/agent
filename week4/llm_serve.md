# Week4 · LLM 本地部署记录（D3 / D4）

> 环境：Windows，RTX 5060 Laptop GPU（8 GB），Ollama 0.40.2
> 记录时间：2026-10-10
> 脚本：`week4/measure_llm.py`（TTFT / 吞吐量）、`week4/_measure_ctx.py`（显存 vs 上下文）、
> `week4/_compare_thinking_local.py`（思考开/关对照）
> **下面每个数字都是实测的**，不是估算。

---

## 一、硬件底数

```
GPU            NVIDIA GeForce RTX 5060 Laptop
总显存          8151 MiB（约 8.0 GB）
空闲（未加载模型）约 6944 MiB
算力            compute 12.0（sm_120，Blackwell 架构）
驱动版本         596.49
Ollama 用的库    cuda_v13
```

> **★ `sm_120` 是个关键约束** —— Blackwell 是新架构，**太老的推理引擎不支持它**。
> Ollama 0.40.2 支持（服务日志里能看到 `library=CUDA compute=12.0`）。
> **如果装的是老版本 Ollama，会出现"装上了但只能用 CPU 跑"。**

---

## 二、安装过程（附踩坑）

| 步骤 | 结果 |
|---|---|
| 安装包 | `OllamaSetup.exe` v0.40.2，**1505 MB** |
| 下载渠道 | **GitHub release**（winget 失败，见下） |
| 下载耗时 | **52.6 分钟**（平均 0.48 MB/s） |
| 安装位置 | `C:\Users\omen\AppData\Local\Programs\Ollama\`（程序约 27 MB） |
| 模型目录 | **`E:\ollama-models`**（改了环境变量） |

### 坑 1：winget 装不上 —— GitHub 不通

```
winget install Ollama.Ollama
→ InternetOpenUrl() failed. 0x80072efd
```

**原因**：winget 从 `github.com` 拉包，而**国内直连 GitHub 超时**。
系统代理开关是关的（`ProxyEnable = 0`），但代理客户端在 `127.0.0.1:7897` 有监听。

**解法**：绕过 winget，用 PowerShell 显式走代理下载：

```powershell
Invoke-WebRequest -Uri $url -OutFile "E:\OllamaSetup.exe" `
  -Proxy "http://127.0.0.1:7897" -TimeoutSec 3600
```

### 坑 2：模型**必须**在下第一个模型之前改目录

```powershell
[Environment]::SetEnvironmentVariable("OLLAMA_MODELS", "E:\ollama-models", "User")
```

**为什么必须提前**：先 `ollama pull` 再改变量的话，**已下到 C 盘的模型不会自己搬过去**，
Ollama 会当作"没有这个模型"**重新下 3 GB**。

**验证生效**（实测）：

```
E:\ollama-models          3.1 GB     ✅
C:\Users\omen\.ollama\models   0 MB  ✅ 没被偷用
```

**安装程序在 C 盘、模型在 E 盘** —— 这是对的：程序几百 MB 没必要搬，模型几个 GB 才是大头。

---

## 三、模型与空间

```
模型        qwen3.5:4b
磁盘占用     3.1 GB（E 盘）
Ollama 显示  3.3 GB
```

**下载明细**（从 manifest 读出来的）：

| 层 | 大小 | 说明 |
|---|---|---|
| **model**（权重） | **2525.9 MB** | 主体 |
| **projector** | **644.3 MB** | **多模态投影层** ← 因为它是 vision 模型 |
| template / license / params | 几十字节 | 元数据 |
| **合计** | **3.10 GB** | |

**下载速度对比（同一晚、同一网络）**：

| 源 | 速度 | 3.1 GB 预计耗时 |
|---|---|---|
| GitHub（装 Ollama 程序） | **0.48 MB/s** | 52.6 分钟（实测） |
| **registry.ollama.ai**（下模型） | **10 MB/s** | **7.6 分钟（实测）** |

**★ 结论：模型源比 GitHub 快 20 倍。** 以后下模型不用挂代理（实测直连 7.55 MB/s，走代理 10.77 MB/s）。

---

## 四、模型能力与架构

```
capabilities    ['completion', 'vision', 'tools', 'thinking']
                ↑ ★ 支持 tools（工具调用）→ Week4 做 Agent 靠这个
```

**架构参数**（决定显存开销）：

| 参数 | 值 | 作用 |
|---|---|---|
| `context_length` | **262144**（256K） | 模型能力上限 |
| `block_count` | 32 | 层数 |
| `attention.head_count` | 16 | 查询头 |
| **`attention.head_count_kv`** | **4** | ★ **KV 头只有查询头的 1/4（GQA）** |
| `embedding_length` | 2560 | 隐藏维度 |
| `feed_forward_length` | 9216 | FFN 维度 |

**默认采样参数**：`temperature 1`、`top_k 20`、`top_p 0.95`、`presence_penalty 1.5`

---

## 五、★ 上下文档位 vs 显存（实测）

**Ollama 按显存自动算的默认值是 4096**（服务日志原文：
`vram-based default context total_vram="8.0 GiB" default_num_ctx=4096`）。

**实测各档位的显存占用**：

| `num_ctx` | 加载后显存 | 模型+KV | KV 增量 | 剩余给系统 |
|---|---|---|---|---|
| 2048 | 5133 MiB | 3673 MiB | — | 3.0 GB |
| **4096**（默认） | 5208 MiB | 3748 MiB | 基准 | 2.9 GB |
| 8192 | 5406 MiB | 3946 MiB | +198 MiB | 2.7 GB |
| **16384** | 5674 MiB | 4214 MiB | +466 MiB | **2.5 GB** |
| 32768 | 6122 MiB | 4662 MiB | +914 MiB | 2.0 GB |
| **65536** | **7089 MiB** | 5629 MiB | +1881 MiB | **788 MiB** |

**验证过高上下文没退回 CPU**：

```
/api/ps 在 num_ctx=65536 时:
  总大小    4965 MiB
  占用显存  4965 MiB
  上下文    65536
  在 GPU 上  100%        ← 全在显卡，没有 CPU 回退
```

**★ 一个反直觉的点**：KV cache 实际约 **30 KB/token**，比按常规注意力公式算的
（head_dim × 2 × kv_heads × layers ≈ **80 KB/token**）**小 2.7 倍**。
**原因就是那个 GQA 设计**（`head_count_kv=4`）。

> **教训**：算出来的不如量出来的。我用公式估的 80 KB/token 让"能不能跑 64K"这个问题的
> 答案从"不可能"变成"实测可以"。**显存这种事必须实测。**

### 建议：设 16384

| 用途 | 需要多少 |
|---|---|
| 单轮问答 | ~1000 |
| **Week4 的 Agent**（多轮 + 工具结果） | **~3000-8000** |
| 长文档摘要 | 32000+ |

**16384 够做 Agent，且留 2.5 GB 给系统**（笔记本还要开 Chrome / PyCharm）。
**65536 只剩 788 MiB，Chrome 一开就可能爆显存**（Ollama 会退回 CPU，速度掉十倍）。

---

## 六、性能指标（实测）

**用原生 API（`/api/chat`）测，关掉思考**：

| 指标 | 实测值 | 说明 |
|---|---|---|
| **冷启动请求** | **3.71 s** | 含把模型读进显存 |
| 热请求（59 输出 token） | 0.75 s | |
| **吞吐量** | **93.2 tokens/s** | |
| **TTFT** | **116 / 122 / 124 ms**（中位数 **122 ms**） | 首 token 到达时间 |
| prompt 处理 | 18 token / 0.059 s | 约 305 tok/s |

**★ TTFT 和吞吐量是两个不同的指标**（手册 4.17 要求能说清）：

```
TTFT      = 从发出请求到收到【第一个】token 的时间  → 用户"感觉快不快"
吞吐量     = 每秒生成多少 token                     → "多久能说完"
```

**一个模型可能 TTFT 很短但吞吐量低**（第一个字很快，后面吐得慢），反过来也有。
本模型：**TTFT 122 ms 很快，吞吐 93 tok/s 也不错**。

---

## 七、★★ 最大的坑：思考模式（这一节最重要）

### 现象

`qwen3.5:4b` **默认开启思考**。同一个问题「用一句话说你好」：

| 设置 | 耗时 | 输出 token | 思考字数 | **正文字数** |
|---|---|---|---|---|
| 默认（不传） | **36.79 s** | 1991 | 6589 | 15 |
| `think=True` | 3.53 s | （截断） | 978 | **0** |
| **`think=False`** | **0.24 s** | **7** | 0 | 10 |

**关思考后快 150 倍。** 而思考模式下，**1991 个 token 里只有 15 个字是正文**。

### 坑的核心：`max_tokens` 被思考吃光

**用 OpenAI 兼容端点（`/v1`）时，思考无法关闭，于是会看到这个**：

| `max_tokens` | 耗时 | completion | **正文字数** | `finish_reason` |
|---|---|---|---|---|
| 60 | 0.92 s | 60 | **0** | `length` |
| 300 | 3.82 s | 300 | **0** | `length` |
| 1000 | 12.48 s | 1000 | **0** | `length` |
| 3000 | 29.65 s | 2370 | 14 | `stop` |

**★ `max_tokens` 给到 1000 时，正文仍然是空的** —— 1000 个 token 全被思考吃掉。
**要给到 3000 才刚够。**

> **这正是 Week3 D1 撞过的那个坑，在本地模型上重演。**
>
> Week3 那次（DeepSeek 云端）：`max_tokens=100` → 正文 0 字符 → `json.loads("")` 报
> `JSONDecodeError` → **看起来像 JSON 格式问题，实际是预算被思考吃了**。
>
> **同一个坑，两个模型，两次踩。**

### 试过但**无效**的关思考方法

| 方法 | 结果 |
|---|---|
| `extra_body={"think": False}` | ❌ 无效 |
| `extra_body={"think": "false"}` | ❌ 无效 |
| `extra_body={"options": {"think": False}}` | ❌ 无效 |
| `extra_body={"enable_thinking": False}` | ❌ 无效 |
| prompt 里加 `/no_think` | ❌ 无效 |
| system 里加 `/no_think` | ❌ 无效 |
| Modelfile 写 `PARAMETER think false` | ❌ `Error: unknown parameter 'think'` |

**结论：Ollama 的 OpenAI 兼容端点（`/v1`）无法关闭思考。**

### ✅ 唯一有效的办法：用原生 API

```python
# 原生端点：http://127.0.0.1:11434/api/chat
{
  "model": "qwen3.5:4b",
  "messages": [{"role": "user", "content": "..."}],
  "think": false,          # ★ 只有这里认这个参数
  "stream": false
}
```

**命令行也一样**：

```powershell
ollama run qwen3.5:4b --think=false        # 关思考（快 150 倍）
ollama run qwen3.5:4b --hidethinking       # 只隐藏输出，照样烧 token
```

### ⚠️ 一个我犯过的测量错误（写下来防重犯）

**我最初测「思考模式对算术有没有用」时，设了 `num_predict=600`，得到「正文全空」，
于是下了个结论：「思考模式是负分」。**

**这个结论是错的**，错在**预算给小了**。给足预算后实测：

| `num_predict` | 耗时 | 思考 | 正文 | `done_reason` | 结果（正确答案 6） |
|---|---|---|---|---|---|
| **600** | 13.08 s | 1689 字 | **0 字** | **`length`** | ❌ 被截断 |
| **3000** | 13.41 s | 2808 字 | 36 字 | `stop` | ✅ **答对 6** |
| 8000 | 13.34 s | 2808 字 | 36 字 | `stop` | ✅ 答对 6 |

**它需要约 2800 字的思考才输出答案。`num_predict=600` 把思考砍断了。**

**★ 而 `done_reason=length` 就在返回值里明确写着"输出被截断"** ——
**信号摆在那儿，我却没用它，反而去下了个"模型能力"的结论。**

### 关于思考模式的正确结论

| 设置 | 算术题（40×60%×25%） | 耗时 |
|---|---|---|
| `think=False` | ❌ **3/3 答 5**（一致的错） | 0.5-4.4 s |
| `think=True` + 给足预算 | ✅ **答 6** | **13.4 s** |

**所以思考是【有用】的 —— 它提高了正确率。真正的代价是【时间】，不是"帮倒忙"。**

而因为 `/v1` 端点关不掉思考，**你在本地没法控制"这步要不要思考"**：
要么每步都等 13 秒（换来正确率），要么完全关掉（快但会算错）。

### ★★ 这对 Week4 的 Agent 意味着什么

**我们的 `week3/day1.py` 和 `week4/agent_calc.py` 都用 OpenAI SDK。**
如果直接指向 Ollama 的 `/v1`：

| 后果 | 具体 |
|---|---|
| **每个 Agent 步骤慢 10-30 秒** | Agent 主循环最多 5 步 → 一个问题等 1-2 分钟 |
| **`max_tokens` 给小了正文会是空的** | 思考先吃掉预算 → `msg.content = ""` → Agent 逻辑判断错 |
| **没有中间选项** | `/v1` 不能按次决定"这步是否思考" |

**三条出路**：

| 方案 | 做法 | 代价 |
|---|---|---|
| **A. 本地用原生 API** | 给 `completion()` 加分支：本地走 `/api/chat`，云端走 SDK | 要写两套调用代码 |
| **B. 云端 API 做 Agent**（已选） | 本地只用来学部署（D3/D4），Agent（D1/D2）继续用 DeepSeek | 花一点钱（实测可忽略） |
| **C. 本地把 `max_tokens` 开到 3000+** | 换来正确率，但每步等 13 秒 | Agent 会非常慢 |

---

## 八、★★ 后端选择决策：Agent 用【云端】，本地只用来学部署

> **决策时间：2026-10-10（Week4 开始前）**
> **结论：D1/D2 的 Agent 用云端 `deepseek-flash`；本地 `qwen3.5:4b` 只用于 D3/D4（部署与指标）。**

### 依据一：本地模型的**速度**不适合 Agent（能力其实是够的）

`week4/_compare_local_vs_cloud.py`，同一批 prompt 打两个后端：

| 测试 | 本地 4B | 云端 |
|---|---|---|
| ① 只输出 JSON（中文键） | ✅ 和云端**完全一样** | ✅ |
| ② system 当输出契约 | ✅ 只给一句（23 字） | ✅ 只给一句（17 字） |
| **③ 算术**（40×60%×25%，答案 6） | 关思考 ❌ 答 5；**开思考 ✅ 答 6（13.4 s）** | ✅ 答 6（0.5 s） |

**★ 注意 ③ 的正确读法**：**本地模型是【能做对】的，但要 13 秒；关掉思考只要 0.5 秒但会算错。**
（我最初因为 `num_predict` 给小了，误判成"本地算术不行"，见第七节末尾的更正。）

**为什么这仍然决定 Agent 用云端**：

| 原因 | 具体 |
|---|---|
| **Agent 是靠多步串起来的** | 一个问题 3-5 步，每步 13 秒 → 1 分钟以上 |
| **本地 `/v1` 关不掉思考** | 你没法"只在该思考的时候思考" |
| **云端又快又对** | 0.5 s 且答对 |

**Agent 要靠模型判断「该不该调工具」，而它每步都慢 13 秒的话，
调试一遍就要几分钟 —— 这个反馈速度没法迭代。**

### 依据二：云端的成本可以忽略（按官方报价算）

`deepseek-flash` 报价（输入未命中缓存 $0.15 / 1M，输出 $0.6 / 1M，低峰半价）。

一次 calculator Agent 问答约 prompt 580 tok / 输出 80 tok，则：

| 折腾程度 | 最贵 | 最省 |
|---|---|---|
| 跑通调试（20 次） | ¥0.038 | ¥0.014 |
| 认真测（50 次） | ¥0.096 | ¥0.036 |
| **反复折腾（200 次）** | **¥0.383** | ¥0.142 |

**★ 实际比这更便宜**：DeepSeek 输入有【缓存命中】价，**便宜 50 倍**（$0.003 vs $0.15）。
Agent 每步都重发整段历史，而 **system + 工具说明每次一字不差 → 大部分输入命中缓存**。

**★ 高峰时段**（北京时间 **09:00-12:00 / 14:00-18:00**，正好是白天写代码的时段）
是低峰的两倍。**晚上跑便宜一半。**

### 那本地模型用来干什么

| 用途 | 为什么 |
|---|---|
| **D3/D4：部署 + 测指标** | 这正是本地部署的考点（显存、TTFT、吞吐量） |
| **学"部署"这件事本身** | 面试能聊"为什么要本地部署、显存怎么算、量化是什么" |
| 格式类任务 | 实测 4B 在格式上和云端持平，这类任务能省则省 |
| **★ 以后做 Agent 的"降级路径"** | 如果哪天要用本地跑 Agent，你得知道有哪些坑（思考模式、上下文） |

### 还有一个副产品：现成的验证用例

**`40 × 60% × 25%` 这道题**：
- 本地关思考 → 答 **5**（错）
- 本地开思考 → 答 **6**（对，13 秒）
- 云端 → 答 **6**（对，0.5 秒）

**等 D1/D2 做完，可以拿它测**：**加了 `calculator` 工具之后，模型能不能答对？**

**如果能 → 就完整闭环了**：发现问题（模型算得慢/会错）→ 理解机制（工具调用）→ 实现 → 验证。

**这比"我学会了 Agent"有说服力得多。** 而且这个对比有实测数据支撑。

---

## 九、这一节能用在哪儿

| 用途 | 怎么用 |
|---|---|
| **面试** | "我实测过一个 4B 多模态模型在 8 GB 显存上的表现：TTFT 122ms、吞吐 93 tok/s；上下文档位从 4K 到 64K 的显存占用我都测了。还发现它的思考模式默认开着，会让 `max_tokens` 被吃光、正文变空。" |
| **踩坑记录** | 三条：winget 走不通 GitHub、OLLAMA_MODELS 必须提前设、OpenAI 端点关不掉思考 |
| **Week4 D4** | TTFT / 吞吐量的定义和实测值现成 |
| **工程判断** | "算出来的不如量出来的" —— KV cache 公式估高 2.7 倍 |

---

## 十、复现命令

```powershell
# 环境变量（改完要重启终端 / 重启 Ollama）
[Environment]::SetEnvironmentVariable("OLLAMA_MODELS", "E:\ollama-models", "User")

# 服务（安装后托盘会有图标，或手动起）
& "$env:LOCALAPPDATA\Programs\Ollama\ollama.exe" serve

# 下模型（不需代理，registry 很快）
& "$env:LOCALAPPDATA\Programs\Ollama\ollama.exe" pull qwen3.5:4b

# 量指标
python week4\measure_llm.py --model qwen3.5:4b --out week4\metrics_qwen3.5-4b.json

# 量不同上下文的显存
python week4\_measure_ctx.py

# 对比思考开/关
python week4\_compare_thinking_local.py

# 对话（记得关思考）
& "$env:LOCALAPPDATA\Programs\Ollama\ollama.exe" run qwen3.5:4b --think=false
```
