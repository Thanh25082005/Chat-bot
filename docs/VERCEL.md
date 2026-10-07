# Hướng dẫn triển khai lên Vercel

Tài liệu này dùng phương án Vercel Python Runtime: Vercel tự nhận diện `app.py` là Flask entrypoint và chạy toàn bộ backend như một Vercel Function. Không cần tạo server riêng, không cần chạy Gunicorn trên Vercel và không cần dùng Docker để deploy.

## 1. Kiến trúc deploy

```text
GitHub: Thanh25082005/Chat-bot
              │ deploy tự động
              ▼
Vercel Python Function (app.py)
       ├── GET /       → templates/index.html
       └── POST /chat  → gọi API model và stream SSE

Vercel CDN
       └── /icon/logo-ngang.svg ← public/icon/logo-ngang.svg
```

Vercel nhận diện `app = Flask(...)` trong `app.py`. Python runtime đọc dependency từ `requirements.txt`; `.python-version` khóa runtime ở Python 3.12. Phản hồi streaming của `/chat` được giữ nguyên để giao diện nhận từng chunk.

## 2. Chuẩn bị trên Vercel

1. Đăng nhập <https://vercel.com> bằng tài khoản GitHub.
2. Chọn **Add New → Project**.
3. Import repository `Thanh25082005/Chat-bot`.
4. Đặt **Root Directory** là thư mục gốc của repository.
5. Giữ **Framework Preset** ở chế độ tự phát hiện. Không đặt Build Command hoặc Output Directory riêng.
6. Thêm các biến môi trường sau cho **Production**, **Preview** và **Development**:

   | Tên | Giá trị |
   |---|---|
   | `API_BASE_URL` | URL gốc, ví dụ `https://token-api.fpt.ai/v1` |
   | `API_KEY` | API key của nhà cung cấp model |
   | `MODEL` | Một hoặc nhiều model, phân tách bằng dấu phẩy |

7. Nhấn **Deploy**.

Không commit `.env` và không đặt API key trong `vercel.json`. Vercel sẽ lưu các biến trên dưới dạng Environment Variables và chỉ truyền chúng vào Function lúc chạy.

## 3. Deploy bằng Vercel CLI

Cài CLI trên máy đã có Node.js:

```bash
npm install --global vercel@latest
vercel login
```

Từ thư mục dự án:

```bash
vercel link
vercel env add API_BASE_URL production
vercel env add API_KEY production
vercel env add MODEL production
vercel --prod
```

CLI sẽ hỏi giá trị của từng biến. Có thể thêm cùng biến cho `preview` và `development` nếu cần:

```bash
vercel env add API_KEY preview
vercel env add API_KEY development
```

Sau khi deploy, CLI in ra URL dạng `https://<project-name>.vercel.app`.

## 4. Kiểm tra sau deploy

Mở URL Vercel trên trình duyệt và kiểm tra:

1. Trang chủ hiển thị giao diện chatbot.
2. Logo tải được tại `https://<project-name>.vercel.app/icon/logo-ngang.svg`.
3. Gửi một câu hỏi ngắn để kiểm tra `POST /chat` và streaming.
4. Nếu có lỗi, mở tab **Logs** trong Vercel Dashboard.

Có thể kiểm tra route bằng curl:

```bash
curl -I https://<project-name>.vercel.app/
curl -I https://<project-name>.vercel.app/icon/logo-ngang.svg
```

## 5. Cấu hình đã có trong repository

### `vercel.json`

```json
{
  "$schema": "https://openapi.vercel.sh/vercel.json",
  "functions": {
    "app.py": {
      "maxDuration": 60
    }
  }
}
```

`maxDuration` giới hạn một lần gọi Function ở 60 giây. Mức thực tế còn phụ thuộc gói Vercel và cấu hình Fluid Compute. Backend có timeout kết nối 10 giây và timeout 45 giây giữa các chunk, nên model cần bắt đầu trả dữ liệu trong thời gian cho phép.

### Asset tĩnh

Logo nằm trong `public/icon/`. Vercel phục vụ `public/**` qua CDN. Khi chạy local hoặc Docker, route `/icon/<filename>` trong Flask là fallback để giữ cùng URL `/icon/logo-ngang.svg`.

### `Dockerfile`

Dockerfile vẫn được giữ cho local hoặc máy chủ riêng. Vercel Python Runtime không đọc `docker-compose.yml` trong quy trình deploy Git thông thường.

## 6. Luồng deploy tự động từ GitHub

Sau khi Project đã liên kết với GitHub:

```bash
git add .
git commit -m "Prepare Vercel deployment"
git push origin main
```

Mỗi lần push vào `main`, Vercel tạo deployment Production mới. Pull Request thường tạo Preview Deployment riêng.

## 7. Sự cố thường gặp

| Hiện tượng | Cách xử lý |
|---|---|
| `404` ở trang chủ | Kiểm tra Root Directory là thư mục gốc và repository có `app.py`. Không đặt nhầm Root Directory thành `docs/`. |
| Logo bị `404` | Kiểm tra file ở `public/icon/logo-ngang.svg` và URL phải là `/icon/logo-ngang.svg`, không phải `/static/...`. |
| `401` từ API model | Kiểm tra `API_KEY` trong đúng Environment (Production/Preview) rồi **Redeploy**. |
| `MODEL` rỗng hoặc sai | Kiểm tra tên model, phân tách bằng dấu phẩy và redeploy. |
| `FUNCTION_INVOCATION_TIMEOUT` | API model phản hồi quá chậm hoặc stream vượt `maxDuration`; dùng model nhanh hơn hoặc tăng giới hạn trong phạm vi gói Vercel cho phép. |
| Chạy local bằng `vercel dev` lỗi | Cài Vercel CLI mới, chạy `vercel link`, tạo biến Development và kiểm tra `requirements.txt`. |

## 8. Giới hạn cần biết

- Function là stateless; lịch sử chat hiện chỉ lưu trong `localStorage` của trình duyệt.
- API key không được đưa vào frontend, nhưng người có quyền xem Vercel Project có thể xem Environment Variables; chỉ cấp quyền cần thiết.
- Vercel giới hạn thời gian, kích thước request/response và tài nguyên Function theo gói. Streaming không thể chạy vô hạn.
- Không sử dụng filesystem của Function để lưu dữ liệu lâu dài. Nếu cần tài khoản, lịch sử dùng chung hoặc analytics, bổ sung database/storage bên ngoài.

## 9. Tài liệu Vercel tham khảo

- <https://vercel.com/docs/frameworks/backend/flask>
- <https://vercel.com/docs/functions/runtimes/python>
- <https://vercel.com/docs/functions/streaming-functions>
- <https://vercel.com/docs/functions/limitations>
