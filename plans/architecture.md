# Implementation Plan v2 — Vinmec AI Assistant (Next.js Monolithic)

**Goal**: Implement MVP aligned with `spec-draft.md` and all files in `plans/`.  
**Architecture**: One Next.js app (App Router) — UI + API route handlers + background jobs.  
**Stack**: Next.js + TypeScript + Tailwind + Prisma + SQLite + OpenAI API + Pytesseract

---

## Phase 1 — Foundation

---

## Step 1 — Project bootstrap & conventions

### Server

- Init Next.js monolithic với TypeScript + Tailwind + Prisma + SQLite
- Cấu trúc thư mục bắt buộc:
  - `app/api/` — route handlers
  - `lib/server/` — business logic, services, AI calls
  - `prisma/` — schema, migrations, seed
  - `scripts/` — db reset, seed, utilities
- Tạo `.env.example` với các biến: `DATABASE_URL`, `REVIEWER_TOKEN`, `OPENAI_API_KEY`, `PYTESSERACT_PATH`
- Định nghĩa unified error response format dùng xuyên suốt toàn app:
  ```json
  { "code": "VALIDATION_ERROR", "message": "...", "details": {} }
  ```
- Setup health endpoint `GET /api/health` trả `{ "status": "ok", "ts": "<ISO timestamp>" }`

### Client

- Cấu trúc thư mục: `app/(routes)/`, `components/`, `lib/client/`
- Base layout với global styles, font (Inter hoặc Roboto)
- Color tokens theo Vinmec design: primary `#004225`, danger `#FF4D4D`, warning `#FFB020`, corner radius `12px`
- Trang `/` placeholder để verify app chạy, không lỗi build

### Checklist done

- [ ] `bun install && bun run dev` chạy không lỗi trên máy mới
- [ ] `GET /api/health` trả 200 OK
- [ ] Team member clone repo, làm theo README, chạy được local end-to-end

---

## Step 2 — Database schema & migration

### Server

- Định nghĩa Prisma schema đầy đủ cho 6 bảng theo `plans/database.md`: `patients`, `medications`, `reminders`, `symptom_logs`, `correction_logs`, `facility_cache`
- Đảm bảo đủ tất cả safety-critical fields:
  - `medications`: `confidence`, `source_type`, `source_ref`, `status`
  - `reminders`: `window_end_at`, `cross_check_confirmed`, `snooze_count`, `last_notified_at`
  - `correction_logs`: `original_payload`, `corrected_payload`, `approval_status`, `reviewed_by`, `review_note`
- Enum statuses:
  - Medication: `DRAFT | ACTIVE | INACTIVE`
  - Reminder: `PENDING | TAKEN | MISSED | SNOOZED`
  - Correction: `NOT_REQUIRED | PENDING_REVIEW | APPROVED | REJECTED`
  - Triage: `GREEN | YELLOW | RED`
- Chạy `prisma migrate dev --name init` từ DB trống
- Viết seed script:
  - 3 patients mẫu với phone và name
  - 5 Vinmec facilities theo đúng tọa độ spec (`facility_cache`): Times City, Royal City, Central Park, Nha Trang, Hai Phong
- Script `bun run db:reset`: drop + migrate + seed chạy 1 lệnh

### Client

- Export Prisma-generated types ra `lib/types.ts` để FE dùng chung (không duplicate type)
- Tạo mock data fixtures khớp shape DB cho dev khi chưa có API thật

### Checklist done

- [ ] `prisma migrate dev` từ DB trống → thành công, không lỗi
- [ ] `bun run db:reset` chạy idempotent nhiều lần
- [ ] Seed sinh đúng 3 patients + 5 Vinmec facilities
- [ ] Prisma Studio query được data và relationships đúng

---

## Step 3 — Auth (MVP simple headers)

### Server

- Middleware `withPatientAuth(handler)`:
  - Đọc header `X-Patient-ID`
  - Nếu thiếu → 401 `{ code: "MISSING_AUTH" }`
  - Query DB kiểm tra patient tồn tại → không tồn tại → 401
  - Inject `patientId` vào request context để handler dùng
- Middleware `withReviewerAuth(handler)`:
  - Đọc header `X-Reviewer-Token`
  - So sánh với `process.env.REVIEWER_TOKEN`
  - Sai hoặc thiếu → 403 `{ code: "FORBIDDEN" }`
