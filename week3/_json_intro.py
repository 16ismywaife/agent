"""json 模块是什么 —— 用"你已经在做的事"讲。

一句话：json 负责在【文本】和【Python 对象】之间来回转换。

D4 的处境：
    模型返回的是一串【文本】：  '{"姓名": "张小明", "分数": 88}'
    你想当【字典】用：          data["姓名"]  → "张小明"

中间那一步就是 json.loads()。
"""
import json
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

print("=" * 74)
print("① 先分清两个东西：JSON 是【文本格式】，dict 是【Python 对象】")
print("=" * 74)

# 这是一串【文本】（字符串）—— 长得像字典，但它不是字典
as_text = '{"姓名": "张小明", "分数": 88}'
# 这是一个真正的【字典】
as_dict = {"姓名": "张小明", "分数": 88}

print(f"  as_text 的类型 = {type(as_text).__name__}")
print(f"  as_dict 的类型 = {type(as_dict).__name__}")
print()
print("  ★ 两者长得几乎一样，但完全不同：")
print("     as_text 是一串【字符】，Python 不知道里面有结构")
print("     as_dict 是【字典】，能用键取值")

print()
print("=" * 74)
print("② json.loads —— 文本 → Python 对象（loads = load string）")
print("=" * 74)
data = json.loads(as_text)
print(f"  json.loads('{{...}}')  ->  {data}")
print(f"  type                   ->  {type(data).__name__}")
print(f"  data['姓名']            ->  {data['姓名']}      ← 现在能按键取值了")
print()
print("  ★ 为什么必须转：模型只能吐【文本】。")
print("     它没法直接给你一个 Python 字典 —— 它只会打字。")
print("     所以拿到文本后，你要自己转成能用的东西。")

print()
print("  反过来也有一对（你在做输出时会用到）：")
print(f"     json.dumps({{'a': 1}})     ->  {json.dumps({'a': 1})!r}    （对象 → 文本，dumps = dump string）")
print(f"     json.dumps({{'a': 1}}, ensure_ascii=False)  -> {json.dumps({'a': 1}, ensure_ascii=False)!r}")
print("        ↑ 这个参数让中文正常显示，不然会变成 \\uXXXX")
print(f"     中文不加参数的后果： {json.dumps({'姓名': '张小明'})!r}")

print()
print("=" * 74)
print("③ 报错的时候长什么样（D4 会遇到）")
print("=" * 74)
print("  模型如果套了代码块，json.loads 会失败：")
bad = '```json\n{"姓名": "张小明"}\n```'
print(f"    输入: {bad!r}")
try:
    json.loads(bad)
except json.JSONDecodeError as e:
    print(f"    ❌ JSONDecodeError: {e}")
    print(f"       ↑ 报错说第 1 行第 1 个字符就不是 JSON 开头")
    print(f"         因为第一个字符是 ` 而不是 {{")
print()
print("  空字符串也会失败：")
try:
    json.loads("")
except json.JSONDecodeError as e:
    print(f"    输入: ''  ->  ❌ JSONDecodeError: {e}")
    print(f"       ↑ 这就是 D1 那个坑：max_tokens 太小 → 正文是空字符串 → 这里报错")
    print(f"         你会以为是格式问题，其实是正文根本没生成出来")

print()
print("=" * 74)
print("④ 读到 Python 里是什么类型（JSON 类型 ↔ Python 类型）")
print("=" * 74)
table = [
    ('{"a": 1}', "对象 object", "dict", json.loads('{"a": 1}')),
    ('[1, 2, 3]', "数组 array", "list", json.loads('[1, 2, 3]')),
    ('"你好"', "字符串 string", "str", json.loads('"你好"')),
    ('88', "数字 number", "int", json.loads('88')),
    ('3.14', "数字 number", "float", json.loads('3.14')),
    ('true', "布尔 boolean", "bool", json.loads('true')),
    ('null', "空 null", "None", json.loads('null')),
]
print(f"  {'JSON 写法':<14}{'JSON 叫法':<16}{'Python 类型':<12}值")
print("  " + "-" * 68)
for src, name, pytype, val in table:
    print(f"  {src:<14}{name:<16}{pytype:<12}{val!r}")
print()
print("  ★ 容易踩的：JSON 里的 true/false/null 是小写，")
print("     而 Python 里是 True/False/None（首字母大写）。互转时它会自动处理。")
