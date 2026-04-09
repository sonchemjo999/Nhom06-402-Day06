# MedReminder - Walkthrough phát triển ứng dụng

> **Session ngày:** 08/04/2026
> **Dự án:** Trợ lý Y tế ảo (Medical AI Assistant) — Nhắc nhở uống thuốc
> **Tech stack:** Python 3.10 + Kivy 2.3.1 + KivyMD 1.2.0 + LangGraph + OpenAI + PIL

---

## 1. Tổng quan dự án

Ứng dụng di động "Trợ lý Y tế ảo" dành cho bệnh nhân, mô phỏng tích hợp AI đọc đơn thuốc + chatbot triage triệu chứng. Thiết kế UI/UX ưu tiên **an toàn y tế** và **chống Automation Bias**.

### Nguyên tắc thiết kế chính (từ spec-draft.md)
- **Precision > Recall:** "Thà không nhắc, còn hơn hướng dẫn sai"
- **Human-in-the-loop:** AI gợi ý, user quyết định cuối cùng (Augmentation)
- **Cross-check bắt buộc:** User PHẢI đối chiếu đơn gốc trước khi lưu
- **Snooze notification:** Nút "Trì hoãn" bắt buộc
- **Nút "Đã uống" phải KHÓA** cho đến khi có thông báo alarm (chống bấm trước)
- **Chuẩn hóa khung giờ y khoa:** Chỉ cho phép chọn mốc thời gian cố định theo hướng dẫn lâm sàng

---

## 2. Cấu trúc thư mục dự án

```
App1/
├── main.py                    # Entry point, khởi tạo MDApp + ScreenManager
├── kv/app_root.kv             # Layout gốc chứa ScreenManager
├── app_datetime.py            # Quản lý ngày giờ app (test alarm, file cache)
├── admin/admin_commands.py    # Lệnh admin: date, gen-image, run-app...
├── .env                       # API Key cho OpenAI (LangGraph agent)
├── .app_datetime             # File cache ngày giờ tùy chỉnh (do admin tạo)
├── spec-draft.md              # Tài liệu đặc tả sản phẩm AI
├── README.md                   # Hướng dẫn sử dụng nhanh
├── walkthrough.md             # File ghi chép phát triển (file này)
│
├── assets/                    # Tài nguyên tĩnh
│   └── prescription_handwritten.png  # Ảnh đơn thuốc giả lập (PIL, có cache)
│
├── kv/                        # UI Layer (KV Language)
│   ├── alarm_popup.kv        #   Popup báo thức toàn màn hình
│   ├── ai_scan_screen.kv      #   UI quét đơn thuốc AI
│   ├── chatbot_screen.kv      #   UI Chatbot triage (Messenger-like)
│   ├── crosscheck_screen.kv   #   UI đối chiếu y khoa (form chỉnh sửa + ảnh)
│   └── home_screen.kv          #   UI trang chủ + timeline + Nút Chat AI
│
├── screens/                   # Logic Layer (Python)
│   ├── __init__.py
│   ├── home_screen.py         #   HomeScreen + AlarmPopup + MedCard (nút khóa/mở)
│   ├── ai_scan_screen.py      #   AIScanScreen (gọi AI core)
│   ├── crosscheck_screen.py   #   CrossCheckScreen (MedEditCard + TimeSlotPopup)
│   └── chatbot_screen.py      #   ChatbotScreen (triage triệu chứng)
│
├── services/                  # Service Layer
│   ├── __init__.py
│   └── alarm_service.py       #   AlarmService: loop nhắc 5 lần
│
├── ai_core/                   # AI Layer (LangGraph + OpenAI)
│   ├── __init__.py
│   ├── agent.py               #   LangGraph agent đọc đơn thuốc
│   ├── tools.py              #   Tool extract_prescription (mock OCR)
│   └── system_prompt.txt    #   System prompt theo spec Prompt 1
│
└── data/                      # Data Layer
    ├── __init__.py
    ├── mock_data.py           #   Mock data (AI results + lịch uống mẫu)
    └── prescription_image.py   #   Tạo ảnh đơn thuốc giả lập bằng PIL (cache)
```

