# MedReminder Web Demo

MedReminder hiện đã được tinh gọn theo hướng **web demo HTML/CSS/JS + FastAPI** để trình bày các flow chính trên trình duyệt:

- Trang chủ xem lịch thuốc mẫu
- Quét đơn thuốc bằng AI/mock
- Cross-check trước khi lưu
- Chatbot phân loại triệu chứng

## Cấu trúc chính

```text
ai_core/      logic AI đọc đơn thuốc
data/         mock data và ảnh đơn thuốc
web/          frontend HTML/CSS/JS
web_api/      backend FastAPI
assets/       ảnh đơn thuốc và icon thuốc
```

## Chạy demo

### 1. Tạo môi trường ảo

Linux/macOS:

```bash
python3 -m venv venv
source venv/bin/activate
```

Windows `cmd`:

```bat
python -m venv venv
venv\Scripts\activate
```

### 2. Cài dependency

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 3. Mở web demo

```bash
python -m uvicorn web_api.app:app --reload
```

Sau đó mở:

```text
http://127.0.0.1:8000
```

## Luồng demo gợi ý

1. Vào `Trang chủ` để xem lịch thuốc mẫu.
2. Sang `Quét đơn` và chọn:
   - `Đơn rõ`
   - `Đọc một phần`
   - `Đơn mờ`
3. Mở `Đối chiếu` để xem kết quả AI, tick xác nhận rồi lưu.
4. Mở `Chatbot` và thử:
   - `hôm nay tôi ổn`
   - `tôi đau đầu và buồn nôn`
   - `tôi khó thở`

## API chính

- `GET /api/health`
- `GET /api/schedule`
- `POST /api/scan`
- `GET /api/prescription-image`
- `POST /api/crosscheck/save`
- `POST /api/chat`

## Ghi chú

- Nếu chưa có `OPENAI_API_KEY`, luồng scan vẫn fallback về mock data để demo.
- `case=partial` được hỗ trợ riêng để kiểm thử flow an toàn với kết quả đọc một phần.
- Trạng thái uống thuốc và lịch sử chat được giữ tạm trong `localStorage` của trình duyệt.
- Repo không còn nhắm tới build APK/Kivy trong nhánh dọn gọn này.
