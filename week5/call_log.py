"""Week5 · 模块：Agent 调用日志（工具调用 → SQLite → SQL 统计）

★★ 这个文件是【骨架】。标着 TODO 的地方要你自己写。★★

分工（和 week3/day1.py、week4/agent_calc.py 一样的规矩）：
  · 外面的部分（自检 / argparse / 连接管理 / 计时器 / 打印表格）=【脚手架】，不用动。
  · 标 TODO 的三处 =【你的交付物】，D2~D4 分三天写。

按天分工：
  D2（今天）：initialize() + record()   ← 能建库、能写进一行
  D3（明天）：Report.stats_by_tool()    ← 按工具汇总
  D4（后天）：Report.slow_calls() + Report.failures()，外加补统计

用法（详见 week5/接口契约.md §4）：
  python week5\\call_log.py --check                 # 自检，不写库、不发请求
  python week5\\call_log.py --sample --report       # 灌样本数据 + 出报表（★ 零成本，验收主要看这条）
  python week5\\call_log.py --report                # 只出报表
  python week5\\call_log.py --self-test             # 用真工具跑一遍，验证日志真的记上了
  python week5\\call_log.py --add calculator --ok --ms 12.3   # 手工写一条

参考手册：4.12 SQL / 数据库

--------------------------------------------------------------------------
接口契约（动手前先读 week5/接口契约.md，别改边界）
  输入：一次工具调用的记录（tool / success / elapsed_ms / ts / args / result / error）
  输出：SQLite 单文件 + 三张报表（按工具汇总 / 慢调用 Top N / 失败清单）
  依赖：只用 Python 标准库 sqlite3（★ 零第三方依赖，考核点要可复现）
  入口：CLI 四种模式 + 可 import 的 CallLogger / log_call
--------------------------------------------------------------------------
"""
import argparse
import json
import math          # ← P95 要用 math.ceil（向上取整）
import os
import sqlite3
import statistics
import sys
import time
from contextlib import contextmanager
from datetime import datetime, timezone

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

OK = "✅"
BAD = "❌"
WARN = "⚠️"

DEFAULT_DB = os.path.join("logs", "agent_calls.db")
SAMPLE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sample_records.jsonl")
RESULT_MAX = 200          # result / error 入库前截断到这个长度（契约 §6 决策点 ①）

# 工具返回这些字样 = 失败（契约 §6 决策点 ②）
# ★ 为什么这么判：week4 的 calculator 是【返回】错误文本，不是抛异常
FAIL_MARKS = ("错误", "error", "Error", "Traceback", "没有这个工具", "不合法")

SCHEMA = """
CREATE TABLE IF NOT EXISTS calls (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    ts         TEXT    NOT NULL,
    tool       TEXT    NOT NULL,
    success    INTEGER NOT NULL,
    elapsed_ms REAL    NOT NULL,
    args       TEXT,
    result     TEXT,
    error      TEXT
);
CREATE INDEX IF NOT EXISTS idx_calls_tool ON calls(tool);
CREATE INDEX IF NOT EXISTS idx_calls_ts   ON calls(ts);
"""


def head(t):
    print("\n" + "=" * 62)
    print(t)
    print("=" * 62)


# ============================================================
# 以下到「你的交付物」为止，全是脚手架，不用改
# ============================================================


def connect(db_path=DEFAULT_DB):
    """连上数据库。文件不存在会自动建；目录不存在会先建目录。"""
    d = os.path.dirname(os.path.abspath(db_path))
    os.makedirs(d, exist_ok=True)
    conn = sqlite3.connect(db_path, timeout=5)
    conn.execute("PRAGMA journal_mode=WAL")     # 允许"边写边读"
    conn.row_factory = sqlite3.Row              # 让查询结果能按列名取（row["tool"]）
    return conn