---

## 3. Đối chiếu yêu cầu — ĐÃ LÀM vs CHƯA HOÀN THÀNH

### Màn hình 1: Trang chủ (HomeScreen) & Danh sách nhắc thuốc

| Yêu cầu | Trạng thái | Ghi chú |
|----------|:----------:|---------|
| Hiển thị timeline cữ thuốc trong ngày | ✅ Xong | `home_screen.kv` — MedCard với giờ, tên, liều, ghi chú |
| Nút "Đã uống" to, rõ ràng | ✅ Xong | MDRaisedButton xanh lá, font 15sp |
| **Quy tắc An toàn 1:** Nút "Đã uống" KHÓA mặc định, chỉ MỞ khi có alarm | ✅ Xong | `med_unlocked=False` luôn, chỉ mở qua `_unlock_med_button()` khi alarm thực sự trigger |
| **Chỉ hiển thị nút khi có thông báo** | ✅ Xong | `opacity: 0` khi chưa alarm, `opacity: 1` khi alarm báo |
| Nút "Trì hoãn 15p" (Snooze) | ✅ Xong | Trong AlarmPopup — `on_snooze()` |
| AlarmService loop 5 lần (0, 1m, 5m, 10m, 15m) | ✅ Xong | `services/alarm_service.py` — demo mode intervals ngắn |
| Popup alarm toàn màn hình + beep | ✅ Xong | `alarm_popup.kv` + winsound.Beep |
| Nút mở Chatbot AI | ✅ Xong | MDRaisedButton "CHAT AI" góc dưới phải |
| Bỏ tất cả icon (app không hiển thị được) | ✅ Xong | Thay `MDTopAppBar icon` bằng `MDFlatButton text "< Trở lại"` |
| Tiếng Việt có dấu đầy đủ | ✅ Xong | Tất cả file `.kv` và `.py` viết lại bằng tiếng Việt chuẩn |

### Màn hình 2: Quét & Đối chiếu Đơn thuốc (Scan & Cross-check)

| Yêu cầu | Trạng thái | Ghi chú |
|----------|:----------:|---------|
| Nút giả lập "Chụp ảnh đơn thuốc" | ✅ Xong | `ai_scan_screen.kv` — MDRaisedButton |
| Loading spinner | ✅ Xong | MDSpinner + threading |
| Mock data JSON (tên thuốc, liều, cách dùng) | ✅ Xong | `data/mock_data.py` |
| AI Agent thật (LangGraph + OpenAI) | ✅ Xong | `ai_core/agent.py` + fallback mock |
| **Ảnh đơn thuốc giả lập** | ✅ Xong | `data/prescription_image.py` (PIL tạo ảnh chữ viết tay) |
| **Quy tắc An toàn 2:** Hiển thị song song Form chỉnh sửa vs Ảnh đơn gốc | ✅ Xong | Form bên trên (sửa được), Ảnh bên dưới (chỉ xem) |
| **Chỉnh sửa từng khung giờ theo mốc y khoa chuẩn** | ✅ Xong | `MedEditCard` + `MedScheduleSlot` + `TimeSlotPopup` |
| **Hệ thống khung giờ chuẩn hóa y khoa** | ✅ Xong | 3 nhóm: Buổi cố định, Theo bữa ăn, PRN |
| Checkbox "Đã đối chiếu kỹ hình ảnh gốc" | ✅ Xong | MDCheckbox bắt buộc trước khi lưu |
| **Nút "Sửa lỗi" (Correction)** nếu AI đọc sai | ✅ Xong | MDFlatButton → Snackbar ghi nhận correction |
| Nút "Lưu lịch nhắc" chỉ sáng khi checkbox tick | ✅ Xong | `disabled: not root.is_confirmed` |

### Màn hình 3: Chatbot AI Agent

