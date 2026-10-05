# `_verify/` —— 手册代码的自检工具

这里放的是**验证手册代码是否真的能跑**的工具，不是六周任务的交付物。

为什么会有这个目录：手册第 4 章的 LLM / Agent / RAG 那几段，是在**没有 API Key** 的情况下写的。
「语法看着对」和「真的能跑」是两件事，所以这里用一套不花钱的办法把它们验掉。

---

## 两种模式

| 模式 | 命令 | 能证明什么 | 花不花钱 |
|---|---|---|---|
| **Mock** | `python verify_handbook_llm.py` | 代码语法对、SDK 用法对、请求结构对、返回解析对、边界处理对 | ❌ 不花钱 |
| **真实** | `python verify_handbook_llm.py --real` | 再加上：**真实模型会不会真的选你的工具**、回答质量、真实 token 计费 | 💰 花几十~几百 token |

**Mock 模式证明不了模型行为。** 它只证明「你的代码说得对不对」，不证明「模型答得好不好」。
两个都跑过，才能说这一段是真正验证过的。

---

## 怎么跑

### 1）Mock 模式（不花钱，随时可跑）

**第一步：开 mock 服务器**（占一个终端窗口，别关）

```powershell
python _verify\mock_openai_server.py
# 看到 mock server on http://127.0.0.1:8799/v1 就是起来了
```

**第二步：另开一个终端，跑验证**

```powershell
python _verify\verify_handbook_llm.py
```

**第三步（可选）：核对实际发出去的请求体**

```powershell
python _verify\check_requests.py _verify\requests.jsonl
```

它会检查：`Authorization` 头有没有带、`tools` 结构是否符合 function-calling 规范、
`tool_call_id` 和 `assistant.tool_calls[].id` 有没有配上、`response_format` /
`temperature` / `stream` 有没有真的进请求体。**服务器把每个请求原样记在 `requests.jsonl` 里。**

### 2）真实模式（填完 `.env` 之后）

```powershell
# 先确认 E:\agent\.env 里 API_KEY 填好了（.env 已被 .gitignore 排除）
python _verify\verify_handbook_llm.py --real
```

`--real` 会把同一批代码打到 `.env` 里的 `BASE_URL`，用真实模型跑一遍。

---

## `requests.jsonl` 是什么

mock 服务器把收到的**每一个请求体原样存成一行 JSON**。它的用处：

- 不用抓包就能看清 SDK 到底发了什么
- 面试时说「我核对过 function calling 的请求结构」时，这就是证据
- 出问题时能对比「我以为发的」和「实际发的」

**这个文件是运行产物，不用提交**（已在 `.gitignore` 里）。

---

## 文件说明

| 文件 | 作用 |
|---|---|
| `mock_openai_server.py` | 本地 OpenAI 兼容服务器，实现 `/v1/chat/completions`（含 tool_calls 与 SSE 流式分块） |
| `verify_handbook_llm.py` | 用手册里的**原样代码**逐段验证，17 项断言 |
| `check_requests.py` | 解析 `requests.jsonl`，核对协议细节 |
| `requests.jsonl` | mock 服务器记录的请求（运行产物，不提交） |

---

## mock 服务器的行为规则

它**故意做得可预测**，方便断言：

| 请求特征 | mock 的响应 |
|---|---|
| 历史里已有 `role: "tool"` | 说明工具执行过了 → 返回最终回答，带上工具结果 |
| 带 `tools` 且还没调过工具 | 返回一个 `tool_calls`，要求调用第一个工具 |
| `response_format={"type":"json_object"}` | 返回合法 JSON（`{"姓名":...,"科目":...,"分数":...}`） |
| 其他 | 返回一段普通文本 |

> ⚠️ 「带 `tools` 就固定要调工具」**是 mock 的设定，不是真实模型的行为**。
> 真实模型会自己判断该不该调——这正是 `--real` 才能验的部分。
