# Week4 · 三个方向体验（Agent / LLM 部署 / 视频 Edge）

> **文档要求**：体验 **Agent、LLM 部署、视频 Edge** 三个方向
> **考核重点**：能独立运行三个最小示例，理解每个方向的**基本工作链路与关键指标**
> **交付物**：`week4/` 三个可运行示例
>
> ★ **本目录和 Week1~3 最大的不同**：这里要**两套 Python 环境**（见第 0 节）。
> 这是本目录最容易踩、而且**踩了不报错**的坑。

---

## 0 · ★★ 先看这个：本目录有两套环境

| 环境 | Python | 关键包 | 用来跑什么 |
|---|---|---|---|
| **`agent`** | 3.11.16 | `openai`、`python-dotenv`、`torch` | **Agent 方向**（`agent_calc.py`）—— 连云端或连本地 Ollama 都用它 |
| **`AMSP_UOD`** | 3.10.20 | `ultralytics`、`opencv`、`torch 2.11.0+cu128` | **视频 Edge 方向**（`video_fps.py`）—— 需要 GPU 版 torch |
| ⚠️ `myenv1` | 3.13.14 | `ultralytics`，但 torch 是 **`2.13.0+cpu`** | ⛔ **别用** —— 见下 |

### ⚠️ 拿错环境的后果：差十几倍，而且不报错

2026-10-12 实测（本机 7 个 conda 环境里，两个都装了 ultralytics）：

| 环境 | torch | 能不能用 GPU |
|---|---|---|
| `myenv1` | `2.13.0+cpu` | ❌ **纯 CPU** |
| `AMSP_UOD` | `2.11.0+cu128` | ✅ **RTX 5060 Laptop** |

**用 `myenv1` 跑 FPS，会安静地输出一个"看起来很正常"的烂数字** —— 不报错、不警告。
**这是 Edge 方向最经典的坑：环境本身就是测量的一部分。**

> **推论**：以后报任何 FPS / 吞吐量之前，先打一句 `torch.cuda.is_available()`。
> `video_fps.py --check` 里已经加了这道闸门（`cuda=False` 直接判自检不过）。

---

## 一、换台机器怎么跑起来

### 1 · Agent 方向（`agent_calc.py`）

```powershell
cd E:\04_脚本与代码\agent
& "D:\anaconda\envs\agent\python.exe" week4\agent_calc.py --check     # 只自检，不花钱
& "D:\anaconda\envs\agent\python.exe" week4\agent_calc.py --sanity    # 发一次请求，看原始返回结构
& "D:\anaconda\envs\agent\python.exe" week4\agent_calc.py             # 跑三个问题
```

- 依赖 `.env`（仓库根目录）：`API_KEY` / `BASE_URL` / `MODEL`
- **默认连云端**（`.env` 里的 `deepseek-flash`）。想连本地 Ollama 需要改 `.env` 的
  `BASE_URL`/`MODEL`（`http://127.0.0.1:11434/v1` + `qwen3.5:4b`）——
  **目前没有 `--local` 开关**，是待办。

### 2 · LLM 部署方向（`measure_llm.py` / `ctx_status.py`）

**先确保 Ollama 服务在跑**（`ollama list` 会自动把它拉起来）：

```powershell
ollama list

& "D:\anaconda\envs\agent\python.exe" week4\measure_llm.py --check    # 只检查环境
& "D:\anaconda\envs\agent\python.exe" week4\measure_llm.py            # 测显存/加载/TTFT/吞吐
& "D:\anaconda\envs\agent\python.exe" week4\ctx_status.py             # 看上下文档位 vs 实际占用
& "D:\anaconda\envs\agent\python.exe" week4\ctx_status.py --ask "你好"  # 看一条消息占多少上下文
```

模型落在 **`E:\07_AI模型\ollama`**（3.1 GB，C 盘 0 MB）。

### 3 · 视频 Edge 方向（★ 未做，见第五节）

```powershell
& "D:\anaconda\envs\AMSP_UOD\python.exe" week4\video_fps.py --check   # ★ 环境必须是 AMSP_UOD
```

骨架在（自检 / 抽帧 / 显存查询都写好了），**两个函数体未写** —— 见 `edge_notes.md` 与第五节。

---

## 二、文件索引

### 交付物（按方向）

| 方向 | 文件 | 状态 |
|---|---|---|
| **Agent** | `agent_calc.py` | ✅ D1/D2 交付物（工具定义 + 主循环） |
| **LLM 部署** | `measure_llm.py` + `metrics_qwen3.5-4b.json` | ✅ D3/D4 交付物（指标 + 记录） |
| | `llm_serve.md` | ✅ D3/D4 实测记录（部署全过程 + 6 档档位表） |
| **视频 Edge** | `edge_notes.md` | ✅ **代替实测**（已有基础说明，见第五节） |
| | `video_fps.py` | ◐ 骨架（函数体未写） |

