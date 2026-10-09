"""证明：给 ask() 加的 format 参数【没有默认值】会把 D1/D2/D3 一起弄坏。"""


def ask_required(client, model, messages, fmt):        # ← 你现在的写法
    return client, model, messages, fmt


def ask_default(client, model, messages, fmt=None):    # ← 加个默认值
    return client, model, messages, fmt


def ask_star(client, model, messages, **kw):           # ← 或者用 **kw（更灵活）
    return client, model, messages, kw


# ==== 问题 1：没有默认值 → 老调用直接崩 ====
print("=" * 66)
print("问题 1：format 没有默认值")
print("=" * 66)
try:
    ask_required("c", "m", ["..."])            # D1/D2/D3 就是这么调的：3 个参数
except TypeError as e:
    print(f"  ❌ ask_required('c','m',[...])  -> TypeError: {e}")
print(f"  ✅ ask_required('c','m',[...], {{}}) -> {ask_required('c','m',[...], {})}")
print()
print("  ★ D1/D2/D3 里都是 3 个参数的调用，所以它们会全部报这个 TypeError。")
print()
print("  加默认值就没事：")
print(f"    ask_default('c','m',[...])       -> {ask_default('c','m',[...])}")
print(f"    ask_default('c','m',[...], {{}})  -> {ask_default('c','m',[...], {})}")

# ==== 问题 2：调用时参数顺序错了 ====
print()
print("=" * 66)
print("问题 2：D4 里的调用 `ask(model, prompt, format)`")
print("=" * 66)
print("  函数签名是  ask(client, model, messages, fmt)")
print("  你写的是  ask(model, prompt, format)")
print("            ↑ 第 1 个位置应该是 client，你传了 model")
print()
try:
    ask_required("mock-model", "从下面的文本中抽取…", {"type": "json_object"}, None)
    print("  （上面这行没崩是因为我的假函数不检查类型 —— 真调用会崩）")
except Exception as e:
    print(f"  {type(e).__name__}: {e}")
print()
print("  真环境里会报什么：")
print("    client 位置收到一个字符串 → 后面 client.chat 就炸")
print("    messages 位置收到一个字符串 → SDK 期望的是【列表】")
print()
print("  正确写法：ask(client, model, messages, fmt)")
print("            ↑↑↑ 前两个永远是这个顺序")

# ==== 问题 3：参数名 format 盖住了内置函数 ====
print()
print("=" * 66)
print("问题 3：参数名叫 format，盖住了 Python 内置的 format()")
print("=" * 66)
print(f"  内置 format(255, 'x')  -> {format(255, 'x')}   （255 的十六进制）")


def shadow(format):
    return format


f = shadow("我盖住了")
print(f"  但 shadow(format='我盖住了') 里，format 就是那个字符串：{f!r}")
print()
print("  ★ 不会报错，但如果你哪天想用内置的 format()，会发现它「不见了」。")
print("    换个名字就行：fmt / response_format / rf")

# ==== 推荐写法 ====
print()
print("=" * 66)
print("推荐：用 **kw（这样 D4 传 format、D5 传 temperature 都不用改函数）")
print("=" * 66)
print(f"  ask_star('c','m',[...])                          -> {ask_star('c','m',['...'])}")
print(f"  ask_star('c','m',[...], response_format={{}})     -> {ask_star('c','m',['...'], response_format={})}")
print(f"  ask_star('c','m',[...], temperature=0, max_tokens=100)")
print(f"       -> {ask_star('c','m',['...'], temperature=0, max_tokens=100)}")
print()
print("  ★ 但要注意：**kw 里收到的东西必须能原样传给 SDK。")
print("    SDK 认 response_format / temperature / max_tokens，")
print("    但不认识 extra_body（那是要单独透传的，completion() 已经帮你处理了）。")
