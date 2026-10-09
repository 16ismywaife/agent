"""D4 里那些「看不懂的语法」—— 逐个拆开，每个都能跑。

这份文件不是在讲 D4，是讲 D4 代码里用到的 Python 语法。
每个都是独立的，从上往下读。
"""
import json
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

print("=" * 74)
print("①  **kw —— 收集任意关键字参数")
print("=" * 74)
print("""
你见过的函数：参数是写死的
    def f(a, b):
        ...

**kw 是「我不知道你会传什么，都先收着」。收到的是一本字典。

    def f(**kw):        # kw 是一本字典
        print(kw)

    f(x=1, y=2)         # 打印 {'x': 1, 'y': 2}
""")


def f1(**kw):
    return kw


print(f"  f1(x=1, y=2)        -> {f1(x=1, y=2)}")
print(f"  f1()                -> {f1()}          ← 不传也行，得到空字典")
print()
print("  ★ 为什么 completion() 要这么写：")
print("     它要把你传的东西原样转交给 SDK，但事先不知道你会传几个。")
print("     你今天要传 response_format，D5 要传 temperature / max_tokens。")

print()
print("=" * 74)
print("②  **字典 —— 把字典「摊开」成关键字参数（和 ① 是一对）")
print("=" * 74)
print("""
① 是「收集进来」，② 是「摊开发出去」。同一个 **，方向相反。

    d = {"a": 1, "b": 2}
    f(**d)      # 等价于 f(a=1, b=2)
""")


def f2(a, b):
    return a + b


d = {"a": 1, "b": 2}
print(f"  f2(**{d})  -> {f2(**d)}      ← 等价于 f2(a=1, b=2)")
print()
print("  ★ 你 Week4 写 Agent 时每天都要用这个：")
print("     TOOLS_IMPL[name](**args)   # args 是模型给的参数字典")
print("     args = {'expression': '1+1'}  →  calculator(expression='1+1')")

print()
print("=" * 74)
print("③  dict(...) / .pop() / .update() —— 三个字典操作")
print("=" * 74)
print("""
completion() 里这三行：
    extra = dict(kw.pop("extra_body", {}) or {})
    extra.update(THINKING_OFF)
    ... create(..., extra_body=extra, **kw)

collections.OrderedDict 之类不管，只看普通 dict：
""")
kw = {"messages": ["..."], "response_format": {"type": "json_object"}}
print(f"  开始时 kw = {kw}")
print()
popped = kw.pop("extra_body", {})      # 取出来并从 kw 里删掉；没有就用默认值 {}
print(f"  kw.pop('extra_body', {{}})  -> {popped}")
print(f"    ↑ kw 里本来没有 extra_body，所以返回默认值 {{}}（空字典）")
print(f"      而且 kw 里也不会被删掉任何东西")
print(f"  现在的 kw = {kw}")

extra = dict(popped or {})
print()
print(f"  dict(popped or {{}})        -> {extra}")
print("    ↑ `or {}` 的作用：如果 popped 是 None 或空字典，就用 {} 顶上")
print("      （因为 extra=None 之后不能再 .update）")

extra.update({"thinking": {"type": "disabled"}})
print()
print(f"  extra.update(THINKING_OFF)  -> {extra}")
print("    ↑ update 是「合进去」：有同名键就覆盖，没有就新增")
print()
print("  ★ 为什么要 pop 出来：")
print("     kw 里的东西最后要作为 **kw 传给 SDK，而 SDK 不认 extra_body 这个参数。")
print("     所以先把它从 kw 里摘出来，单独作为一个参数传。")

print()
print("=" * 74)
print("④  except Exception as e —— 把「错误本身」接住")
print("=" * 74)
print("""
你见过的：
    try:
        ...
    except:
        print("出错了")

加 as e 之后，e 就是那个错误对象，能问它「你叫什么名字」。
""")


def f4():
    return int("这不是数字")


try:
    f4()
except Exception as e:
    print(f"  捕获到: {e}")
    print(f"  type(e)          -> {type(e)}")
    print(f"  type(e).__name__ -> {type(e).__name__}      ← 只要类名，不要那串地址")
    print(f"  str(e)           -> {str(e)}")
