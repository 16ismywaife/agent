"""安全地把 API Key 写进 .env —— 输入时屏幕上不显示任何字符。

为什么用这个而不是手打/直接编辑：
  - 手打容易多空格、少字符，而 401 报错不会告诉你"你多打了一个空格"
  - 粘贴进终端时字符会显示在屏幕上（还可能进命令历史）
  - 这个脚本用 getpass 读输入：不显示、不进历史、不落盘到别处

用法：
  python week3\\_set_key.py
"""
import getpass
import os
import re
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ENV = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".env")
ENV = os.path.normpath(ENV)

print("=" * 60)
print("把 API Key 安全地写进 .env")
print("=" * 60)
print(f"\n目标文件：{ENV}\n")

if not os.path.exists(ENV):
    print("❌ 没找到 .env。先执行：copy .env.example .env")
    sys.exit(2)

print("把 Key 粘贴过来然后回车。")
print("（屏幕上不会显示任何字符 —— 这是正常的，不是没输入进去）\n")
try:
    key = getpass.getpass("API_KEY: ")
except KeyboardInterrupt:
    print("\n已取消")
    sys.exit(1)

key = key.strip()
# 常见粘贴事故：连引号一起复制进来
if len(key) >= 2 and key[0] == key[-1] and key[0] in "\"'":
    key = key[1:-1].strip()
    print("（检测到两端有引号，已自动去掉）")

if not key:
    print("❌ 没读到内容。再跑一次，注意粘贴后要按回车。")
    sys.exit(1)

if re.search(r"\s", key):
    print("❌ Key 里含空格或换行。请重新复制（不要多选到空格）。")
    sys.exit(1)

if key.startswith("你的") or key in ("sk-xxx", "sk-xxxx"):
    print("❌ 这看起来还是占位符，不是真的 Key。")
    sys.exit(1)

# 写回 .env
with open(ENV, encoding="utf-8") as f:
    text = f.read()

if not re.search(r"(?m)^API_KEY\s*=", text):
    print("❌ .env 里没有 API_KEY= 这一行")
    sys.exit(1)

text = re.sub(r"(?m)^(API_KEY\s*=).*$", lambda m: m.group(1) + key, text, count=1)
with open(ENV, "w", encoding="utf-8") as f:
    f.write(text)

print(f"\n✅ 已写入。Key 长度 {len(key)}，开头 {key[:6]}…，结尾 …{key[-4:]}")
print("   （只显示首尾用于核对，完整 Key 不会打印）")

# 顺手确认不在 git 里
try:
    import subprocess
    repo = os.path.dirname(ENV)
    r = subprocess.run(["git", "check-ignore", "-q", ".env"], cwd=repo, capture_output=True)
    if r.returncode == 0:
        print("✅ .env 已被 .gitignore 排除（安全）")
    else:
        print("❌ 警告：.env 没有被 git 忽略！先修 .gitignore 再用")
        sys.exit(1)
except Exception:
    pass

print("\n下一步（自检，不花钱，不发请求）：")
print("   python week3\\day1.py --check")
