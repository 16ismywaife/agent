"""Week5 · 最小版：整个模块就三件事 —— 建表 / 记一笔 / 查出来

★ 只有两个 TODO，加起来 7 行。整个文件这么短，你能一眼看完。
   正式版（带命令行、三张报表）在 call_log.py，等 D4 再说，现在不用管它。

跑法：
    D:\\anaconda\\envs\\agent\\python.exe week5\\call_log_min.py

跑完你应该看到 3 行记录，其中 1 行是失败的（除零）。
"""
import os
import sqlite3
import time
from datetime import datetime, timezone

DB = "logs/min.db"

SCHEMA = """
CREATE TABLE IF NOT EXISTS calls (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    ts         TEXT    NOT NULL,
    tool       TEXT    NOT NULL,
    success    INTEGER NOT NULL,
    elapsed_ms REAL    NOT NULL
);
"""


# ======================= 你的两个函数（共 7 行）=======================

def initialize(conn):
    """TODO ①  建表

    就三件事：
        conn.executescript(SCHEMA)   # 执行上面那段建表语句（可以一次跑多句）
        conn.commit()                # ★ 不提交，改动不生效
        return conn                  # 方便链式调用
    """
    conn.executescript(SCHEMA)
    conn.commit()
    return conn


def insert_call(conn, row):
    """TODO ②  写一行进表

    四件事：
        写 INSERT 语句，列顺序：ts, tool, success, elapsed_ms
        值用 ? 占位符 —— ★ 永远别用 f-string 拼 SQL
        conn.execute(语句, 参数元组)     # 参数从 row 里取：row["tool"] / row["ts"] ...
        conn.commit()
    """
    conn.execute(
        "INSERT into calls (ts, tool, success, elapsed_ms) VALUES (?, ?, ?, ?)",
        (row["ts"], row["tool"], row["success"], row["elapsed_ms"]),
    )
    conn.commit()


# ======================= 下面全是我写好的，看懂了就行 =======================

def now():
    return datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")


def record(conn, tool, fn, *args):
    """跑一次 fn，量出耗时，记进表。★ 计时只夹住 fn 本身。"""
    t0 = time.perf_counter()
    try:
        result = fn(*args)
        ok = True
    except Exception as e:          # 工具崩了也要记下来
        result, ok = e, False
    ms = (time.perf_counter() - t0) * 1000

    insert_call(conn, {
        "ts": now(),
        "tool": tool,
        "success": 1 if ok else 0,
        "elapsed_ms": round(ms, 3),
    })
    return result


def demo():
    # ★ 相对路径 "logs/min.db" 是相对【你从哪个目录运行】的，不是相对这个文件。
    #   在 PyCharm 里直接 Run，工作目录默认是脚本所在目录（week5\），
    #   数据库就会落在 week5\logs\ 里。所以这里先把目录建出来，免得报
    #   "unable to open database file"（这个报错不会告诉你是路径问题）。
    os.makedirs(os.path.dirname(DB) or ".", exist_ok=True)
    print("数据库写到: " + os.path.abspath(DB))
    conn = sqlite3.connect(DB)
    initialize(conn)

    # 用真的计算，不用模型（不花钱、不联网）
    record(conn, "calc", eval, "23*7+15")      # 1: 正常
    record(conn, "calc", eval, "6*7")          # 2: 正常
    record(conn, "calc", eval, "1/0")          # 3: 应该失败（除零）

    print("\n表里现在有：")
    for r in conn.execute("SELECT id, tool, success, elapsed_ms FROM calls"):
        print("  ", r)
    conn.close()


if __name__ == "__main__":
    try:
        demo()
    except NotImplementedError as e:
        print(f"\n⚠️  {e}")
        print("   → 先写 initialize()（3 行），再写 insert_call()（4 行）")
        print("   → 提示写在两个函数的 docstring 里")