def now_iso():
    """当前时间，ISO8601 带时区。

    ★ 为什么不写 sqlite 的 CURRENT_TIMESTAMP：它是 UTC 且不带时区标记，
      报表里显示出来会和你本地时间差 8 小时 —— 属于"看起来正常但是错的"。
    """
    return datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")


def looks_failed(result_or_exc):
    """这次调用算不算失败（契约 §6 决策点 ②）。"""
    if isinstance(result_or_exc, BaseException):
        return True
    text = "" if result_or_exc is None else str(result_or_exc)
    return any(m in text for m in FAIL_MARKS)


def truncate(v, n=RESULT_MAX):
    if v is None:
        return None
    s = str(v)
    return s if len(s) <= n else s[:n] + "…(截断)"


class CallTimer:
    """一次调用的计时器。★ 计时只夹住【工具真正执行】的那一段。

    为什么 not 用 time.time()：系统对时/夏令时会让差值算成负数，
    所以计时一律用 time.perf_counter()（单调时钟）。
    """

    def __init__(self, tool, args=None):
        self.tool = tool
        self.args = args
        self.t0 = None
        self.elapsed_ms = None

    def stop(self, result_or_exc):
        """结束计时，返回要入库的一条记录（dict）—— 这部分脚手架写好了。"""
        self.elapsed_ms = (time.perf_counter() - self.t0) * 1000.0 if self.t0 else 0.0
        failed = looks_failed(result_or_exc)
        return {
            "ts": now_iso(),
            "tool": self.tool,
            "success": 0 if failed else 1,
            "elapsed_ms": round(self.elapsed_ms, 3),
            "args": truncate(json.dumps(self.args, ensure_ascii=False)) if self.args is not None else None,
            "result": None if failed else truncate(result_or_exc),
            "error": truncate(result_or_exc) if failed else None,
        }


class CallLogger:
    """记一条工具调用。两种用法（契约 §1.3）：

        with CallLogger() as lg:
            t = lg.begin("calculator", {"expression": "(23*7+15)/2"})
            r = calculator("(23*7+15)/2")          # ← 你原本的代码，一行不动
            lg.record(t, r)

    或者一步到位：
        r = log_call("calculator", calculator, expression="(23*7+15)/2")
    """

    def __init__(self, db_path=DEFAULT_DB):
        self.db_path = db_path
        self.conn = None

    # ---- 脚手架：连接生命周期 ----
    def __enter__(self):
        self.conn = connect(self.db_path)
        initialize(self.conn)
        return self

    def __exit__(self, *exc_info):
        if self.conn:
            self.conn.close()
            self.conn = None
        return False

    def begin(self, tool, args=None):
        """开始计时（脚手架）。"""
        t = CallTimer(tool, args)
        t.t0 = time.perf_counter()
        return t

    def record(self, timer, result_or_exc):
        """结束计时并落盘（→ TODO ②）。返回工具原本的结果，方便链式调用。"""
        row = timer.stop(result_or_exc)
        insert_call(self.conn, row)
        return result_or_exc


# ---------------------------- TODO ① ----------------------------
def initialize(conn):
    """建表 + 建索引（幂等：跑多少次都不会坏）。

    要做三件事：
      1. 用 conn.executescript(SCHEMA) 执行上面那份建表语句
         （executescript 能一次执行多句，普通 execute 一次只能一句）
      2. conn.commit()  —— ★ 不提交，改动不生效（手册 4.12 里那句"必须提交"）
      3. 返回 conn 自己，方便链式写

    验收（自己跑一遍看）：
      python week5\\call_log.py --self-test
      → 应该打印 OK 建表，并且 sqlite3 里能看到 calls 表
    """
    # TODO: 在这里写你的代码（提示：三行就够）
    conn.executescript(SCHEMA)
    conn.commit()
    return conn


