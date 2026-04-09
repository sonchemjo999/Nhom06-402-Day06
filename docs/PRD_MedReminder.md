# MedReminder - ứng dụng nhắc nhở uống thuốc Vinmec

## 1. Tổng quan sản phẩm

### 1.1 Mô tả ngắn

MedReminder là ứng dụng nhắc nhở uống thuốc y tế được phát triển bởi Vinmec, sử dụng AI để đọc đơn thuốc từ hình ảnh, tự động tạo lịch uống thuốc và nhắc nhở người dùng đúng giờ. Ứng dụng được xây dựng trên nền tảng Python với Kivy/KivyMD cho giao diện di động.

### 1.2 Người dùng mục tiêu

- Bệnh nhân đang điều trị ngoại trú tại Vinmec
- Người cao tuổi cần nhắc nhở uống thuốc đúng giờ
- Người chăm sóc bệnh nhân
- Nhân viên y tế Vinmec (trong tương lai)

### 1.3 Vấn đề mà sản phẩm giải quyết

- Quên uống thuốc đúng giờ
- Uống sai liều hoặc sai thuốc
- Không hiểu rõ đơn thuốc từ bác sĩ
- Thiếu công cụ hỗ trợ sức khỏe tại nhà

---

## 2. Mô hình kinh doanh

### 2.1 Mô hình hoạt động

- **B2C**: Người dùng cá nhân tải ứng dụng miễn phí từ App Store/CH Play
- **B2B**: Tích hợp với hệ thống Vinmec HIS để nhận đơn thuốc điện tử
- **Freemium**: Các tính năng cơ bản miễn phí, tính năng nâng cao yêu cầu đăng ký

### 2.2 Nguồn doanh thu

1. Quảng cáo dịch vụ Vinmec ( không ảnh hưởng đến trải nghiệm người dùng)
2. Đăng ký Premium: nhắc nhở không giới hạn, AI nâng cao, báo cáo sức khỏe
3. Tích hợp B2B với các phòng khám, bệnh viện khác

---

## 3. Các tính năng chính

### 3.1 Tính năng Cốt lõi

| Tính năng | Mô tả | Ưu tiên |
|-----------|--------|---------|
| Đọc đơn thuốc bằng AI | Chụp ảnh đơn thuốc, AI trích xuất thông tin | P0 |
| Tạo lịch uống thuốc | Tự động tạo lịch dựa trên đơn thuốc | P0 |
| Nhắc nhở uống thuốc | Thông báo + âm thanh + rung khi đến giờ | P0 |
| Xác nhận đã uống | Người dùng xác nhận đã uống thuốc | P0 |
| Tư vấn triệu chứng AI | Chatbot phân loại mức độ nghiêm trọng | P1 |
| Theo dõi lịch sử | Lưu trữ lịch sử uống thuốc | P1 |
| Chế độ nhiều người dùng | Quản lý thuốc cho nhiều thành viên | P2 |

### 3.2 Tính năng Bổ sung

| Tính năng | Mô tả | Ưu tiên |
|-----------|--------|---------|
| Giao diện Dark Mode | Chuyển đổi giao diện sáng/tối | P1 |
| Tuỳ chỉnh âm báo | Chọn nhạc chuông nhắc nhở | P1 |
| Nhắc nhở bổ sung | Snooze nhiều lần trước khi bỏ qua | P2 |
| Widget màn hình chính | Hiển thị lịch thuốc trên màn hình chính | P2 |
| Kết nối thiết bị y tế | Đồng bộ với máy đo huyết áp, đường huyết | P3 |

---

## 4. Phân tích đối thủ

### 4.1 Đối thủ trực tiếp

| Ứng dụng | Điểm mạnh | Điểm yếu | Giá |
|----------|-----------|-----------|-----|
| MedMinder | Giao diện đẹp, nhiều tích hợp | Phức tạp, ít phổ biến ở VN | $5/tháng |
| Drugs.com | Cơ sở dữ liệu thuốc lớn | Không có nhắc nhở thông minh | Miễn phí |
| Bệnh viện 108 App | Liên kết bệnh viện | Chỉ dùng trong bệnh viện | Miễn phí |

