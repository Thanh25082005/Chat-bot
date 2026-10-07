# Tổng quan dự án

OLPAI Chatbot là ứng dụng hỏi đáp sử dụng Flask ở backend và giao diện HTML/CSS/JavaScript ở frontend. Backend giữ API key ở phía máy chủ, nhận lịch sử hội thoại từ trình duyệt rồi chuyển tiếp yêu cầu đến một dịch vụ chat tương thích với OpenAI.

## Mục lục tài liệu

- [Chỉ mục tài liệu](DOCS.md)
- [Hướng dẫn sử dụng và cấu hình](USAGE.md)
- [Hướng dẫn Docker](DOCKER.md)
- [Triển khai Vercel](VERCEL.md)

## Chức năng chính

- Trả lời hội thoại nhiều lượt và hiển thị phản hồi theo streaming.
- Chọn model từ danh sách cấu hình trong biến `MODEL`.
- Lưu lịch sử chat trong `localStorage` của trình duyệt.
- Hiển thị Markdown cơ bản và các câu hỏi gợi ý.
- Theo dõi ước lượng token, giới hạn 2.000 token cho mỗi phiên ở giao diện.
- Tự thử model khác khi model hiện tại nhận HTTP 429.
- Chạy được trực tiếp bằng Python, Docker/Gunicorn hoặc Vercel Functions.

## Luồng xử lý

```text
Trình duyệt
    │ POST /chat (messages, model)
    ▼
Flask / Gunicorn
    │ Authorization: Bearer API_KEY
    ▼
API chat tương thích OpenAI
    │ SSE chunks
    ▼
Trình duyệt hiển thị phản hồi theo luồng
```

API key chỉ nằm trong biến môi trường của backend. Frontend không gọi trực tiếp đến nhà cung cấp model.

## Thành phần

| Thành phần | Vai trò |
|---|---|
| `app.py` | Flask app, proxy `/chat`, streaming SSE và xử lý lỗi API. |
| `templates/index.html` | Giao diện, gửi tin nhắn, chọn model và lịch sử chat. |
| `public/icon/` | Logo tĩnh được Vercel CDN và Flask phục vụ. |
| `check_key.py` | Kiểm tra API key và các model đã cấu hình. |
| `temp.env` | Mẫu cấu hình không chứa key thật. |
| `Dockerfile` | Tạo image production chạy Gunicorn với user không phải root. |
| `docker-compose.yml` | Khai báo dịch vụ, cổng, biến môi trường và healthcheck. |
| `vercel.json` | Cấu hình thời gian chạy cho Flask Function trên Vercel. |
| `docs/` | Tài liệu dự án, sử dụng và Docker. |

## API nội bộ

`GET /` trả về giao diện web.

`POST /chat` nhận JSON dạng:

```json
{
  "model": "gemma-3-27b-it",
  "messages": [
    {"role": "user", "content": "Xin chào"}
  ]
}
```

Phản hồi có MIME type `text/event-stream`. Mỗi chunk có tiền tố `data: ` và sự kiện `data: [DONE]` kết thúc luồng.

## Giới hạn hiện tại

- Chưa có đăng nhập, phân quyền hoặc rate limit ở lớp Flask.
- Lịch sử chỉ được lưu trong trình duyệt hiện tại, không lưu ở server.
- Giới hạn 2.000 token là ước lượng phía giao diện; hạn mức thật phụ thuộc nhà cung cấp API.
- Cần một API tương thích với `POST /chat/completions` và hỗ trợ streaming.
