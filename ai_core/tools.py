"""
=============================================================================
 AI Core - Tools cho Agent đọc đơn thuốc
=============================================================================
 File: ai_core/tools.py
 Mô tả: Tool mô phỏng OCR + NLP trên đơn thuốc.

 Theo spec-draft.md (section 6.2, Prompt 1):
   - Trích xuất: tên thuốc, liều (mg), số viên, lần/ngày, ngày
   - confidence >= 0.8 → success
   - confidence < 0.8  → failure, yêu cầu human review
   - Không bịa tên! Chữ mờ → "UNCLEAR"

 Theo spec-draft.md (section 6.5):
   - Core Logic: Image → Tesseract (OCR) → Prompt → JSON
   - Trong MVP: dùng mock text thay cho ảnh thật
=============================================================================
"""

import json
import random
from langchain_core.tools import tool


# ============================================================
# MOCK PRESCRIPTION DATA
# Mô phỏng kết quả OCR từ ảnh đơn thuốc
# ============================================================

# Đơn thuốc RÕ RÀNG (mô phỏng OCR thành công, chữ in rõ)
CLEAR_PRESCRIPTION = """
PHÒNG KHÁM ĐA KHOA VINMEC TIMES CITY
Bác sĩ: TS.BS Nguyễn Văn An — Khoa Nội tổng hợp
Ngày kê: 08/04/2026

Bệnh nhân: Trần Thị Bình (Nữ, 45 tuổi)
Mã BN: VNM-2026-00462
Chẩn đoán: Viêm họng cấp, sốt nhẹ

ĐƠN THUỐC:
1. Paracetamol 500mg — Uống 1 viên × 3 lần/ngày (sáng 7h, trưa 13h, tối 19h) — sau ăn
   Thời gian: 5 ngày
2. Amoxicillin 500mg — Uống 1 viên × 2 lần/ngày (sáng 8h, tối 20h) — sau ăn 1 giờ
   Thời gian: 7 ngày
3. Vitamin C 1000mg — Uống 1 viên sủi × 1 lần/ngày (sáng 9h) — hòa nước
   Thời gian: 10 ngày

Lưu ý: Uống đủ nước, nghỉ ngơi. Tái khám sau 5 ngày nếu triệu chứng không giảm.
Ký tên: [chữ ký BS]
"""

# Đơn thuốc MỜ / KHÔNG RÕ (mô phỏng OCR thất bại, chữ viết tay mờ)
BLURRY_PRESCRIPTION = """
PHÒ... KH... ĐA KH... V...MEC
B...sĩ: ...yễn V... ... — Kh... ...ội

B...nh nhân: Tr... ...ị ...
Mã ...: VNM-2026-...
...đoán: ...ê... ...ọng ...ấp

ĐƠN ...ỐC:
1. P...ce...mol 5...mg — ...ng 1 v... × ... lần/...ày
2. ...oxi...lin ...mg — ...ng ... v... × ... lần/...
3. ... (không đọc được)

...ời gian ...ều trị: ... ngày
... tên: [mờ]
"""


@tool
def extract_prescription(prescription_text: str) -> str:
    """
    Trích xuất thông tin thuốc từ kết quả OCR đơn thuốc.

    Tham số:
    - prescription_text: Nội dung đơn thuốc dạng text (kết quả từ OCR).
      Nếu chứa nhiều ký tự '...' hoặc thiếu thông tin → đơn bị mờ.

    Trả về:
    - JSON string chứa thông tin trích xuất với confidence score.
      confidence >= 0.8 → đọc thành công
      confidence < 0.8  → không đọc được, cần human review
    """
    # Đếm số vị trí bị mất thông tin (dấu ...)
    blur_count = prescription_text.count("...")

    if blur_count > 10:
        # === ĐƠN MỜ: KHÔNG đoán mò (theo spec: "Không bịa tên! Chữ mờ → UNCLEAR") ===
        return json.dumps({
            "extraction_status": "failed",
            "confidence": round(max(0.1, 1.0 - blur_count * 0.03), 2),
            "reason": f"Đơn thuốc quá mờ, phát hiện {blur_count} vị trí không đọc được. "
                      "Cần nhập tay hoặc liên hệ Dược sĩ.",
            "blur_positions": blur_count,
            "medications_found": 0,
            "ask_human": True,
            "raw_text_preview": prescription_text[:150].strip() + "..."
        }, ensure_ascii=False)
    else:
        # === ĐƠN RÕ: Trích xuất thông tin ===
        return json.dumps({
            "extraction_status": "success",
            "confidence": 0.95,
            "medications": [
                {
                    "drug": "Paracetamol",
                    "dosage": "500mg",
                    "qty": 1,
                    "freq": 3,
                    "days": 5,
                    "times": ["07:00", "13:00", "19:00"],
                    "notes": "Sau ăn",
                    "confidence": 0.97
                },
                {
                    "drug": "Amoxicillin",
                    "dosage": "500mg",
                    "qty": 1,
                    "freq": 2,
                    "days": 7,
                    "times": ["08:00", "20:00"],
                    "notes": "Sau ăn 1 giờ",
                    "confidence": 0.94
                },
                {
                    "drug": "Vitamin C",
                    "dosage": "1000mg",
                    "qty": 1,
                    "freq": 1,
                    "days": 10,
                    "times": ["09:00"],
                    "notes": "Buổi sáng, hòa nước (viên sủi)",
                    "confidence": 0.96
                }
            ],
            "doctor": "TS.BS Nguyễn Văn An — Khoa Nội tổng hợp",
            "diagnosis": "Viêm họng cấp, sốt nhẹ",
            "patient": "Trần Thị Bình",
            "patient_code": "VNM-2026-00462",
            "prescription_date": "08/04/2026"
        }, ensure_ascii=False)


def get_mock_prescription(case: str = "random") -> str:
    """
    Lấy nội dung đơn thuốc mock để test.
    Mô phỏng kết quả OCR (Tesseract) trên ảnh đơn thuốc.

    Tham số:
        case: "clear" = đơn rõ, "blurry" = đơn mờ, "random" = ngẫu nhiên
    """
    if case == "clear":
        return CLEAR_PRESCRIPTION
    elif case == "blurry":
        return BLURRY_PRESCRIPTION
    else:
        return random.choice([CLEAR_PRESCRIPTION, BLURRY_PRESCRIPTION])
