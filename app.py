import os
import json
import time
import logging
import requests
from flask import Flask, render_template, request, Response, send_from_directory, stream_with_context
from dotenv import load_dotenv

load_dotenv()

# Vercel serves public/ through its CDN. Flask has a small local fallback so
# the same /icon/... URL also works with `python app.py` and Docker.
app = Flask(__name__, static_folder=None)
logging.basicConfig(level=logging.INFO)
log = logging.getLogger("olpai")

# Any OpenAI-compatible provider; defaults to FPT AI
API_BASE_URL = (os.getenv("API_BASE_URL") or "https://token-api.fpt.ai/v1").rstrip("/")
API_URL = f"{API_BASE_URL}/chat/completions"
API_KEY = os.getenv("API_KEY")
# MODEL in .env is a comma-separated list; the first one is the default
MODELS = [m.strip() for m in (os.getenv("MODEL") or "").split(",") if m.strip()]
MODEL = MODELS[0] if MODELS else None


@app.route("/")
def index():
    return render_template("index.html", models=MODELS)


@app.route("/icon/<path:filename>")
def icon(filename):
    return send_from_directory(os.path.join(app.root_path, "public", "icon"), filename)


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

    def open_stream():
        # On 429 (rate limit) fall back to the other configured models
        candidates = [model] + [m for m in MODELS if m != model]
        for m in candidates:
            payload["model"] = m
            # (connect timeout, max silence between chunks)
            resp = requests.post(API_URL, headers=headers, json=payload, stream=True, timeout=(10, 45))
            log.info("upstream model=%s status=%s", m, resp.status_code)
            if resp.status_code != 429:
                return resp
            log.warning("model %s rate-limited: %s", m, resp.text[:300])
            resp.close()
        return None

    def generate():
        start = time.time()
        first = None
        try:
            resp = open_stream()
            if resp is None:
                yield sse_error("Model đang quá tải (giới hạn lượt dùng). Vui lòng thử lại sau ít phút.")
                return
            with resp:
                log.info("upstream headers_in=%.1fs", time.time() - start)
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