- RBAC guard: trong mọi patient handler, so sánh `resource.patient_id === ctx.patientId` → không khớp → 403
- PHI masking trong server logs: trước khi `console.log`, replace phone/name với `[MASKED]` qua helper `maskPHI(obj)`

### Client

- Helper `apiClient(patientId)`: wrapper fetch tự inject `X-Patient-ID` vào mọi request
- Khi nhận 401: redirect về `/select-patient` hoặc hiển thị modal chọn patient
- Khi nhận 403: toast notification "Bạn không có quyền thực hiện thao tác này"
- Ẩn tất cả action reviewer-only (nút Approve/Reject) khỏi patient UI

### Checklist done

- [ ] Call không có `X-Patient-ID` → 401
- [ ] Call sai `X-Reviewer-Token` → 403
- [ ] Patient A dùng `X-Patient-ID` của patient B để đọc data → 403
- [ ] Server logs không in phone/name plaintext

---

## Step 4 — API scaffolding & contracts

### Server

- Scaffold tất cả route handlers theo `plans/api_spec.md` (stub — trả đúng shape, chưa cần logic thật):
  - `POST /api/medications/extract`
  - `POST /api/medications/{id}/activate`
  - `POST /api/corrections`
  - `POST /api/corrections/{id}/approve`
  - `POST /api/reminders/{id}/confirm`
  - `POST /api/reminders/{id}/snooze`
  - `POST /api/symptoms/triage`
  - `POST /api/daily-checks`
  - `POST /api/emergency/nearby`
  - `GET /api/patients/{id}/history`
  - `GET /api/metrics/safety`
- Dùng Zod schema validate request body cho từng endpoint — payload sai schema → 422 với `details` liệt kê field lỗi
- Tất cả handlers dùng unified error format đã định nghĩa ở Step 1

### Client

- API client layer typed: mỗi endpoint một async function với typed input/output từ Zod schema
- Error mapper `mapApiError(code)`: chuyển error code thành message tiếng Việt thân thiện
- Custom hook `useApi<T>(fn)`: trả `{ data, loading, error, execute }` — dùng chung cho mọi call

### Checklist done

- [ ] Tất cả 11 endpoint gọi được, trả 200 với stub response đúng shape
- [ ] Payload sai Zod schema → 422 với `details` field rõ ràng
- [ ] FE có thể gọi mọi endpoint với typed response (TypeScript không báo lỗi)

---

## Phase 2 — Core Features

---

## Step 5 — OCR + AI medication extraction

> **Safety-critical**: Output sai schema hoặc confidence thấp phải bị chặn hoàn toàn — không lưu DB.

### Server

Implement `POST /api/medications/extract` với pipeline:

1. **Nhận image**: parse `multipart/form-data`, validate file là image (jpg/png/webp)
2. **OCR**: chạy Pytesseract trên image → raw text (cấu hình tiếng Việt: `lang='vie+eng'`)
3. **LLM extraction**: gọi OpenAI API với extraction prompt từ `plans/ai_prompts.md`
   - System prompt: strict JSON only, never fabricate
   - User message: raw OCR text
4. **Parse & validate output**:
   - Parse JSON từ response
   - Validate đủ fields: `drug_name`, `dosage`, `qty_per_intake`, `frequency_per_day`, `duration_days`, `confidence`, `status`, `ask_human`
   - Nếu parse lỗi hoặc field bắt buộc missing → reject toàn bộ, không lưu, trả 422
5. **Safety rules**:
   - Nếu `confidence < 0.8` → override `status = "UNCLEAR"`, `ask_human = true`
   - Nếu `drug_name = "UNCLEAR"` → `ask_human = true` bất kể confidence
   - `status = "UNCLEAR"` → không lưu DB, trả response để FE hiển thị cảnh báo
6. **Lưu DB**: chỉ lưu khi `status = "READY_FOR_REVIEW"`:
   - Tạo record `medications` với `status = "DRAFT"`, `source_type = "PRESCRIPTION_IMAGE"`, `source_ref = <upload_filename_or_hash>`
7. **Response**: trả `medication_draft` object + `status`

### Client

- UI upload ảnh: drag & drop + tap to upload, preview thumbnail
- Loading state khi OCR+AI xử lý: skeleton card với message "Đang đọc toa thuốc..."
- Nếu `status = "UNCLEAR"`: hiển thị banner đỏ "AI không chắc chắn về thông tin này – vui lòng nhập thủ công hoặc liên hệ dược sĩ"
- Nếu `status = "READY_FOR_REVIEW"`: hiển thị draft card với confidence label, dẫn sang `PrescriptionReviewModal`
- Confidence bar: màu xanh nếu >= 0.8, vàng nếu 0.6-0.8, đỏ nếu < 0.6

