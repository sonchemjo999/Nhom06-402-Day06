from langchain_core.tools import tool
from datetime import datetime, timedelta

# Mock Data
user_medications = {}
today_reminders = {}
_medication_counter = 1
_reminder_counter = 1

# Danh sách bệnh viện & Bác sĩ giả lập
HOSPITALS = [
    {"name": "Bệnh viện Đa khoa Quốc tế Vinmec", "address": "458 Minh Khai, Hai Bà Trưng", "hotline": "024 3974 3556"},
    {"name": "Bệnh viện Bạch Mai", "address": "78 Giải Phóng, Phương Mai", "hotline": "024 3869 3731"},
    {"name": "Bệnh viện Việt Đức", "address": "40 Tràng Thi, Hoàn Kiếm", "hotline": "19001902"}
]
DOCTOR_INFO = {"name": "BS. Nguyễn Văn An", "phone": "090-123-4567", "specialty": "Nội tổng quát"}

@tool
def triage_symptom(symptoms: str) -> str:
    """Phân loại triệu chứng y tế để đưa ra hướng dẫn."""
    # Đưa biến HOSPITALS vào thẳng trong hàm để không bao giờ bị lỗi NameError
    HOSPITALS = [
        "BV Bạch Mai: 024 3869 3731",
        "BV Vinmec: 024 3974 3556",
        "BV Việt Đức: 19001902"
    ]
    
    s = symptoms.lower()
    
    # Bổ sung thêm từ khóa "sốt 40" vào nhóm khẩn cấp
    if any(k in s for k in ["khó thở", "đau ngực", "ngất", "co giật", "sốt 39", "sốt 40"]):
        return f"Tình trạng khẩn cấp. Cần đến bệnh viện hoặc gọi cấp cứu ngay. SĐT BS An: 090-123-4567. BV gần nhất: {', '.join(HOSPITALS)}"
    
    if any(k in s for k in ["đau đầu", "sốt", "ho", "mệt", "đau bụng"]):
        return "Tình trạng cần theo dõi. Khuyên người dùng theo dõi sức khỏe trong 24h. Nếu không đỡ, hãy gọi BS An: 090-123-4567."
    
    return "Tình trạng nhẹ. Khuyên người dùng nghỉ ngơi tại nhà và uống nhiều nước."

@tool
def get_schedule() -> str:
    """Lấy lịch thuốc."""
    return "Lịch thuốc: 08:00 - Paracetamol 500mg (1 viên)."

tools_list = [triage_symptom, get_schedule]

@tool
def check_adherence(medication_id: int, reminder_time: str) -> str:
    """Xác nhận đã uống thuốc."""
    return f" Đã ghi nhận bạn uống thuốc lúc {reminder_time}. Giỏi lắm!"

tools_list = [triage_symptom, get_schedule, check_adherence]