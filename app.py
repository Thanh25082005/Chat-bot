import os
import json
import time
import logging
import requests
from flask import Flask, render_template, request, Response, stream_with_context
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
log = logging.getLogger("olpai")

API_URL = "https://token-api.fpt.ai/v1/chat/completions"
API_KEY = os.getenv("API_KEY")
# MODEL in .env is a comma-separated list; the first one is the default
MODELS = [m.strip() for m in (os.getenv("MODEL") or "").split(",") if m.strip()]
MODEL = MODELS[0] if MODELS else None


@app.route("/")
def index():
    return render_template("index.html", models=MODELS)


@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    messages = data.get("messages", [])
    model = data.get("model")
    if model not in MODELS:
        model = MODEL

    payload = {
        "model": model,
        "messages": messages,
        "temperature": 1,
        "max_tokens": 2048,
        "top_p": 1,
        "top_k": 40,
        "presence_penalty": 0,
        "frequency_penalty": 0,
        "stream": True,
    }

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}",
    }

    def sse_error(msg):
        return f"data: {json.dumps({'error': msg}, ensure_ascii=False)}\n\n"

    def generate():
        start = time.time()
        first = None
        try:
            # (connect timeout, max silence between chunks)
            with requests.post(API_URL, headers=headers, json=payload, stream=True, timeout=(10, 45)) as resp:
                log.info("upstream status=%s headers_in=%.1fs", resp.status_code, time.time() - start)
                if resp.status_code != 200:
                    body = resp.text[:300]
                    log.warning("upstream error %s: %s", resp.status_code, body)
                    yield sse_error(f"API lỗi {resp.status_code}: {body}")
                    return
                for line in resp.iter_lines():
                    if not line:
                        continue
                    decoded = line.decode("utf-8")
                    if not decoded.startswith("data: "):
                        continue
                    chunk = decoded[6:]
                    if first is None:
                        first = time.time() - start
                        log.info("first chunk after %.1fs", first)
                    if chunk == "[DONE]":
                        yield "data: [DONE]\n\n"
                        break
                    yield f"data: {chunk}\n\n"
                log.info("done total=%.1fs", time.time() - start)
        except requests.exceptions.Timeout:
            log.warning("upstream timeout after %.1fs (first chunk: %s)", time.time() - start, first)
            yield sse_error("API phản hồi quá chậm (timeout). Vui lòng thử lại.")
        except requests.exceptions.RequestException as e:
            log.warning("upstream request failed: %r", e)
            yield sse_error("Không kết nối được tới API. Vui lòng thử lại.")

    return Response(
        stream_with_context(generate()),
        mimetype="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
