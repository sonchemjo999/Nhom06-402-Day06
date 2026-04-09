# API Specification

MVP REST endpoints aligned with `spec-draft.md` safety requirements.

## 1. Medication Extraction & Review

### `POST /api/medications/extract`
- **Input**: `multipart/form-data` with `image`
- **Output**:
  ```json
  {
    "medication_draft": {
      "drug_name": "Paracetamol",
      "dosage": "500mg",
      "qty_per_intake": 1,
      "frequency_per_day": 3,
      "duration_days": 7,
      "confidence": 0.86
    },
    "status": "READY_FOR_REVIEW"
  }
  ```

### `POST /api/medications/{medication_id}/activate`
- **Purpose**: Patient confirms preview to enable reminders.
- **Input**: `{ "approved_by_patient": true }`
- **Output**: `{ "status": "ACTIVE" }`

### `POST /api/corrections`
- **Purpose**: Store user correction from reminder, symptom, or location.
- **Input**:
  ```json
  {
    "target_type": "MEDICATION",
    "target_id": 123,
    "corrected_payload": { "dosage": "250mg" }
  }
  ```
- **Output**:
  ```json
  {
    "correction_id": 98,
    "approval_status": "PENDING_REVIEW"
  }
  ```

### `POST /api/corrections/{correction_id}/approve`
- **Purpose**: Pharmacist/doctor approval for medication corrections.
- **Auth**: Requires `X-Reviewer-Token` header.
- **Input**: `{ "decision": "APPROVE", "review_note": "Verified with original prescription" }`
- **Output**: `{ "approval_status": "APPROVED" }`

## 2. Reminders

### `POST /api/reminders/{reminder_id}/confirm`
- **Input**: `{ "status": "TAKEN", "cross_check_confirmed": true }`
- **Output**: `{ "status": "TAKEN", "confirmed_at": "2026-04-08T08:02:00Z" }`

### `POST /api/reminders/{reminder_id}/snooze`
- **Input**: `{ "minutes": 15 }`
- **Output**: `{ "status": "SNOOZED", "next_notify_at": "2026-04-08T08:15:00Z" }`

## 3. Symptom Triage & Daily Check

### `POST /api/symptoms/triage`
- **Input**: `{ "text": "I have high fever and seizures" }`
- **Output**:
  ```json
  {
    "level": "RED",
    "confidence": 0.97,
    "reason": "High fever with seizures is a red flag",
    "action": "GO_TO_EMERGENCY",
    "follow_up_questions": []
  }
  ```

### `POST /api/daily-checks`
- **Input**: `{ "text": "Feeling a bit tired today" }`
- **Output**:
  ```json
  {
    "status": "NEED_MORE_INFO",
    "next_question": "On a scale of 1 to 10, how tired do you feel?"
  }
  ```

## 4. Emergency Facility Suggestion

### `POST /api/emergency/nearby`
- **Input**:
  ```json
  {
    "lat": 10.804,
    "lng": 106.711,
    "symptom_context": "difficulty breathing"
  }
  ```
- **Note**: `symptom_context` is used to filter `specialties` in `facility_cache`. If no specialty match is found, skip the filter and return top 3 nearest facilities (Vinmec prioritized).
- **Output**:
  ```json
  {
    "recommendation": "GO_NOW",
    "facilities": [
      { "name": "Vinmec Central Park", "distance_km": 2.1, "open_status": "OPEN" }
    ]
  }
  ```

## 5. History & Metrics

### `GET /api/patients/{id}/history`
- **Output**: medications, reminders, symptom logs, correction logs, adherence metrics.

### `GET /api/metrics/safety`
- **Output**:
  ```json
  {
    "clinical_precision": 0.999,
    "low_confidence_reject_rate": 0.96,
    "cross_check_adherence": 0.82,
    "high_confidence_failure_rate": 0.002
  }
  ```
- **Thresholds** (for alert logic):
  - `clinical_precision` < 0.98 => alert; any single dangerous wrong-dose incident => stop system
  - `high_confidence_failure_rate` > 0.005 => alert
  - `cross_check_adherence` < 0.60 => alert, trigger UI/UX review