# ---------------------------- TODO ② ----------------------------
def insert_call(conn, row):
    """把一条记录写进 calls 表。

    要做四件事：
      1. 写 INSERT 语句，用 ? 占位符 —— ★ 永远别用 f-string 拼 SQL（SQL 注入 + 引号地狱）
         列顺序：ts, tool, success, elapsed_ms, args, result, error
      2. 参数从 row 这个 dict 里取：row["tool"] / row["success"] / … （worker 见 CallTimer.stop）
      3. conn.execute(语句, 参数元组)
      4. conn.commit()

    边界（D3 自查会用到）：
      · 不存在的列名 → 报错，正好说明你在写 SQL 时要对齐上面的表结构
      · 同一秒写多条 → id 自增，不冲突

    验收：
      python week5\\call_log.py --add calculator --ok --ms 12.3
      python week5\\call_log.py --report       ← 能看到刚写的这条
    """
    # TODO: 在这里写你的代码
    conn.execute(
        "INSERT into calls (ts, tool, success, elapsed_ms,args,result,error) VALUES (?, ?, ?, ?,?,?,?)",
        (row["ts"], row["tool"], row["success"], row["elapsed_ms"], row["args"], row["result"], row["error"]),
    )
    conn.commit()


# ---------------------------- TODO ③ ----------------------------
class Report:
    """三张报表。★ 这里考的 SQL，不是 Python。

    全部通过 self.q(sql, params) 执行：
        rows = self.q("SELECT tool, COUNT(*) AS n FROM calls GROUP BY tool")
    返回的是 sqlite3.Row 列表，按列名取：row["tool"] / row["n"]。
    """

    def __init__(self, db_path=DEFAULT_DB):
        self.conn = connect(db_path)

    def q(self, sql, params=()):
        """脚手架：执行一条查询，返回所有行。"""
        return self.conn.execute(sql, params).fetchall()

    def close(self):
        self.conn.close()

    # ---------------- D3 ----------------
    def stats_by_tool(self):
        """① 按工具汇总：每个工具 调了几次 / 成功率% / 平均耗时 / P95 耗时。

        目标输出（每行一个 dict）：
            {"tool": "calculator", "n": 12, "rate": 91.7, "avg_ms": 11.3, "p95_ms": 24.8}

        要用的 SQL 知识（手册 4.12）：
          GROUP BY tool          —— 按工具分组
          COUNT(*) AS n          —— 计数
          AVG(success)*100       —— ★ success 是 0/1，它的【平均数就是成功率】，乘 100 变百分比
          AVG(elapsed_ms)        —— 平均耗时
          ROUND(x, 1)            —— 保留 1 位小数
          ORDER BY n DESC        —— 调用次数多的排前面

        ★ P95 怎么算 —— 先【用 Python 想清楚】，再翻译成 SQL（别反过来）：
          把耗时从小到大排成一列。P95 有两种常见定义，本模块【统一用 nearest-rank】：

              第 k 名 = 排序后第 ceil(0.95 × n) 个，名次从 1 数起

              n=3  → ceil(2.85) = 3 → 第 3 个（也就是最大的那个）
              n=10 → ceil(9.5)  = 10
              n=12 → ceil(11.4) = 12
              n=20 → ceil(19)   = 19

          SQL 里对应：ORDER BY elapsed_ms LIMIT 1 OFFSET (第k名 - 1)
              → OFFSET 从 0 数起，所以 n=12 时 offset = 11
              → 偏移量先查 COUNT(*) 算好再传进去（查两次，简单直接，别硬凑成一条 SQL）

          边界：
              · n = 1 → k = 1，offset = 0
              · n = 0 → 这个工具根本没有行，GROUP BY 也不会给你这一组
              · ★ 先手算几个 n 验证你的公式，再写 SQL。公式错的话，
                报表会给你一个【看起来很正常】的错数字 —— Week3/Week4 踩过 4 次同类坑

        边界（要自己拿数据试）：
          · 某个工具只调了 1 次 → P95 就是它自己
          · 某个工具从没成功过 → 成功率 0.0
          · 表还是空的 → 返回空列表，不要崩

        > **★ 更正（2026-10-20）**：这份骨架早先写过一句
        > 「AVG(success)*100 在 SQLite 里会取整」—— **那是错的，别信**。
        > 实测（12 次里 10 次成功）：`AVG(success)` = 0.8333…，`ROUND(AVG(success)*100,1)` = **83.3**。
        > SQLite 的 AVG 返回 REAL，不做整型截断，所以 `AVG(success)*100` 直接就能用。
        > **记一笔**：这是"凭印象写断言"的一次翻车 —— 断言要么自己跑一遍，要么标注"未验证"。
        """
        # TODO: 在这里写你的代码
        rows = self.q("""
                SELECT tool, COUNT(*) AS n,
                       ROUND(AVG(success)*100, 1) AS rate,
                       ROUND(AVG(elapsed_ms), 1)  AS avg_ms
                FROM calls
                GROUP BY tool
                ORDER BY n DESC
            """)

        out = []
        for r in rows:
                n = r["n"]  # 这个工具调了几次
                k = math.ceil(0.95 * n)  # 第 95% 名次（从 1 数）
                p95 = self.q(
                    "SELECT elapsed_ms FROM calls WHERE tool = ? "
                    "ORDER BY elapsed_ms LIMIT 1 OFFSET ?",
                    (r["tool"], k - 1),  # OFFSET 从 0 数，所以减 1
                )[0]["elapsed_ms"]
                out.append({
                    "tool": r["tool"],
                    "n": n,
                    "rate": r["rate"],
                    "avg_ms": r["avg_ms"],
                    "p95_ms": p95,
                })
        return out

    # ---------------- D4 ----------------
    def slow_calls(self, limit=10):
        """② 最慢的 N 次：按耗时倒序，返回 [{"ts","tool","elapsed_ms"}, …]。

        SQL 知识：ORDER BY elapsed_ms DESC LIMIT ?
        ★ LIMIT 也能用 ? 占位符（不要用 f-string 拼数字）
        """
        # TODO: 在这里写你的代码
        raise NotImplementedError("slow_calls 还没写（D4 的任务）")

    def failures(self, limit=50):
        """③ 失败清单：success = 0 的那些，返回 [{"ts","tool","elapsed_ms","error"}, …]。

        SQL 知识：WHERE success = ?  （传 0 进去）
        ★ 为什么不用 WHERE success = 0 直接写死：手册 4.12 那张表讲的就是
          "占位符"这件事 —— 参数化的写法换任何条件都不用改语句结构。
        """
        # TODO: 在这里写你的代码
        raise NotImplementedError("failures 还没写（D4 的任务）")


