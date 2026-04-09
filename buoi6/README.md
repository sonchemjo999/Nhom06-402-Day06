# MediRemind — Trợ lý Nhắc thuốc & Chăm sóc Sức khỏe

AI Agent sử dụng LangGraph giúp người dùng quản lý việc uống thuốc đúng giờ, theo dõi triệu chứng sức khỏe, và nhận tư vấn phân loại mức độ nghiêm trọng.

## Cài đặt

```bash
# 1. Tạo virtual environment
python -m venv venv

# 2. Kích hoạt
venv\Scripts\activate        # Windows
# source venv/bin/activate   # Mac/Linux

# 3. Cài thư viện
pip install -r requirements.txt
```

## Cấu hình

Mở file `.env` và thay API key:

```
OPENAI_API_KEY=sk-proj-your-key-here
```

## Chạy

```bash
# Test API trước
python test_api.py

# Chạy agent
python agent.py
```

## Cấu trúc project

```
buoi6_medi remind/
├── .env                  # API key (không commit)
├── .gitignore
├── requirements.txt      # Thư viện cần cài
├── system_prompt.txt    # System prompt cho agent
├── tools.py              # 4 tools: add_medication, get_schedule, check_adherence, triage_symptom
├── agent.py              # LangGraph agent + chat loop
├── logger.py             # Ghi log session
├── test_api.py           # Sanity check API
└── logs/                 # Thư mục chứa logs session
```

## Tính năng chính

### 1. Thêm thuốc và tạo lịch nhắc
- Người dùng cung cấp thông tin đơn thuốc (tên, liều, tần suất, giờ)
- Agent tạo lịch nhắc và xác nhận trước khi kích hoạt

### 2. Xem lịch nhắc hằng ngày
- Hiển thị các cữ uống trong ngày
- Trạng thái: Đã uống / Chưa uống / Quên uống / Đã tạm dừng

### 3. Ghi nhận việc uống thuốc
- Người dùng xác nhận đã uống thuốc đúng giờ
- Hệ thống cập nhật lịch sử

### 4. Phân loại triệu chứng (Triage)
- **GREEN (🟢)**: Theo dõi tại nhà
- **YELLOW (🟡)**: Nên gặp bác sĩ trong 24h
- **RED (🔴)**: Đến cơ sở y tế NGAY

## Ví dụ sử dụng

```
Bạn: Tôi được bác sĩ kê thuốc Paracetamol 500mg, uống 3 lần/ngày vào 8h, 14h, 20h trong 7 ngày

MediRemind đang suy nghĩ...
  🔧 Gọi tool: add_medication({'drug_name': 'Paracetamol', 'dosage': '500mg', 'frequency': 3, 'times': '08:00,14:00,20:00', 'days': 7})

MediRemind: ✅ Đã thêm thuốc vào danh sách!

  💊 Paracetamol — 500mg
  📋 Tần suất: 3 lần/ngày
  ⏰ Giờ uống: 08h00, 14h00, 20h00
  📅 Thời gian: Thứ 2 (2026-04-09) → Thứ 2 (2026-04-15)
  🆔 Mã thuốc: #1

  💡 Em sẽ nhắc anh/chị vào các giờ trên. Hãy xác nhận lại thông tin trước khi em kích hoạt nhắc nhở nha!
```

## Lệnh điều khiển

| Lệnh | Mô tả |
|------|-------|
| `quit` / `exit` | Thoát chương trình |
| `cache` | Xem thống kê cache |
| `clear [keyword]` | Xóa cache (toàn bộ hoặc theo từ khóa) |

## An toàn

⚠️ **Lưu ý quan trọng:**
- Agent chỉ là trợ lý nhắc nhở, **không thể thay thế** bác sĩ
- Mọi thông tin thuốc cần được **xác nhận bởi người dùng** trước khi kích hoạt
- Triệu chứng nghiêm trọng → luôn khuyến khích đến cơ sở y tế
- Nguyên tắc: **"Thà không nhắc, còn hơn nhắc sai"**
