"""
==============================================================================
 AI Core - Agent doc don thuoc (Mock Mode)
==============================================================================
 File: ai_core/agent.py

 Mo ta:
   Ham scan_prescription(case) tra ve mock result theo 6 loai case.

 Case:
   "clear"       -> confidence ~95%, success, day du thong tin
   "blurry"      -> confidence ~23%, failure
   "card"        -> confidence ~48%, partial success
   "handwritten" -> confidence ~38%, failure
   "stain"       -> confidence ~52%, partial success
   "random"      -> chon ngau nhien theo phan bo xac suat

 Chi dung mock — khong goi AI thuc.

 Doc lap khoi LangGraph (khong can cai dat langgraph).
==============================================================================
"""

import random


# =============================================================================
# MOCK RESULTS
# =============================================================================

MOCK_RESULTS = {

    "clear": {
        "status": "success",
        "confidence": 0.95,
        "message": "Doc don thuoc thanh cong. Tat ca thong tin deu ro rang.",
        "doctor": "TS.BS Nguyen Van A",
        "diagnosis": "Viem hong cap, sot nhe",
        "patient": "Tran Thi B",
        "prescription_date": "08/04/2026",
        "medications": [
            {
                "name": "Paracetamol 500mg",
                "dosage": "1 vien x 3 lan/ngay",
                "schedule": [
                    {"time": "07:00", "note": "sau an sang"},
                    {"time": "13:00", "note": "sau an trua"},
                    {"time": "19:00", "note": "sau an toi"},
                ],
                "days": 5,
            },
            {
                "name": "Amoxicillin 500mg",
                "dosage": "1 vien x 2 lan/ngay",
                "schedule": [
                    {"time": "08:00", "note": "sau an sang 1h"},
                    {"time": "20:00", "note": "sau an toi 1h"},
                ],
                "days": 7,
            },
            {
                "name": "Vitamin C 1000mg",
                "dosage": "1 vien x 1 lan/ngay",
                "schedule": [{"time": "09:00", "note": "buoi sang, hoa nuoc"}],
                "days": 10,
            },
        ],
    },

    "blurry": {
        "status": "failure",
        "confidence": 0.23,
        "message": "Don thuoc qua mo, khong doc duoc chinh xac ten thuoc. "
                   "Vui long nhap tay hoac lien he duoc si.",
        "medications": [],
    },

    "card": {
        "status": "success",
        "confidence": 0.48,
        "message": "Don tren card nho, mot so thong tin bi cat hoac mo. "
                   "Vui long kiem tra ky.",
        "doctor": "BS. Le Thi C",
        "medications": [
            {
                "name": "Paracetamol 500mg",
                "dosage": "1 vien x 2 lan/ngay",
                "schedule": [
                    {"time": "07:00", "note": "sau an"},
                    {"time": "19:00", "note": "sau an"},
                ],
                "days": 5,
            },
            {
                "name": "Omeprazole 20mg",
                "dosage": "1 vien x 1 lan/ngay",
                "schedule": [{"time": "08:00", "note": "truoc an 30p"}],
                "days": 14,
            },
        ],
    },

    "handwritten": {
        "status": "failure",
        "confidence": 0.38,
        "message": "Don viet tay, kha nang doc chinh xac thap. "
                   "Vui long nhap tay hoac hoi bac si.",
        "medications": [],
    },

    "stain": {
        "status": "success",
        "confidence": 0.52,
        "message": "Co vet ban nuoc tren anh, mot so vi tri khong doc duoc. "
                   "Thong tin ben duoi la phan cua AI doan.",
        "medications": [
            {
                "name": "Metformin 500mg",
                "dosage": "1 vien x 2 lan/ngay",
                "schedule": [
                    {"time": "07:00", "note": "sau an sang"},
                    {"time": "19:00", "note": "sau an toi"},
                ],
                "days": 30,
            },
            {
                "name": "Aspirin 81mg",
                "dosage": "1 vien x 1 lan/ngay",
                "schedule": [{"time": "21:00", "note": "truoc khi ngu"}],
                "days": 30,
            },
        ],
    },
}

# Phan bo xac suat thuc te (tong = 100%)
_WEIGHTED_CASES = [
    ("clear",       0.45),
    ("blurry",      0.20),
    ("card",        0.15),
    ("handwritten", 0.10),
    ("stain",       0.10),
]


# =============================================================================
# MAIN ENTRY POINT
# =============================================================================

def scan_prescription(image_path=None, case: str = "random") -> dict:
    """
    Ham chinh: Quet don thuoc (mock mode).

    Args:
        image_path: Bo qua (chi dung mock tren may tinh)
        case: "clear" | "blurry" | "card" | "handwritten" | "stain" | "random"

    Returns:
        dict: {status, confidence, message, medications, ...}
    """
    if case == "random":
        cases, weights = zip(*_WEIGHTED_CASES)
        case = random.choices(list(cases), weights=list(weights), k=1)[0]

    result = MOCK_RESULTS.get(case, MOCK_RESULTS["clear"]).copy()
    result["_case"] = case  # de screen biet dang test case nao
    return result


def get_case_distribution() -> dict:
    """Tra ve phan bo cac loai case de hien thi cho user."""
    return {case: {"weight": w} for case, w in _WEIGHTED_CASES}
