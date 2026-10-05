"""本地 OpenAI 兼容 mock 服务器 —— 只用于验证手册里的代码协议是否正确。

它实现 /v1/chat/completions 的真实协议形状（含 tool_calls 与 stream 的 SSE 分块），
让 openai SDK 真正走一遍「构造请求 → HTTP → 解析响应 → 返回对象」的全链路。

★ 它不验证「模型回答得好不好」，只验证「你的代码说得对不对」。
   真实 API 的最终验证仍需你自己的 API Key（见 verify_handbook_llm.py --real）。
"""
import json
import os
import sys
import time
import uuid
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

RECORD = os.environ.get("MOCK_RECORD", os.path.join(os.path.dirname(os.path.abspath(__file__)), "requests.jsonl"))


def _now():
    return int(time.time())


def _usage(prompt=42, completion=17):
    return {"prompt_tokens": prompt, "completion_tokens": completion, "total_tokens": prompt + completion}


def _math_answer(text):
    """从问题里抠出一个算术表达式并算出来（mock 的「业务逻辑」）。"""
    import re
    m = re.search(r"[-+*/(). \d]{3,}", text)
    if not m:
        return None
    expr = m.group(0).strip()
    try:
        return expr, eval(expr, {"__builtins__": {}}, {})
    except Exception:
        return None


def build_response(body):
    """按请求体决定 mock 的行为，返回 (response_json, is_stream)。

    规则（故意做得可预测，方便断言）：
      1. 历史里有 role=tool  → 说明工具已执行，给最终回答
      2. 带 tools 且还没调过 → 返回一个 tool_calls
      3. response_format=json_object → 返回合法 JSON
      4. 其他 → 普通文本回答
    """
    messages = body.get("messages", [])
    has_tool_result = any(m.get("role") == "tool" for m in messages)
    has_tools = bool(body.get("tools"))
    is_stream = bool(body.get("stream"))
    want_json = (body.get("response_format") or {}).get("type") == "json_object"

    user_text = ""
    for m in messages:
        if m.get("role") == "user":
            user_text = m.get("content") or ""

    if has_tool_result:
        tool_content = ""
        for m in messages:
            if m.get("role") == "tool":
                tool_content = m.get("content") or ""
        message = {
            "role": "assistant",
            "content": "工具返回的结果是 %s，这就是答案。" % tool_content,
            "tool_calls": None,
        }
        finish = "stop"
    elif has_tools:
        # mock 固定要求调用第一个工具 —— 用来验证 agent 主循环写得对不对
        tool_name = body["tools"][0]["function"]["name"]
        if tool_name == "calculator":
            found = _math_answer(user_text)
            args = {"expression": found[0]} if found else {"expression": "1+1"}
        else:
            args = {}
        message = {
            "role": "assistant",
            "content": None,
            "tool_calls": [{
                "id": "call_" + uuid.uuid4().hex[:20],
                "type": "function",
                "function": {"name": tool_name, "arguments": json.dumps(args, ensure_ascii=False)},
            }],
        }
        finish = "tool_calls"
    elif want_json:
        message = {
            "role": "assistant",
            "content": json.dumps({"姓名": "张小明", "科目": "数学", "分数": 88}, ensure_ascii=False),
            "tool_calls": None,
        }
        finish = "stop"
    else:
        message = {
            "role": "assistant",
            "content": "（mock 回答）已收到你的 %d 条消息。温度=%s，max_tokens=%s。"
                       % (len(messages), body.get("temperature"), body.get("max_tokens")),
            "tool_calls": None,
        }
        finish = "stop"

    resp = {
        "id": "chatcmpl-" + uuid.uuid4().hex[:24],
        "object": "chat.completion",
        "created": _now(),
        "model": body.get("model", "mock-model"),
        "choices": [{"index": 0, "message": message, "finish_reason": finish}],
        "usage": _usage(),
    }
    return resp, is_stream


class Handler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def log_message(self, *a):
        pass

    def _json(self, obj, status=200):
        raw = json.dumps(obj, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)

    def do_GET(self):
        if self.path.rstrip("/") in ("/health", "/v1/health"):
            self._json({"status": "ok"})
        else:
            self._json({"error": {"message": "not found"}}, 404)

    def do_POST(self):
        length = int(self.headers.get("Content-Length") or 0)
        raw = self.rfile.read(length).decode("utf-8", "replace")

        if "/chat/completions" not in self.path:
            self._json({"error": {"message": "unsupported path " + self.path}}, 404)
            return

        try:
            body = json.loads(raw)
        except Exception as e:
            self._json({"error": {"message": "bad json: %s" % e}}, 400)
            return

        with open(RECORD, "a", encoding="utf-8") as f:
            f.write(json.dumps({
                "path": self.path,
                "auth": bool(self.headers.get("Authorization")),
                "body": body,
            }, ensure_ascii=False) + "\n")

        resp, is_stream = build_response(body)
        if not is_stream:
            self._json(resp)
            return

        # ---- SSE 流式 ----
        self.send_response(200)
        self.send_header("Content-Type", "text/event-stream")
        self.send_header("Cache-Control", "no-cache")
        self.send_header("Connection", "keep-alive")
        self.end_headers()

        base = {
            "id": resp["id"], "object": "chat.completion.chunk",
            "created": resp["created"], "model": resp["model"],
        }
        content = resp["choices"][0]["message"].get("content") or ""
        pieces = [content[i:i + 6] for i in range(0, len(content), 6)] or [""]

        def send(obj):
            self.wfile.write(("data: " + json.dumps(obj, ensure_ascii=False) + "\n\n").encode("utf-8"))
            self.wfile.flush()

        send({**base, "choices": [{"index": 0, "delta": {"role": "assistant", "content": ""},
                                   "finish_reason": None}]})
        for p in pieces:
            send({**base, "choices": [{"index": 0, "delta": {"content": p}, "finish_reason": None}]})
            time.sleep(0.01)
        send({**base, "choices": [{"index": 0, "delta": {}, "finish_reason": "stop"}]})
        self.wfile.write(b"data: [DONE]\n\n")
        self.wfile.flush()


def main():
    port = int(os.environ.get("MOCK_PORT", "8799"))
    if os.path.exists(RECORD):
        os.remove(RECORD)
    srv = ThreadingHTTPServer(("127.0.0.1", port), Handler)
    print("mock server on http://127.0.0.1:%d/v1" % port, flush=True)
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
