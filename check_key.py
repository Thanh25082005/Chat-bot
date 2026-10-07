"""Kiểm tra API key (theo API_BASE_URL trong .env) còn hoạt động không.

Cách dùng:
    .venv/bin/python check_key.py            # dùng API_KEY trong .env
    .venv/bin/python check_key.py sk-xxxx    # kiểm tra một key khác
"""
import os
import sys
import requests
from dotenv import load_dotenv

load_dotenv()

BASE_URL = (os.getenv("API_BASE_URL") or "https://token-api.fpt.ai/v1").rstrip("/")

key = sys.argv[1] if len(sys.argv) > 1 else os.getenv("API_KEY")
if not key:
    sys.exit("❌ Không tìm thấy API_KEY trong .env và không truyền key vào.")

models = [m.strip() for m in (os.getenv("MODEL") or "").split(",") if m.strip()]
headers = {"Authorization": f"Bearer {key}"}
print(f"API: {BASE_URL}")
print(f"Key: {key[:6]}…{key[-4:]} (dài {len(key)} ký tự)")

try:
    r = requests.get(f"{BASE_URL}/models", headers=headers, timeout=15)
except requests.exceptions.RequestException as e:
    sys.exit(f"❌ Không kết nối được tới API: {e}")

if r.status_code == 401:
    sys.exit(f"❌ Key KHÔNG hợp lệ (401): {r.text[:200]}")
if r.status_code != 200:
    sys.exit(f"⚠️  API trả về {r.status_code}: {r.text[:200]}")

print("✅ Key hợp lệ.")
available = [m.get("id") for m in r.json().get("data", [])]
if available:
    print(f"Model khả dụng ({len(available)}): {', '.join(available)}")

# Gọi thử chat với từng model trong .env
for model in models:
    try:
        r = requests.post(
            f"{BASE_URL}/chat/completions",
            headers=headers,
            json={"model": model, "messages": [{"role": "user", "content": "hi"}], "max_tokens": 5},
            timeout=30,
        )
        status = "✅" if r.status_code == 200 else f"❌ {r.status_code}: {r.text[:150]}"
    except requests.exceptions.RequestException as e:
        status = f"❌ lỗi kết nối: {e}"
    print(f"  chat {model}: {status}")