# ============================================================
# 下面是脚手架 + 入口，不用改
# ============================================================


def log_call(tool, fn, **kwargs):
    """一步到位版：执行 fn(**kwargs) 并记一条日志。"""
    with CallLogger() as lg:
        timer = lg.begin(tool, kwargs or None)
        try:
            result = fn(**kwargs)
        except BaseException as e:          # 工具抛异常也要记下来（契约 §1.3）
            lg.record(timer, e)
            raise
        return lg.record(timer, result)


def print_table(title, rows, cols):
    head(title)
    if not rows:
        print(f"{WARN} 没有数据 —— 先灌样本（--sample）或者跑（--self-test）")
        return
    print("  " + "".join(str(c[0]).ljust(c[2]) for c in cols))
    print("  " + "-" * sum(c[2] for c in cols))
    for r in rows:
        print("  " + "".join(str(r[c[0]] if r[c[0]] is not None else "-").ljust(c[2]) for c in cols))
    print(f"\n  （共 {len(rows)} 行）")


def do_report(db_path, out_path=None):
    """出三张报表。★ 每张单独兜底：某一张还没写（TODO），另外两张照样能看。

    这样 D3 写完表① 就能立刻验收，不用等 D4 把表②③也写完。
    """
    rep = Report(db_path)
    try:
        lines = []

        # ---------- 表 ① ----------
        try:
            rows = rep.stats_by_tool()
        except NotImplementedError:
            head("报表 ① · 按工具汇总")
            print(f"{WARN} stats_by_tool() 还没写（D3 的任务）")
            rows = []
        if rows:
            cols = [("tool", "工具", 14), ("n", "次数", 8), ("rate", "成功率%", 10),
                    ("avg_ms", "平均ms", 10), ("p95_ms", "P95ms", 10)]
            print_table("报表 ① · 按工具汇总", rows, cols)
            for r in rows:
                lines.append("| {tool} | {n} | {rate} | {avg_ms} | {p95_ms} |".format(**dict(r)))

        # ---------- 表 ② ----------
        try:
            rows = rep.slow_calls(10)
        except NotImplementedError:
            head("报表 ② · 最慢的 10 次")
            print(f"{WARN} slow_calls() 还没写（D4 的任务）")
            rows = []
        if rows:
            cols = [("ts", "时间", 26), ("tool", "工具", 14), ("elapsed_ms", "耗时ms", 10)]
            print_table("报表 ② · 最慢的 10 次", rows, cols)

        # ---------- 表 ③ ----------
        try:
            rows = rep.failures()
        except NotImplementedError:
            head("报表 ③ · 失败清单")
            print(f"{WARN} failures() 还没写（D4 的任务）")
            rows = []
        if rows:
            cols = [("ts", "时间", 26), ("tool", "工具", 14), ("elapsed_ms", "耗时ms", 10),
                    ("error", "错误", 40)]
            print_table("报表 ③ · 失败清单", rows, cols)

        if out_path:
            with open(out_path, "w", encoding="utf-8") as f:
                f.write("# 调用日志报表（由 week5/call_log.py --report 生成）\n\n")
                f.write("| 工具 | 次数 | 成功率% | 平均ms | P95ms |\n|---|---|---|---|---|\n")
                f.write("\n".join(lines) + "\n")
            print(f"\n{OK} 报表已写入 {out_path}")
    finally:
        rep.close()


