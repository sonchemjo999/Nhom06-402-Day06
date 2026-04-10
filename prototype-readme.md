# MedReminder – Prototype README

---

## Mô tả Prototype

MedReminder là ứng dụng nhắc nhở uống thuốc tích hợp AI, cho phép người dùng chụp ảnh đơn thuốc để tự động trích xuất thông tin và tạo lịch uống thuốc cá nhân hoá. Ứng dụng chạy trên nền tảng Python/KivyMD, bao gồm AlarmService chạy nền, màn hình CrossCheck xác nhận thuốc, và chatbot phân loại mức độ triệu chứng.

---

## Level

**Working Prototype** – Ứng dụng chạy được trên thiết bị Android/desktop, các luồng P0 hoạt động end-to-end: quét đơn thuốc → xác nhận → nhắc nhở → xác nhận đã uống.

---

## Link Prototype

| Loại | Link |
|------|------|
| GitHub Repository | github.com/sonchemjo999/Nhom06-402-Day06 |
| Demo Video |https://drive.google.com/file/d/1vSn_o7D9VCtaXQPb8AaF3af3_gzVc1IB/view?usp=sharing|
| Figma Wireframes | https://canva.link/1uvwt55b8ju8fq1 |

---

## Tools và API đã dùng

| Thành phần | Công nghệ / API |
|-----------|----------------|
| Mobile Framework | Python 3.10 + KivyMD 2.0 |
| AI Orchestration | LangGraph 0.2+ |
| LLM / OCR | OpenAI GPT-4o-mini API |
| Alarm & Notification | Kivy `Clock`, Android `plyer` notification |
| Lưu trữ dữ liệu | JSON (local storage) |
| Camera | `kivy.uix.camera` |
| Containerisation | Docker *(dev environment)* |
| Version Control | Git / GitHub |

---

## Phân công

| Thành viên | MSSV | Role | Phụ trách cụ thể |
|-----------|------|------|-----------------|
| Nguyễn Anh Quân | 2A202600132 | Delivery Manager | Quản lý tiến độ, phân chia task theo sprint, review PR, đảm bảo nhóm ship đúng deadline |
| Phạm Đăng Phong | 2A202600254 | Fullstack Developer | Xây dựng toàn bộ UI screens (HomeScreen, AIScanScreen, CrossCheckScreen, ChatbotScreen, SettingsScreen), tích hợp backend logic vào giao diện |
| Võ Thiên Phú | 2A202600336 | PM + System Architecture | Viết PRD, vẽ flowchart user journey, xác định feature priority (P0–P3), thiết kế kiến trúc hệ thống (UI → Services → AI Core → External) |
| Phan Dương Định | 2A202600277 | Backend Developer / AI Engineer / Prompt Engineer | Xây dựng LangGraph agent, viết OCR tool và Prescription Extraction tool, tích hợp OpenAI API, thiết kế system prompt và few-shot examples cho đọc đơn thuốc |
| Phạm Minh Khang | 2A202600417 | Prompt Engineer + System Design | Thiết kế và tối ưu prompt chatbot phân loại triệu chứng, hỗ trợ system design cho AI Core layer, kiểm thử prompt với các edge case đơn thuốc tiếng Việt |
| Đào Hồng Sơn | 2A202600462 | Head of Engineering | Dẫn dắt kỹ thuật toàn nhóm, thiết kế AlarmService (snooze logic, attempt_counter, MISSED state), SoundManager, ThemeManager, review architecture và code quality |