### 4.2 Lợi thế cạnh tranh của MedReminder

1. **Tích hợp AI đọc đơn thuốc** - Không đối thủ nào có tính năng này ở Việt Nam
2. **AI phân loại triệu chứng** - Tích hợp chatbot tư vấn sức khỏe
3. **Liên kết Vinmec** - Thương hiệu uy tín, mạng lưới bệnh viện rộng khắp
4. **Giao diện tiếng Việt** - Tối ưu cho người Việt

---

## 5. Kiến trúc hệ thống

### 5.1 Sơ đồ kiến trúc

```
┌─────────────────────────────────────────────────────────────┐
│                    MedReminder App (Kivy)                     │
├─────────────┬──────────────┬───────────────┬─────────────────┤
│ Home Screen │ AI Scan      │ CrossCheck    │ Chatbot         │
│             │ Screen       │ Screen        │ Screen          │
└──────┬──────┴──────┬───────┴───────┬───────┴────────┬────────┘
       │             │               │                 │
       ▼             ▼               ▼                 ▼
┌─────────────────────────────────────────────────────────────┐
│                    Services Layer                            │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐  │
│  │ Alarm       │  │ Sound       │  │ Notification        │  │
│  │ Service     │  │ Manager     │  │ Service             │  │
│  └─────────────┘  └─────────────┘  └─────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────────────────────────────┐
│                    AI Core Layer (LangGraph)                │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐  │
│  │ Agent       │  │ OCR Tool    │  │ Prescription        │  │
│  │             │  │             │  │ Extraction Tool    │  │
│  └─────────────┘  └─────────────┘  └─────────────────────┘  │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                    External Services                        │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐  │
│  │ OpenAI API │  │ Vinmec HIS  │  │ Local Storage        │  │
│  │ (GPT-4o)   │  │ (Future)    │  │ (JSON Files)        │  │
│  └─────────────┘  └─────────────┘  └─────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

### 5.2 Sơ đồ luồng người dùng

```
[Khởi động App]
       │
       ▼
┌──────────────────┐
│   Home Screen    │
│  Hiển thị lịch  │
│  thuốc hôm nay  │
└────────┬─────────┘
         │
    ┌────┴────┐
    │         │
    ▼         ▼
┌───────┐  ┌───────────┐
│ Đến   │  │ Nút       │
│ giờ   │  │ "Thêm     │
│ uống  │  │  thuốc"   │
│ thuốc │  └─────┬─────┘
└───┬───┘        │
    │            │
    ▼            ▼
┌───────────┐  ┌──────────────────┐
│ Alarm     │  │  AI Scan Screen  │
│ Popup     │  │  Chụp/Xem ảnh    │
│ (Bật     │  │  đơn thuốc       │
│  nhạc,   │  └────────┬─────────┘
│  rung)   │           │
└───┬─────┘           │
    │            ┌────┴────┐
    │            │         │
    │            ▼         ▼
    │     ┌───────────┐ ┌────────────┐
    │     │ AI đọc   │ │ Đọc thất   │
    │     │ thành    │ │ bại → Nhập │
    │     │ công     │ │ tay        │
    │     └─────┬────┘ └────────────┘
    │           │
    │           ▼
    │    ┌──────────────────┐
    │    │ CrossCheck Screen│
    │    │ Xem, sửa, xác   │
    │    │ nhận thông tin   │
    │    └────────┬─────────┘
    │             │
    │             ▼
    │    ┌──────────────────┐
    │    │ Lưu và quay về   │
    │    │ Home Screen       │
    │    └────────┬─────────┘
    │             │
    └─────────────┘
         │
         ▼
