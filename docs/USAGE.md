# Hướng dẫn sử dụng và cấu hình

## 1. Yêu cầu

- Python 3.10 trở lên nếu chạy trực tiếp. Image Docker dùng Python 3.12.
- Một API key còn hiệu lực từ nhà cung cấp hỗ trợ Chat Completions và streaming.
- Git nếu muốn clone mã nguồn.

## 2. Cài đặt chạy trực tiếp

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

Mở `.env`, thay giá trị mẫu bằng cấu hình thật rồi chạy:

```bash
python app.py
```

Truy cập <http://localhost:5000>.

## 3. Cấu hình biến môi trường

```dotenv
API_BASE_URL="https://token-api.fpt.ai/v1"
API_KEY="your-api-key"
MODEL="gemma-3-27b-it,gemma-4-26B-A4B-it"
```

| Biến | Bắt buộc | Mô tả |
|---|---:|---|
| `API_BASE_URL` | Không | URL gốc của API. Ứng dụng tự nối `/chat/completions`; mặc định là FPT AI. |
| `API_KEY` | Có | Key được gửi ở header `Authorization: Bearer ...`. |
| `MODEL` | Có | Một hoặc nhiều model, phân tách bằng dấu phẩy. Model đầu tiên là mặc định. |

Không thêm `/chat/completions` vào `API_BASE_URL`. Ví dụ endpoint khác:

```dotenv
# OpenRouter
API_BASE_URL="https://openrouter.ai/api/v1"
API_KEY="your-openrouter-key"
MODEL="google/gemma-4-26b-a4b-it:free"

# Ollama hoặc server nội bộ tương thích OpenAI
API_BASE_URL="http://localhost:11434/v1"
API_KEY="ollama"
MODEL="llama3.2"
```

Tên model phải khớp với nhà cung cấp. `.env` bị loại khỏi Git và Docker context; không đưa key thật vào `temp.env`.

## 4. Sử dụng giao diện

1. Gõ câu hỏi rồi nhấn **Enter** hoặc nút gửi.
2. Nhấn **Shift + Enter** để xuống dòng.
3. Chọn model ở góc trên bên phải. Lựa chọn được ghi nhớ trong trình duyệt.
4. Nhấn một câu hỏi gợi ý để gửi nhanh.
5. Nhấn **🔄 Phiên mới** để xóa ngữ cảnh hiện tại và bắt đầu phiên khác.
6. Nhấn **📜 Lịch sử** để xem hoặc xóa các phiên đã lưu.

Phiên cũ chỉ đọc. Muốn chat tiếp, hãy tạo phiên mới. Lịch sử nằm trong `localStorage`, vì vậy sẽ mất khi xóa dữ liệu trang hoặc đổi trình duyệt.

### Token và phản hồi

Thanh token dùng ước lượng khoảng 4 ký tự/token, tối đa 2.000 token cho mỗi phiên ở giao diện. Khi đầy, ô nhập bị khóa và cần bấm **Phiên mới**. Phản hồi được stream ngay khi API trả chunk và hỗ trợ Markdown cơ bản như code block, `inline code`, in đậm và in nghiêng.

## 5. Kiểm tra API key

Script này gọi `/models` rồi gửi một request thử đến từng model trong `MODEL`, vì vậy có thể tiêu tốn hạn mức:

```bash
.venv/bin/python check_key.py
.venv/bin/python check_key.py sk-example
```

Không ghi key thật vào lệnh, commit hoặc log công khai.

## 6. Gọi API nội bộ bằng curl

```bash
curl -N http://localhost:5000/chat \
  -H 'Content-Type: application/json' \
  -d '{"model":"gemma-3-27b-it","messages":[{"role":"user","content":"Xin chào"}]}'
```

Kết quả là `text/event-stream`; đọc các dòng `data: ...` đến khi gặp `data: [DONE]`.

## 7. Xử lý lỗi

| Lỗi | Cách xử lý |
|---|---|
| `401 Unauthorized` | Kiểm tra `API_KEY`, quyền key và `API_BASE_URL`. |
| `404 Not Found` | Dùng URL gốc, không lặp `/v1` hoặc `/chat/completions`. |
| Model không tồn tại | Kiểm tra chính xác tên trong `MODEL`. |
| HTTP 429 | Backend thử lần lượt các model còn lại; nếu vẫn lỗi, chờ nhà cung cấp bỏ giới hạn. |
| Không vào được `localhost:5000` | Kiểm tra tiến trình hoặc mapping cổng Docker. |
| Timeout | Kiểm tra mạng/API provider; timeout kết nối là 10 giây và timeout giữa các chunk là 45 giây. |

## 8. Bảo mật

- Chỉ lưu key thật trong `.env` hoặc secret manager.
- Nếu key từng bị lộ, thu hồi và tạo key mới.
- Khi công khai Internet, đặt ứng dụng sau HTTPS reverse proxy và bổ sung xác thực/rate limit.