> **手册 vs 实际的文件名**：手册 D4 写的产出是 `week4/bench.py`，
> 实际是 `measure_llm.py`；手册 D6 写的也是 `bench.py`，实际并入 `video_fps.py`。

### 计划外产出（不是本周要求，但做完了）

| 文件 | 干什么 |
|---|---|
| `iq_test.py` | 模型能力评测：**25 题 / 8 类，自动打分**（`--backend local\|cloud\|both`） |
| `personas.py` | **10 个人设**合集 + 实测哪些真能改变模型行为（`--list` / `--try` / `--test`） |
| `ctx_status.py` | 查本地模型的**上下文档位 vs 实际占用** |

### 实验证据脚本（md 里的数据都能重跑）

| 文件 | 测什么 |
|---|---|
| `_measure_ctx.py` | 不同上下文长度下占多少显存（6 档） |
| `_compare_local_vs_cloud.py` | 同一批问题，本地 `qwen3.5:4b` vs 云端 `deepseek-flash` |
| `_compare_thinking_local.py` | 开/关思考的耗时与 token 对比 |

### 学习 / 练习

| 文件 | 说明 |
|---|---|
| `_drill.md` | **Agent 代码回忆练习清单**（关掉参考凭记忆写；第 5 节是盲区记录表） |

---

## 三、三个方向的关键指标（★ 考核点名）

| 方向 | 关键指标 | 一句话 |
|---|---|---|
| **Agent** | **调用成功率** | 模型决定调什么，**执行的是你的代码**；失败要能兜住 |
| **LLM 部署** | **显存 / TTFT / 吞吐量** | TTFT 影响"感觉快不快"，吞吐影响"多久说完" |
| **视频 Edge** | **FPS** | 视频 25–30 FPS，处理速度低于它就跟不上实时 |

### ★ 一个容易混的区分（Edge 方向的核心）

```
GFLOPs / 参数量  →  模型【有多重】   （静态，算出来的）
FPS             →  模型【跑得多快】   （动态，测出来的，受硬件/精度/批大小影响）
```

---

## 四、本周实测到的关键数据

| 数据 | 值 | 出处 |
|---|---|---|
| 显存占用（`num_ctx=4096`） | **5202 / 8151 MiB** | `llm_serve.md` |
| 上下文档位 vs 显存（6 档） | 2048→5133 … 65536→7089 MiB，**全程 100% GPU** | `llm_serve.md` |
| **TTFT**（首 token） | **122 ms** | `llm_serve.md` |
| **吞吐量** | **93.2 tok/s** | `llm_serve.md` |
| 冷启动加载 | 3.71 s | `llm_serve.md` |
| Agent 三类问题 | 算术→`calculator` ✅ / 日期→`get_time` ✅ / 闲聊→不调工具 ✅ | 提交 `0f49957`（week4 D2） |
| 工具说明的 token 成本 | 1 个工具 **303** → 2 个工具 **344**（**+41**） | 2026-10-13 实测 |
| 本地 4B 关思考 | 多步算术 **1/4**（会自信地错） | `iq_test.py` |

### ★ 一个 API 层结论（会反复咬人）

**Ollama 的 OpenAI 兼容端点关不掉思考。** `think` / `chat_template_kwargs` / `/no_think`
三条路都试过，无效；**只有原生 API 能关**。后果：思考会占满 `max_tokens` → 正文为空。

---

## 五、视频 Edge 方向为什么没有实测（★ 诚实说明）

**这个方向我有更高标准的实践**：

- **2026 暑期 · 校企协同课题（42 天）**：以 YOLOv11n 为基线做 **14+ 组单变量消融**
- **2026 秋 · 独立论文**：**自建 FPS / GFLOPs / 参数量测量脚本**，覆盖 9 个检测器配置 / 4 个架构族

**所以本仓库不重复"加载模型跑一帧"这一层。**

- 关键指标说明 + 已有实践 → **`week4/edge_notes.md`**
- `video_fps.py` 骨架**保留**，以后想补实测随时能写（命令见第一节第 3 条）

> **Week6 汇报第 5 页照实写这一条。** 手册原则：
> **写清楚没做完什么不扣分，假装做完才扣分。**

---

## 六、自查（D7）

- [x] **三个方向都有交付物**（Agent ✅ / 部署 ✅ / Edge 用 `edge_notes.md` 代替 ✅）
- [x] 能说出每个方向的**关键指标**（Agent=调用成功率；部署=显存/TTFT/吞吐；Edge=FPS）
- [x] 能讲清 **Agent 里"LLM 怎么决定调用工具"**（靠 `TOOLS_SPEC` 的 description + system）
- [x] 依赖环境写清了（**两套环境 + CPU/GPU 坑**，见第 0 节）
- [ ] 本地 Ollama 的 `--local` 开关（待办，可选）

---

## 七、每天结束时

```powershell
git add . && git commit -m "..." && git push
```
并在 `notes/log.md` 记 3 行（**第 6 周汇报第 3-4 页的原料**）。
