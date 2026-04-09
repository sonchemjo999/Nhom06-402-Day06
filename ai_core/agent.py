"""
AI Core - OCR đơn thuốc bằng PaddleOCR.

Luồng:
  Ảnh đơn thuốc -> PaddleOCR -> heuristic parser -> JSON cấu trúc
"""

from __future__ import annotations

import os
import time
import re
from pathlib import Path
from statistics import mean

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parent.parent

load_dotenv(PROJECT_ROOT / ".env")

_OCR_ENGINE = None

ROUTE_PATTERNS = [
    ("nhỏ mắt", "nhỏ mắt"),
    ("nhỏ mũi", "nhỏ mũi"),
    ("xịt", "xịt"),
    ("bôi", "bôi"),
    ("đặt", "đặt"),
    ("tiêm", "tiêm"),
    ("uống", "uống"),
]

# Mocked OCR result for testing / demo when we only want to accept an uploaded image
# and return deterministic data after a small delay to simulate processing time.
MOCK_RESULT_SUCCESS = {
    "status": "success",
    "confidence": 0.95,
    "message": "Đọc đơn thuốc thành công",
    "medications": [
        {
            "name": "Paracetamol 500mg",
            "dosage": "1 viên",
            "icon": "ic_med_tablet_round_scored.png",
            "schedule": [
                {"time": "07:00", "note": "Sau ăn sáng"},
                {"time": "13:00", "note": "Sau ăn trưa"},
                {"time": "19:00", "note": "Sau ăn tối"},
            ],
        },
        {
            "name": "Amoxicillin 500mg",
            "dosage": "1 viên",
            "icon": "ic_med_capsule_standard.png",
            "schedule": [
                {"time": "08:00", "note": "Sau ăn sáng 1 tiếng"},
                {"time": "20:00", "note": "Sau ăn tối 1 tiếng"},
            ],
        },
        {
            "name": "Vitamin C 1000mg",
            "dosage": "1 viên sủi",
            "icon": "icon_tablets.png",
            "schedule": [
                {"time": "09:00", "note": "Buổi sáng, hòa nước"},
            ],
        },
    ],
}


def _ocr_lang() -> str:
    return os.getenv("PADDLE_OCR_LANG", "latin").strip() or "latin"


def _ocr_use_angle_cls() -> bool:
    return os.getenv("PADDLE_OCR_USE_ANGLE_CLS", "true").strip().lower() != "false"


def _get_ocr_engine():
    global _OCR_ENGINE
    if _OCR_ENGINE is not None:
        return _OCR_ENGINE

    try:
        from paddleocr import PaddleOCR
    except ImportError as exc:
        raise RuntimeError(
            "Thiếu PaddleOCR hoặc PaddlePaddle. Hãy cài dependency theo requirements.txt."
        ) from exc

    _OCR_ENGINE = PaddleOCR(
        use_angle_cls=_ocr_use_angle_cls(),
        lang=_ocr_lang(),
        show_log=False,
    )
    return _OCR_ENGINE


def _normalize_space(text: str) -> str:
    return re.sub(r"\s+", " ", (text or "")).strip()


def _extract_ocr_lines(image_path: str) -> list[dict]:
    ocr = _get_ocr_engine()
    result = ocr.ocr(image_path, cls=_ocr_use_angle_cls())
    lines = []
    if not result:
        return lines

    for page in result:
        if not page:
            continue
        for item in page:
            if not item or len(item) < 2:
                continue
            text = _normalize_space(item[1][0] if item[1] else "")
            confidence = float(item[1][1]) if item[1] and len(item[1]) > 1 else 0.0
            if text:
                lines.append({"text": text, "confidence": confidence})
    return lines


def _looks_like_medication_start(text: str) -> bool:
    normalized = text.lower()
    return bool(
        re.match(r"^\s*\d+[\.\)]\s*", normalized)
        or ("mg" in normalized or "ml" in normalized or "mcg" in normalized)
    )


def _group_medication_lines(lines: list[dict]) -> list[list[dict]]:
    groups = []
    current = []
    for line in lines:
        text = line["text"]
        if _looks_like_medication_start(text) and current:
            groups.append(current)
            current = [line]
        else:
            current.append(line)
    if current:
        groups.append(current)
    return groups


def _detect_route(text: str) -> str:
    lowered = text.lower()
    for needle, route in ROUTE_PATTERNS:
        if needle in lowered:
            return route
    return "UNCLEAR"