| Yêu cầu | Trạng thái | Ghi chú |
|----------|:----------:|---------|
| Giao diện Text Chat giống Messenger | ✅ Xong | `chatbot_screen.kv` — bubble chat UI |
| Tách `send_message()` và `receive_message()` | ✅ Xong | Sẵn sàng cắm TTS/STT |
| Chatbot chào: "Hôm nay sức khỏe thế nào?" | ✅ Xong | `on_enter` → auto greet |
| Từ khóa bình thường → ghi nhận | ✅ Xong | Keyword matching: "tốt", "bình thường", "ổn" |
| Từ khóa nguy hiểm → RED alert | ✅ Xong | "khó thở", "sốt cao", "co giật" → banner đỏ |
| Nút "Gợi ý BV cấp cứu gần nhất" | ✅ Xong | MDRaisedButton đỏ hiện khi detect nguy hiểm |

### Hạ tầng & Bug fixes

| Yêu cầu | Trạng thái | Ghi chú |
|----------|:----------:|---------|
| KivyMD 1.2.0 Snackbar API | ✅ Fixed | `MDSnackbar(MDLabel(text=...))` |
| KV ids chưa sẵn sàng khi on_enter | ✅ Fixed | `Clock.schedule_once` |
| Unicode print crash Windows cp1252 | ✅ Fixed | Bỏ emoji trong `print()` |
| System prompt theo spec Prompt 1 | ✅ Xong | `ai_core/system_prompt.txt` |
| Fallback mock khi thiếu API key | ✅ Xong | `ai_core/agent.py` auto-detect |
| **Module app_datetime (quản lý ngày giờ)** | ✅ Xong | `app_datetime.py` — lưu file `.app_datetime` |
| **Đồng hồ đứng im khi có `.app_datetime`** | ✅ Fixed | Mốc ảo + cộng thời gian thực (`time.time()`); đồng hồ chạy từng giây |
| **Alarm lệch giờ so với UI** | ✅ Fixed | `alarm_service.py` dùng `get_app_now()` thay vì `datetime.now()` |
| **Đồng hồ Home không refresh** | ✅ Fixed | `StringProperty` + `Clock.schedule_interval` trên `HomeScreen` |
| **Lệnh admin (date, set-date, gen-image...)** | ✅ Xong | `admin/admin_commands.py` — test alarm + ảnh |
| **Cache ảnh đơn thuốc (PIL)** | ✅ Xong | Kiểm tra tồn tại trước khi tạo |
| **30 file MP3 báo thức từ Mewdicate** | ✅ Xong | `assets/sounds/` |
| **Phát âm thanh alarm (pygame.mixer + winsound)** | ✅ Xong | `sound_manager.py` |
| **Rung khi báo thức (Windows beep)** | ✅ Xong | `sound_manager.py` |
| **Lưu cài đặt Dark Mode / Sound / Vibration** | ✅ Xong | `app_settings.py` — file `.app_settings.json` |
| **Chọn file chuông (popup 30 MP3 + nghe thử)** | ✅ Xong | `sound_manager.py` + `settings_screen.py` |
| **Âm thanh lặp đến khi xác nhận** | ✅ Xong | `play_alarm(loops=-1)` trong `sound_manager.py` |
| **Kivy 2.3.1 + KivyMD 1.2.0 BoxShadow crash** | ✅ Fixed | Sửa `site-packages/kivymd/uix/behaviors/elevation.py` — shadow_radius default `[0]`→`[0,0,0,0]`, border_radius KV `[1,1,1,1]` |
| **UI phong cách thẻ (HomeScreen + thanh nav dưới)** | ✅ Xong | `kv/home_screen.kv` — MedCard cao, bo góc 16dp, header teal, bottom nav bar |

---

## 4. Hệ thống Alarm - Chi tiết kỹ thuật