### Checklist done

- [ ] Upload ảnh rõ → `medication_draft` hợp lệ, confidence > 0.8, lưu DB với status DRAFT
- [ ] Upload ảnh mờ → `status = "UNCLEAR"`, không có record nào trong DB
- [ ] LLM trả JSON lỗi format → 422, không lưu DB
- [ ] `drug_name = "UNCLEAR"` → `ask_human = true`, UI hiển thị cảnh báo
- [ ] Confidence bar hiển thị màu đúng theo ngưỡng

---

## Step 6 — Patient review + activate + correction workflow

> **Safety-critical**: Mọi correction medication bắt buộc qua `PENDING_REVIEW` — không auto-apply trong bất kỳ trường hợp nào.

### Server

**Activate medication** (`POST /api/medications/{id}/activate`):
- Validate `approved_by_patient = true`
- Validate medication status = `DRAFT` (không activate lại nếu đã ACTIVE)
- Đổi `status = "ACTIVE"`, set `updated_at`
- Sinh reminders: với mỗi ngày trong `duration_days`, với mỗi lần trong `frequency_per_day`:
  - `scheduled_time` = ngày hiện tại + offset giờ đều nhau trong ngày
  - `window_end_at = scheduled_time + 15 phút`
  - `status = "PENDING"`

**Tạo correction** (`POST /api/corrections`):
- Validate `target_type`, `target_id`, `corrected_payload`
- Lấy `original_payload` từ entity hiện tại (medication record)
- Lưu `correction_logs` với `approval_status = "PENDING_REVIEW"` — **luôn luôn, không exception**
- Response: `{ correction_id, approval_status: "PENDING_REVIEW" }`

**Approve correction** (`POST /api/corrections/{id}/approve`):
- Require `withReviewerAuth` middleware
- Validate `decision: "APPROVE" | "REJECT"`, `review_note`
- Set `reviewed_by`, `review_note`, `reviewed_at`
- Nếu `APPROVE` và `target_type = "MEDICATION"`: apply `corrected_payload` lên medication record, update `updated_at`
- Nếu `REJECT`: chỉ update correction log, medication không thay đổi

### Client

**`PrescriptionReviewModal`**:
- Hiển thị ảnh toa thuốc gốc (nếu có) + tất cả fields extracted
- Confidence label trên mỗi field (nếu field là UNCLEAR → highlight đỏ)
- Editable fields: `drug_name`, `dosage`, `qty_per_intake`, `frequency_per_day`, `duration_days`
- Actions:
  - "Xác nhận lịch uống" → gọi activate (chỉ enable nếu không có field UNCLEAR)
  - "Chỉnh sửa & gửi duyệt" → gọi corrections với edited payload
  - "Gửi cho dược sĩ review" → tạo correction với payload gốc

**`CorrectionStatusBanner`**:
- `PENDING_REVIEW`: màu vàng, message "Đang chờ duyệt bởi dược sĩ/bác sĩ. Lịch uống hiện tại vẫn áp dụng."
- `APPROVED`: màu xanh, message "Chỉnh sửa đã được duyệt và áp dụng."
- `REJECTED`: màu đỏ, message "Chỉnh sửa bị từ chối. Lý do: `{review_note}`", kèm nút "Gửi lại chỉnh sửa"

### Checklist done

- [ ] Activate không có correction → `medications.status = ACTIVE`, reminders được sinh đúng số lượng (`frequency_per_day * duration_days`)
- [ ] Chỉnh sửa → `correction_logs.approval_status = PENDING_REVIEW`, medication không thay đổi
- [ ] Approve với reviewer token hợp lệ → medication cập nhật đúng theo `corrected_payload`
- [ ] Approve không có reviewer token → 403
- [ ] Banner hiển thị đúng state theo `approval_status`

---

## Step 7 — Reminder engine (5-min scheduler)

### Server

**Background cron job** (chạy mỗi 5 phút trong Next.js runtime):
- Query reminders: `status IN ("PENDING", "SNOOZED") AND scheduled_time <= now()`
- Với mỗi reminder due: gửi notification (log + webhook/in-app), cập nhật `last_notified_at = now()`
- Auto-miss: query reminders `status IN ("PENDING", "SNOOZED") AND window_end_at < now()` → batch update `status = "MISSED"`

