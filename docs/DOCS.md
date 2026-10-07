# Tài liệu dự án OLPAI Chatbot

Đây là file chỉ mục tài liệu chính của dự án. Chọn nội dung cần xem:

- [Tổng quan dự án và kiến trúc](PROJECT.md)
- [Cài đặt, cấu hình và hướng dẫn sử dụng](USAGE.md)
- [Chạy và vận hành bằng Docker](DOCKER.md)
- [Triển khai lên Vercel](VERCEL.md)

## Khởi động nhanh

### Chạy trực tiếp

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp temp.env .env
python app.py
```

Mở <http://localhost:5000> sau khi điền `API_KEY`, `API_BASE_URL` và `MODEL` trong `.env`.

### Chạy Docker

```bash
cp temp.env .env
docker compose up -d --build
```

Xem chi tiết trong [DOCKER.md](DOCKER.md).

### Deploy Vercel

Import repository `Thanh25082005/Chat-bot` vào Vercel, khai báo các Environment Variables rồi deploy. Xem quy trình đầy đủ trong [VERCEL.md](VERCEL.md).

Không commit `.env` hoặc API key thật vào repository.
