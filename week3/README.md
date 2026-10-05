# Week3 · 现代 AI 模型体验（大模型分支）

**本周主题**：LLM API 调用 —— Prompt、多轮对话、**结构化输出**、参数实验
**本周交付物**：LLM 调用脚本 + 参数实验记录
**文档要求**：二选一 ①视觉 YOLO ②大模型 → **你选了 ②**

---

## 开跑前：先补训练循环（如果还记不牢）

`practice_train_loop/` 是为「记不住训练循环」专门做的两个练习，**和 Week3 无关，随时可以做**：

```powershell
cd week3\practice_train_loop
python mytrain.py        # 填空：自己把 5 步写出来（不填也能跑，精度会停在 10%）
python breakdown.py      # 故意写坏：自动逐个破坏，看"缺了会怎样"（约 1 分钟）
```

详细说明见 `practice_train_loop/README.md`。

---

## D1 · 跑通第一次调用

**三步，十分钟。**

### 第 1 步：配 `.env`

```powershell
cd E:\agent
copy .env.example .env
notepad .env
```

填三个值（`.env.example` 里有国内各厂商的地址清单）：

```
API_KEY=你从厂商后台复制的密钥
BASE_URL=https://api.deepseek.com/v1
MODEL=deepseek-flash
```

> ⚠️ **`deepseek-chat` 已失效**（网上老教程还在写），用它会 404。
> 当前 DeepSeek 的模型名：`deepseek-flash`（推荐）、`deepseek-v4-pro`。
>
> **`.env` 已经被 `.gitignore` 排除**，永远不会提交。但还是建议填完跑一下自检确认。
>
> **别手打 Key** —— 多一个空格就是 401，而报错不会告诉你多打了空格：
> ```powershell
> python week3\_set_key.py     # 输入时不显示、不进命令历史
> ```

### 第 2 步：自检（不花钱）

```powershell
python week3\day1.py --check
```

五项全过再往下走：

```
✅ 找到 .env
✅ .env 已被 .gitignore 排除（安全）
✅ API_KEY 已读到：sk-xxx…xxxx（长度 35）
✅ BASE_URL = https://api.deepseek.com/v1
✅ MODEL = deepseek-flash
```

**任何一项 ❌，它会直接告诉你该改什么**，不用猜。

### 第 3 步：真跑

```powershell
python week3\day1.py            # D1 单轮对话
python week3\day1.py --all      # D1~D5 全部示例
```

---

## `day1.py` 里有什么

| 段落 | 对应 | 你会看到 |
|---|---|---|
| 环境自检 | D1 | 五项检查 + 出错时的中文诊断 |
| `d1_single` | D1 单轮 | 一次对话 + **token 用量**（影响成本） |
| `d2_prompt` | D2 Prompt | 同一问题，**有/无 system** 的输出对比 |
| `d3_multi` | D3 多轮 | 3 轮对话，并显示 **history 增长到几条** |
| `d4_structured` | D4 ★ | **`response_format` 强制 JSON** + 正则兜底两套方案 |
| `d5_params` | D5 参数 | `temperature` 0/0.7/1.5 各跑 3 次，看**输出是否相同**；`max_tokens` 的截断效果 |

**为什么它比手册里的三行示例长**：第一次配 API 最容易撞 401 / 404 / 连接失败，
原版示例只会甩一个 traceback，看不出哪一步错了。这里把每一步摊开，
出错直接说「改哪个变量」。

---

## 不用花钱也能先验证代码

`.env` 还没配、或者不想花 token 时，可以先用本地 mock 服务器验证：

```powershell
# 窗口 1
python _verify\mock_openai_server.py
# 窗口 2
python _verify\verify_handbook_llm.py
```

它会用**真实的 `openai` SDK** 打真实 HTTP，检查请求结构、`tool_calls` 配对、
`response_format`、`stream` 分块是否正确。详见 `_verify/README.md`。

---

## D2~D7 的产出要求（来自培养方案 + 手册）

| 天 | 主题 | 交付物 |
|---|---|---|
| D1 | 跑通第一次调用 | `day1.py` 跑通 + `.env` |
| D2 | Prompt 基础 | `prompt_compare.md`（3 组对比：有/无 system、有/无示例、直接问/先分析） |
| D3 | 多轮对话 | 多轮脚本 + 历史管理说明 |
| D4 | **结构化输出 ★** | JSON 提取脚本（**Agent 的地基**） |
| D5 | 参数实验 | `params_report.md`（temperature / max_tokens 的实测对比） |
| D6 | 保存与整理 | `week3/README.md` 更新 + 结果落盘 |
| D7 | 收尾自查 | 能解释模型的**输入与输出** |

**考核重点**：能**改变输入和参数**、**保存结果**，并**解释模型的输入与输出**。
不是「会调用 API」——那谁都会。

---

## 每天结束时

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