**Confirm** (`POST /api/reminders/{id}/confirm`):
- Idempotency: nếu `status` đã là `TAKEN` → trả 200 không làm gì
- Validate `cross_check_confirmed = true` bắt buộc (nếu false → 422)
- Set `status = "TAKEN"`, `confirmed_at = now()`

**Snooze** (`POST /api/reminders/{id}/snooze`):
- Validate `minutes = 15` (fixed, không nhận giá trị khác)
- Validate `status != "TAKEN"` và `status != "MISSED"`
- `scheduled_time += 15 phút`, `window_end_at = scheduled_time + 15 phút`
- `status = "SNOOZED"`, `snooze_count += 1`
- Idempotency key: `reminder_id + "snooze" + snooze_count` — không tạo duplicate

### Client

**`MedicationReminderCard`**:
- Header: tên thuốc, liều, `qty_per_intake` viên
- Giờ uống + countdown đến `window_end_at`
- Status badge: PENDING (xanh nhạt), SNOOZED (vàng), TAKEN (xanh), MISSED (xám)
- Actions:
  - "Đã uống thuốc" → chỉ enable sau khi tick checkbox cross-check
  - "Nhắc lại 15 phút" → snooze
  - "Sai liều" → mở inline form tạo correction
- Checkbox bắt buộc: "Tôi đã kiểm tra lại toa thuốc gốc trước khi uống" — disable nút "Đã uống thuốc" nếu chưa tick
- Disable buttons khi request đang pending (set `loading = true`) để tránh double-submit
- Status MISSED: card mờ, nút "Báo cáo sự cố" thay thế actions

### Checklist done

- [ ] Confirm thành công → `status = TAKEN`, cron không retry thêm
- [ ] Snooze → `scheduled_time` dịch +15 phút, `window_end_at` cập nhật, `snooze_count` tăng
- [ ] Quá `window_end_at` không confirm → cron set `status = MISSED`
- [ ] Double-submit confirm → idempotent, không tạo duplicate event, trả 200
- [ ] Confirm mà `cross_check_confirmed = false` → FE chặn, không call API
- [ ] Cron chạy 5 phút một lần, không bị race condition trên cùng reminder

---

## Step 8 — Daily check + Symptom triage AI

> **Safety-critical**: Uncertain → luôn escalate lên mức cao hơn, KHÔNG downplay. Hard rules override LLM output hoàn toàn.

### Server

**Triage** (`POST /api/symptoms/triage`):

1. **Hard rules check** (trước LLM, override hoàn toàn):
   - Detect keywords: `fever >= 40` + `seizures/co giật` → `RED`
   - `difficulty breathing/khó thở` → `RED`
   - `severe chest pain/đau ngực dữ dội` → `RED`
   - `fever/sốt` + `headache/đau đầu` (không có red flag) → `YELLOW`
   - Nếu match hard rule → dừng, không gọi LLM, trả kết quả với `reason` giải thích rule nào triggered
2. **LLM triage**: gọi OpenAI API với triage prompt từ `plans/ai_prompts.md`
3. **Uncertainty escalation**: nếu LLM trả `is_uncertain = true` → tăng level: GREEN→YELLOW, YELLOW→RED
4. **Hard rule override**: nếu hard rule detect RED nhưng LLM trả thấp hơn → force RED, log override event
5. **Lưu DB**: tạo `symptom_logs` với đầy đủ: `level`, `confidence`, `reason`, `action`, `follow_up_questions` (JSON array), `source = "MANUAL"`

**Daily check** (`POST /api/daily-checks`):
1. Gọi daily-check prompt với input text
2. Parse JSON output: `status`, `reply`, `severity_score_needed`, `next_question`
3. Logic routing:
   - `status = "NORMAL"` → lưu `symptom_logs` với `risk_level = "GREEN"`, trả `reply` để đóng session
   - `status = "NEED_MORE_INFO"` → trả `next_question` hỏi severity 1-10
   - `status = "ESCALATE_TRIAGE"` → tự động gọi triage flow với input gốc, trả kết quả triage
4. Lưu `symptom_logs` với `source = "DAILY_CHECK"`

### Client