def _extract_strength(text: str) -> str | None:
    match = re.search(r"\b\d+(?:[.,]\d+)?\s?(?:mg|g|mcg|µg|ml|iu|ui|%)\b", text, re.I)
    return match.group(0) if match else None


def _extract_days(text: str) -> int | None:
    match = re.search(r"(\d+)\s*ngày", text, re.I)
    return int(match.group(1)) if match else None


def _extract_frequency(text: str) -> str | None:
    patterns = [
        r"\d+\s*lần\s*/\s*ngày",
        r"ngày\s*\d+\s*lần",
        r"sáng\s*trưa\s*tối",
        r"sáng\s*chiều",
        r"sáng\s*tối",
        r"trưa\s*tối",
        r"khi\s*đau",
        r"khi\s*sốt",
        r"prn",
    ]
    lowered = text.lower()
    for pattern in patterns:
        match = re.search(pattern, lowered, re.I)
        if match:
            return match.group(0)
    return None


def _extract_timing_notes(text: str) -> str | None:
    note_patterns = [
        r"sau ăn(?:\s*\d+\s*giờ)?",
        r"trước ăn(?:\s*\d+\s*phút)?",
        r"trước ngủ",
        r"sáng(?:\s*\d+h)?(?:,\s*trưa\s*\d+h,\s*tối\s*\d+h)?",
        r"trưa(?:\s*\d+h)?",
        r"tối(?:\s*\d+h)?",
        r"khi đau",
        r"khi sốt",
        r"hòa nước",
    ]
    lowered = text.lower()
    found = []
    for pattern in note_patterns:
        for match in re.finditer(pattern, lowered, re.I):
            value = _normalize_space(match.group(0))
            if value not in found:
                found.append(value)
    if found:
        return ", ".join(found)
    return None


def _extract_dosage_per_use(text: str) -> str | None:
    match = re.search(
        r"(?:uống|bôi|nhỏ mắt|nhỏ mũi|xịt|đặt|tiêm)\s+(\d+(?:[\/.,]\d+)?\s*(?:viên|v|gói|ống|ml|giọt|thìa|muỗng))",
        text,
        re.I,
    )
    return _normalize_space(match.group(1)) if match else None


def _extract_schedule(text: str) -> list[dict]:
    schedule = []
    for hour, minute in re.findall(r"(\d{1,2})\s*(?:h|:)\s*(\d{0,2})", text, re.I):
        hh = int(hour)
        mm = int(minute) if minute else 0
        time_str = f"{hh:02d}:{mm:02d}"
        if not any(item["time"] == time_str for item in schedule):
            schedule.append({"time": time_str, "note": None})
    return schedule


def _extract_name(text: str) -> str:
    cleaned = re.sub(r"^\s*\d+[\.\)]\s*", "", text).strip()
    stop_words = [
        "uống",
        "bôi",
        "nhỏ mắt",
        "nhỏ mũi",
        "xịt",
        "đặt",
        "tiêm",
        "thời gian",
        "ngày",
    ]
    end_index = len(cleaned)
    lowered = cleaned.lower()
    for word in stop_words:
        idx = lowered.find(word)
        if idx != -1:
            end_index = min(end_index, idx)
    candidate = _normalize_space(cleaned[:end_index].strip(" -,:;"))
    return candidate or "UNCLEAR"


def _medication_from_group(group: list[dict]) -> dict | None:
    raw_text = _normalize_space(" ".join(item["text"] for item in group))
    if len(raw_text) < 4:
        return None

    confidences = [item["confidence"] for item in group if item.get("confidence") is not None]
    avg_conf = mean(confidences) if confidences else 0.0

    name = _extract_name(raw_text)
    strength = _extract_strength(raw_text)
    dosage_per_use = _extract_dosage_per_use(raw_text)
    route = _detect_route(raw_text)
    frequency_text = _extract_frequency(raw_text)
    days = _extract_days(raw_text)
    timing_notes = _extract_timing_notes(raw_text)
    schedule = _extract_schedule(raw_text)
    is_prn = any(token in raw_text.lower() for token in ["khi đau", "khi sốt", "prn"])

    uncertain_fields = []
    if not name or name == "UNCLEAR":
        name = "UNCLEAR"
        uncertain_fields.append("name")
    if not strength:
        uncertain_fields.append("strength")
    if not dosage_per_use:
        uncertain_fields.append("dosage_per_use")
    if route == "UNCLEAR":
        uncertain_fields.append("route")

    med_conf = round(min(0.98, max(0.25, avg_conf)), 2)
    if len(uncertain_fields) >= 2:
        med_conf = round(max(0.35, med_conf - 0.18), 2)
    elif uncertain_fields:
        med_conf = round(max(0.45, med_conf - 0.08), 2)

    return {
        "raw_text": raw_text,
        "name": name,
        "strength": strength,
        "dosage_per_use": dosage_per_use,
        "route": route,
        "frequency_text": frequency_text,
        "days": days,
        "timing_notes": timing_notes,
        "is_prn": is_prn,
        "confidence": med_conf,
        "uncertain_fields": uncertain_fields,
        "schedule": schedule,
    }


