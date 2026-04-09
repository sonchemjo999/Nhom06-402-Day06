# Database Schema Specification

SQLite with Prisma ORM for MVP. All trust/safety fields required by `spec-draft.md` are included.

## 1. Core Tables

### `patients`
| Column | Type | Description |
|---|---|---|
| `id` | Integer (PK) | Unique patient id |
| `name` | String | Full name |
| `phone` | String | Contact number |
| `created_at` | DateTime | Account creation time |

### `medications`
| Column | Type | Description |
|---|---|---|
| `id` | Integer (PK) | Unique medication row |
| `patient_id` | Integer (FK -> patients.id) | Owner patient |
| `drug_name` | String | Medicine name |
| `dosage` | String | Strength (e.g. 500mg) |
| `qty_per_intake` | Integer | Number of pills/ml per intake |
| `frequency_per_day` | Integer | Times per day |
| `duration_days` | Integer | Treatment duration in days |
| `confidence` | Float | AI extraction confidence score |
| `source_type` | String | `PRESCRIPTION_IMAGE`, `EHR`, `MANUAL` |
| `source_ref` | String | Image/EHR reference id for traceability |
| `status` | String | `DRAFT`, `ACTIVE`, `INACTIVE` |
| `created_at` | DateTime | Creation time |
| `updated_at` | DateTime | Last update time |

### `reminders`
| Column | Type | Description |
|---|---|---|
| `id` | Integer (PK) | Unique reminder row |
| `patient_id` | Integer (FK -> patients.id) | Owner patient |
| `medication_id` | Integer (FK -> medications.id) | Target medication |
| `scheduled_time` | DateTime | Planned intake time |
| `status` | String | `PENDING`, `TAKEN`, `MISSED`, `SNOOZED` |
| `snooze_count` | Integer | Number of snoozes |
| `window_end_at` | DateTime | Retry deadline (scheduled_time + 15 min); mark MISSED after this |
| `last_notified_at` | DateTime | Last push/send timestamp |
| `confirmed_at` | DateTime | Time user confirmed taken |
| `cross_check_confirmed` | Boolean | User confirmed checking physical prescription |
| `created_at` | DateTime | Creation time |

### `symptom_logs`
| Column | Type | Description |
|---|---|---|
| `id` | Integer (PK) | Unique symptom row |
| `patient_id` | Integer (FK -> patients.id) | Owner patient |
| `source` | String | `DAILY_CHECK` or `MANUAL` |
| `text` | Text | User symptom input |
| `severity_score` | Integer | 1-10 severity if collected |
| `risk_level` | String | `GREEN`, `YELLOW`, `RED` |
| `confidence` | Float | Triage confidence score |
| `reason` | Text | Why model assigned this risk level |
| `action` | String | `HOME_MONITOR`, `CALL_DOCTOR`, `GO_TO_EMERGENCY` |
| `follow_up_questions` | Text (JSON) | Follow-up questions and answers |
| `created_at` | DateTime | Log timestamp |

### `correction_logs`
| Column | Type | Description |
|---|---|---|
| `id` | Integer (PK) | Unique correction row |
| `patient_id` | Integer (FK -> patients.id) | Owner patient |
| `target_type` | String | `MEDICATION`, `SYMPTOM`, `LOCATION` |
| `target_id` | Integer | Id of corrected entity |
| `original_payload` | Text (JSON) | Original AI output |
| `corrected_payload` | Text (JSON) | User correction |
| `approval_status` | String | `NOT_REQUIRED`, `PENDING_REVIEW`, `APPROVED`, `REJECTED` |
| `reviewed_by` | String | Clinician/pharmacist id |
| `review_note` | Text | Review explanation |
| `created_at` | DateTime | User correction timestamp |
| `reviewed_at` | DateTime | Review completion timestamp |

### `facility_cache`
| Column | Type | Description |
|---|---|---|
| `id` | Integer (PK) | Unique facility row |
| `name` | String | Facility name |
| `lat` | Float | Latitude |
| `lng` | Float | Longitude |
| `is_vinmec` | Boolean | Vinmec priority flag |
| `specialties` | Text (JSON) | Supported specialties list |
| `open_status` | String | `OPEN`, `CLOSED`, `UNKNOWN` |
| `updated_at` | DateTime | Last sync timestamp |

## 2. Key Relationships
- `patients` (1) -> (*) `medications`
- `medications` (1) -> (*) `reminders`
- `patients` (1) -> (*) `symptom_logs` (covers both daily checks and manual triage)
- `patients` (1) -> (*) `correction_logs`

## 3. Business Rules
- Medication corrections (`target_type=MEDICATION`) must always start at `PENDING_REVIEW`.
- Reminder confirm/snooze writes are idempotent (`reminder_id` + event key).
- PHI fields encrypted at rest in production (SQLite plain for hackathon MVP only).

## 4. Seed Data for `facility_cache`
Hardcode 5 Vinmec locations in migration script (no external API needed):

| name | lat | lng | is_vinmec | open_status |
|---|---|---|---|---|
| Vinmec Times City | 20.9955 | 105.8690 | true | OPEN |
| Vinmec Royal City | 20.9975 | 105.8155 | true | OPEN |
| Vinmec Central Park | 10.7942 | 106.7218 | true | OPEN |
| Vinmec Nha Trang | 12.2388 | 109.1967 | true | OPEN |
| Vinmec Hai Phong | 20.8449 | 106.6881 | true | OPEN |
