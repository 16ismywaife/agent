"""生成 week5/sample_records.jsonl —— 样本数据生成器（脚手架，一次性的）

★ 为什么用脚本生成而不是手写：以后要加边界数据（比如"某个工具只调 1 次"）
  改一下这里的列表重跑就行，不用手工数 JSON。

★ 这份数据是【造】的，不是实测的。目的：
    · 让报表①有多个工具、成功率不是 100%（否则看不出统计的效果）
    · 让报表③非空（含失败记录，错误信息照 week4 calculator 的真实返回格式写）
    · 覆盖边界：只调 1 次的工具、慢调用、无参工具

用法：D:\\anaconda\\envs\\agent\\python.exe week5\\_make_sample.py
"""
import io
import json
import os

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sample_records.jsonl")

# (ts, tool, success, elapsed_ms, args, result, error)
ROWS = [
    # ---------- calculator：成功 ----------
    ("2026-10-12T14:03:11+08:00", "calculator", 1, 12.4, '{"expression": "(23*7+15)/2"}', "88.0", None),
    ("2026-10-12T14:03:29+08:00", "calculator", 1, 9.8, '{"expression": "23 * 7"}', "161", None),
    ("2026-10-12T14:05:02+08:00", "calculator", 1, 11.1, '{"expression": "128*128/4"}', "4096.0", None),
    ("2026-10-13T10:12:40+08:00", "calculator", 1, 14.7, '{"expression": "2**10"}', "1024", None),
    ("2026-10-13T10:13:05+08:00", "calculator", 1, 8.3, '{"expression": "(1+2+3)*4"}', "24", None),
    ("2026-10-13T10:20:51+08:00", "calculator", 1, 120.6, '{"expression": "sum(range(10000000))"}', "49999995000000", None),
    ("2026-10-14T09:41:18+08:00", "calculator", 1, 10.2, '{"expression": "365*24*60"}', "525600", None),
    ("2026-10-14T09:44:33+08:00", "calculator", 1, 7.9, '{"expression": "100-37"}', "63", None),
    ("2026-10-15T16:02:07+08:00", "calculator", 1, 13.5, '{"expression": "(88+12)/2"}', "50.0", None),
    ("2026-10-15T16:03:44+08:00", "calculator", 1, 6.1, '{"expression": "7*7"}', "49", None),
    ("2026-10-16T11:22:19+08:00", "calculator", 1, 15.9, '{"expression": "3.14159*2*2"}', "12.56636", None),
    ("2026-10-17T15:31:02+08:00", "calculator", 1, 9.4, '{"expression": "(1024-24)/8"}', "125.0", None),
    ("2026-10-18T09:15:38+08:00", "calculator", 1, 3800.5, '{"expression": "sum(range(30000000))"}', "449999985000000", None),
    ("2026-10-18T09:16:02+08:00", "calculator", 1, 11.8, '{"expression": "6*7"}', "42", None),
    # ---------- calculator：失败（错误文本照 week4/agent_calc.py 的真实格式） ----------
    ("2026-10-13T10:21:30+08:00", "calculator", 0, 0.6, '{"expression": "1/0"}', None, "计算错误division by zero"),
    ("2026-10-17T15:32:11+08:00", "calculator", 0, 0.5, '{"expression": "sqrt(16)"}', None, "错误，含未知字符"),
    # ---------- get_time：无参工具 ----------
    ("2026-10-12T14:06:00+08:00", "get_time", 1, 0.4, "{}", "2026-10-12T14:06:00+08:00", None),
    ("2026-10-14T09:45:12+08:00", "get_time", 1, 0.3, "{}", "2026-10-14T09:45:12+08:00", None),
    ("2026-10-16T11:23:01+08:00", "get_time", 1, 0.5, "{}", "2026-10-16T11:23:01+08:00", None),
    ("2026-10-18T09:16:30+08:00", "get_time", 1, 0.3, "{}", "2026-10-18T09:16:30+08:00", None),
    # ---------- weather：★ 边界样本，本模块唯一的"只有失败"的工具 ----------
    ("2026-10-15T16:04:20+08:00", "weather", 0, 0.3, '{"city": "广州"}', None, "没有这个工具：weather"),
    ("2026-10-16T11:24:15+08:00", "weather", 0, 0.3, '{"city": "广州"}', None, "没有这个工具：weather"),
    # ---------- search：★ 边界样本，只调过 1 次（P95 == 自己） ----------
    ("2026-10-18T09:17:44+08:00", "search", 1, 245.7, '{"q": "yolov8n"}', "3 条结果", None),
]


def main():
    with io.open(OUT, "w", encoding="utf-8", newline="\n") as f:
        f.write("# 样本数据（造的数据，非实测）—— 由 week5/_make_sample.py 生成\n")
        for r in ROWS:
            f.write(json.dumps({
                "ts": r[0], "tool": r[1], "success": r[2], "elapsed_ms": r[3],
                "args": r[4], "result": r[5], "error": r[6],
            }, ensure_ascii=False) + "\n")

    from collections import Counter
    c = Counter(r[1] for r in ROWS)
    fail = Counter(r[1] for r in ROWS if r[2] == 0)
    print(f"写入 {len(ROWS)} 条 → {OUT}")
    for t, n in c.most_common():
        print(f"  {t:12s} 共 {n:2d} 次，失败 {fail.get(t, 0)} 次")
    print("\n自己先手算一遍（等下和 SQL 对账）：")
    print("  calculator P95 应该是：", sorted(r[3] for r in ROWS if r[1] == "calculator"))
    print("  get_time   P95 应该是：", sorted(r[3] for r in ROWS if r[1] == "get_time"))


if __name__ == "__main__":
    main()
