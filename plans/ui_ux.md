# UI/UX Specification

Required MVP UX flows from `spec-draft.md` covering trust, safety, correction, and emergency handling.

## 1. Design Principles

- **Trust by default**: Always show data source and confidence label on extracted medication.
- **Safety first**: Emergency actions are persistent and highly visible for RED triage.
- **Human-in-the-loop**: Medication correction never auto-applies; always show review status.
- **Low-friction**: Key actions (`Confirmed taken`, `Snooze 15 min`, `SOS`) are one tap.

## 2. Core Screens and Required Components

### `MedicationReminderCard`
- **Actions**: `Confirmed taken`, `Snooze 15 min`, `Wrong dosage`.
- **States**: `PENDING`, `SNOOZED`, `TAKEN`, `MISSED`.
- **Rule**: Before allowing `Confirmed taken`, show checkbox: `I have checked against my physical prescription`.

### `PrescriptionReviewModal`
- **Purpose**: Preview extracted medication before activation.
- **Fields**: `drug_name`, `dosage`, `qty_per_intake`, `frequency_per_day`, `duration_days`, `confidence`.
- **Actions**: `Confirm schedule`, `Edit`, `Send for pharmacist review`.

### `CorrectionStatusBanner`
- **States**: `PENDING_REVIEW`, `APPROVED`, `REJECTED`.
- **Message**: Explicitly states that medication edits require pharmacist/doctor approval before taking effect.

### `DailyCheckChat`
- **Trigger**: Daily prompt at 20:00.
- **Flow**: Normal reply -> close session; vague reply -> ask 1-10 severity scale; concerning reply -> escalate to triage.
- **Quick actions**: `Rate severity 1-10`, `Connect to medical staff`.

### `EmergencyPanel`
- **Trigger**: `RED` triage result or severe symptom keywords detected.
- **Content**: Top 3 nearest facilities (Vinmec first), distance, open/closed status.
- **Actions**: `Call emergency`, `Update location`, `Find another location`.

## 3. UX for Failure Paths (Mandatory)

- If AI dosage is wrong, user can report directly from reminder card (`Wrong dosage`).
- If triage seems unsafe, user can force human escalation with `SOS`.
- If location suggestion is wrong or outdated, user can re-pin location and re-query nearest facilities.

## 4. Visual Identity

| Element | Value |
|---|---|
| Primary | `#004225` (Vinmec Green) |
| Background | `#FFFFFF` |
| Danger | `#FF4D4D` |
| Warning | `#FFB020` |
| Corner Radius | `12px` |
| Typography | `Inter` or `Roboto` |