**`DailyCheckChat`**:
- Trigger: daily prompt lúc 20:00 (hoặc manual trigger từ bottom nav)
- Opening message: "Hôm nay bạn cảm thấy thế nào sau khi uống thuốc?"
- Multi-turn conversation:
  - Nhận `NEED_MORE_INFO`: hiển thị câu hỏi follow-up + slider 1-10 với quick select buttons
  - Nhận `ESCALATE_TRIAGE`: hiển thị spinner "Đang phân tích triệu chứng..." → transition sang kết quả triage
- Kết quả triage:
  - Level badge: GREEN (xanh), YELLOW (vàng), RED (đỏ với animation pulse)
  - `reason` text giải thích
  - `action` recommendation: HOME_MONITOR / CALL_DOCTOR / GO_TO_EMERGENCY
- Nút "Kết nối nhân viên y tế" luôn hiển thị trong chat (không cần chờ RED)
- RED result → tự động mở `EmergencyPanel`

### Checklist done

- [ ] Input "sốt 40 độ và co giật" → `RED + GO_TO_EMERGENCY` (hard rule, không qua LLM)
- [ ] Input "mệt mệt" → `NEED_MORE_INFO` + câu hỏi severity 1-10
- [ ] LLM trả `is_uncertain = true + YELLOW` → escalate thành RED
- [ ] `symptom_logs` được lưu đầy đủ fields sau mỗi session
- [ ] RED result tự động trigger EmergencyPanel

---

## Step 9 — Emergency nearby facilities

### Server

**`POST /api/emergency/nearby`**:
- Input: `lat`, `lng`, `symptom_context` (string)
- Tính khoảng cách Haversine từ `(lat, lng)` đến tất cả facilities trong `facility_cache`
- Map `symptom_context` → specialty keywords (e.g. "khó thở" → "cardiology,pulmonology")
- Filter facilities có specialty match (kiểm tra trong JSON array `specialties`)
- **Fallback**: nếu không có facility nào match specialty → bỏ filter, lấy top 3 gần nhất
- Sort:
  - Primary: khoảng cách tăng dần
  - Tiebreak: `is_vinmec = true` được ưu tiên trong cùng distance bucket (±0.5km)
- Filter thêm `open_status = "OPEN"` (nếu tất cả đều CLOSED thì giữ lại để hiển thị)
- Trả top 3: `name`, `distance_km` (round 1 decimal), `open_status`, `is_vinmec`
- Response kèm `recommendation: "GO_NOW"` nếu input RED context

### Client

**`EmergencyPanel`**:
- Auto-trigger khi triage level = RED
- Top 3 facility cards: tên, khoảng cách, badge OPEN/CLOSED, Vinmec logo nếu `is_vinmec`
- Button "Gọi cấp cứu 115" → `tel:115`
- Button "Cập nhật vị trí" → request Geolocation API (`navigator.geolocation.getCurrentPosition`) → re-query nearby với coords mới
- Button "Tìm cơ sở khác" → re-query với danh sách trừ đi 3 cơ sở đã hiển thị
- SOS button persistent: sau khi EmergencyPanel trigger, hiển thị floating SOS button ở bottom-right cho đến khi user dismiss

### Checklist done

- [ ] RED triage → EmergencyPanel hiển thị top 3 facilities đúng sort (Vinmec ưu tiên)
- [ ] Specialty keyword match → filter đúng, Vinmec vẫn ưu tiên trong kết quả
- [ ] Không có specialty match → fallback top 3 gần nhất hoạt động
- [ ] "Cập nhật vị trí" → danh sách refresh với coords mới
- [ ] SOS button persistent sau khi EmergencyPanel được trigger

---

## Phase 3 — Polish & Observability

---

## Step 10 — Complete UI/UX flows

### Server

- Thêm đủ error codes cho mọi edge case:
  - `CORRECTION_EXPIRED`: correction đã quá hạn xử lý
  - `REMINDER_WINDOW_CLOSED`: confirm sau `window_end_at`
  - `MEDICATION_NOT_ACTIVE`: thao tác trên medication không ACTIVE
  - `ALREADY_CONFIRMED`: confirm idempotent response
- Kiểm tra tất cả API states có đủ field cho FE render đúng

### Client

Hoàn thiện tất cả states của từng component:

**`MedicationReminderCard`**:
- PENDING → SNOOZED → TAKEN (happy path)
- MISSED (sad path): mờ, nút báo cáo sự cố
- Wrong dosage: inline correction form, submit → CorrectionStatusBanner

