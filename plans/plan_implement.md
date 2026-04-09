# Implementation Plan (Next.js Monolithic)

Goal: implement MVP aligned with `spec-draft.md` and all files in `plans/`.
Architecture: one Next.js app (App Router) handles UI + API route handlers + background jobs.

## Step 1 - Project bootstrap and conventions

### Server làm gì
- [ ] Khởi tạo Next.js monolithic với TypeScript + Tailwind + Prisma + SQLite
- [ ] Tạo cấu trúc kỹ thuật: `app/api/`, `lib/server/`, `prisma/`, `scripts/`
- [ ] Tạo `.env.example` (DB URL, reviewer token, AI keys)
- [ ] Thiết lập chuẩn response lỗi chung (`code`, `message`, `details`)

### Client làm gì
- [ ] Tạo cấu trúc UI: `app/(routes)/`, `components/`, `lib/client/`
- [ ] Thiết lập base layout, global styles, state strategy (server/client components)
- [ ] Tạo trang health/demo cơ bản để verify app chạy được

### Checklist test feature
- [ ] `bun install` và `bun run dev` chạy thành công trên máy mới
- [ ] Truy cập trang chủ không lỗi build/runtime
- [ ] API health endpoint trả về 200
- [ ] Team follow được README để chạy local end-to-end

---

## Step 2 - Database schema and migration

### Server làm gì
- [ ] Định nghĩa Prisma schema theo `plans/database.md`
- [ ] Tạo migration đầu tiên cho: `patients`, `medications`, `reminders`, `symptom_logs`, `correction_logs`, `facility_cache`
- [ ] Thêm enums trạng thái: `PENDING`, `TAKEN`, `SNOOZED`, `MISSED`, `PENDING_REVIEW`, ...
- [ ] Viết seed script: 3-5 patients + 5 cơ sở Vinmec

### Client làm gì
- [ ] Chưa cần UI mới, chỉ cần adapter types để đọc dữ liệu seed cho dev
- [ ] Tạo mock-safe types đồng bộ với Prisma models

### Checklist test feature
- [ ] `prisma migrate` chạy được từ DB trống
- [ ] `prisma db seed` sinh dữ liệu đúng số lượng yêu cầu
- [ ] Truy vấn thử đọc dữ liệu từ route test trả đúng shape
- [ ] Có script reset DB + reseed chạy 1 lệnh

---

## Step 3 - Auth (MVP simple)

### Server làm gì
- [ ] Implement guard đọc `X-Patient-ID` cho patient APIs
- [ ] Implement reviewer guard với `X-Reviewer-Token` từ `.env`
- [ ] Chặn truy cập thiếu header/token với 401/403 chuẩn
- [ ] Mask PII/PHI trong server logs

### Client làm gì
- [ ] Tạo helper inject headers cho call API
- [ ] Thêm trạng thái UI khi gặp 401/403 (session missing, no permission)
- [ ] Chặn thao tác reviewer-only ở UI patient

### Checklist test feature
- [ ] Route patient gọi không có `X-Patient-ID` trả 401
- [ ] Route reviewer gọi sai token trả 403
- [ ] Route reviewer gọi đúng token trả 200
- [ ] Log kiểm tra không lộ thông tin nhạy cảm

---

## Step 4 - API scaffolding (contracts)

### Server làm gì
- [ ] Scaffold toàn bộ route handlers theo `plans/api_spec.md`
- [ ] Dùng Zod validate request/response
- [ ] Áp dụng unified error format cho mọi endpoint
- [ ] Viết API docs ngắn gọn cho route handlers

### Client làm gì
- [ ] Tạo API client layer typed theo contract
- [ ] Tạo error mapper để hiển thị lỗi thân thiện trên UI
- [ ] Tạo service hooks/fetchers dùng chung

### Checklist test feature
- [ ] Danh sách endpoint MVP đều callable
- [ ] Payload sai schema trả lỗi đúng format
- [ ] Contract test pass cho các endpoint chính
- [ ] API docs nội bộ khớp với hành vi thực tế

---

## Step 5 - OCR + medication extraction

### Server làm gì
- [ ] Pipeline: `image -> OCR text -> extraction prompt -> strict JSON`
- [ ] Validate strict JSON và reject output sai schema
- [ ] Rule an toàn: `confidence < 0.8` => `status=UNCLEAR`, `ask_human=true`
- [ ] Lưu draft vào `medications` với trạng thái `DRAFT`

### Client làm gì
- [ ] UI upload ảnh toa thuốc
- [ ] Hiển thị kết quả extract + confidence + trạng thái `UNCLEAR/DRAFT`
- [ ] Hiển thị cảnh báo rõ khi cần người dùng review thủ công

