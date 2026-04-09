"""
FastAPI app cho MedReminder web demo.

Mục tiêu:
- Phục vụ frontend HTML/CSS/JS từ cùng một server
- Tái sử dụng AI core và mock data hiện có
- Cung cấp API đơn giản để demo 4 flow: Home, Scan, Cross-check, Chatbot
"""

from __future__ import annotations

import copy
import os
import shutil
import uuid
from pathlib import Path
from typing import Any

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from ai_core.agent import scan_prescription_image
from data.mock_data import SAMPLE_SCHEDULE
from data.prescription_image import create_prescription_image


PROJECT_ROOT = Path(__file__).resolve().parent.parent
WEB_DIR = PROJECT_ROOT / "web"
ASSETS_DIR = PROJECT_ROOT / "assets"
UPLOAD_DIR = PROJECT_ROOT / "tmp_uploads"


RED_KEYWORDS = [
    "kho tho",
    "khó thở",
    "sot cao",
    "sốt cao",
    "co giat",
    "co giật",
    "dau nguc",
    "đau ngực",
    "bat tinh",
    "bất tỉnh",
    "xuat huyet",
    "xuất huyết",
    "ngat",
    "ngất",
    "sot 40",
    "sốt 40",
    "sot 41",
    "sốt 41",
]

YELLOW_KEYWORDS = [
    "met",
    "mệt",
    "dau dau",
    "đau đầu",
    "buon non",
    "buồn nôn",
    "chong mat",
    "chóng mặt",
    "mat ngu",
    "mất ngủ",
    "phat ban",
    "phát ban",
    "dau bung",
    "đau bụng",
    "tieu chay",
    "tiêu chảy",
]

GREEN_KEYWORDS = [
    "tot",
    "tốt",
    "binh thuong",
    "bình thường",
    "on",
    "ổn",
    "khoe",
    "khỏe",
    "ok",
    "good",
    "duoc",
    "được",
]


app = FastAPI(
    title="MedReminder Web Demo",
    version="1.0.0",
    docs_url="/docs",
    redoc_url=None,
)


if ASSETS_DIR.exists():
    app.mount("/assets", StaticFiles(directory=str(ASSETS_DIR)), name="assets")

if WEB_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(WEB_DIR)), name="static")

UPLOAD_DIR.mkdir(exist_ok=True)
app.mount("/uploads", StaticFiles(directory=str(UPLOAD_DIR)), name="uploads")


_saved_crosscheck_payload: dict[str, Any] = {
    "confirmed": False,
    "medications": [],
}
_current_uploaded_image_url: str | None = None


class ChatRequest(BaseModel):
    message: str = Field(min_length=1)


class CrosscheckSaveRequest(BaseModel):
    confirmed: bool
    medications: list[dict[str, Any]] = Field(default_factory=list)


def _icon_url(icon_name: str | None) -> str | None:
    if not icon_name:
        return None
    return f"/assets/icons/medications/{icon_name}"


def _save_uploaded_file(upload: UploadFile) -> tuple[str, str]:
    suffix = Path(upload.filename or "upload.jpg").suffix.lower()
    if suffix not in {".png", ".jpg", ".jpeg", ".webp"}:
        raise HTTPException(status_code=400, detail="Chỉ hỗ trợ ảnh PNG, JPG, JPEG hoặc WEBP.")

    file_name = f"{uuid.uuid4().hex}{suffix}"
    target_path = UPLOAD_DIR / file_name
    with target_path.open("wb") as buffer:
        shutil.copyfileobj(upload.file, buffer)
    return str(target_path), f"/uploads/{file_name}"


def _normalize_medication(med: dict[str, Any]) -> dict[str, Any]:
    raw_schedule = med.get("schedule") or []
    legacy_note = med.get("notes")
    timing_notes = med.get("timing_notes")
    if not timing_notes and legacy_note:
        timing_notes = legacy_note
    schedule = []
    for slot in raw_schedule:
        if not isinstance(slot, dict):
            continue
        schedule.append(
            {
                "time": slot.get("time"),
                "note": slot.get("note"),
            }
        )

    name = med.get("name") or med.get("drug") or "UNCLEAR"
    strength = med.get("strength")
    if not strength:
        strength = med.get("dosage") if med.get("qty") is None else None

    dosage_per_use = med.get("dosage_per_use")
    if not dosage_per_use:
        if med.get("qty") is not None:
            qty = med.get("qty")
            dosage_per_use = f"{qty} đơn vị"
        else:
            dosage_per_use = med.get("dosage")

    frequency_text = med.get("frequency_text")
    if not frequency_text and med.get("freq") is not None:
        frequency_text = f"{med['freq']} lần/ngày"

    days = med.get("days")
    route = med.get("route") or ("uống" if schedule or frequency_text else "UNCLEAR")
    is_prn = bool(med.get("is_prn"))
    if not is_prn and timing_notes:
        note_text = str(timing_notes).lower()
        if "khi đau" in note_text or "khi sốt" in note_text or "prn" in note_text:
            is_prn = True

    uncertain_fields = med.get("uncertain_fields")
    if uncertain_fields is None:
        uncertain_fields = []

    return {
        "raw_text": med.get("raw_text"),
        "name": name,
        "strength": strength,
        "dosage_per_use": dosage_per_use,
        "route": route,
        "frequency_text": frequency_text,
        "days": days,
        "timing_notes": timing_notes,
        "is_prn": is_prn,
        "confidence": med.get("confidence"),
        "uncertain_fields": uncertain_fields,
        "schedule": schedule,
        "icon": med.get("icon"),
        "icon_url": _icon_url(med.get("icon")),
    }


