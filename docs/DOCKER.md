# Hướng dẫn chạy Docker

## 1. Chuẩn bị

Cần cài Docker Engine và Docker Compose v2. Kiểm tra:

```bash
docker --version
docker compose version
```

Tạo file `.env` ở thư mục gốc của dự án. Có thể bắt đầu từ mẫu:

```bash
cp temp.env .env
```

Sau đó điền `API_KEY` và kiểm tra `API_BASE_URL`, `MODEL`. File `.env` không được commit.

## 2. Chạy bằng Docker Compose

Build image và khởi động nền:

```bash
docker compose up -d --build
```

Ứng dụng được mở tại <http://localhost:5000>. Compose sẽ tự khởi động lại container nếu tiến trình thoát và báo trạng thái qua healthcheck.

Các lệnh quản lý thường dùng:

```bash
docker compose ps
docker compose logs -f olpai-chatbot
docker compose restart olpai-chatbot
docker compose stop
docker compose down
```

Sau khi sửa `app.py`, template hoặc dependency, chạy lại `docker compose up -d --build` để tạo image mới.

## 3. Chạy image thủ công

```bash
docker build -t olpai-chatbot:latest .
docker run -d \
  --name olpai-chatbot \
  --restart unless-stopped \
  -p 5000:5000 \
  --env-file .env \
  olpai-chatbot:latest
```

Xem log hoặc dừng container:

```bash
docker logs -f olpai-chatbot
docker stop olpai-chatbot
docker rm olpai-chatbot
```

## 4. Cấu hình image

`Dockerfile` hiện:

- Dùng `python:3.12-slim` để giảm kích thước image.
- Cài dependency từ `requirements.txt` không lưu pip cache.
- Chạy Gunicorn với 2 worker, 8 thread và timeout 120 giây để phù hợp streaming.
- Chạy bằng user `appuser`, không chạy tiến trình ứng dụng bằng root.
- Có `HEALTHCHECK` gọi `GET /`.
- Ghi access/error log ra stdout/stderr để `docker logs` đọc được.

`.dockerignore` loại `.env`, `.venv`, Git metadata, cache Python, tài liệu và file tạm khỏi build context. Dockerfile chỉ copy các file runtime cần thiết.

## 5. Cổng và healthcheck

Container lắng nghe cổng `5000`. Compose ánh xạ cổng máy host bằng biến tùy chọn:

```bash
APP_PORT=8080 docker compose up -d --build
```

Sau đó truy cập <http://localhost:8080>. Healthcheck không gọi API model; nó chỉ kiểm tra Flask có trả trang chủ hay không. Trạng thái xem bằng:

```bash
docker inspect --format='{{json .State.Health}}' olpai-chatbot
```

## 6. Xuất image sang máy khác

```bash
docker save olpai-chatbot:latest | gzip > olpai-chatbot.tar.gz
```

Ở máy đích:

```bash
gunzip -c olpai-chatbot.tar.gz | docker load
docker run -d --name olpai-chatbot -p 5000:5000 --env-file .env olpai-chatbot:latest
```

Luôn tạo `.env` riêng trên máy đích; không đóng gói API key vào image.

## 7. Sự cố thường gặp

- **Container thoát ngay:** chạy `docker compose logs olpai-chatbot` và kiểm tra `.env`.
- **Healthcheck unhealthy:** kiểm tra `docker compose ps`, log ứng dụng và mapping cổng; healthcheck chỉ gọi `GET /` nên lỗi thường nằm ở tiến trình Gunicorn.
- **API trả 401/404:** kiểm tra `API_KEY`, `API_BASE_URL` và tên model trong `.env`, sau đó recreate container bằng `docker compose up -d --build --force-recreate`.
- **Cổng 5000 đã được dùng:** đặt `APP_PORT=8080` hoặc đổi mapping trong `docker-compose.yml`.
- **Phản hồi bị ngắt:** không đặt reverse proxy timeout thấp hơn 120 giây; giữ buffering tắt cho SSE.
