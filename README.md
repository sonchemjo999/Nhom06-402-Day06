# MedReminder - Trợ lý Y tế ảo

> Ứng dụng nhắc nhở uống thuốc thông minh dành cho bệnh nhân.
> Tích hợp AI đọc đơn thuốc + chatbot triage triệu chứng.

---

## 1. Tổng quan

**MedReminder** là ứng dụng mô phỏng (MVP) được xây dựng bằng Python + Kivy/KivyMD, mô phỏng tích hợp:

- **AI đọc đơn thuốc** (LangGraph + OpenAI) — trích xuất thông tin thuốc từ hình ảnh đơn
- **Chatbot triage triệu chứng** — phân loại mức độ nguy hiểm (GREEN / YELLOW / RED)
- **Hệ thống nhắc thuốc** — alarm thông minh theo giờ cố định, chống bấm trước
- **Đối chiếu y khoa** — bắt buộc xác nhận trước khi lưu lịch

### Nguyên tắc thiết kế cốt lõi

| Nguyên tắc | Mô tả |
|-------------|--------|
| **Precision > Recall** | "Thà không nhắc, còn hơn hướng dẫn sai" |
| **Human-in-the-loop** | AI gợi ý, user quyết định cuối cùng |
| **Cross-check bắt buộc** | PHẢI đối chiếu đơn gốc trước khi lưu |
| **Nút "Đã uống" KHÓA** | Chỉ mở khi có thông báo alarm thực sự |
| **Khung giờ chuẩn hóa** | Chỉ chọn mốc giờ theo hướng dẫn lâm sàng |

---

## 2. Các màn hình chính

### 2.1. Trang chủ (HomeScreen)

- **Icon thuốc bên trái** mỗi MedCard (PNG từ Mewdicate, `IconImage` widget)
- **Đồng hồ thời gian thực** cập nhật mỗi giây (dùng `Clock.schedule_interval`)
- Timeline lịch uống thuốc trong ngày
- **Nút "Đã uống"**: ẨN hoàn toàn khi chưa có alarm → CHỈ HIỆN khi popup bật
- Nút "Quét đơn thuốc mới" và "Chat AI"
- AlarmService chạy nền, check mỗi 10 giây (demo mode)

### 2.2. Quét đơn thuốc (AIScanScreen)

- Nhấn "Quét" → gọi AI agent → loading spinner
- Kết quả: success (hiện thông tin) hoặc failure (banner cảnh báo)
- Tự động fallback sang mock data nếu không có API key

### 2.3. Xác nhận đơn thuốc (CrossCheckScreen)

- **Form chỉnh sửa** bên trên: mỗi thuốc có thể sửa từng khung giờ
- **Ảnh đơn thuốc gốc** bên dưới: hình ảnh giả lập chữ viết tay
- **Checkbox đối chiếu BẮT BUỘC** trước khi lưu
- **Hệ thống khung giờ chuẩn hóa** (xem mục 4)

### 2.4. Chatbot AI (ChatbotScreen)

- Giao diện chat kiểu Messenger/Zalo
- Phân loại triệu chứng: GREEN → ghi nhận, YELLOW → hỏi mức độ, RED → cảnh báo cấp cứu
- Tách riêng `send_message()` / `receive_message()` sẵn sàng cắm TTS/STT

### 2.5. Cài đặt (SettingsScreen)

- **Dark/Light Mode toggle** - Chuyển đổi chủ đề toàn bộ app
- Quay về trang chủ bằng nút cog ở góc phải

---

## 3. Tech stack

| Thành phần | Công nghệ | Phiên bản |
|-------------|-----------|-----------|
| UI Framework | Kivy | 2.3.1 |
| Material Design | KivyMD | 1.2.0 |
| AI Agent | LangGraph | (tùy chọn) |
| LLM | OpenAI GPT-4o-mini | (tùy chọn) |
| Xử lý ảnh | Pillow (PIL) | (tùy chọn) |
| Ngôn ngữ | Python | 3.10 |

---

## 4. Khung giờ chuẩn hóa y khoa

App không cho nhập giờ tự do. Tất cả khung giờ được **chuẩn hóa** theo 3 nhóm:

### Nhóm 1: Buổi cố định (theo nhịp sinh học)

| Tên buổi | Khung giờ | Mặc định | Lý do y khoa |
|-----------|-----------|-----------|---------------|
| **Sáng** | 06:00 - 08:00 | 06:00 | Thuốc nội tiết, thuốc bổ — uống khi đói bụng |
| **Trưa** | 11:30 - 13:00 | 12:00 | Gắn liền bữa ăn trưa |
| **Chiều-Tối** | 18:00 - 20:00 | 19:00 | Thuốc kháng sinh, thuốc dạ dày — uống với bữa tối |
| **Trước khi ngủ** | 21:00 - 22:00 | 21:30 | Thuốc huyết áp, statin — gan tổng hợp cholesterol mạnh lúc ngủ |

