"""re 模块是什么 —— 只讲 D4 用到的那两个东西，不讲别的。

D4 里你只用到一行 re：
    re.search(r"\\{.*\\}", 文本, re.S)

这一行有 3 个组成部分，加上 re 本身是什么，一共 4 件事。就这 4 件。
"""
import re
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

print("=" * 74)
print("① re 是什么？—— 在文本里「按形状」找东西")
print("=" * 74)
print("""
Python 自带的正则表达式模块（标准库，不用装）。

re 用在哪：你知道【要找的东西长什么形状】，但不知道【它具体是什么】。

  用 in 就行：   "姓名" in "他叫张小明，姓名字段"     ← 找固定字符串
  要用 re：      在模型返回的那坨废话里，找「一对花括号夹着的东西」
                 ← 你不知道内容是什么，但知道它的【形状】是 { ... }
""")

text = "好的，我帮你抽取出来了：\n```json\n{\n  \"姓名\": \"张小明\",\n  \"分数\": 88\n}\n```\n希望有帮助！"
print(f"  真实例子（模型返回的原文）：")
print(f"    {repr(text)}")
print(f"  ↑ 前后全是废话，中间才是你要的。但你【没法用 in 找】—— 因为内容每次都不一样。")

print()
print("=" * 74)
print("② re.search(模式, 文本) —— 找【第一个】匹配，找不到返回 None")
print("=" * 74)
print("""
search = 搜索。它返回一个「匹配对象」，不是直接返回内容。
要拿内容得调 .group(0)。
""")
m = re.search(r"姓名", text)
print(f"  m = re.search(r'姓名', 文本)")
print(f"  m            ->  {m}          ← 匹配对象，不是字符串")
print(f"  m.group(0)   ->  {m.group(0)!r}      ← 这才是匹配到的那段文字")
print()
print("  ★ 找不到时：")
m2 = re.search(r"不存在的词", text)
print(f"    re.search(r'不存在的词', 文本)  ->  {m2}")
print(f"    返回 None —— 所以直接 m2.group(0) 会崩：")
try:
    m2.group(0)
except AttributeError as e:
    print(f"      AttributeError: {e}")
print(f"    ★ 这就是 D4 里那个 if m else None 存在的原因")

print()
print("=" * 74)
print("③ 模式 r\"\\{.*\\}\" 逐字拆解")
print("=" * 74)
chars = [
    ('r"..."', '原始字符串。让 \\ 不被 Python 先吃掉一层（正则里要写很多 \\，不加 r 会很痛苦）'),
    ('\\{',      '一个【字面的】左花括号。（{ 在正则里有特殊含义，所以要转义）'),
    ('.',       '【任意一个字符】—— 正则最核心的符号'),
    ('*',       '前面的符号重复【0 次或多次】'),
    ('.*',      '任意多个任意字符 = 中间是什么都行'),
    ('\\}',      '一个【字面的】右花括号'),
]
for pat, desc in chars:
    print(f"  {pat:<8}{desc}")
print()
print("  合起来读：")
print("    「一个左花括号  →  中间随便什么  →  一个右花括号」")
print()
m3 = re.search(r"\{.*\}", text, re.S)
print(f"  套在真实文本上：")
print(f"    m3.group(0)  ->  {m3.group(0)!r}")

print()
print("=" * 74)
print("④ re.S —— 让 . 也能匹配【换行符】。这是最容易漏的一个")
print("=" * 74)
print("""
默认情况下 . 匹配「任意字符，但【不包括换行】」。

而模型返回的 JSON 几乎总是多行的：
    {
      "姓名": "张小明"      ← { 后面紧跟的就是一个换行
    }
""")
no_s = re.search(r"\{.*\}", text)              # 忘写 re.S
with_s = re.search(r"\{.*\}", text, re.S)      # 写了 re.S
print(f"  忘了 re.S： re.search(r'\\{{.*\\}}', 文本)      ->  {no_s}")
print(f"              ↑ 返回 None！【完全没匹配到】，连一行都没匹配上")
print(f"              原因：{{ 后面紧跟换行，. 不匹配换行 → 第一步就失败")
print()
print(f"  有了 re.S： re.search(r'\\{{.*\\}}', 文本, re.S)  ->  匹配成功")
print(f"              {with_s.group(0)!r}")
print()
print("  ★★ 为什么这个坑特别危险：")
print("     返回 None 之后你调 .group(0)，报的是：")
print("       AttributeError: 'NoneType' object has no attribute 'group'")
print("     报错【完全没提 re.S】→ 你会以为是自己正则写错了，然后去改正则")
print("     但正则本身没错，是漏了一个标志位。")
print()
print("  ★ 正确写法必须判空：")
print("     m = re.search(r\"\\{.*\\}\", 文本, re.S)")
print("     data = json.loads(m.group(0)) if m else None")
print("                                    ↑ 这个判空不能省")

print()
print("=" * 74)
print("小结：这一行拆成 4 块")
print("=" * 74)
print("""  re.           → 在文本里按形状找东西（标准库）
  search(...)   → 找第一个匹配；找不到返回 None，所以要判空
  r"\\{.*\\}"     → 一个左花括号 + 中间随便什么 + 一个右花括号
  , re.S        → 让 . 也能匹配换行（多行 JSON 必须加）

  ★ 你只在 D4 用这一行。不用学整个 re 模块。
""")
