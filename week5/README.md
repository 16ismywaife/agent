# Week5 · Agent 调用日志（工具调用 → SQLite → SQL 统计）

> **这个模块做什么**：给 Agent 每次调工具记一条账（调了什么、成没成、花了多久），
> 存进一个 SQLite 文件，然后用 SQL 查出「哪个工具最不稳、哪次最慢、失败都错在哪」。
>
> **边界**：日志是**包在工具外面的一层** —— `week4/agent_calc.py` 的工具函数一行都不改。
> 完整输入 / 输出 / 依赖 / 入口见 **[接口契约.md](接口契约.md)**（D1 交付物）。

---

## 一、现在到哪一步了（2026-10-20）

| 天 | 内容 | 状态 |
|---|---|---|
| D1 | 定模块 + 写接口契约 | ✅ [接口契约.md](接口契约.md) —— **5 个边界决策已拍板（§6）** |
| **D2** | 搭骨架 + 最小可用版本 | ◐ **骨架已给，等写 2 个函数**（见下） |
| D3 | 补核心逻辑（按工具汇总） | ⬜ |
| D4 | 补统计 + 异常处理 | ⬜ |
| D5 | 可复现性测试（三种） | ⬜ |
| D6 | README（在整体项目中的作用） | ⬜ |
| D7 | 收尾自查 | ⬜ |

### D2 要你写的只有两个函数

| 位置 | 函数 | 干什么 | 大概几行 |
|---|---|---|---|
| `call_log.py` | `initialize(conn)` | 建表 + 建索引 | **3 行** |
| `call_log.py` | `insert_call(conn, row)` | 把一条记录写进表 | **4 行** |

**其余全是脚手架**（连接管理、计时器、参数解析、打印表格、自检）—— 按 `week4/agent_calc.py` 的老规矩：脚手架管够，核心你自己写。

> D3 的 `Report.stats_by_tool()`、D4 的 `slow_calls()` / `failures()` 也已经把骨架和 SQL 提示写好了，但它们**不是今天的事**。

---

## 二、怎么跑

```powershell
# ① 环境自检（不写库、不花钱）—— 现在就能跑
D:\anaconda\envs\agent\python.exe week5\call_log.py --check

# ② 造样本数据（已经造好了，23 条，含故意的失败记录）
D:\anaconda\envs\agent\python.exe week5\_make_sample.py

# ③ 灌样本 + 出报表（★ 验收主要看这条，零成本）
D:\anaconda\envs\agent\python.exe week5\call_log.py --sample --report

# ④ 用真工具跑一遍，看日志是不是真记上了（走 week4 的 calculator / get_time，不联网）
D:\anaconda\envs\agent\python.exe week5\call_log.py --self-test

# ⑤ 手工写一条（测边界用）
D:\anaconda\envs\agent\python.exe week5\call_log.py --add calculator --ok --ms 12.3
```

> ⚠️ 现在跑 ③④⑤ 都会提示 `initialize 还没写（D2 的任务）` —— **这是对的**，不是 bug。

---

## 三、文件

| 文件 | 是什么 | 谁写的 |
|---|---|---|
| `接口契约.md` | D1 交付物：输入/输出/依赖/入口 + 5 个决策点 | AI 起草，你确认 |
| `call_log.py` | 模块本体（CLI + `CallLogger` + `Report`） | 骨架 AI，**核心你写** |
| `_make_sample.py` | 样本数据生成器（造 23 条，含失败/单次/慢调用） | AI |
| `sample_records.jsonl` | 生成出来的样本数据（**造的数据，不是实测**） | 脚本产物 |
| `report_sample.md` | 报表输出样例（D2 跑通后生成） | 脚本产物 |

**依赖：零第三方库**（只用 `sqlite3` 等标准库）—— 契约 §3 的硬要求，考核点之一是"可复现"。

---

## 四、D2 验收标准（做完自己勾）

- [ ] `--check` 通过
- [ ] `initialize()` 写完 → 库里出现 `calls` 表和两个索引（`sqlite3 logs\agent_calls.db ".schema"` 看得到）
- [ ] `insert_call()` 写完 → `--add calculator --ok --ms 12.3` 后 `--report` 能看到这条
- [ ] `--sample` 灌进的 23 条**一条不多一条不少**（`SELECT COUNT(*) FROM calls`）
- [ ] `--self-test` 里那条 `1/0` **被判成失败**（`success=0`，error 列有内容）—— 这验证了"失败判定"逻辑
- [ ] 能一句话说清：**输入是什么、输出是什么**（契约 §7 第 1 条）

---

## 五、在整体项目中的作用（★ 手册 D6 点名必须写）

Week4 的 `run_agent()` 只有"跑通 / 没跑通"两个状态。这个模块是**方向 3 评测的可观测层**：
加上它之后才有**成功率、P95 耗时、失败原因**这些能写进简历和 Week6 汇报的数字。
同时它顺带补掉简历上的 **SQL** 缺口（手册 4.12）。

---

## 六、已知前提

| 项 | 状态 |
|---|---|
| 工作目录 | `E:\04_脚本与代码\agent`（原 `E:\agent` 随盘损坏，2026-10-16） |
| 数据库文件 | `logs\agent_calls.db` —— `logs/` 已 gitignore，**不入库** |
| 需要 `.env` 吗 | ❌ **不需要**。本模块不发任何网络请求，全部离线可跑 |
| 能花 API 钱吗 | ❌ 不会。`--self-test` 走的是本地 `calculator` / `get_time`，不调 LLM |
