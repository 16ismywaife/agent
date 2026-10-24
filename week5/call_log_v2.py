"""call_log_v2.py —— 从零开始，每一行都是我自己写的

规则（对 AI 也适用）：
  · 这个文件里**不允许 AI 代写代码**。AI 只能讲、只能提示，代码必须我自己敲。
  · 每完成一步，文件要能独立跑起来、能看见输出。
  · 写完一步就 commit 一次。

目标：整个文件 80 行以内，做完六件事。

  [ ] 第 1 步  建库 + 建表          → 跑完能看到 calls 表存在
  [ ] 第 2 步  记一笔（insert）     → 表里多一行
  [ ] 第 3 步  查全部（select）     → 终端打出所有记录
  [ ] 第 4 步  按工具汇总           → 4 行统计（次数/成功率/平均耗时）
  [ ] 第 5 步  打印成表格           → 好看一点，带表头和对齐
  [ ] 第 6 步  命令行参数           → python call_log_v2.py --report 能用

怎么跑（每一步都一样）：
    cd "E:\\04_脚本与代码\\agent"
    D:\\anaconda\\envs\\agent\\python.exe week5\\call_log_v2.py
"""
import sqlite3

DB="logs/v2.db"
def connect():
    return sqlite3.connect(DB)

def init(conn):
    conn.executescript("""
    CREATE TABLE IF NOT EXISTS calls (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    ts          TEXT NOT NULL,
    tool        TEXT NOT NULL,
    success     INTEGER NOT NULL,
    elapsed_ms  REAL NOT NULL
    )
    """)
    conn.commit()
    print("done")


def add(conn):
    conn.execute(
        "INSERT INTO calls(ts,tool,success,elapsed_ms) VALUES (?,?,?,?)",
        ("2026-10-23T15:45","calculator",1,12.3),
    )
    conn.commit()
    conn.executemany("INSERT INTO calls(ts,tool,success,elapsed_ms) VALUES (?,?,?,?)",
    [("2026-10-23T10:00", "calculator", 1, 8.3),
    ("2026-10-23T10:01", "calculator", 0, 0.6),
    ("2026-10-23T10:02", "get_time",   1, 0.4),
    ("2026-10-23T10:03", "calculator", 1, 12.4),]
                 )
    conn.commit()


def report(conn):
    sql="""
    SELECT tool,
    count(*) AS n,
    ROUND(AVG(success)*100,1) AS rate,
    ROUND(AVG(elapsed_ms),1) AS avg_ms
    FROM calls
    GROUP BY tool
    ORDER BY n DESC
    """
    rows=conn.execute(sql).fetchall()

    print(f"{'tool':<12}{'n':>4}{'rate':>8}{'avg_ms':>9}")
    for t,n,rate,avg in rows:
        print(f"{t:<12}{n:>4}{rate:>8}{avg:>9}")

if __name__ == "__main__":
    conn=connect()
    init(conn)
    add(conn)
    report(conn)
    conn.close()
