"""
==============================================================================
 Mock Data - Dữ liệu giả lập cho AI đọc đơn thuốc
==============================================================================
 File: data/mock_data.py
 Mô tả: Chứa 2 bộ dữ liệu giả lập mô phỏng kết quả trả về từ AI:
   1. Happy Path: AI đọc được rõ ràng, độ tự tin cao.
   2. Failure Mode: AI không đọc được, độ tự tin thấp.

 Trong ứng dụng thực tế, module này sẽ được thay thế bằng
 API call đến model AI thực sự.
==============================================================================
"""

# --- Trường hợp 1: Happy Path - Độ tự tin cao ---
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

# --- Trường hợp 2: Failure Mode ---
MOCK_RESULT_FAILURE = {
    "status": "failure",
    "confidence": 0.23,
    "message": "Không thể đọc chính xác đơn thuốc.",
    "medications": [],
}

# --- Dữ liệu mẫu cho HomeScreen (lịch uống thuốc trong ngày) ---
SAMPLE_SCHEDULE = [
    {
        "time": "07:00",
        "name": "Paracetamol 500mg",
        "dosage": "1 viên",
        "note": "Sau ăn sáng",
        "taken": False,
        "icon": "ic_med_tablet_round_scored.png",
    },
    {
        "time": "08:00",
        "name": "Amoxicillin 500mg",
        "dosage": "1 viên",
        "note": "Sau ăn sáng 1 tiếng",
        "taken": False,
        "icon": "ic_med_capsule_standard.png",
    },
    {
        "time": "09:00",
        "name": "Vitamin C 1000mg",
        "dosage": "1 viên sủi",
        "note": "Buổi sáng, hòa nước",
        "taken": False,
        "icon": "icon_tablets.png",
    },
    {
        "time": "13:00",
        "name": "Paracetamol 500mg",
        "dosage": "1 viên",
        "note": "Sau ăn trưa",
        "taken": False,
        "icon": "ic_med_tablet_round_scored.png",
    },
    {
        "time": "19:00",
        "name": "Paracetamol 500mg",
        "dosage": "1 viên",
        "note": "Sau ăn tối",
        "taken": False,
        "icon": "ic_med_tablet_round_scored.png",
    },
    {
        "time": "20:00",
        "name": "Amoxicillin 500mg",
        "dosage": "1 viên",
        "note": "Sau ăn tối 1 tiếng",
        "taken": False,
        "icon": "ic_med_capsule_standard.png",
    },
]