### Nhóm 2: Theo bữa ăn (quy định khoảng cách)

| Tên | Mặc định | Ghi chú | Thuốc ví dụ |
|-----|-----------|---------|-------------|
| **Trước ăn (30-60 phút)** | 07:30 | Hấp thu nhanh khi bụng đói | Alendronate, Azithromycin |
| **Trong bữa ăn** | 08:00 | Trộn với thức ăn | Amoxicillin |
| **Sau ăn (15-30 phút)** | 08:30 | Tránh kích ứng đường tiêu hóa | NSAIDs, Doxycycline |
| **Sau ăn 1 tiếng** | 09:00 | Hấp thu tốt sau ăn no | Phần lớn kháng sinh |

### Nhóm 3: PRN (Khi có triệu chứng)

| Tên | Ghi chú | Khoảng cách tối thiểu |
|-----|---------|-----------------------|
| **Khi sốt/đau** | Thuốc hạ sốt, giảm đau | Cách nhau 4-6 tiếng |
| **Khi cần** | Thuốc giãn phế quản, chống dị ứng | Tùy loại thuốc |

---

## 5. Cài đặt và chạy

### 5.1. Cài đặt thư viện

```bash
pip install --user kivy kivymd pillow
pip install langchain langchain-openai langgraph python-dotenv  # (tùy chọn)
```

### 5.2. Chạy ứng dụng

```bash
cd G:\AI_THUC_CHIEN_20K_2026_K1\test_app\App1
python main.py
```

### 5.3. Lệnh Admin (test & debug)

Dùng `admin_commands.py` để quản lý ngày giờ, ảnh, và chạy app.

```bash
cd G:\AI_THUC_CHIEN_20K_2026_K1\test_app\App1
python admin_commands.py <command>
```

| Lệnh | Mô tả |
|------|--------|
| `date` | Hiển thị ngày giờ app đang dùng |
| `set-date "DD/MM/YYYY HH:MM:SS"` | Đặt ngày giờ tùy chỉnh (LƯU QUA LẦN CHẠY) |
| `reset-date` | Reset về ngày giờ hệ thống |
| `gen-image` | Tạo ảnh đơn thuốc giả lập (bỏ cache, tạo lại) |
| `show-image` | Xem thông tin + mở ảnh |
| `clear-cache` | Xóa ảnh đã cache |
| `run-app` | Chạy ứng dụng |
| `help` | Hiển thị trợ giúp |

#### Ví dụ test alarm:

```bash
# Đặt giờ trước 1 phút -> alarm sẽ trigger đúng giờ mốc thuốc
python admin_commands.py set-date "08/04/2026 06:59:00"
python admin_commands.py run-app

# Reset về ngày thực
python admin_commands.py reset-date
```

#### Ví dụ test ảnh đơn thuốc:

```bash
# Tạo ảnh mới (bỏ cache)
python admin_commands.py gen-image

# Mở xem ảnh
python admin_commands.py show-image
```

#### Các format ngày giờ hỗ trợ:

```
"08/04/2026 10:30:00"    ngày/tháng/năm  giờ:phút:giây
"08/04/2026 10:30"        ngày/tháng/năm  giờ:phút
"08/04/2026"              ngày/tháng/năm
"2026-04-08 10:30:00"    năm-tháng-ngày  giờ:phút:giây
"2026-04-08"              năm-tháng-ngày
```

### 5.4. Đồng hồ trên Home và nhắc thuốc

- **Không có file `.app_datetime`:** `get_app_now()` = giờ hệ thống; đồng hồ cập nhật mỗi giây; alarm so khớp cùng nguồn thời gian đó.
- **Có file `.app_datetime` (lệnh `set-date`):** App lưu **mốc thời gian ảo** và cộng thêm **thời gian thực đã trôi** kể từ lần đọc đầu trong phiên chạy → đồng hồ **vẫn chạy từng giây** (không còn “đứng im” như chỉ đọc một chuỗi cố định). `AlarmService` cũng dùng `get_app_now()`, nên nhắc thuốc **không lệch** so với số giờ hiển thị.
- **Trên giao diện:** giờ/ngày/thứ bind qua `StringProperty` (`clock_display`, `date_display`, `day_display`) để Kivy tự làm mới nhãn mỗi khi tick.

### 5.5. Âm thanh báo thức