**`PrescriptionReviewModal`**:
- UNCLEAR fields highlighted, disable confirm button
- Edit mode: inline editable fields với validation
- Sau submit correction: modal đóng, CorrectionStatusBanner xuất hiện

**`DailyCheckChat`**:
- Opening → multi-turn → resolution (NORMAL / TRIAGE / ESCALATE)
- Severity slider 1-10 với nhãn "Nhẹ" và "Rất nặng"
- Session timeout (nếu không reply trong 5 phút): lưu partial log, close session

**`EmergencyPanel`**:
- Loading state khi đang tìm nearby
- Empty state khi tất cả facilities CLOSED
- Error state khi geolocation bị deny: hướng dẫn nhập địa chỉ thủ công

**Global UX rules**:
- Mọi error state đều có next action rõ ràng (không có dead-end)
- Network error / timeout: toast với nút "Thử lại"
- Mọi destructive action (activate, correction) có confirmation step

### Checklist done

- [ ] Demo được 3 flows chính end-to-end: Extract → Reminder → Daily Check
- [ ] Cross-check checkbox bắt buộc không thể bypass (test bằng cách call confirm API trực tiếp → 422)
- [ ] Mọi API error hiển thị message đúng context (không hiện "Something went wrong")
- [ ] Không có dead-end UI ở bất kỳ flow nào

---

## Step 11 — Safety metrics & observability

### Server

Implement `GET /api/metrics/safety` — tính toàn bộ từ DB:

- `clinical_precision` = tỉ lệ medications ACTIVE không có correction `APPROVED` (chưa bị sửa sau khi activate)
  - Formula: `(active_medications - medications_with_approved_corrections) / active_medications`
- `low_confidence_reject_rate` = tỉ lệ extraction attempts bị reject vì `confidence < 0.8`
  - Formula: `unclear_count / total_extract_attempts`
- `cross_check_adherence` = tỉ lệ reminders TAKEN có `cross_check_confirmed = true`
  - Formula: `taken_with_cross_check / total_taken`
- `high_confidence_failure_rate` = tỉ lệ extractions `confidence >= 0.8` nhưng sau đó có correction APPROVED
  - Formula: `high_conf_with_correction / high_conf_total`

Alert thresholds (log warning/critical, response kèm `alerts` array):
- `clinical_precision < 0.98` → warning alert
- `high_confidence_failure_rate > 0.005` → critical alert
- `cross_check_adherence < 0.60` → warning alert + `"trigger_ux_review": true`

### Client

**Dashboard `/admin/metrics`**:
- 4 metric cards với giá trị hiện tại + threshold indicator (xanh/vàng/đỏ)
- Alert banner đỏ khi có critical alert, vàng khi có warning
- Bảng correction logs: loại lỗi (field nào bị sửa), số lượng theo ngày/tuần
- Nút refresh metrics thủ công

### Checklist done

- [ ] Metrics endpoint tính đúng với dữ liệu seed
- [ ] Inject data có lỗi → alert tương ứng xuất hiện trong response và UI
- [ ] Dashboard hiển thị đủ 4 metrics với threshold colors

---

## Step 12 — Testing & hardening

### Server (unit + integration tests)

**Unit tests** — business rules:
- Confidence threshold: input < 0.8 → UNCLEAR (không lưu DB)
- Hard triage rules: từng keyword combination → đúng level
- Uncertainty escalation: GREEN+uncertain → YELLOW; YELLOW+uncertain → RED
- Correction approval: PENDING_REVIEW không apply, APPROVED thì apply
- Reminder idempotency: double confirm trả 200 không tạo duplicate

**Integration tests** — full API flows:
- Extract → Activate → Generate Reminders → Confirm flow
- Correction → PENDING_REVIEW → Approve → Medication updated flow
- Daily Check → ESCALATE → Triage → RED → Emergency nearby flow

**Security tests**:
- Missing `X-Patient-ID` → 401
- Wrong `X-Reviewer-Token` → 403
- Patient truy cập resource của patient khác → 403
- `corrected_payload` chứa SQL injection attempt → sanitized/rejected
- Symptom text chứa prompt injection ("Ignore previous instructions") → LLM output vẫn đúng schema

### Client (component + E2E tests)