print()
print("  ★ 答案里那句就用到了：")
print('     print(f"json_object 不可用（{type(e).__name__}）...")')
print("     它会打印「json_object 不可用（BadRequestError）」")
print("     —— 让你知道到底是哪种错，而不是只看到'出错了'")

print()
print("=" * 74)
print("⑤  f-string 里写花括号 —— 必须双写")
print("=" * 74)
print("""
f-string 里 { } 是「占位符」的意思（要填变量进去）。
所以如果你真的想输出一个花括号，得写两遍：
    {{  ->  输出一个 {
    }}  ->  输出一个 }
""")
name = "张小明"
print(f'  单个花括号 = 占位符：f"你好 {{name}}"     -> 你好 {name}')
print(f'  双写 = 字面花括号：  f"格式：{{{{\\"姓名\\": \\"\\"}}}}"  -> 格式：{{"姓名": ""}}')
print()
print("  ★ 这就是 D4 里那行的原因：")
print("""     prompt = (f'从下面的文本中抽取信息，只输出 JSON...\\n'
               f'格式：{{"姓名": "", "科目": "", "分数": 0}}\\n\\n文本：{text}\\n')
                    ↑↑ 双写 → 输出字面的 {        ↑↑ 双写 → 输出字面的 }""")
print()
print("  ★ 有没有更简单的写法？有 —— 不用 f-string 拼，用普通引号：")
plain = '格式：{"姓名": "", "科目": "", "分数": 0}\n\n文本：' + "张小明这次数学考了 88 分。"
print(f'     {plain[:40]!r}...')
print("     但那样就要用 + 拼字符串。两种都行，f-string 双写更常见。")

print()
print("=" * 74)
print("⑥  (raw or \"\")[:160] —— or 兜底 + 切片")
print("=" * 74)
print("""
拆成两步看：
    raw or ""     如果 raw 是 None，就用 "" 顶替（不然切片会崩）
    [:160]        取前 160 个字符（防止刷屏）
""")
raw_none = None
print(f"  raw=None       时： (raw or '')      -> {(raw_none or '')!r}")
print(f"                      (raw or '')[:5]  -> {(raw_none or '')[:5]!r}    ← 不崩")
try:
    raw_none[:5]
except TypeError as e:
    print(f"  不写 or 的话：    raw[:5]          -> TypeError: {e}")
long_text = "x" * 200
print(f"  长文本切片：      ('x'*200)[:160]  -> 长度 {len(long_text[:160])}（原长 {len(long_text)}）")

print()
print("=" * 74)
print("⑦  r.choices[0].message.content —— 一层层往下取")
print("=" * 74)
print("""
这不是什么特殊语法，就是「连续取值」。用嵌套字典演示同一件事：
""")

resp = {
    "choices": [
        {"message": {"content": "你好，这是正文"}}
    ]
}
print(f"  resp                          -> {type(resp).__name__}（字典）")
print(f"  resp['choices']               -> 列表，长度 {len(resp['choices'])}")
print(f"  resp['choices'][0]            -> 第 0 个候选（字典）")
print(f"  resp['choices'][0]['message'] -> {resp['choices'][0]['message']}")
print(f"  ...[0]['message']['content']  -> {resp['choices'][0]['message']['content']!r}")
print()
print("  ★ SDK 返回的是【对象】不是字典，所以写法是 .choices 而不是 ['choices']：")
print("     resp.choices[0].message.content")
print("     ↑ 点号取属性        ↑ 方括号取列表元素")
print()
print("  ★ 报错时看【最右边那个名字】就知道断在哪一层：")
print("     AttributeError: 'NoneType' object has no attribute 'content'")
print("                      ↑ 说明 .message 是 None，不是 content 拼错了")

print()
print("=" * 74)
print("小结：这些都不难，只是【没见过】")
print("=" * 74)
print("""  **kw / **字典    收集与摊开          → Week4 写工具调用必用
  dict/pop/update  字典三个操作         → 会 .get 就会这些
  except ... as e  接住错误对象         → 能看到具体错在哪
  f"{{}}"           f-string 里写花括号 → 双写
  x or ""          空值兜底             → 防止 None 崩
  a.b[0].c         连续取值             → 就是一层层往下
""")