def _normalize_scan_result(result: dict[str, Any]) -> dict[str, Any]:
    medications = [_normalize_medication(med) for med in result.get("medications", [])]
    status = result.get("status")

    if not status:
        extraction_status = result.get("extraction_status")
        if extraction_status == "success":
            status = "success"
        else:
            status = "failure"

    if status not in {"success", "partial", "failure"}:
        status = "partial" if medications else "failure"

    if status == "success" and any(
        med.get("uncertain_fields") or med.get("name") == "UNCLEAR" for med in medications
    ):
        status = "partial"

    ask_human = result.get("ask_human")
    if ask_human is None:
        ask_human = status != "success"

    review_flags = list(result.get("review_flags") or [])
    if result.get("reason") and "LOW_CONFIDENCE" not in review_flags and status != "success":
        review_flags.append("LOW_CONFIDENCE")

    message = result.get("message")
    if not message:
        if status == "success":
            message = "Hệ thống đã đọc được đơn thuốc. Vui lòng kiểm tra lại với ảnh gốc trước khi lưu."
        elif status == "partial":
            message = "Hệ thống đã đọc được một phần đơn thuốc. Vui lòng kiểm tra lại các mục chưa rõ."
        else:
            message = "Hệ thống chưa đọc đủ rõ đơn thuốc. Vui lòng nhập tay hoặc nhờ nhân viên y tế kiểm tra."

    return {
        "status": status,
        "confidence": float(result.get("confidence", 0.0) or 0.0),
        "ask_human": bool(ask_human),
        "message": message,
        "medications": medications,
        "review_flags": review_flags,
    }


def _schedule_payload() -> list[dict[str, Any]]:
    items = []
    for item in SAMPLE_SCHEDULE:
        row = copy.deepcopy(item)
        row["unlocked"] = False
        row["icon_url"] = _icon_url(row.get("icon"))
        items.append(row)
    return items


def _chat_reply(message: str) -> dict[str, Any]:
    text = message.strip()
    normalized = text.lower()

    if any(keyword in normalized for keyword in RED_KEYWORDS):
        return {
            "level": "danger",
            "reply": (
                "CẢNH BÁO! Triệu chứng bạn mô tả có thể nguy hiểm.\n\n"
                "Bạn nên tìm hỗ trợ y tế ngay. Nếu khó thở, đau ngực, co giật hoặc bất tỉnh, "
                "hãy gọi 115 hoặc đến cơ sở cấp cứu gần nhất."
            ),
            "show_emergency_button": True,
        }

    if any(keyword in normalized for keyword in YELLOW_KEYWORDS):
        return {
            "level": "warning",
            "reply": (
                "Mình đã ghi nhận triệu chứng của bạn. Bạn hãy theo dõi kỹ mức độ khó chịu, "
                "uống thuốc đúng theo đơn và liên hệ bác sĩ nếu triệu chứng tăng lên.\n\n"
                "Nếu muốn, bạn có thể mô tả thêm mức độ từ 1 đến 10."
            ),
            "show_emergency_button": False,
        }

    if any(keyword in normalized for keyword in GREEN_KEYWORDS):
        return {
            "level": "normal",
            "reply": (
                "Rất tốt. Bạn hãy tiếp tục dùng thuốc đúng giờ và theo dõi sức khỏe như bình thường. "
                "Nếu có thay đổi bất thường, hãy báo lại để được hướng dẫn tiếp."
            ),
            "show_emergency_button": False,
        }

    return {
        "level": "normal",
        "reply": (
            "Cảm ơn bạn đã chia sẻ. Bạn có thể mô tả rõ hơn triệu chứng hiện tại, "
            "ví dụ đau đầu, buồn nôn, khó thở, sốt hay mệt mỏi không?"
        ),
        "show_emergency_button": False,
    }


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/api/schedule")
def get_schedule() -> dict[str, Any]:
    return {"items": _schedule_payload()}


@app.post("/api/scan")
def post_scan(
    file: UploadFile = File(...),
) -> dict[str, Any]:
    global _current_uploaded_image_url

    image_path, image_url = _save_uploaded_file(file)
    _current_uploaded_image_url = image_url
    result = scan_prescription_image(image_path)

    normalized = _normalize_scan_result(result)
    normalized["uploaded_image_url"] = _current_uploaded_image_url
    normalized["source_filename"] = file.filename
    return normalized


@app.get("/api/prescription-image")
def get_prescription_image() -> dict[str, str]:
    if _current_uploaded_image_url:
        return {"url": _current_uploaded_image_url}
    image_path = create_prescription_image(force=False)
    image_name = os.path.basename(image_path)
    return {"url": f"/assets/{image_name}"}


@app.post("/api/crosscheck/save")
def save_crosscheck(payload: CrosscheckSaveRequest) -> dict[str, Any]:
    if not payload.confirmed:
        raise HTTPException(status_code=400, detail="Bạn cần xác nhận thông tin trước khi lưu.")

    _saved_crosscheck_payload["confirmed"] = True
    _saved_crosscheck_payload["medications"] = payload.medications
    return {
        "status": "saved",
        "message": "Đã lưu lịch thuốc cho bản demo.",
        "saved_count": len(payload.medications),
    }


@app.post("/api/chat")
def post_chat(payload: ChatRequest) -> dict[str, Any]:
    return _chat_reply(payload.message)


@app.get("/")
def root() -> FileResponse:
    return FileResponse(WEB_DIR / "index.html")