def load_sample(db_path):
    """把 sample_records.jsonl 灌进库（脚手架）。

    ★ 样本是【造】出来的，不是真跑出来的 —— 这一点会在报表头注明，
      免得以后自己都忘了这堆数字不是实测（Week4 那条教训：数字长得正常 ≠ 是真的）。
    """
    if not os.path.exists(SAMPLE):
        print(f"{BAD} 找不到样本文件：{SAMPLE}")
        return 0
    n = 0
    with CallLogger(db_path) as lg:
        for line in open(SAMPLE, encoding="utf-8"):
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            rec = json.loads(line)
            insert_call(lg.conn, {
                "ts": rec["ts"],
                "tool": rec["tool"],
                "success": rec["success"],
                "elapsed_ms": rec["elapsed_ms"],
                "args": rec.get("args"),
                "result": rec.get("result"),
                "error": rec.get("error"),
            })
            n += 1
    print(f"{OK} 灌入 {n} 条样本记录 → {db_path}")
    print(f"{WARN} 注意：这些是【造】的样本，不是实测数据")
    return n


def do_self_test(db_path):
    """用真工具跑一遍，验证"日志真的记上了"（脚手架 + TODO ① ②）。

    这条是 D2 的验收：日志写在工具外面，工具本身一行没改。
    """
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    try:
        from week4.agent_calc import calculator, get_time
    except Exception as e:
        print(f"{WARN} import 不到 week4/agent_calc.py（{type(e).__name__}）—— 跳过真工具测试")
        calculator = lambda expression: str(eval(expression, {"__builtins__": {}}, {}))
        get_time = lambda: now_iso()

    head("自检 · 用真工具跑一遍，看有没有记上")
    cases = [
        ("calculator", {"expression": "(23*7+15)/2"}, "应该成功"),
        ("calculator", {"expression": "23 * 7"}, "带空格的表达式"),
        ("calculator", {"expression": "1/0"}, "应该失败（除零）"),
        ("get_time", {}, "无参数工具"),
    ]
    for tool, kwargs, note in cases:
        with CallLogger(db_path) as lg:
            timer = lg.begin(tool, kwargs or None)
            try:
                fn = {"calculator": calculator, "get_time": get_time}[tool]
                out = fn(**kwargs)
            except Exception as e:
                out = e
            lg.record(timer, out)
        failed = looks_failed(out)
        flag = BAD if failed else OK
        print(f"  {flag} {tool}({kwargs}) → {str(out)[:60]!r}   ({note})")
    print(f"\n{OK} 一共写了 {len(cases)} 条到 {db_path}")
    print("   → 现在跑：python week5\\call_log.py --report")