### Flow nhắc thuốc
```
[AlarmService check mỗi 10s]
        ↓
[Giờ hiện tại == Giờ thuốc?]  →  NO → tiếp tục check
        ↓ YES
[Đã uống chưa?]  →  YES → bỏ qua
        ↓ NO
[Mở khóa nút "Đã uống" trên HomeScreen + Hiện AlarmPopup + BEEP]
        ↓
[User chọn:]
  ├── "ĐÃ UỐNG" → confirm, dừng alarm
  └── "Snooze"  → nhắc lại sau interval
        ↓
[Loop tối đa 5 lần]
  Lần 1: ngay       | Demo: 0s
  Lần 2: +1 phút    | Demo: +10s
  Lần 3: +5 phút    | Demo: +20s
  Lần 4: +10 phút   | Demo: +30s
  Lần 5: +15 phút   | Demo: +40s
```

### QUY TẮC AN TOÀN MỚI (08/04/2026)
```
QUY TẮC: Nút "Đã uống" trên HomeScreen LUÔN ẨN và DISABLED.
         Chỉ HIỆN khi alarm thực sự bật popup.

  HomeScreen load_schedule()
      ↓
  med_unlocked = False  ← Luôn khóa
      ↓
  AlarmService check thấy đến giờ
      ↓
  _on_alarm_triggered()
      ↓
  _unlock_med_button(med_time, med_name)
      ↓
  med_unlocked = True  ← Chỉ mở khi CÓ thông báo
```

---

## 5. Hệ thống khung giờ chuẩn hóa y khoa

### Nguyên tắc thiết kế
Trong y khoa, thời điểm uống thuốc phụ thuộc rất lớn vào sự tương tác giữa thuốc và thức ăn, cũng như nhịp sinh học của cơ thể. App cung cấp các **mốc thời gian chuẩn hóa** để:

- Tránh người dùng nhập linh tinh ("lúc nào nhớ thì uống", "10h34 sáng")
- Đảm bảo cơ sở dữ liệu gọn gàng, AI dễ xử lý lên lịch
- Phù hợp với hướng dẫn lâm sàng thực tế

### Nhóm 1: Buổi cố định (theo nhịp sinh học)

| Tên buổi | Khung giờ | Mặc định | Lý do y khoa |
|----------|-----------|----------|--------------|
| **Sáng** | 06:00 - 08:00 | 06:00 | Thuốc nội tiết, thuốc bổ — uống khi đói bụng |
| **Trưa** | 11:30 - 13:00 | 12:00 | Gắn liền bữa ăn trưa |
| **Chiều-Tối** | 18:00 - 20:00 | 19:00 | Thuốc kháng sinh, thuốc dạ dày — uống với bữa tối |
| **Trước khi ngủ** | 21:00 - 22:00 | 21:30 | Thuốc huyết áp, statin — gan tổng hợp cholesterol mạnh lúc ngủ |

### Nhóm 2: Theo bữa ăn (quy định khoảng cách)

| Tên | Mặc định | Ghi chú | Thuốc ví dụ |
|-----|----------|---------|-------------|
| **Trước ăn (30-60 phút)** | 07:30 | Hấp thu nhanh khi bụng đói | Alendronate, Azithromycin |
| **Trong bữa ăn** | 08:00 | Trộn với thức ăn | Amoxicillin |
| **Sau ăn (15-30 phút)** | 08:30 | Tránh kích ứng đường tiêu hóa | NSAIDs, Doxycycline |
| **Sau ăn 1 tiếng** | 09:00 | Hấp thu tốt sau ăn no | Phần lớn kháng sinh |

### Nhóm 3: PRN (Khi có triệu chứng)

| Tên | Ghi chú | Khoảng cách tối thiểu |
|-----|---------|----------------------|
| **Khi sốt/đau** | Thuốc hạ sốt, giảm đau | Cách nhau 4-6 tiếng |
| **Khi cần** | Thuốc giãn phế quản, chống dị ứng | Tùy loại thuốc |

> **Lưu ý quan trọng:** PRN chỉ áp dụng cho thuốc không có lịch cố định. Khoảng cách tối thiểu phải được tuân thủ nghiêm ngặt để tránh quá liều.

---

## 6. AI Core — Kiến trúc