### Checklist test feature
- [ ] Upload ảnh rõ cho ra medication draft hợp lệ
- [ ] Upload ảnh mờ/khó đọc trả về `UNCLEAR`
- [ ] Output sai JSON không được lưu vào DB
- [ ] UI hiển thị đúng trạng thái và cảnh báo

---

## Step 6 - Patient review + activate medication

### Server làm gì
- [ ] Endpoint activate medication (`approved_by_patient=true`)
- [ ] Endpoint gửi correction (`POST /api/corrections`)
- [ ] Rule: correction medication luôn vào `PENDING_REVIEW` (không auto-apply)
- [ ] Lưu lịch sử thay đổi để audit

### Client làm gì
- [ ] Xây `PrescriptionReviewModal`: source, confidence, editable fields
- [ ] Cho phép user xác nhận dùng thuốc hoặc gửi correction
- [ ] Hiển thị `CorrectionStatusBanner` theo `PENDING_REVIEW/APPROVED/REJECTED`

### Checklist test feature
- [ ] User activate medication thành công khi không chỉnh sửa
- [ ] User chỉnh sửa thông tin tạo correction `PENDING_REVIEW`
- [ ] Không có correction nào auto-apply
- [ ] Banner trạng thái correction hiển thị đúng

---

## Step 7 - Reminder engine (5 minutes)

### Server làm gì
- [ ] Chạy reminder job mỗi 5 phút (cron/background worker)
- [ ] Rule window: `window_end_at = scheduled_time + 15 phút`
- [ ] Retry đến khi `TAKEN` hoặc quá `window_end_at` thì `MISSED`
- [ ] Endpoint `confirm` và `snooze 15 minutes` có idempotency key

### Client làm gì
- [ ] `MedicationReminderCard` với actions: confirm, snooze, report wrong dosage
- [ ] Hiển thị trạng thái reminder theo thời gian thực tế
- [ ] Disable nút khi request đang pending để tránh double submit

### Checklist test feature
- [ ] Confirm thành công thì reminder ngừng retry
- [ ] Snooze thành công thì lịch nhắc dời +15 phút
- [ ] Quá `window_end_at` không confirm thì thành `MISSED`
- [ ] Gửi trùng idempotency key không tạo action trùng

---

## Step 8 - Daily check + symptom triage

### Server làm gì
- [ ] Implement triage prompt với hard rules theo `plans/ai_prompts.md`
- [ ] Rule: uncertain thì escalate mức rủi ro (không downplay)
- [ ] Daily check: input mơ hồ phải hỏi thêm severity 1-10
- [ ] Lưu `symptom_logs` với đầy đủ: level, confidence, reason, action, severity_score

### Client làm gì
- [ ] Xây `DailyCheckChat` flow hỏi đáp nhiều bước
- [ ] UI yêu cầu nhập severity khi thiếu thông tin
- [ ] Hiển thị rõ kết luận triage + khuyến nghị hành động

### Checklist test feature
- [ ] Input red-flag trả `RED` + `GO_TO_EMERGENCY`
- [ ] Input thiếu rõ ràng trigger câu hỏi follow-up
- [ ] Case uncertain bị escalate đúng rule
- [ ] Bản ghi symptom_logs được lưu đủ fields

---

## Step 9 - Emergency nearby facilities

### Server làm gì
- [ ] Endpoint `POST /api/emergency/nearby`
- [ ] Filter theo location + open status + specialty
- [ ] Fallback: nếu không có specialty phù hợp thì bỏ specialty filter
- [ ] Ưu tiên Vinmec trong kết quả top

### Client làm gì
- [ ] Xây `EmergencyPanel`: call emergency, update location, find another location
- [ ] Hiển thị top 3 cơ sở gần nhất với thông tin cần thiết
- [ ] Luồng retry tìm lại khi user đổi vị trí

### Checklist test feature
- [ ] Case `RED` hiển thị top 3 cơ sở gần nhất
- [ ] Kết quả có ưu tiên Vinmec khi có dữ liệu phù hợp
- [ ] Đổi location cập nhật danh sách đúng
- [ ] Fallback specialty hoạt động khi không có match

---

## Step 10 - Complete mandatory UI/UX flows

### Server làm gì
- [ ] Hoàn thiện các API state cho correction/reminder/daily-check/emergency
- [ ] Đảm bảo mọi trạng thái lỗi có mã lỗi rõ ràng cho UI mapping

### Client làm gì
- [ ] Hoàn thiện `MedicationReminderCard`, `CorrectionStatusBanner`, `DailyCheckChat`, `EmergencyPanel`
- [ ] Bắt buộc checkbox cross-check trước khi confirm taken
- [ ] Hoàn thiện states: happy path, low-confidence, failure, correction