def do_add(db_path, tool, ok, ms, error=None):
    """手工写一条（脚手架）—— 用来测边界。"""
    with CallLogger(db_path) as lg:
        insert_call(lg.conn, {
            "ts": now_iso(), "tool": tool, "success": 1 if ok else 0,
            "elapsed_ms": float(ms), "args": None,
            "result": "手工写入" if ok else None,
            "error": error or (None if ok else "手工写入的失败记录"),
        })
    print(f"{OK} 写入 1 条：tool={tool} success={1 if ok else 0} elapsed_ms={ms}")


def check():
    head("自检 · 环境")
    ok = True
    print(f"{OK} Python {sys.version.split()[0]}（需要 3.11+，本机 {sys.executable}）")
    try:
        print(f"{OK} sqlite3 可用，版本 {sqlite3.sqlite_version}（标准库自带，不用装）")
    except Exception as e:
        print(f"{BAD} sqlite3 不可用：{e}")
        ok = False
    print(f"{OK} 样本文件：{'在' if os.path.exists(SAMPLE) else '还没生成'}")
    print(f"{OK} 默认库路径：{DEFAULT_DB}（logs/ 已 gitignore，不会提交）")
    print(f"{OK} 第三方依赖：无（契约 §3 要求零依赖）")
    print(f"\n{'✅ 自检通过' if ok else '❌ 自检没过'}")
    return 0 if ok else 2


def main():
    ap = argparse.ArgumentParser(description="Week5 · Agent 调用日志（工具调用 → SQLite → SQL 统计）")
    ap.add_argument("--check", action="store_true", help="只自检环境")
    ap.add_argument("--sample", action="store_true", help="灌样本数据（造的数据）")
    ap.add_argument("--report", action="store_true", help="出三张报表")
    ap.add_argument("--self-test", action="store_true", help="用真工具跑一遍，验证日志记上了")
    ap.add_argument("--add", metavar="TOOL", help="手工写一条记录")
    ap.add_argument("--ok", action="store_true", help="配合 --add：这条是成功的")
    ap.add_argument("--ms", type=float, default=10.0, help="配合 --add：耗时毫秒")
    ap.add_argument("--error", help="配合 --add：错误信息")
    ap.add_argument("--db", default=DEFAULT_DB, help=f"数据库路径（默认 {DEFAULT_DB}）")
    ap.add_argument("--out", help="把报表①写到文件")
    args = ap.parse_args()

    if args.check:
        return check()

    try:
        if args.sample:
            load_sample(args.db)
        if args.self_test:
            do_self_test(args.db)
        if args.add:
            do_add(args.db, args.add, args.ok, args.ms, args.error)
        if args.report or args.out:
            do_report(args.db, args.out)
        if not any([args.sample, args.self_test, args.add, args.report, args.out]):
            ap.print_help()
            print(f"\n{WARN} 什么都没做 —— 至少给一个动作，比如 --sample --report")
    except NotImplementedError as e:
        print(f"\n{WARN} {e}")
        print("   → D2：先写 initialize() 和 insert_call()")
        print("   → D3：再写 Report.stats_by_tool()")
        print("   → D4：再写 slow_calls() / failures()")
        return 3
    return 0


if __name__ == "__main__":
    sys.exit(main())