- **30 file MP3** đã copy từ Mewdicate vào `assets/sounds/` (pills.mp3, bell.mp3, ringtone_*.mp3, notification_*.mp3...).
- **Cài đặt → Chọn âm thanh:** danh sách đầy đủ file trong thư mục; lưu vào `.app_settings.json` (`alarm_sound_file`).
- **Lặp cho đến khi xử lý xong:** nhạc lặp vô hạn (`loops=-1` với pygame) hoặc beep lặp (Clock); rung lặp mỗi ~2 giây; gọi `stop_alarm()` khi bấm **Đã uống** hoặc **Trì hoãn** trên popup.
- Mặc định: `pills.mp3`.
- Phát bằng **pygame.mixer**; trên Windows fallback sang **winsound** nếu pygame lỗi.
- **Tắt/bật âm thanh / rung** trong mục **Cài đặt** → nhớ qua các lần chạy (file `.app_settings.json`).

---

## 6. Cấu trúc file

```
App1/
├── main.py                    # Entry point
├── app_datetime.py           # Quản lý ngày giờ (file cache .app_datetime)
├── app_settings.py           # Lưu Dark Mode / Sound / Vibration (.app_settings.json)
├── sound_manager.py         # Phát MP3 + Rung (pygame.mixer / winsound)
├── admin_commands.py        # Lệnh admin: date, gen-image, run-app...
├── app_root.kv              # Layout gốc (ScreenManager)
│
├── assets/
│   ├── prescription_handwritten.png  # Ảnh đơn thuốc (PIL, có cache)
│   ├── icons/
│   │   └── medications/             # 42 icon thuốc PNG (từ Mewdicate)
│   └── sounds/                     # 30 file MP3 (từ Mewdicate)
│
├── kv/                      # UI Layer
│   ├── home_screen.kv
│   ├── ai_scan_screen.kv
│   ├── crosscheck_screen.kv
│   ├── chatbot_screen.kv
│   ├── alarm_popup.kv
│   └── settings_screen.kv  # Dark/Light Mode toggle
│
├── screens/                 # Logic Layer
│   ├── home_screen.py      # (AlarmPopup, MedCard, IconImage, nút khóa/mở)
│   ├── ai_scan_screen.py  # (AI core integration)
│   ├── crosscheck_screen.py # (MedEditCard, TimeSlotPopup)
│   ├── chatbot_screen.py   # (Triage logic)
│   └── settings_screen.py  # (Dark/Light Mode)
│
├── services/
│   └── alarm_service.py    # Loop nhắc 5 lần
│
├── theme_manager.py         # Dark/Light Mode + EventDispatcher
│
├── ai_core/
│   ├── agent.py             # LangGraph agent + fallback mock
│   └── tools.py            # Mock OCR
│
└── data/
    ├── mock_data.py        # Dữ liệu mẫu
    └── prescription_image.py # Tạo ảnh đơn thuốc (cache)
```

---

## 7. Tính năng cốt lõi đã hoàn thành

| Tính năng | Trạng thái |
|-----------|-----------|
| Timeline thuốc trong ngày | ✅ |
| Nút "Đã uống" KHÓA mặc định, chỉ MỞ khi alarm | ✅ |
| Popup alarm toàn màn hình + beep + Snooze | ✅ |
| AlarmService loop 5 lần (0s, 10s, 20s, 30s, 40s) | ✅ |
| Quét đơn thuốc bằng AI (LangGraph + OpenAI) | ✅ |
| Fallback mock data khi không có API key | ✅ |
| Ảnh đơn thuốc giả lập (PIL, có cache) | ✅ |
| Form chỉnh sửa khung giờ theo mốc y khoa chuẩn | ✅ |
| 3 nhóm khung giờ (Buổi / Bữa ăn / PRN) | ✅ |
| Checkbox đối chiếu BẮT BUỘC trước lưu | ✅ |
| Chatbot triage GREEN / YELLOW / RED | ✅ |
| Tách send_message / receive_message (sẵn TTS/STT) | ✅ |
| Dark/Light Mode toggle | ✅ |
| Icon thuốc PNG bên trái MedCard (từ Mewdicate) | ✅ |
| Đồng hồ thực tế cập nhật mỗi giây | ✅ |
| Tiếng Việt có dấu đầy đủ | ✅ |
| Ngày giờ tùy chỉnh (file cache .app_datetime) | ✅ |
| Lệnh admin (date, gen-image, run-app...) | ✅ |
| 30 file MP3 báo thức (từ Mewdicate) | ✅ |
| Phát âm thanh alarm (pygame.mixer) | ✅ |
| Rung khi báo thức | ✅ |
| Lưu cài đặt (Dark Mode + Sound + Vibration) qua các lần chạy | ✅ |

---

## 8. TODO tương lai

- [ ] SQLite database (theo spec section 6.3)
- [ ] Push notification Android/iOS (Firebase)
- [ ] Correction log → pipeline retrain AI
- [ ] Export báo cáo tuân thủ cho bác sĩ
- [ ] Tích hợp TTS/STT cho chatbot
- [ ] Tìm bệnh viện thật qua Google Maps API
- [ ] Xác thực OTP/token (bảo mật PHI)
