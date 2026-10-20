"""样板：往 SQLite 里建表 + 记一笔（逐行讲解版）

★ 这个文件跟 Week5 的模块没关系，是【样板】——
  场景故意换成"记跑步"，就是为了让你照着结构改写，而不是照抄。

跑法：
    D:\\anaconda\\envs\\agent\\python.exe week5\\_demo_sqlite.py

跑完你会看到：表建好了、3 行数据、还有一句查询结果。
"""
import sqlite3

# ---------------------------------------------------------------
# 第 0 步：连数据库
# ---------------------------------------------------------------
conn = sqlite3.connect("logs/demo_runs.db")
#     ↑ 连一个文件。文件不存在会自动创建（连目录都没有才会报错）

# ---------------------------------------------------------------
# 第 1 步：建表  ← ★ 这就是你要写的 initialize() 在干的事
# ---------------------------------------------------------------
conn.executescript("""
CREATE TABLE IF NOT EXISTS runs (
    id       INTEGER PRIMARY KEY AUTOINCREMENT,   -- 编号，自动 +1，不用你管
    day      TEXT    NOT NULL,                    -- 哪天跑的，如 '2026-10-20'
    km       REAL    NOT NULL,                    -- 跑了多少公里
    minutes  REAL    NOT NULL                     -- 花了多少分钟
);
""")
# ↑ executescript = 一次执行【多句】SQL；普通 execute 一次只能一句
# ↑ IF NOT EXISTS = 表已经存在就不报错（所以这步可以重复跑，不会坏）

conn.commit()
# ↑ ★ 必须提交。不 commit 的话，改动只在内存里，关掉就没了
#   这一行最容易忘，而且【不报错】—— 你会以为写成功了

# ---------------------------------------------------------------
# 第 2 步：写一行  ← ★ 这就是你要写的 insert_call() 在干的事
# ---------------------------------------------------------------
row = {"day": "2026-10-20", "km": 5.0, "minutes": 32.5}    # 假装量出来的一次

conn.execute(
    "INSERT INTO runs (day, km, minutes) VALUES (?, ?, ?)",
    #                                            ↑ 三个问号 = 三个坑，等着你填
    (row["day"], row["km"], row["minutes"]),
    # ↑ ★ 参数用一个【元组】按顺序给进去，顺序必须和问号一一对应
    #   为什么用 ? 而不是拼字符串：
    #     f"VALUES ('{row['day']}', ...)"  ← 别看它也能跑
    #     遇到带引号的内容就崩，而且能被注入（手册 4.12 那句"防 SQL 注入"）
)
conn.commit()
# ↑ 又是 commit。★ 规律：凡是【改了数据】（INSERT/UPDATE/DELETE）都要 commit；
#   光是【查】（SELECT）不用

# ---------------------------------------------------------------
# 第 3 步（可选）：多写几行，让后面查询有东西看
# ---------------------------------------------------------------
for r in [
    {"day": "2026-10-21", "km": 3.2, "minutes": 20.0},
    {"day": "2026-10-22", "km": 8.1, "minutes": 51.0},
]:
    conn.execute("INSERT INTO runs (day, km, minutes) VALUES (?, ?, ?)",
                 (r["day"], r["km"], r["minutes"]))
conn.commit()

# ---------------------------------------------------------------
# 第 4 步：查出来看
# ---------------------------------------------------------------
print("表里现在有：")
for r in conn.execute("SELECT id, day, km, minutes FROM runs"):
    print("  ", r)
#     ↑ 每行是一个元组：(1, '2026-10-20', 5.0, 32.5)
#       想按列名取的话，要先设 conn.row_factory = sqlite3.Row

print("\n统计一下：")
for r in conn.execute("SELECT COUNT(*) AS n, AVG(km) AS avg_km FROM runs"):
    print("   一共", r[0], "次，平均", round(r[1], 2), "公里")
#     ↑ COUNT = 几行；AVG = 平均值。这就是"用 SQL 做统计"的最小样子

conn.close()
# ↑ 用完关掉。不关在小脚本里没大事，但养成习惯