┌──────────────────┐
│  Alarm Service   │
│  chạy nền, đợi   │
│  đến giờ nhắc   │
└──────────────────┘
```

---

## 6. Thiết kế giao diện

### 6.1 Màu sắc chủ đạo

| Màu | Hex | Sử dụng |
|-----|-----|---------|
| Xanh dương chính | #2196F3 | Nút chính, tiêu đề |
| Xanh lá Vinmec | #00A651 | Thành công, đã xác nhận |
| Đỏ cảnh báo | #F44336 | Nhắc nhở, nguy hiểm |
| Cam nhắc nhở | #FF9800 | Cảnh báo nhẹ |
| Nền sáng | #F5F5F5 | Chế độ Light Mode |
| Nền tối | #1E1E1E | Chế độ Dark Mode |

### 6.2 Typography

| Yếu tố | Font | Kích thước | Trọng lượng |
|--------|------|------------|-------------|
| Tiêu đề chính | Roboto Bold | 24sp | 700 |
| Tiêu đề phụ | Roboto Medium | 18sp | 500 |
| Nội dung | Roboto Regular | 16sp | 400 |
| Ghi chú | Roboto Light | 14sp | 300 |
| Nhãn | Roboto Medium | 12sp | 500 |

### 6.3 Layout chính

```
┌────────────────────────────────┐
│       AppBar Vinmec            │
├────────────────────────────────┤
│                                │
│        Nội dung chính          │
│        (ScreenManager)         │
│                                │
│                                │
│                                │
├────────────────────────────────┤
│  🏠    📷    💬    ⚙️          │
│ Trang  Quét  Chat  Cài         │
│ Chủ   AI   Bot   Đặt          │
└────────────────────────────────┘
```

---

## 7. Yêu cầu kỹ thuật

### 7.1 Backend

| Thành phần | Công nghệ | Phiên bản tối thiểu |
|-----------|-----------|-------------------|
| Runtime | Python | 3.10+ |
| Web Framework | FastAPI | 0.100+ (tương lai) |
| AI Engine | LangGraph | 0.2+ |
| LLM | OpenAI GPT-4o-mini | Latest |
| Database | PostgreSQL | 15+ (tương lai) |
| Cache | Redis | 7+ (tương lai) |

### 7.2 Frontend (Mobile)

| Thành phần | Công nghệ | Phiên bản |
|-----------|-----------|-----------|
| Framework | KivyMD | 2.0+ |
| Python | Python | 3.10+ |
| Camera | kivy.camera | Built-in |
| Storage | JSON | - |

### 7.3 DevOps

| Thành phần | Công nghệ |
|-----------|-----------|
| Container | Docker |
| CI/CD | GitHub Actions |
| Monitoring | Sentry |
| Analytics | Firebase Analytics |

### 7.4 Yêu cầu về hiệu suất

| Chỉ số | Mục tiêu |
|--------|---------|
| Thời gian khởi động | < 3 giây |
| Phản hồi AI | < 5 giây |
| Thông báo đến | < 1 giây |
| Dung lượng App | < 100MB |
| Pin tiêu thụ | < 5%/ngày |

---

## 8. Bảo mật và quyền riêng tư

### 8.1 Dữ liệu cá nhân

| Loại dữ liệu | Mức độ nhạy cảm | Xử lý |
|-------------|-----------------|-------|
| Thông tin thuốc | Cao | Mã hoá, chỉ lưu cục bộ |
| Triệu chứng sức khỏe | Rất cao | Không lưu trữ, chỉ xử lý tạm |
| Hình ảnh đơn thuốc | Cao | Xoá sau khi xử lý |
| Thông tin bệnh viện | Cao | Liên kết Vinmec HIS |

### 8.2 Quyền ứng dụng

| Quyền | Lý do |
|-------|-------|
| Camera | Chụp ảnh đơn thuốc |
| Thông báo | Nhắc nhở uống thuốc |
| Bộ nhớ | Lưu hình ảnh tạm thời |
| Âm thanh | Phát nhạc chuông báo |

### 8.3 Tuân thủ pháp luật

- Luật An ninh mạng Việt Nam 2015
- Nghị định 13/2023/NĐ-CP về bảo vệ dữ liệu cá nhân
- Quy định của Bộ Y tế về đơn thuốc điện tử

---

## 9. Kế hoạch phát triển

### 9.1 Phase 1: MVP (Hoàn thành ✅)

- [x] Giao diện cơ bản 5 màn hình
- [x] Alarm Service với thông báo
- [x] AI đọc đơn thuốc (mock + API)
- [x] CrossCheck xác nhận thuốc
- [x] Chatbot phân loại triệu chứng
- [x] Dark Mode

### 9.2 Phase 2: V1.0 (Q2/2026)

- [ ] Đăng ký/Đăng nhập người dùng
- [ ] Lưu trữ đơn thuốc lịch sử
- [ ] Kết nối Vinmec HIS thực tế
- [ ] Xuất báo cáo sức khỏe
- [ ] Widget màn hình chính

### 9.3 Phase 3: V2.0 (Q3/2026)

- [ ] Chế độ nhiều người dùng
- [ ] Kết nối thiết bị y tế (Bluetooth)
- [ ] Nhắc nhở bổ sung thuốc
- [ ] Tích hợp bảo hiểm
- [ ] Giao diện cho bác sĩ

---

## 10. Chỉ số thành công (KPIs)

### 10.1 KPIs người dùng

| Chỉ số | Mục tiêu 6 tháng |
|--------|------------------|
| Số lượt tải | 100,000+ |
| MAU (Active Users) | 30,000 |
| DAU (Daily Active) | 10,000 |
| Tỷ lệ giữ chân | > 60% |
| Rating App Store | > 4.5 sao |

### 10.2 KPIs sức khỏe

| Chỉ số | Mục tiêu |
|--------|----------|
| Tỷ lệ tuân thủ thuốc | > 85% |
| Số lần nhắc nhở hiệu quả | > 90% |
| Giảm tái nhập viện | > 20% |

### 10.3 KPIs kỹ thuật

| Chỉ số | Mục tiêu |
|--------|----------|
| Uptime | > 99.5% |
| Crash rate | < 0.1% |
| App size | < 100MB |

---

## 11. Rủi ro và giải pháp

| Rủi ro | Mức độ | Giải pháp |
|--------|--------|-----------|
| AI đọc sai đơn thuốc | Cao | Bắt buộc xác nhận con người |
| Người dùng tắt thông báo | Trung bình | Nhắc nhở trong app thường xuyên |
| Dữ liệu bị xâm nhập | Cao | Mã hoá đầu cuối, tuân thủ PDPL |
| Cạnh tranh từ đối thủ | Thấp | Đi đầu về AI + thương hiệu Vinmec |
| Không tương thích thiết bị | Trung bình | Test đa dạng thiết bị Android |

---

## 12. Tài liệu liên quan

| Tài liệu | Mô tả |
|----------|-------|
| Flowchart | Sơ đồ luồng người dùng chi tiết |
| Wireframes | Thiết kế chi tiết từng màn hình |
| API Documentation | Tài liệu API (tương lai) |
| Security Policy | Chính sách bảo mật |
| Privacy Policy | Chính sách quyền riêng tư |
| Terms of Service | Điều khoản sử dụng |

---

## 13. Thông tin phiên bản

| Phiên bản | Ngày | Người phê duyệt | Ghi chú |
|----------|------|-----------------|---------|
| 1.0 | 2026-04-09 | Vinmec R&D | MVP hoàn thành |
| 1.1 | (Dự kiến Q2/2026) | | Phase 2 release |

---

**Tài liệu này được tạo bởi**: AI Assistant
**Ngày tạo**: 2026-04-09
**Trạng thái**: Hoàn thành
