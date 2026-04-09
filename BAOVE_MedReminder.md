# 🛡️ TÀI LIỆU BẢO VỆ ĐỒ ÁN — MedReminder
> **Mục đích**: Chuẩn bị câu hỏi & câu trả lời cho buổi bảo vệ. Đọc kỹ từng phần, nắm vững lý do đằng sau mọi quyết định thiết kế.

---

## 📋 MỤC LỤC

1. [Tổng quan & Ý tưởng sản phẩm](#1-tổng-quan--ý-tưởng-sản-phẩm)
2. [Chức năng AI đọc đơn thuốc](#2-chức-năng-ai-đọc-đơn-thuốc)
3. [Hệ thống nhắc nhở & Alarm Service](#3-hệ-thống-nhắc-nhở--alarm-service)
4. [CrossCheck Screen — Xác nhận thông tin thuốc](#4-crosscheck-screen--xác-nhận-thông-tin-thuốc)
5. [Chatbot phân loại triệu chứng](#5-chatbot-phân-loại-triệu-chứng)
6. [Kiến trúc hệ thống & Công nghệ](#6-kiến-trúc-hệ-thống--công-nghệ)
7. [Bảo mật & Quyền riêng tư](#7-bảo-mật--quyền-riêng-tư)
8. [So sánh đối thủ & Lợi thế cạnh tranh](#8-so-sánh-đối-thủ--lợi-thế-cạnh-tranh)
9. [Hạn chế & Rủi ro](#9-hạn-chế--rủi-ro)
10. [Câu hỏi khó thường gặp](#10-câu-hỏi-khó-thường-gặp)

---

## 1. TỔNG QUAN & Ý TƯỞNG SẢN PHẨM

### ❓ "Tại sao lại làm ứng dụng nhắc uống thuốc? Vấn đề có thật không?"

**✅ Trả lời:**
Vấn đề quên uống thuốc là thực tế nghiêm trọng trong y tế:
- Theo WHO, tỷ lệ bệnh nhân không tuân thủ dùng thuốc đúng cách lên tới **50%** ở các bệnh mãn tính.
- Hậu quả: bệnh tái phát, tái nhập viện, tốn kém chi phí điều trị.
- Ở Việt Nam, người cao tuổi thường dùng 3–5 loại thuốc/ngày, khó nhớ hết giờ và liều lượng.
- Đơn thuốc viết tay từ bác sĩ thường khó đọc, bệnh nhân không hiểu rõ cách dùng.

> **MedReminder** giải quyết đúng 3 vấn đề cốt lõi: **quên uống**, **uống sai liều**, và **không hiểu đơn thuốc**.

---

### ❓ "Tại sao lại gắn thương hiệu Vinmec?"

**✅ Trả lời:**
- Vinmec là hệ thống bệnh viện tư hàng đầu Việt Nam, có uy tín cao về y tế.
- Người dùng tin tưởng hơn vào ứng dụng y tế có thương hiệu bệnh viện uy tín đứng sau.
- Hướng đến tích hợp thực tế với **Vinmec HIS** (Hospital Information System) trong tương lai để nhận đơn thuốc điện tử trực tiếp.
- Mô hình B2B với Vinmec tạo nguồn doanh thu bền vững hơn so với ứng dụng độc lập.

---

### ❓ "Người dùng mục tiêu của các bạn là ai? Có quá rộng không?"

**✅ Trả lời:**
Chúng tôi xác định **3 nhóm người dùng chính** với độ ưu tiên rõ ràng:

| Nhóm | Đặc điểm | Cách tiếp cận |
|------|----------|---------------|
| **Ưu tiên 1** — Bệnh nhân ngoại trú | Có đơn thuốc cụ thể, cần nhắc nhở | Core feature: scan + alarm |
| **Ưu tiên 2** — Người cao tuổi | Ít quen công nghệ, cần UI đơn giản | Font lớn, UX đơn giản |
| **Ưu tiên 3** — Người chăm sóc | Quản lý thuốc cho người thân | Multi-user (Phase 2) |

MVP tập trung vào nhóm 1 và 2 trước — đây là cách tiếp cận đúng đắn, tránh over-engineering.

---

## 2. CHỨC NĂNG AI ĐỌC ĐƠN THUỐC

### ❓ "AI đọc đơn thuốc hoạt động như thế nào? Độ chính xác bao nhiêu?"

**✅ Trả lời — Quy trình gồm 3 bước:**

```
Ảnh đơn thuốc
     │
     ▼
[Bước 1] Tiền xử lý ảnh
  • Normalize độ sáng
  • Sharpen để tăng độ nét chữ
  • Chuẩn bị payload
     │
     ▼
[Bước 2] OCR + AI (GPT-4o-mini qua LangGraph)
  • Tool: extract_prescription()
  • System Prompt: Medical OCR guidelines
  • Trích xuất: tên thuốc, liều lượng, tần suất, thời điểm uống
     │
     ▼
[Bước 3] Đánh giá confidence score
  • confidence >= 0.8 → Chuyển sang CrossCheck
  • confidence < 0.8  → Yêu cầu nhập tay
```

**Về độ chính xác:** GPT-4o-mini với visual input có độ chính xác cao cho text chuẩn. Với đơn thuốc viết tay khó đọc, hệ thống tự nhận biết và fallback về nhập tay — **không bao giờ lưu kết quả sai mà không có xác nhận người dùng**.

---

### ❓ "Tại sao dùng GPT-4o-mini mà không dùng mô hình OCR chuyên biệt như Tesseract?"

**✅ Trả lời:**
| Tiêu chí | Tesseract (OCR thuần) | GPT-4o-mini (LLM + Vision) |
|----------|----------------------|-----------------------------|
| Nhận diện chữ viết tay | Yếu | **Tốt hơn đáng kể** |
| Hiểu ngữ cảnh y tế | Không | **Có** (hiểu "1v x 2 lần/ngày") |
| Chuẩn hóa tên thuốc | Không | **Có** (viết tắt → tên đầy đủ) |
| Trích xuất có cấu trúc | Cần post-processing | **Trả về JSON trực tiếp** |
| Chi phí | Miễn phí | Trả phí theo usage |

> Trong bài toán đọc đơn thuốc — vốn có ngôn ngữ y tế chuyên ngành, chữ viết tay, viết tắt — LLM có vision vượt trội so với OCR thuần túy.

---

### ❓ "Nếu AI đọc sai thuốc, bệnh nhân uống sai có nguy hiểm không? Các bạn xử lý thế nào?"

**✅ Trả lời — Cơ chế an toàn nhiều lớp:**

1. **Confidence threshold**: Kết quả dưới 80% tự động chuyển về nhập tay.
2. **CrossCheck bắt buộc**: Người dùng PHẢI tick checkbox xác nhận trước khi lưu — không thể bỏ qua.
3. **Hiển thị song song**: Màn hình CrossCheck cho thấy cả kết quả AI lẫn ảnh gốc đơn thuốc để người dùng so sánh.
4. **Có thể chỉnh sửa**: Mọi trường thông tin đều có thể sửa trực tiếp.
5. **Thông điệp cảnh báo rõ ràng**: *"Vui lòng kiểm tra kỹ tên thuốc và liều lượng"* xuất hiện nổi bật.

> Triết lý thiết kế: **AI hỗ trợ, con người quyết định**. AI không bao giờ tự động lưu mà không có sự xác nhận của người dùng.

---

### ❓ "LangGraph là gì? Tại sao dùng LangGraph thay vì gọi OpenAI API trực tiếp?"

**✅ Trả lời:**
LangGraph là framework xây dựng **AI Agent có trạng thái (stateful)**, cho phép:
- Định nghĩa **tool** rõ ràng: `extract_prescription()`, chatbot tools...
- Quản lý **flow** xử lý phức tạp: thử lại khi thất bại, fallback logic.
- Dễ **mở rộng** thêm tool mới (ví dụ: tra cứu tương tác thuốc) mà không refactor toàn bộ code.
- **Kiểm soát** rõ ràng hơn so với gọi API trực tiếp — biết chính xác tool nào được gọi, input/output là gì.

> Nếu gọi OpenAI trực tiếp, code sẽ cứng nhắc. LangGraph cho phép chúng tôi xây dựng một **AI Agent pipeline** có thể mở rộng theo Phase 2, 3.

---

## 3. HỆ THỐNG NHẮC NHỞ & ALARM SERVICE

### ❓ "Alarm hoạt động như thế nào khi app bị tắt/minimize?"

**✅ Trả lời:**
AlarmService chạy như một **background service** sử dụng `Clock.schedule_interval` của Kivy:
- Trong **demo/test**: interval = 10 giây (để tiện kiểm tra).
- Trong **production**: interval = 30 giây để cân bằng pin và độ chính xác.
- Service liên tục check danh sách thuốc trong storage, so sánh với giờ hiện tại.
- Khi đến giờ → hiện `AlarmPopup` toàn màn hình + phát âm thanh + rung.

**Về trường hợp app bị kill:** Đây là giới hạn của Kivy trên Android — app bị kill thì background thread cũng bị dừng. Giải pháp trong **Phase 2** là tích hợp Android Foreground Service thực sự hoặc WorkManager để đảm bảo nhắc nhở kể cả khi app bị đóng hoàn toàn.

---

### ❓ "Cơ chế Snooze hoạt động thế nào? Tại sao giới hạn 5 lần?"

**✅ Trả lời:**
```
Attempt 1 → Popup lần 1
Attempt 2 → Snooze 5 phút → Popup lần 2
...
Attempt 5 → Snooze → Popup lần 5
Attempt > 5 → Đánh dấu "MISSED", dừng nhắc
```

**Tại sao giới hạn 5 lần:**
- Sau 5 lần nhắc (tương đương ~50 phút), nếu vẫn không uống → coi như đã bỏ qua có chủ đích.
- Tránh app nhắc mãi gây phiền nhiễu → người dùng tắt thông báo hoàn toàn.
- Trạng thái "MISSED" được ghi log để theo dõi lịch sử tuân thủ.

---

### ❓ "Tại sao dùng JSON để lưu dữ liệu thay vì database thực như SQLite hay PostgreSQL?"

**✅ Trả lời:**
Đây là quyết định **hợp lý cho MVP** vì:
1. **Đơn giản**: Không cần setup database, không có migration phức tạp.
2. **Portable**: File JSON dễ đọc, dễ debug trong quá trình phát triển.
3. **Đủ dùng cho MVP**: Với ~10–20 thuốc/người, JSON hoàn toàn đáp ứng về hiệu năng.
4. **Roadmap rõ ràng**: Phase 2 sẽ migrate sang **PostgreSQL** khi có tính năng đăng nhập/đồng bộ đám mây.

> SQLite sẽ là bước trung gian phù hợp nếu cần quan hệ dữ liệu phức tạp hơn trước khi lên PostgreSQL.

---

## 4. CROSSCHECK SCREEN — XÁC NHẬN THÔNG TIN THUỐC

### ❓ "CrossCheck Screen có giao diện như thế nào? Tại sao thiết kế 2 cột?"

**✅ Trả lời:**
```
┌─────────────────────────────────────────────────────────────┐
│                    CrossCheck Screen                         │
│  ┌─────────────────────┐  │  ┌──────────────────────────┐  │
│  │   KẾT QUẢ AI        │  │  │  ẢNH GỐC ĐƠN THUỐC      │  │
│  │ • Tên thuốc         │  │  │  (Zoomable)              │  │
│  │ • Liều lượng        │  │  │                          │  │
│  │ • Giờ uống          │  │  │                          │  │
│  │ • Confidence: 95%   │  │  │                          │  │
│  └─────────────────────┘  │  └──────────────────────────┘  │
│                                                              │
│  ⚠️  Vui lòng kiểm tra kỹ trước khi lưu                    │
│  ☐  Tôi đã xác nhận thông tin chính xác                    │
│                                                              │
│  [ Hủy ]                       [ Xác nhận & Lưu ]          │
└─────────────────────────────────────────────────────────────┘
```

**Lý do thiết kế 2 cột:**
- Người dùng **đối chiếu trực tiếp** kết quả AI với ảnh gốc mà không cần chuyển qua lại màn hình.
- Giảm cognitive load: thay vì nhớ thông tin từ ảnh rồi so sánh, người dùng thấy cả hai cùng lúc.
- Tuân theo nguyên tắc UX: **Recognition over Recall** (nhận diện dễ hơn nhớ lại).

---

### ❓ "Tại sao bắt buộc tick checkbox mới lưu được? Có phiền không?"

**✅ Trả lời:**
Đây là **quyết định thiết kế có chủ đích vì lý do an toàn y tế:**
- Thuốc là lĩnh vực nhạy cảm — lưu sai thông tin có thể gây hại sức khỏe.
- Checkbox buộc người dùng **dừng lại và đọc** thay vì bấm nhanh qua màn hình.
- Tạo ra **trách nhiệm pháp lý rõ ràng**: người dùng xác nhận đã kiểm tra.
- Tương tự các hệ thống y tế chuyên nghiệp áp dụng nguyên tắc **double-check** trước khi thực hiện.

> Không phải mọi UX friction đều là xấu — đôi khi **cản trở có chủ đích** bảo vệ người dùng.

---

## 5. CHATBOT PHÂN LOẠI TRIỆU CHỨNG

### ❓ "Chatbot hoạt động thế nào? Có thực sự dùng AI không?"

**✅ Trả lời — Chatbot dùng 2 tầng phân tích:**

**Tầng 1 — Keyword Detection (nhanh, không cần API):**
| Mức độ | Từ khóa | Hành động |
|--------|---------|-----------|
| 🟢 AN TOÀN | tốt, khỏe, bình thường, ok | Phản hồi tích cực, khuyến khích |
| 🟡 CẢNH BÁO | mệt, đau đầu, buồn nôn, sốt nhẹ | Khuyên theo dõi, uống đủ nước |
| 🔴 NGUY HIỂM | khó thở, sốt cao, co giật, ngất | Khuyên gọi cấp cứu ngay |

**Tầng 2 — LangGraph Agent (phân tích ngữ cảnh phức tạp):**
- Khi câu hỏi không khớp keyword đơn giản.
- Phân tích toàn bộ context cuộc hội thoại.
- Kết hợp thông tin thuốc đang dùng để đưa ra lời khuyên phù hợp.

---

### ❓ "Chatbot có phải bác sĩ không? Điều này có vi phạm pháp luật không?"

**✅ Trả lời:**
Chatbot **KHÔNG chẩn đoán bệnh** — đây là điểm quan trọng:
- Chatbot **phân loại mức độ khẩn cấp của triệu chứng**, không kê đơn hay chẩn đoán.
- Chức năng tương tự **triage sơ bộ** — giúp người dùng biết có cần đến gặp bác sĩ ngay không.
- Mọi phản hồi đều có disclaimer: *"Đây không phải lời khuyên y tế chính thức. Hãy gặp bác sĩ để được tư vấn cụ thể."*
- Tương tự cách các ứng dụng sức khỏe lớn như WebMD, Ada Health hoạt động hợp pháp.

---

### ❓ "Tại sao chatbot cần biết thuốc bệnh nhân đang dùng?"

**✅ Trả lời:**
Đây là **lợi thế độc đáo** của chatbot tích hợp vào ứng dụng nhắc thuốc:
- Biết bệnh nhân đang dùng thuốc gì → có thể cảnh báo **tác dụng phụ** liên quan.
- Ví dụ: Bệnh nhân báo "đau bao tử" + đang dùng Aspirin → chatbot có thể liên kết nguyên nhân và khuyên ăn no trước khi uống thuốc.
- Đây là tính năng mà **không ứng dụng nào ở Việt Nam** hiện có.

---

## 6. KIẾN TRÚC HỆ THỐNG & CÔNG NGHỆ

### ❓ "Tại sao dùng Python + Kivy thay vì React Native hay Flutter?"

**✅ Trả lời:**
| Tiêu chí | React Native / Flutter | Python + Kivy |
|----------|------------------------|---------------|
| Tích hợp AI/ML | Cần bridge riêng | **Native Python — tích hợp trực tiếp** |
| LangGraph | Không hỗ trợ | **Tích hợp hoàn toàn** |
| Học tập | Phải học Dart/JS | **Python đã quen** |
| Production-ready | Tốt hơn | Đủ cho MVP |

> **Lý do cốt lõi**: Dự án tập trung vào AI Pipeline (LangGraph, GPT-4o-mini). Python là ngôn ngữ tự nhiên nhất cho AI/ML. Dùng Kivy cho phép **toàn bộ stack viết bằng Python**, giảm context-switching và tăng tốc độ phát triển.

---

### ❓ "Kiến trúc 3 lớp của hệ thống là gì?"

**✅ Trả lời:**

```
┌──────────────────────────────────────────────────────┐
│  LAYER 1: Presentation (Kivy/KivyMD Screens)          │
│  HomeScreen │ AIScanScreen │ CrossCheckScreen │ Chatbot│
└─────────────────────────┬────────────────────────────┘
                           │
┌─────────────────────────▼────────────────────────────┐
│  LAYER 2: Services (Business Logic)                   │
│  AlarmService │ SoundManager │ NotificationService     │
└─────────────────────────┬────────────────────────────┘
                           │
┌─────────────────────────▼────────────────────────────┐
│  LAYER 3: AI Core + External                         │
│  LangGraph Agent │ GPT-4o-mini │ JSON Storage         │
└──────────────────────────────────────────────────────┘
```

- **Tách biệt rõ ràng** giữa UI, business logic và AI/data layer.
- Dễ **thay thế từng layer**: ví dụ đổi JSON sang PostgreSQL mà không ảnh hưởng UI.
- Dễ **test từng phần** độc lập.

---

### ❓ "Tại sao dùng FastAPI cho backend trong tương lai thay vì Django?"

**✅ Trả lời:**
- **FastAPI** phù hợp hơn với **microservices** và **async** — cần thiết khi xử lý AI API calls.
- Django phù hợp với monolithic web app có ORM phức tạp — quá nặng cho một backend API thuần.
- FastAPI có **auto-generated OpenAPI docs** — tiện cho team frontend tích hợp.
- **Performance**: FastAPI nhanh hơn Django REST Framework ~2-3 lần trong benchmark thực tế.

---

## 7. BẢO MẬT & QUYỀN RIÊNG TƯ

### ❓ "Dữ liệu y tế của người dùng được bảo vệ như thế nào?"

**✅ Trả lời — Chiến lược bảo mật nhiều lớp:**

| Loại dữ liệu | Mức nhạy cảm | Cách xử lý |
|-------------|-------------|------------|
| Thông tin thuốc | Cao | Mã hoá, **chỉ lưu cục bộ** |
| Ảnh đơn thuốc | Cao | **Xoá ngay sau khi xử lý** |
| Triệu chứng sức khỏe | Rất cao | **Không lưu**, chỉ xử lý trong session |
| Lịch sử uống thuốc | Cao | Lưu local, mã hoá |

**Quyền truy cập tối thiểu:**
- Camera: Chỉ khi người dùng chủ động mở AIScanScreen.
- Thông báo: Bắt buộc cho core feature nhắc nhở.
- Không yêu cầu: Location, Contacts, Internet (ngoài AI API calls).

---

### ❓ "Các bạn tuân thủ luật pháp nào về dữ liệu y tế?"

**✅ Trả lời:**
1. **Luật An ninh mạng Việt Nam 2015**: Không lưu trữ dữ liệu người dùng trên server nước ngoài cho dữ liệu cá nhân nhạy cảm.
2. **Nghị định 13/2023/NĐ-CP**: Về bảo vệ dữ liệu cá nhân — có cơ chế xin phép, giải thích lý do thu thập.
3. **Quy định Bộ Y tế về đơn thuốc điện tử**: Đảm bảo tương thích khi tích hợp Vinmec HIS.

> **Giải pháp**: Lưu dữ liệu cục bộ (on-device) là giải pháp an toàn nhất cho MVP — không cần lo server-side breach.

---

## 8. SO SÁNH ĐỐI THỦ & LỢI THẾ CẠNH TRANH

### ❓ "Đã có nhiều app nhắc uống thuốc rồi. MedReminder khác gì?"

**✅ Trả lời:**

| Tính năng | MedReminder | MedMinder | Drugs.com | BV108 App |
|----------|:-----------:|:---------:|:---------:|:---------:|
| AI đọc đơn thuốc | ✅ | ❌ | ❌ | ❌ |
| Chatbot phân loại triệu chứng | ✅ | ❌ | ❌ | ❌ |
| Giao diện tiếng Việt | ✅ | ❌ | Một phần | ✅ |
| Tích hợp bệnh viện VN | ✅ (Vinmec) | ❌ | ❌ | BV108 only |
| Miễn phí cơ bản | ✅ | ❌ ($5/tháng) | ✅ | ✅ |
| CrossCheck an toàn | ✅ | ❌ | ❌ | ❌ |

> **Điểm khác biệt duy nhất ở Việt Nam**: Kết hợp AI đọc đơn thuốc + phân loại triệu chứng + thương hiệu Vinmec trong một ứng dụng.

---

### ❓ "Nếu Google hay Apple làm tính năng tương tự thì sao?"

**✅ Trả lời:**
- Google/Apple Health chỉ làm **platform** — không đi sâu vào nghiệp vụ y tế cụ thể của từng quốc gia.
- **Lợi thế địa phương**: Đơn thuốc Việt Nam có format, viết tắt, tên thuốc riêng — cần train model hoặc prompt engineer theo đặc thù Việt Nam.
- **Tích hợp Vinmec HIS** là moat thực sự — bất kỳ đối thủ nào cũng phải đàm phán lại từ đầu.
- Về dài hạn: nếu Big Tech vào thị trường này, đó là **xác nhận thị trường có giá trị** — còn hiện tại chúng tôi đang di chuyển nhanh hơn.

---

## 9. HẠN CHẾ & RỦI RO

### ❓ "Hạn chế lớn nhất của ứng dụng hiện tại là gì?"

**✅ Trả lời trung thực — Thể hiện sự hiểu biết sâu:**

1. **Lưu trữ cục bộ (JSON)**: Mất dữ liệu nếu xóa app, không đồng bộ đa thiết bị. → *Giải pháp: Phase 2 thêm cloud sync.*

2. **Background service trên Android**: Kivy không có Foreground Service thực sự, app bị kill sẽ mất nhắc nhở. → *Giải pháp: Phase 2 tích hợp Android WorkManager.*

3. **Phụ thuộc OpenAI API**: Nếu API down hoặc tăng giá sẽ ảnh hưởng. → *Giải pháp: Fallback về nhập tay, xem xét self-hosted model trong Phase 3.*

4. **Chưa có đăng nhập**: Không phân biệt người dùng, không bảo vệ dữ liệu riêng tư trên thiết bị chung. → *Phase 2.*

> Nhận biết hạn chế và có roadmap rõ ràng thể hiện team hiểu sản phẩm và lập kế hoạch nghiêm túc.

---

### ❓ "Nếu AI đọc sai tên thuốc mà người dùng không phát hiện thì sao? Trách nhiệm thuộc về ai?"

**✅ Trả lời:**
- Hệ thống có **nhiều cơ chế ngăn ngừa** (như đã giải thích ở mục 2).
- Về mặt pháp lý: Ứng dụng là **công cụ hỗ trợ**, không thay thế bác sĩ hay dược sĩ. Tương tự như máy tính bỏ túi hỗ trợ kế toán — sai số cuối cùng là trách nhiệm người dùng.
- **Terms of Service** sẽ nêu rõ disclaimer này.
- Thiết kế bắt buộc xác nhận chính là **cơ chế chuyển giao trách nhiệm** hợp pháp từ hệ thống sang người dùng.

---

## 10. CÂU HỎI KHÓ THƯỜNG GẶP

### ❓ "Các bạn đã test ứng dụng chưa? Kết quả thế nào?"

**✅ Trả lời:**
- MVP đã hoàn thành đầy đủ 5 màn hình chính.
- Đã test toàn bộ happy path: scan ảnh → crosscheck → alarm → confirm.
- Đã test fallback: confidence thấp → nhập tay; snooze → attempt counter tăng đúng.
- **Chỉ số hiệu suất đạt được:**
  - Thời gian khởi động: < 3 giây ✅
  - Phản hồi AI: < 5 giây ✅
  - Thông báo popup: < 1 giây ✅
- Chưa có user testing thực tế với bệnh nhân thật — đây là bước tiếp theo sau MVP.

---

### ❓ "Doanh thu từ đâu? Freemium có hiệu quả không?"

**✅ Trả lời:**
**3 nguồn doanh thu:**

1. **Quảng cáo Vinmec** (không xâm lấn UX): Vinmec promote dịch vụ khám chữa bệnh trực tiếp đến đúng đối tượng bệnh nhân — CPM cao, engagement tốt.

2. **Premium subscription**: Nhắc nhở không giới hạn, AI nâng cao, báo cáo sức khỏe, đồng bộ đa thiết bị.

3. **B2B với phòng khám**: Tích hợp API, white-label solution cho các bệnh viện khác.

> **Freemium hợp lý vì**: User acquisition cost gần bằng 0 (Vinmec có sẵn bệnh nhân), conversion chỉ cần 5–10% là có lợi nhuận.

---

### ❓ "Tại sao chọn KivyMD 2.0+? Framework này có đang được maintain tốt không?"

**✅ Trả lời:**
- KivyMD 2.0 được release năm 2024, đang active development.
- Cung cấp **Material Design 3** components — đủ để xây UI chuyên nghiệp.
- Điểm quan trọng: **Python-native** cho phép tích hợp AI libraries (LangGraph, OpenAI) mà không cần bridge.
- Nhược điểm thừa nhận: Ecosystem nhỏ hơn Flutter, ít tài liệu hơn. Tuy nhiên đây là trade-off chấp nhận được cho một team Python-first.

---

### ❓ "KPIs 100,000 lượt tải trong 6 tháng có thực tế không?"

**✅ Trả lời:**
Đây là **mục tiêu aspirational** cho scenario có hỗ trợ từ Vinmec:
- Vinmec phục vụ hàng triệu bệnh nhân/năm trên toàn quốc.
- Nếu Vinmec recommend app cho bệnh nhân ngoại trú → conversion tự nhiên rất cao.
- **Thực tế hơn**: 10,000 MAU trong 6 tháng đầu là benchmark hợp lý cho B2C health app tại Việt Nam.
- Quan trọng hơn số lượt tải là **tỷ lệ tuân thủ thuốc > 85%** — đây mới là KPI y tế thực sự có ý nghĩa.

---

### ❓ "Dark Mode có phải waste of time không? Tại sao ưu tiên P1?"

**✅ Trả lời:**
- Người dùng thường uống thuốc vào **tối và sáng sớm** — Dark Mode giảm mỏi mắt đáng kể.
- Với người cao tuổi, màn hình sáng chói vào ban đêm là vấn đề thực tế.
- Implementation không phức tạp: ThemeManager đã được tích hợp từ đầu, toggle chỉ cần đổi color palette.
- ROI cao: Tính năng nhỏ nhưng tăng **retention** và **user satisfaction** đáng kể.

---

## 🎯 CHECKLIST TRƯỚC KHI BẢO VỆ

- [ ] Tất cả thành viên đều hiểu **AI pipeline**: ảnh → OCR → LangGraph → confidence → CrossCheck
- [ ] Nắm vững **lý do thiết kế CrossCheck bắt buộc xác nhận** (an toàn y tế)
- [ ] Giải thích được **Snooze logic** và tại sao giới hạn 5 lần
- [ ] Biết phân biệt chatbot **triage** vs **chẩn đoán bệnh** (legal important!)
- [ ] Có thể demo **happy path** mượt mà: scan → crosscheck → lưu → alarm → confirm
- [ ] Sẵn sàng thừa nhận hạn chế và có **roadmap Phase 2** rõ ràng
- [ ] Nhớ **3 điểm khác biệt cốt lõi**: AI đọc đơn thuốc + chatbot triệu chứng + Vinmec integration

---

> **💡 Tip bảo vệ**: Khi không biết câu trả lời → thừa nhận thẳng thắn và nói "Đây là điểm chúng tôi sẽ nghiên cứu thêm trong Phase 2" thay vì đoán mò. Hội đồng đánh giá cao sự trung thực hơn là câu trả lời sai tự tin.

---

*Tài liệu bảo vệ — MedReminder v1.0 | Ngày: 09/04/2026*
