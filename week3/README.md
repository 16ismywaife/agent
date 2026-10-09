# Week3 · 现代 AI 模型体验（大模型分支）

> **本周主题**：LLM API 调用 —— Prompt、多轮对话、**结构化输出**、参数实验
> **状态**：**D1~D5 已完成**（`day1.py` 里 5 个函数体全部自己填写）
> **文档要求**：二选一 ①视觉 YOLO ②大模型 → **选了 ②**

---

## 一、换台机器怎么跑起来

### 1. 装依赖

```powershell
pip install openai python-dotenv
```

### 2. 配 `.env`（在仓库根目录，不是这里）

```powershell
cd E:\agent
copy .env.example .env
python week3\_set_key.py       # ★ 用它填 Key：不显示、不进命令历史
notepad .env                   # 再补 BASE_URL 和 MODEL
```

三个值：

```
API_KEY=<用 _set_key.py 填>
BASE_URL=https://api.deepseek.com/v1
MODEL=deepseek-flash
```

> ⚠️ **`deepseek-chat` 已失效**（网上老教程还在写），用它会 404。
> 当前 DeepSeek 的模型名：`deepseek-flash`（推荐，支持 JSON + Tool Calls）、`deepseek-v4-pro`。
>
> ⚠️ **别手打 Key** —— 多一个空格就是 401，而报错不会告诉你多打了空格。

### 3. 自检 + 跑

```powershell
python week3\day1.py --check        # 只自检，不花钱、不发请求
python week3\day1.py --only 1       # 只跑 D1
python week3\day1.py --all          # D1~D5 全部
```

### 4. 不花钱也能先验证代码

`.env` 还没配时，用本地 mock 服务器跑通协议层：

```powershell
# 窗口 1
python _verify\mock_openai_server.py
# 窗口 2
python _verify\verify_handbook_llm.py
```

用**真实的 `openai` SDK** 打真实 HTTP，检查请求结构、`tool_calls` 配对、
`response_format`、`stream` 分块。详见 `_verify/README.md`。

---

## 二、文件索引

### 交付物（本周的核心产出）

| 文件 | 对应 | 内容 |
|---|---|---|
| **`day1.py`** | D1~D5 | **主脚本**。5 个函数体是自己写的，其余是脚手架 |
| `prompt_compare.md` | D2 | system 有没有用的对照实验（n=5×2 组） |
| `multiturn_notes.md` | D3 | 多轮对话与历史管理（含 `role` 写错的坑） |
| `structured_output_notes.md` | D4 ★ | 结构化输出（含 2×2 对照） |
| `params_notes.md` | D5 | `temperature` / `max_tokens` / `finish_reason` |

### 参考与工具

| 文件 | 作用 |
|---|---|
| `answer/day1_answer.py` | **参考实现**。自己写不出来时对照用（不是入口） |
| `_set_key.py` | 安全地把 Key 写进 `.env`（不显示、不进历史、自动去引号） |
| `practice_train_loop/` | 训练循环记忆练习（**和 Week3 无关**，随时可做） |

### 知识点讲解（换机器重看有用）

| 文件 | 讲什么 |
|---|---|
| `_syntax_d4.py` | D4 里那些看不懂的语法：`**kw`、`except as e`、f-string 花括号、`or ""` |
| `_json_intro.py` | `json` 模块：JSON 是文本、dict 是对象，`loads`/`dumps`，两种失败长什么样 |
| `_re_d4_only.py` | `re` 模块：只讲 D4 用到的那一行，拆成 4 块 |
| `_diag_thinking.py` | 思考模式：为什么 `max_tokens` 会被思考 token 吃光 |

### 实验证据脚本（md 里的数据都能重跑复现）

| 文件 | 复现什么 |
|---|---|
| `_diag_temp0.py` | `temperature=0` 的确定性（n=10）→ `params_notes.md` 第一节 |
| `_diag_length_contract.py` | 长度契约的降幅 → `multiturn_notes.md` 第六节 |
| `_diag_d4_grid.py` | 措辞×约束的 2×2 网格 → `structured_output_notes.md` 第三节 |
| `_diag_d3_context.py` | 为什么不传历史就答不出指代 → `multiturn_notes.md` 第二节 |

---

## 三、`day1.py` 里有什么

```powershell
python week3\day1.py --check        # 自检（不发请求）
python week3\day1.py --only N       # 只跑第 N 天（N=1~5）
python week3\day1.py --all          # 全部
```

| 段落 | 对应 | 会看到 |
|---|---|---|
| `check_env` | — | 五项自检 + 出错时的中文诊断（脚手架） |
| `d1_single` | D1 | 一次对话 + token 用量 |
| `d2_prompt` | D2 | 同一问题，**有/无 system** 各跑 5 次 |
| `d3_multi` | D3 | 3 轮对话 + history 长度 |
| `d4_structured` | D4 ★ | **`response_format` 强制 JSON** + 正则兜底 |
| `d5_params` | D5 | `temperature` / `max_tokens` 的影响 |

**为什么它比手册的三行示例长**：第一次配 API 最容易撞 401/404/连接失败，
原版示例只会甩一个 traceback，看不出哪一步错了。这里把每一步摊开，
出错直接说「改哪个变量」。

> **⚠️ 后来发现这个脚手架给多了** —— D4 那 5 轮卡的全是脚手架语法
> （`**kw`、参数顺序、引号），不是知识点。见 `notes/log.md` 的 Week3 小结。

---

## 四、本周实测到的关键数据

| 发现 | 数据 | 出处 |
|---|---|---|
| **system 是「输出契约」，不是「人设」** | 明确措辞时软约束 5/5；含糊时只有 1/5，失败方式全是套 markdown 代码块 | `prompt_compare.md` / `structured_output_notes.md` |
| **`response_format` 只管语法、不管 schema** | 5 次调用的字段名和结构各不同（`name`/`scores`/多出 `type`） | `structured_output_notes.md` 第四节 |
| **`max_tokens` 把思考 token 算在内** | 思考**开**时 `max_tokens=100` → 正文 **0 字符**；思考**关**时 50 → 88 字符（被截断） | `params_notes.md` 第二节 / `_diag_thinking.py` |
| **`temperature=0` 高度确定** | 同一问题连发 10 次，**逐字相同** | `params_notes.md` 第一节 / `_diag_temp0.py` |
| **长度契约有复利** | `completion_tokens` 降 94%，末轮 `prompt_tokens` 降 92% | `multiturn_notes.md` 第六节 |

---

## 五、D6 / D7 的产出要求

| 天 | 主题 | 交付物 |
|---|---|---|
| D6 | 保存与整理 | **本文件** + 脚本整理 |
| D7 | 收尾自查 | 能解释模型的**输入与输出** |

**考核重点**：能**改变输入和参数**、**保存结果**，并**解释模型的输入与输出**。
不是「会调用 API」——那谁都会。

---

## 六、每天结束时

```powershell
cd E:\agent
git add .
git commit -m "week3: dayX ..."
git push
```

**然后往 `notes/log.md` 写三行**（做了 / 卡了 / 解了）。
第 6 周汇报第 3 页和面试的「你遇到最难的问题」都从这里取。

> ⚠️ **提交前先 `git status` 确认看不到 `.env`。** 它一旦进了 git 历史，
> 删 commit 也删不干净 —— 只能去厂商后台吊销重发。