```
[User bấm "Quét"] → [AIScanScreen] → [ai_core/agent.py]
                                            ↓
                                     [LangGraph Agent]
                                            ↓
                                  [Tool: extract_prescription]
                                            ↓
                                     [JSON kết quả]
                                            ↓
                          [CrossCheckScreen: Form chỉnh sửa vs Ảnh đơn gốc]
                                            ↓
                              [User chỉnh sửa khung giờ theo mốc y khoa]
                                            ↓
                              [User tick checkbox đối chiếu]
                                            ↓
                                  [Lưu lịch nhắc thuốc]
```

---

## 7. Chatbot Triage — Logic phân loại

```
User input → Keyword matching:
  ├── GREEN: "tốt", "bình thường", "ổn", "khỏe"
  │     → "Tuyệt vời! Hãy tiếp tục duy trì"
  │
  ├── YELLOW: "mệt", "đau đầu", "buồn nôn"
  │     → "Mức độ 1-10? Nếu >7 nên gặp bác sĩ"
  │
  └── RED: "khó thở", "sốt cao", "co giật", "đau ngực"
        → Banner ĐỎ + Nút "Tìm bệnh viện cấp cứu"
```

---

## 8. Cách chạy ứng dụng

### 8.1. Cài đặt

```bash
pip install --user kivy kivymd pillow
pip install langchain langchain-openai langgraph python-dotenv  # (tùy chọn)
```

### 8.2. Chạy ứng dụng

```bash
cd G:\AI_THUC_CHIEN_20K_2026_K1\test_app\App1
python main.py
```

### 8.3. Lệnh Admin (test & debug)

Dùng file `admin/admin_commands.py` để quản lý ngày giờ, ảnh, và chạy app.

```bash
cd G:\AI_THUC_CHIEN_20K_2026_K1\test_app\App1
python admin/admin_commands.py <command>
```

| Lệnh | Mô tả |
|-------|--------|
| `date` | Hiển thị ngày giờ app đang dùng |
| `set-date "08/04/2026 07:00:00"` | Đặt ngày giờ tùy chỉnh (LƯU QUA LẦN CHẠY) |
| `reset-date` | Reset về ngày giờ hệ thống |
| `gen-image` | Tạo ảnh đơn thuốc giả lập (bỏ cache, tạo lại) |
| `show-image` | Xem thông tin + mở ảnh |
| `clear-cache` | Xóa ảnh đã cache |
| `run-app` | Chạy ứng dụng |
| `help` | Hiển thị trợ giúp |

#### Ví dụ test alarm:

```bash
# Cách 1: Đặt giờ trước 1 phút -> alarm sẽ trigger đúng giờ
python admin/admin_commands.py set-date "08/04/2026 06:59:00"
python admin/admin_commands.py run-app

# Reset về ngày thực
python admin/admin_commands.py reset-date
```

#### Ví dụ test ảnh:

```bash
# Tạo ảnh mới (bỏ cache)
python admin/admin_commands.py gen-image

# Mở xem ảnh
python admin/admin_commands.py show-image
```

### 8.4. Các format ngày giờ hỗ trợ

```
"08/04/2026 10:30:00"    (ngày/tháng/năm  giờ:phút:giây)
"08/04/2026 10:30"        (ngày/tháng/năm  giờ:phút)
"08/04/2026"              (ngày/tháng/năm)
"2026-04-08 10:30:00"    (năm-tháng-ngày  giờ:phút:giây)
"2026-04-08"              (năm-tháng-ngày)
```

---

## 9. TODO tương lai (ngoài scope MVP)

- [x] ~~Form nhập thuốc bằng tay~~ → Form chuẩn hóa đã có (MedEditCard + TimeSlotPopup)
- [ ] SQLite database (theo spec section 6.3)
- [ ] Push notification Android/iOS (Firebase)
- [ ] Correction log → pipeline retrain AI
- [ ] Export báo cáo tuân thủ cho bác sĩ
- [ ] Tích hợp TTS/STT cho chatbot
- [ ] Tìm bệnh viện thật qua Google Maps API
- [ ] Xác thực OTP/token (bảo mật PHI)