- Component tests: MedicationReminderCard renders đúng tất cả states
- Component tests: CorrectionStatusBanner hiển thị đúng message theo approval_status
- E2E: patient upload ảnh → review → activate → confirm reminder (happy path)
- Network failure simulation: API timeout → retry button hiển thị, sau retry thành công → UI cập nhật

### Checklist done

- [ ] Unit test suite pass trên tất cả business rules
- [ ] Integration tests pass cho 3 flow chính
- [ ] Security tests pass (không có endpoint nào bypass được)
- [ ] Dry-run demo toàn bộ flow 3 lần liên tiếp không lỗi

---

## Step 13 — Demo release

### Server

- Chuẩn bị sample data đầy đủ:
  - 2-3 patients với tên và phone thực tế (fake)
  - 2 prescription images mẫu: 1 rõ (confidence > 0.9), 1 mờ (trigger UNCLEAR)
  - Medication schedules đang ACTIVE với reminders PENDING cho demo
- Mock fallback system:
  - Nếu Pytesseract không available → dùng hardcoded OCR text từ `scripts/mock_ocr.ts`
  - Nếu OpenAI API lỗi (rate limit, timeout) → dùng hardcoded response từ `scripts/mock_ai.ts`
  - Env flag `DEMO_MODE=true` để switch toàn bộ AI calls sang mock
- Tag release: `git tag mvp-demo-v1` với CHANGELOG.md ngắn

### Client

- Kịch bản demo 7-10 phút:
  1. Upload ảnh toa → review → activate → xem reminder timeline
  2. Confirm reminder với cross-check checkbox
  3. Báo sai liều → tạo correction → reviewer approve
  4. Daily check chat → trigger RED triage → EmergencyPanel
  5. Xem safety metrics dashboard
- Polish UI: xóa placeholder text, align spacing, đảm bảo không có console.error trong demo
- Màn hình backup: nếu AI service lỗi → hiển thị fallback UI (không crash, không blank screen)
- Demo script: `docs/DEMO_SCRIPT.md` với các bước cụ thể để bất kỳ team member nào cũng chạy được

### Checklist done

- [ ] Full demo flow chạy không lỗi 3 lần liên tiếp
- [ ] `DEMO_MODE=true` hoạt động, toàn bộ AI calls dùng mock
- [ ] Backup path hoạt động khi OCR/LLM fail (fallback UI visible)
- [ ] Release tagged `mvp-demo-v1`, CHANGELOG có nội dung

---

## Global Definition of Done (MVP)

- [ ] Next.js monolithic chạy ổn định: UI + API + cron jobs
- [ ] 3 AI prompts hoạt động với strict JSON output và schema validation
- [ ] Medication correction bắt buộc qua reviewer approval — không có exception
- [ ] Reminder có snooze 15 phút + cross-check checkbox bắt buộc trước confirm
- [ ] Triage có hard rules override + uncertain escalation (không downplay)
- [ ] Emergency suggestion hiển thị top 3 cơ sở gần nhất (Vinmec ưu tiên)
- [ ] 4 safety metrics available và tracked với alert thresholds

---

## File Reference Guide

| Step | File cần đọc | Phần quan trọng |
|------|-------------|-----------------|
| Step 2 | `plans/database.md` | Toàn bộ schema, enums, seed data, business rules |
| Step 3 | `plans/architecture.md` | Section 4: Security and Trust Controls |
| Step 4 | `plans/api_spec.md` | Tất cả endpoint contracts + response shapes |
| Step 5 | `plans/ai_prompts.md`, `plans/api_spec.md` | Extraction prompt + `POST /api/medications/extract` |
| Step 6 | `plans/api_spec.md`, `plans/ui_ux.md` | Activate/corrections endpoints + PrescriptionReviewModal, CorrectionStatusBanner |
| Step 7 | `plans/database.md`, `plans/api_spec.md` | Reminder fields + confirm/snooze endpoints |
| Step 8 | `plans/ai_prompts.md`, `plans/database.md` | Triage + daily-check prompts, hard rules, symptom_logs |
| Step 9 | `plans/api_spec.md`, `plans/ui_ux.md` | `POST /api/emergency/nearby` + EmergencyPanel |
| Step 10 | `plans/ui_ux.md` | Section 2: Core Screens, Section 3: Failure Paths |
| Step 11 | `plans/architecture.md`, `plans/api_spec.md` | Section 5: Reliability Controls, `GET /api/metrics/safety` |
| Step 12-13 | Tất cả files trên | Full review trước demo |