### Checklist test feature
- [ ] Demo được đủ 3 tính năng chính end-to-end
- [ ] Cross-check checkbox bắt buộc trước confirm
- [ ] Luồng lỗi API hiển thị thông báo đúng ngữ cảnh
- [ ] Không có dead-end UI (user luôn có next action)

---

## Step 11 - Metrics + observability

### Server làm gì
- [ ] Thu thập metrics: `clinical_precision`, `low_confidence_reject_rate`, `cross_check_adherence`, `high_confidence_failure_rate`
- [ ] Tạo endpoint/report cho safety metrics
- [ ] Thiết lập ngưỡng cảnh báo theo spec
- [ ] Track correction volume theo từng loại lỗi

### Client làm gì
- [ ] Tạo trang dashboard nội bộ để xem metrics chính
- [ ] Hiển thị cảnh báo threshold vượt ngưỡng
- [ ] Bảng theo dõi correction trends cho team review

### Checklist test feature
- [ ] Metrics endpoint trả số liệu đúng công thức
- [ ] Trigger dữ liệu mẫu thấy alert bật đúng ngưỡng
- [ ] Dashboard render được đầy đủ metrics bắt buộc
- [ ] Có thể dùng số liệu cho safety review/demo

---

## Step 12 - Testing and hardening

### Server làm gì
- [ ] Unit tests cho business rules quan trọng (unclear, escalate, approval, idempotency)
- [ ] Integration tests cho API flows end-to-end
- [ ] Test bảo mật: thiếu auth, sai role, invalid JSON, duplicate retry

### Client làm gì
- [ ] Component/integration tests cho các UI flow bắt buộc
- [ ] E2E tests cho các hành trình chính của patient
- [ ] Test UX lỗi mạng/API timeout và khả năng recover

### Checklist test feature
- [ ] Test suite pass trên critical flows
- [ ] Không còn bug blocker cho demo MVP
- [ ] Có test evidence cho các yêu cầu safety quan trọng
- [ ] Chạy dry-run demo ít nhất 2-3 lần không lỗi nghiêm trọng

---

## Step 13 - Demo release

### Server làm gì
- [ ] Chuẩn bị sample data + sample prescription images + mock fallback cho OCR/LLM
- [ ] Đóng gói cấu hình chạy demo ổn định
- [ ] Tag release nội bộ `mvp-demo-v1`

### Client làm gì
- [ ] Chốt kịch bản demo 7-10 phút
- [ ] Tối ưu UI copy và thứ tự flow cho demo mượt
- [ ] Chuẩn bị màn hình backup khi AI service lỗi

### Checklist test feature
- [ ] Demo full flow: Extract -> Reminder -> Daily Check -> Emergency -> Correction Review
- [ ] Có backup path hoạt động khi OCR/LLM fail
- [ ] Team member nào cũng chạy được kịch bản demo
- [ ] Bản release được tag và truy vết được

---

## Global Definition of Done (MVP)
- [ ] Next.js monolithic chạy ổn định (UI + API + jobs)
- [ ] 3 prompts hoạt động với strict JSON
- [ ] Medication correction bắt buộc qua reviewer approval
- [ ] Reminder có snooze 15 phút + cross-check checkbox
- [ ] Triage có hard rules + uncertain escalation
- [ ] Emergency suggestion hiển thị cơ sở gần nhất (Vinmec ưu tiên)
- [ ] Safety metrics khả dụng để theo dõi threshold

---

## File Reference Guide (per Step)

| Step | File(s) cần đọc | Ghi chú |
|------|-----------------|---------|
| Step 2 | `plans/database.md` | Toàn bộ schema, enums, seed data |
| Step 3 | `plans/architecture.md` (Security) | Auth headers, RBAC rules |
| Step 4 | `plans/api_spec.md` | Endpoint contracts |
| Step 5 | `plans/ai_prompts.md`, `plans/api_spec.md` | Extraction prompt + endpoint |
| Step 6 | `plans/api_spec.md`, `plans/ui_ux.md` | Activate/corrections + review modal |
| Step 7 | `plans/database.md`, `plans/api_spec.md` | Reminder rules + confirm/snooze |
| Step 8 | `plans/ai_prompts.md`, `plans/database.md` | Triage/daily-check + logs |
| Step 9 | `plans/api_spec.md`, `plans/ui_ux.md` | Nearby endpoint + EmergencyPanel |
| Step 10 | `plans/ui_ux.md` | Components + state flows |
| Step 11 | `plans/architecture.md`, `plans/api_spec.md` | Safety metrics + thresholds |
| Step 12-13 | Toàn bộ files trên | Full review trước demo |
