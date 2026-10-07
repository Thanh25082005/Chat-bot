# Tài liệu sử dụng OLPAI Chatbot

Tài liệu này hướng dẫn cài đặt, cấu hình, chạy và sử dụng OLPAI Chatbot. Ứng dụng gồm một giao diện web Flask và một lớp trung gian gọi đến API chat tương thích với OpenAI.

## 1. Yêu cầu

- Python 3.10 trở lên nếu chạy trực tiếp. Docker sử dụng Python 3.12.
- Một API key còn hiệu lực.
- Nhà cung cấp API phải hỗ trợ endpoint `POST /chat/completions`, định dạng `messages` của OpenAI và streaming.
- Git chỉ cần thiết nếu muốn tải mã nguồn bằng lệnh `git clone`.

Ứng dụng không gửi API key xuống trình duyệt. Key chỉ được đọc ở backend từ biến môi trường `API_KEY`.

## 2. Cài đặt và chạy trên máy

### Linux/macOS

```bash
git clone https://github.com/Thanh25082005/Chat-bot.git
cd Chat-bot

python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

cp temp.env .env
```

### Windows PowerShell

```powershell
git clone https://github.com/Thanh25082005/Chat-bot.git
cd Chat-bot

py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt

Copy-Item temp.env .env
```

Mở `.env` và điền thông tin API trước khi khởi động. Không commit file `.env` lên Git.

```dotenv
API_BASE_URL="https://token-api.fpt.ai/v1"
API_KEY="your-api-key"
MODEL="gemma-3-27b-it,gemma-4-26B-A4B-it"
```

Chạy ứng dụng:

```bash
python app.py
```

Mở <http://localhost:5000> trên trình duyệt.

## 3. Cấu hình API

| Biến | Bắt buộc | Ý nghĩa |
|---|---:|---|
| `API_BASE_URL` | Không | URL gốc của API tương thích OpenAI. Ứng dụng tự nối thêm `/chat/completions`. Mặc định là `https://token-api.fpt.ai/v1`. |
| `API_KEY` | Có | Khóa xác thực gửi trong header `Authorization: Bearer ...`. |
| `MODEL` | Có | Một hoặc nhiều model, phân tách bằng dấu phẩy. Model đầu tiên là mặc định và các model còn lại được dùng dự phòng khi gặp HTTP 429. |

`API_BASE_URL` phải là URL gốc, không thêm `/chat/completions`. Ví dụ:

```dotenv
# FPT AI
API_BASE_URL="https://token-api.fpt.ai/v1"
API_KEY="your-fpt-key"
MODEL="gemma-3-27b-it,gemma-4-26B-A4B-it"

# OpenRouter
API_BASE_URL="https://openrouter.ai/api/v1"
API_KEY="your-openrouter-key"
MODEL="google/gemma-4-26b-a4b-it:free"

# Ollama hoặc máy chủ OpenAI-compatible nội bộ
API_BASE_URL="http://localhost:11434/v1"
API_KEY="ollama"
MODEL="llama3.2"
```

Tên model phải đúng với tên mà nhà cung cấp API hỗ trợ. Danh sách model trong `MODEL` được hiển thị ở menu chọn model trên giao diện.

## 4. Cách sử dụng giao diện

1. Nhập câu hỏi vào ô nhập ở cuối trang và nhấn **Enter** hoặc nút gửi.
2. Nhấn **Shift + Enter** để xuống dòng mà không gửi tin nhắn.
3. Chọn một model trong menu ở góc trên bên phải. Lựa chọn này được lưu trong trình duyệt.
4. Chọn một câu hỏi gợi ý ở màn hình chào để gửi nhanh.
5. Nhấn **🔄 Phiên mới** để xóa ngữ cảnh phiên hiện tại và bắt đầu cuộc trò chuyện mới.
6. Nhấn **📜 Lịch sử** để xem các phiên đã lưu. Phiên cũ ở chế độ chỉ đọc; muốn chat tiếp, hãy bấm **Phiên mới**.
7. Có thể xóa từng phiên trong bảng lịch sử.

Phản hồi được hiển thị theo luồng ngay khi model trả dữ liệu. Nội dung Markdown cơ bản được hỗ trợ gồm code block, `inline code`, in đậm, in nghiêng và xuống dòng.

### Giới hạn token

Thanh tiến trình ước lượng token bằng công thức khoảng 4 ký tự cho một token. Mỗi phiên có giới hạn giao diện là 2.000 token. Khi chạm giới hạn, ô nhập bị khóa và cần tạo phiên mới. Đây là giới hạn phía giao diện, không phải hạn mức của nhà cung cấp API.