def _build_result_from_lines(lines: list[dict]) -> dict:
    if not lines:
        return {
            "status": "failure",
            "confidence": 0.0,
            "ask_human": True,
            "message": "Không đọc được nội dung từ ảnh đơn thuốc.",
            "medications": [],
            "review_flags": ["EMPTY_OCR_RESULT"],
        }

    groups = _group_medication_lines(lines)
    medications = []
    for group in groups:
        med = _medication_from_group(group)
        if med is not None and (
            med["name"] != "UNCLEAR"
            or med["strength"]
            or med["dosage_per_use"]
            or med["frequency_text"]
        ):
            medications.append(med)

    if not medications:
        return {
            "status": "failure",
            "confidence": 0.15,
            "ask_human": True,
            "message": "Hệ thống chưa tách được thông tin thuốc từ ảnh. Vui lòng kiểm tra lại chất lượng ảnh.",
            "medications": [],
            "review_flags": ["NO_MEDICATION_EXTRACTED"],
        }

    med_confidences = [med["confidence"] for med in medications]
    overall_conf = round(mean(med_confidences), 2)
    has_uncertain = any(med["uncertain_fields"] for med in medications)

    status = "success"
    ask_human = False
    review_flags = []
    if overall_conf < 0.5:
        status = "failure"
        ask_human = True
        medications = []
        review_flags.append("LOW_CONFIDENCE_OCR")
    elif has_uncertain or overall_conf < 0.82:
        status = "partial"
        ask_human = True
        review_flags.append("CHECK_MANUALLY")

    if status == "success":
        message = "Hệ thống đã đọc được đơn thuốc. Vui lòng kiểm tra lại với ảnh gốc trước khi lưu."
    elif status == "partial":
        message = "Hệ thống đã đọc được một phần đơn thuốc. Vui lòng kiểm tra lại các mục chưa rõ."
    else:
        message = "Hệ thống chưa đọc đủ rõ đơn thuốc. Vui lòng chụp lại ảnh rõ hơn hoặc nhập tay."

    return {
        "status": status,
        "confidence": overall_conf if status != "failure" else min(overall_conf, 0.49),
        "ask_human": ask_human,
        "message": message,
        "medications": medications,
        "review_flags": review_flags,
    }


def scan_prescription_image(image_path: str) -> dict:
    """
    Simplified OCR entrypoint for demo/testing mode:
    - Validate the uploaded image exists.
    - Wait 5 seconds to mimic processing latency.
    - Return MOCK_RESULT_SUCCESS (deterministic mocked output).

    This keeps the rest of the parsing helpers available for future re-enablement
    of the real OCR flow, but forces a mocked response here so callers only need
    to upload an image and get a predictable result.
    """
    if not image_path or not os.path.exists(image_path):
        return {
            "status": "failure",
            "confidence": 0.0,
            "ask_human": True,
            "message": "Không tìm thấy ảnh đơn thuốc để xử lý.",
            "medications": [],
            "review_flags": ["MISSING_IMAGE"],
        }

    # Simulate processing time so behavior resembles a real OCR call
    time.sleep(5)

    # Return deterministic mocked output (success) for demo/testing
    return MOCK_RESULT_SUCCESS


def scan_prescription(case: str = "random") -> dict:
    return {
        "status": "failure",
        "confidence": 0.0,
        "ask_human": True,
        "message": "Luồng scan cũ đã bị vô hiệu. Hãy dùng scan_prescription_image() với ảnh upload.",
        "medications": [],
        "review_flags": ["LEGACY_SCAN_DISABLED"],
    }
