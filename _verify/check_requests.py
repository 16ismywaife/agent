"""检查 mock 服务器记录下来的真实请求体，确认协议细节传对了。"""
import json
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

path = sys.argv[1]
recs = []
with open(path, encoding="utf-8") as f:
    for line in f:
        line = line.strip()
        if line:
            recs.append(json.loads(line))

print("共记录 %d 个请求\n" % len(recs))

problems = []

# 1. 所有请求都要带 Authorization
no_auth = [i for i, r in enumerate(recs) if not r["auth"]]
if no_auth:
    problems.append("有 %d 个请求没带 Authorization 头" % len(no_auth))
else:
    print("✅ 全部请求都带 Authorization 头（api_key 真的传出去了）")

# 2. 找带 tools 的请求
tool_reqs = [r for r in recs if r["body"].get("tools")]
print("\n=== 带 tools 的请求：%d 个 ===" % len(tool_reqs))
if tool_reqs:
    b = tool_reqs[0]["body"]
    spec = b["tools"][0]["function"]
    print("  tools[0].type          =", b["tools"][0]["type"])
    print("  function.name          =", spec["name"])
    print("  function.description   =", spec["description"][:40], "…")
    print("  parameters.required    =", spec["parameters"].get("required"))
    print("  parameters.properties  =", list(spec["parameters"]["properties"].keys()))
    if b["tools"][0]["type"] != "function" or spec["name"] != "calculator":
        problems.append("tools 结构不对")
    else:
        print("  ✅ tools 结构符合 OpenAI function-calling 规范")

    # 3. 工具执行完那一轮，历史里应该有 role=tool + tool_call_id
    with_tool_result = [r for r in recs
                        if any(m.get("role") == "tool" for m in r["body"]["messages"])]
    print("\n=== 带 tool 结果的请求：%d 个 ===" % len(with_tool_result))
    if with_tool_result:
        msgs = with_tool_result[0]["body"]["messages"]
        print("  消息角色序列:", [m.get("role") for m in msgs])
        tool_msgs = [m for m in msgs if m.get("role") == "tool"]
        for tm in tool_msgs:
            print("  tool 消息 tool_call_id =", tm.get("tool_call_id"))
            print("  tool 消息 content      =", tm.get("content"))
        # 上游必须有一条 assistant 带 tool_calls
        asst_with_calls = [m for m in msgs if m.get("role") == "assistant" and m.get("tool_calls")]
        if not tool_msgs or not asst_with_calls:
            problems.append("tool 结果轮次缺少 assistant.tool_calls 或 tool_call_id")
        elif not tool_msgs[0].get("tool_call_id"):
            problems.append("tool 消息缺 tool_call_id")
        else:
            ids_match = tool_msgs[0]["tool_call_id"] in [tc["id"] for tc in asst_with_calls[0]["tool_calls"]]
            print("  ✅ tool_call_id 与 assistant.tool_calls[].id 对得上: %s" % ids_match)
            if not ids_match:
                problems.append("tool_call_id 对不上")
            # assistant 消息被回传时 tool_calls 必须还在（不能丢）
            print("  ✅ assistant.tool_calls[0].function.arguments =",
                  asst_with_calls[0]["tool_calls"][0]["function"]["arguments"])
    else:
        problems.append("没有任何一轮把 tool 结果发回去 —— agent 循环没走完")

# 4. response_format
json_reqs = [r for r in recs if (r["body"].get("response_format") or {}).get("type") == "json_object"]
print("\n=== response_format=json_object 的请求：%d 个 ===" % len(json_reqs))
if json_reqs:
    print("  ✅ response_format 被正确序列化进请求体")
else:
    problems.append("response_format 没传出去")

# 5. 参数
temps = sorted({r["body"].get("temperature") for r in recs if r["body"].get("temperature") is not None})
maxtoks = sorted({r["body"].get("max_tokens") for r in recs if r["body"].get("max_tokens") is not None})
print("\n=== 参数 ===")
print("  出现过的 temperature:", temps)
print("  出现过的 max_tokens :", maxtoks)
if temps != [0, 0.7, 1.5]:
    problems.append("temperature 三个值没都传出去: %s" % temps)
else:
    print("  ✅ temperature 0 / 0.7 / 1.5 都真的传到了请求体里")

# 6. stream
streams = [r for r in recs if r["body"].get("stream")]
print("\n=== stream=True 的请求：%d 个 ===" % len(streams))
if streams:
    print("  ✅ stream 标记被传出去")
else:
    problems.append("stream 没传出去")

# 7. 路径
paths = sorted({r["path"] for r in recs})
print("\n=== 请求路径 ===")
print(" ", paths)
if paths != ["/v1/chat/completions"]:
    problems.append("路径异常: %s" % paths)
else:
    print("  ✅ 都打在 /v1/chat/completions（base_url 拼接正确）")

print("\n" + "=" * 60)
if problems:
    print("❌ 发现问题：")
    for p in problems:
        print("  -", p)
    sys.exit(1)
print("✅ 协议层面全部正确")
