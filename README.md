# MedReminder Web Demo

MedReminder hiện là bản demo web cho bài toán nhắc nhở uống thuốc và đọc đơn thuốc y tế.

Stack hiện tại:
- Frontend: HTML/CSS/JavaScript thuần
- Backend: FastAPI
- OCR: PaddleOCR chạy local

Flow chính:
- Trang chủ phong cách MyVinmec
- Người dùng tải ảnh đơn thuốc
- Hệ thống OCR ảnh bằng PaddleOCR
- Tự chuyển sang màn hình đối chiếu
- Chatbot theo dõi triệu chứng

## Cấu trúc chính

```text
ai_core/      OCR và trích xuất dữ liệu đơn thuốc
data/         mock schedule và ảnh mẫu dùng nội bộ
web/          giao diện web
web_api/      FastAPI backend
assets/       icon và tài nguyên tĩnh
```

## Cài đặt

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

Lưu ý:
- `paddleocr` và `paddlepaddle` khá nặng, thời gian cài có thể lâu.
- Nếu `paddlepaddle` không cài được trên máy bạn, cần chọn đúng bản theo OS/CPU.

## Cấu hình `.env`

Repo không cần API key.

Tạo `.env` từ `.env.example`:

```bash
cp .env.example .env
```

Nội dung mặc định:

```env
PADDLE_OCR_LANG=latin
PADDLE_OCR_USE_ANGLE_CLS=true
```

## Chạy demo

```bash
python -m uvicorn web_api.app:app --reload
```

Mở trình duyệt tại:

```text
http://127.0.0.1:8000
```

## Luồng sử dụng

1. Vào `Trang chủ`.
2. Nhấn `Nhắc nhở uống thuốc` hoặc đi tới `Đặt lịch`.
3. Tải ảnh đơn thuốc lên ở màn quét.
4. Hệ thống OCR xong sẽ tự chuyển sang màn `Đối chiếu`.
5. Người dùng kiểm tra lại thông tin và xác nhận trước khi lưu.
6. Có thể mở `Chatbot` để thử flow triệu chứng.

## API chính

- `GET /api/health`
- `GET /api/schedule`
- `POST /api/scan`
- `GET /api/prescription-image`
- `POST /api/crosscheck/save`
- `POST /api/chat`

## Ghi chú kỹ thuật

- OCR hiện dùng PaddleOCR local, không còn dùng Gemini/OpenAI.
- Phần trích xuất thuốc sau OCR hiện là heuristic parser trong [ai_core/agent.py](/home/nauqhna/Nhom06-402-Day06/ai_core/agent.py).
- Trạng thái chat và vài dữ liệu giao diện được giữ tạm trong `localStorage`.
- Bản demo ưu tiên flow và trải nghiệm trình bày, chưa phải hệ thống lâm sàng production-ready.
