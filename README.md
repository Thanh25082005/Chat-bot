# OlpAI Chatbot — HaUI

Tài liệu dự án được tổ chức trong thư mục [`docs/`](docs/): [tổng quan](docs/PROJECT.md), [hướng dẫn sử dụng](docs/USAGE.md) và [hướng dẫn Docker](docs/DOCKER.md).

Ứng dụng chatbot hỏi đáp thông minh, sử dụng mô hình ngôn ngữ lớn (LLM) **DeepSeek-V4-Flash** thông qua API của **FPT AI**, được phát triển bởi Trường Đại học Công nghiệp Hà Nội (HaUI).

---

## Mô tả chức năng

### 1. Giao diện hội thoại (Chat UI)
- Giao diện web dark mode hiện đại, thân thiện với người dùng
- Hiển thị tin nhắn theo dạng bong bóng (bubble), phân biệt rõ người dùng và AI
- Hỗ trợ cuộn lịch sử hội thoại mượt mà

### 2. Streaming response
- Phản hồi của AI được hiển thị theo từng ký tự ngay khi nhận được, giống ChatGPT
- Con trỏ nhấp nháy trong lúc AI đang trả lời

### 3. Hội thoại đa lượt (Multi-turn)
- Lưu toàn bộ lịch sử hội thoại trong phiên làm việc
- AI nhớ ngữ cảnh các tin nhắn trước để trả lời nhất quán

### 4. Render Markdown cơ bản
- Hiển thị khối code với nền tối (```` ``` ```)
- Hỗ trợ `inline code`, **in đậm**, *in nghiêng*

### 5. Gợi ý câu hỏi
- Màn hình chào hiển thị 4 câu hỏi gợi ý để người dùng bắt đầu nhanh
- Nhấn vào gợi ý để gửi ngay

### 6. Nhập liệu thông minh
- Nhấn **Enter** để gửi tin nhắn
- Nhấn **Shift + Enter** để xuống dòng
- Ô nhập tự động giãn theo nội dung (tối đa 5 dòng)

### 7. Phiên mới
- Nút **🔄 Phiên mới** để reset hội thoại về trạng thái ban đầu (phiên cũ vẫn được lưu trong lịch sử)

### 8. Lịch sử chat
- Nút **📜 Lịch sử** mở panel liệt kê các phiên chat đã lưu trong `localStorage` của trình duyệt
- Xem lại và xóa từng phiên; phiên cũ chỉ ở chế độ xem, không gửi thêm tin nhắn

### 9. Chọn model
- Dropdown chọn model trên giao diện; danh sách lấy từ biến `MODEL` trong `.env` (phân tách bằng dấu phẩy, model đầu tiên là mặc định)
- Lựa chọn được ghi nhớ trong trình duyệt; backend chỉ chấp nhận model nằm trong danh sách

### 10. Giới hạn token mỗi phiên
- Thanh tiến trình hiển thị số token đã dùng / **2000** (ước lượng ~4 ký tự/token), đổi màu cảnh báo từ 75% và nguy hiểm ở 100%
- Khi đạt giới hạn: hiện thông báo, khóa ô nhập và gợi ý bắt đầu phiên mới

### 11. Xử lý lỗi & timeout
- Timeout kết nối 10s, tối đa 45s im lặng giữa các chunk
- Hiển thị gợi ý "đang chờ phản hồi" sau 3s, thông báo lỗi rõ ràng khi API lỗi, timeout hoặc mất kết nối
- Backend ghi log thời gian phản hồi đầu tiên và tổng thời gian

### 12. Bảo mật API Key
- API Key được lưu trong file `.env`, xử lý hoàn toàn ở backend
- Frontend không bao giờ tiếp xúc trực tiếp với API Key
- File `.env` bị loại khỏi Docker image (`.dockerignore`), chỉ nạp khi chạy container

### 13. Đóng gói Docker
- `Dockerfile` (python:3.12-slim, chạy gunicorn bằng user không phải root) và `docker-compose.yml`

---

## Công nghệ sử dụng

| Thành phần | Công nghệ |
|---|---|
| Backend | Python · Flask |
| Frontend | HTML · CSS · JavaScript (Vanilla) |
| LLM API | FPT AI — `token-api.fpt.ai` |
| Mô hình | DeepSeek-V4-Flash |
| Cấu hình | python-dotenv |
| Triển khai | gunicorn · Docker |

---

## Cài đặt & Chạy

```bash
# 1. Cài đặt thư viện
pip install -r requirements.txt

# 2. Cấu hình API Key trong .env
printf 'API_BASE_URL="https://token-api.fpt.ai/v1"\nAPI_KEY="your-api-key"\nMODEL="DeepSeek-V4-Flash"\n' > .env
# API_BASE_URL: endpoint tương thích OpenAI bất kỳ (mặc định FPT AI)

# 3. Chạy ứng dụng
python app.py
```

Truy cập tại: **http://localhost:5000**

### Chạy bằng Docker

```bash
docker compose up -d --build
# hoặc
docker build -t olpai-chatbot:latest .
docker run -d -p 5000:5000 --env-file .env --name olpai-chatbot olpai-chatbot:latest
```

Xuất image sang máy khác: `docker save olpai-chatbot:latest | gzip > olpai-chatbot.tar.gz` rồi `docker load < olpai-chatbot.tar.gz`.

---

## Cấu trúc thư mục

```
olpai-chatbot/
├── app.py                  # Flask backend, proxy API
├── templates/
│   └── index.html          # Giao diện chatbot
├── static/
│   └── icon/
│       └── logo-ngang.svg  # Logo HaUI
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── .dockerignore
├── .env                    # API_BASE_URL, API_KEY, MODEL (không commit)
├── docs/
│   ├── PROJECT.md           # Tổng quan và kiến trúc
│   ├── USAGE.md             # Cài đặt và sử dụng
│   └── DOCKER.md            # Build, chạy và vận hành Docker
└── README.md
```

---

*HaUI · Trường Đại học Công nghiệp Hà Nội*