Lịch sử chat được lưu trong `localStorage` của trình duyệt hiện tại. Xóa dữ liệu trang hoặc đổi trình duyệt sẽ làm mất lịch sử đó.

## 5. Chạy bằng Docker

Tạo `.env` ở thư mục gốc như phần cấu hình, sau đó chạy:

```bash
docker compose up -d --build
```

Truy cập <http://localhost:5000>. Xem log và dừng dịch vụ bằng:

```bash
docker compose logs -f
docker compose down
```

Chạy thủ công không dùng Compose:

```bash
docker build -t olpai-chatbot:latest .
docker run -d \
  --name olpai-chatbot \
  --restart unless-stopped \
  -p 5000:5000 \
  --env-file .env \
  olpai-chatbot:latest
```

Container chạy Gunicorn với hai worker và tám thread mỗi worker. Dùng Docker/Gunicorn khi triển khai; `python app.py` phù hợp cho phát triển cục bộ.

## 6. Kiểm tra API key

Script `check_key.py` gọi endpoint `/models`, sau đó thử chat với từng model trong biến `MODEL`:

```bash
.venv/bin/python check_key.py
# hoặc kiểm tra một key khác
.venv/bin/python check_key.py sk-example
```

Lệnh này tạo request thật đến nhà cung cấp và có thể tiêu tốn hạn mức. Không ghi API key trực tiếp vào Git hoặc chia sẻ log chứa key.

## 7. API của ứng dụng

### `GET /`

Trả về giao diện web chatbot.

### `POST /chat`

Nhận JSON gồm danh sách tin nhắn và model:

```json
{
  "model": "gemma-3-27b-it",
  "messages": [
    {"role": "user", "content": "Xin chào"}
  ]
}
```

Phản hồi là `text/event-stream`. Mỗi dòng `data: ...` chứa một chunk theo định dạng Chat Completions; sự kiện `data: [DONE]` đánh dấu kết thúc. Có thể kiểm tra bằng `curl`:

```bash
curl -N http://localhost:5000/chat \
  -H 'Content-Type: application/json' \
  -d '{"model":"gemma-3-27b-it","messages":[{"role":"user","content":"Xin chào"}]}'
```

Backend chỉ chấp nhận model nằm trong biến `MODEL`. Nếu model gửi từ trình duyệt không hợp lệ, model mặc định sẽ được dùng.

## 8. Xử lý lỗi thường gặp

| Hiện tượng | Cách kiểm tra |
|---|---|
| `401 Unauthorized` | Kiểm tra `API_KEY`, quyền của key và đúng nhà cung cấp trong `API_BASE_URL`. |
| `404 Not Found` | Đảm bảo `API_BASE_URL` là URL gốc và không lặp `/v1` hoặc `/chat/completions`. |
| Model không tồn tại | Kiểm tra chính xác tên model và cập nhật biến `MODEL`. |
| HTTP 429 | Model đang bị giới hạn lượt dùng. Backend sẽ thử các model còn lại trong `MODEL`; nếu tất cả đều bị giới hạn, hãy chờ rồi thử lại. |
| Không mở được trang | Kiểm tra tiến trình có chạy ở cổng 5000 và cổng Docker có ánh xạ `5000:5000`. |
| Container thiếu cấu hình | Đảm bảo file `.env` tồn tại cạnh `docker-compose.yml`, sau đó chạy lại `docker compose up -d --build`. |
| Phản hồi quá chậm | Backend có timeout kết nối 10 giây và timeout khi không nhận chunk 45 giây. Kiểm tra mạng, API provider và log bằng `docker compose logs -f`. |

## 9. Cấu trúc chính

```text
app.py                 Backend Flask, proxy API và SSE
templates/index.html   Giao diện, JavaScript và quản lý lịch sử
static/icon/           Logo giao diện
check_key.py           Kiểm tra key và model
temp.env               Mẫu cấu hình không chứa key thật
Dockerfile             Image production chạy Gunicorn
docker-compose.yml     Cấu hình chạy container
requirements.txt       Thư viện Python
```

## 10. Lưu ý bảo mật

- Chỉ lưu key thật trong `.env` hoặc secret manager của môi trường triển khai.
- Không đưa `.env` vào commit, Docker image hoặc ảnh chụp màn hình log.
- Nếu key từng bị lộ, hãy thu hồi và tạo key mới ngay.
- Ứng dụng hiện chưa có đăng nhập, phân quyền hoặc giới hạn request ở lớp Flask. Khi công khai Internet, nên đặt sau reverse proxy HTTPS và bổ sung cơ chế xác thực/rate limit phù hợp.
