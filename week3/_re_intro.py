"""re 模块入门 —— 就用 D4 那个真实场景讲。"""
import re
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# ============ 这是模型可能返回的东西（真实格式）============
model_output = '''好的，我帮你抽取出来了：

```json
{
  "姓名": "张小明",
  "科目": "数学",
  "分数": 88
}
```

希望有帮助！'''

print("=" * 72)
print("第 1 步：先看原始文本长什么样（注意有换行）")
print("=" * 72)
print(repr(model_output))
print()
print("行数:", len(model_output.splitlines()))

# ============ 派生：不用 re，用最笨的办法 ============
print()
print("=" * 72)
print("第 2 步：不用 re 行不行？—— 用字符串方法硬抠")
print("=" * 72)
i = model_output.find("{")
j = model_output.rfind("}")
print(f"  第一个 {{ 在位置 {i}")
print(f"  最后一个 }} 在位置 {j}")
print(f"  抠出来: {model_output[i:j+1]!r}")
print()
print("  ★ 对于这个例子——能行！但很脆：")
print("    · 如果模型在 JSON 后面又提到别的花括号，rfind 就抠错了")
print("    · 如果文本里先说「格式是 {...}」然后再给真的 JSON，find 就抠错了")

# ============ 用 re ============
print()
print("=" * 72)
print("第 3 步：用 re.search 找「花括号之间的内容」")
print("=" * 72)

print("\n--- 忘了 re.S 会怎样 ---")
m_no_s = re.search(r"\{.*\}", model_output)
print(f"  re.search 返回: {m_no_s!r}")
print("  ← 返回 None！【完全没匹配到】，连一行都没匹配上")
print("    原因：JSON 的 { 后面紧跟的就是换行，而默认 . 不匹配换行，")
print("          所以匹配在第一个字符之后就失败了")
print()
print("  ★★ 这一步的真正危险在这里：")
try:
    m_no_s.group(0)
except AttributeError as e:
    print(f"     直接调 .group(0) → AttributeError: {e}")
print("     你会以为是自己正则写错了，其实是漏了 re.S")
print()
print("  ★ 所以正则兜底的正确写法必须判空：")
print("     m = re.search(r'\\{.*\\}', text, re.S)")
print("     data = json.loads(m.group(0)) if m else None")
print("                                      ↑★ 这个 if m else None 不能省")

print("\n--- 加上 re.S 之后 ---")
m = re.search(r"\{.*\}", model_output, re.S)
print(f"  匹配到: {m.group(0)!r}")
print("  ← 整个多行 JSON 都拿到了")

# ============ 拆解那个模式 ============
print()
print("=" * 72)
print("第 4 步：拆解 r\"\\{.*\\}\" 这个模式")
print("=" * 72)
parts = [
    ("r\"...\"", "raw string（原始字符串）—— 让 \\ 不被 Python 先处理一层"),
    ("{", "普通字符，但 { } 在正则里有特殊含义，所以要写成 \\{ \\}"),
    ("\\{", "转义后的「左花括号」，表示【字面意义上的】左花括号"),
    (".", "【任意一个字符】—— 这是正则的核心符号"),
    ("*", "【重复前一个符号 0 次或多次】"),
    (".*", "任意多个任意字符 = 中间什么都行"),
    ("\\}", "转义后的右花括号"),
    ("re.S", "标志位：让 . 也能匹配【换行符】。没有它，遇到换行就停"),
]
for pat, desc in parts:
    print(f"  {pat:<10} {desc}")
print()
print("  合起来读：『一个左花括号，中间随便什么（包括换行），到一个右花括号』")

# ============ 常用函数 ============
print()
print("=" * 72)
print("第 5 步：re 最常用的四个函数")
print("=" * 72)
text = "张三 88 分，李四 92 分，王五 76 分"
print(f"  文本: {text}\n")
first = re.search(r"\d+", text).group(0)
allnum = re.findall(r"\d+", text)
subbed = re.sub(r"\d+", "X", text)
print(f"  re.search(r'\\d+', text)     -> {first}   （找【第一个】匹配）")
print(f"  re.findall(r'\\d+', text)    -> {allnum}   （找【全部】）")
print(f"  re.sub(r'\\d+', 'X', text)   -> {subbed}   （替换）")
print(f"  re.match(...)  只能从【开头】匹配，一般不用，容易踩坑")
print()
print("  search 和 findall 是最常用的两个。D4 用 search。")

# ============ 常见符号速查 ============
print()
print("=" * 72)
print("第 6 步：正则符号速查（先认这几个就够）")
print("=" * 72)
table = [
    (".", "任意一个字符（除了换行，除非加 re.S）"),
    ("*", "前一个符号 0 次或多次"),
    ("+", "前一个符号 1 次或多次"),
    ("?", "前一个符号 0 次或 1 次"),
    ("\\d", "一个数字 0-9"),
    ("\\w", "一个字母/数字/下划线"),
    ("\\s", "一个空白（空格/制表/换行）"),
    ("[]", "字符集合，如 [abc] 匹配 a 或 b 或 c"),
    ("{}", "重复次数，如 \\d{3} 匹配三个数字  ← 注意和字面花括号区分！"),
    ("()", "分组，把匹配的一部分单独拿出来"),
    ("^", "行首"),
    ("$", "行尾"),
]
for sym, desc in table:
    print(f"  {sym:<6} {desc}")
