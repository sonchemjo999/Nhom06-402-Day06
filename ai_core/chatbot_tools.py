"""
==============================================================================
 Chatbot Tools - Công cụ y tế cho Chatbot AI
==============================================================================
 File: ai_core/chatbot_tools.py

 Cung cấp các @tool cho chatbot y tế:
   - check_drug_interaction  : Kiểm tra tương tác thuốc
   - get_dosage_info         : Lấy thông tin liều lượng
   - get_side_effects        : Lấy tác dụng phụ
   - search_hospital         : Tìm bệnh viện cấp cứu
   - get_symptom_advice       : Gợi ý theo triệu chứng (GREEN/YELLOW/RED)
==============================================================================
"""

from langchain_core.tools import tool

# ============================================================================
# MOCK DATA — THUỐC VÀ TƯƠNG TÁC
# ============================================================================

DRUG_DB = {
    "paracetamol": {
        "name": "Paracetamol",
        "generic": "Acetaminophen",
        "dosage_adult": "500mg - 1000mg mỗi lần, tối đa 4g/ngày",
        "dosage_child": "10-15mg/kg mỗi lần, tối đa 60mg/kg/ngày",
        "frequency": "Cách nhau 4-6 giờ",
        "max_daily": "4g (4000mg)",
        "take_with": "Uống sau ăn hoặc khi no",
        "side_effects": "Hiếm gặp khi dùng đúng liều. Quá liều → tổn thương gan.",
        "contraindications": "Người suy gan nặng, dị ứng paracetamol.",
    },
    "ibuprofen": {
        "name": "Ibuprofen",
        "generic": "Ibuprofen",
        "dosage_adult": "200mg - 400mg mỗi lần, tối đa 1200mg/ngày (OTC)",
        "dosage_child": "5-10mg/kg mỗi lần, tối đa 40mg/kg/ngày",
        "frequency": "Cách nhau 6-8 giờ",
        "max_daily": "1200mg (OTC) - 3200mg (theo chỉ định)",
        "take_with": "Uống sau ăn để giảm kích ứng dạ dày",
        "side_effects": "Đau dạ dày, buồn nôn, nhức đầu. Lạm dụng → loét dạ dày.",
        "contraindications": "Loét dạ dày, suy thận, phụ nữ mang thai 3 tháng cuối.",
    },
    "amoxicillin": {
        "name": "Amoxicillin",
        "generic": "Amoxicillin",
        "dosage_adult": "250mg - 500mg mỗi lần, 3 lần/ngày",
        "dosage_child": "20-90mg/kg/ngày chia 2-3 lần",
        "frequency": "Mỗi 8 giờ (3 lần/ngày)",
        "max_daily": "Theo cân nặng và chỉ định bác sĩ",
        "take_with": "Uống trước hoặc sau ăn, không ảnh hưởng hấp thu",
        "side_effects": "Tiêu chảy, phát ban, buồn nôn. Hiếm: dị ứng nặng.",
        "contraindications": "Dị ứng penicillin, suy gan.",
    },
    "omeprazole": {
        "name": "Omeprazole",
        "generic": "Omeprazole",
        "dosage_adult": "20mg - 40mg mỗi lần, 1-2 lần/ngày",
        "dosage_child": "0.7-3.3mg/kg/ngày chia 1-2 lần",
        "frequency": "Uống sáng trước bữa ăn 30 phút",
        "max_daily": "40mg/ngày (OTC), 80mg/ngày (theo chỉ định)",
        "take_with": "Uống lúc đói, trước bữa ăn sáng 30 phút",
        "side_effects": "Đau đầu, buồn nôn, táo bón. Dùng dài hạn → thiếu B12, magiê.",
        "contraindications": "Dị ứng PPI, dùng chung với rilpivirine, nelfinavir.",
    },
    "metformin": {
        "name": "Metformin",
        "generic": "Metformin Hydrochloride",
        "dosage_adult": "500mg x 2 lần/ngày, tăng dần đến 2000mg/ngày",
        "dosage_child": "Trên 10 tuổi: 500mg x 2 lần/ngày",
        "frequency": "Uống trong bữa ăn để giảm tác dụng phụ",
        "max_daily": "2550mg/ngày",
        "take_with": "Uống trong hoặc sau bữa ăn",
        "side_effects": "Buồn nôn, tiêu chảy, đau bụng (thường hết sau vài tuần).",
        "contraindications": "Suy thận nặng (eGFR<30), nhiễm toan lactic, trước X-quang có tiêm.",
    },
    "aspirin": {
        "name": "Aspirin",
        "generic": "Acetylsalicylic Acid",
        "dosage_adult": "75mg - 100mg/ngày (phòng ngừa tim mạch), 300-900mg (giảm đau)",
        "dosage_child": "KHÔNG dùng cho trẻ dưới 16 tuổi (nguy cơ Reye)",
        "frequency": "Uống sau ăn, không nằm ngay sau khi uống",
        "max_daily": "4000mg/ngày (giảm đau)",
        "take_with": "Uống sau ăn với nhiều nước",
        "side_effects": "Kích ứng dạ dày, chảy máu, dị ứng.",
        "contraindications": "Trẻ dưới 16 tuổi, dị ứng NSAID, loét dạ dày, hemophilia.",
    },
    "loratadine": {
        "name": "Loratadine",
        "generic": "Loratadine",
        "dosage_adult": "10mg x 1 lần/ngày",
        "dosage_child": "Trẻ 2-12 tuổi: 5mg x 1 lần/ngày (cân nặng <30kg)",
        "frequency": "1 lần/ngày, không phụ thuộc bữa ăn",
        "max_daily": "10mg/ngày",
        "take_with": "Có thể uống lúc đói hoặc no",
        "side_effects": "Khô miệng, đau đầu, buồn ngủ (ít hơn thế hệ cũ).",
        "contraindications": "Dị ứng loratadine.",
    },
    "vitamin_c": {
        "name": "Vitamin C",
        "generic": "Ascorbic Acid",
        "dosage_adult": "75mg - 200mg/ngày (người lớn)",
        "dosage_child": "Trẻ 1-3 tuổi: 15mg, 4-8 tuổi: 25mg, 9-13 tuổi: 45mg",
        "frequency": "1-2 lần/ngày",
        "max_daily": "2000mg/ngày (người lớn)",
        "take_with": "Uống sau ăn, chia nhỏ để hấp thu tốt hơn",
        "side_effects": "Liều cao (>2000mg) → tiêu chảy, sỏi thận.",
        "contraindications": "Sỏi thận, rối loạn chuyển hóa oxalat.",
    },
}

# Tương tác thuốc: "drug_a|drug_b" → mức độ
DRUG_INTERACTIONS = {
    "paracetamol|ibuprofen": {
        "level": "SAFE",
        "note": "Có thể dùng xen kẽ: paracetamol 4h → ibuprofen 6h. Giảm đau hiệu quả hơn dùng riêng.",
    },
    "aspirin|ibuprofen": {
        "level": "CAUTION",
        "note": "Ibuprofen có thể làm giảm tác dụng chống kết dính tiểu cầu của aspirin. "
               "Nếu cần dùng cả 2 → cách nhau ít nhất 30 phút (uống aspirin trước).",
    },
    "paracetamol|metformin": {
        "level": "SAFE",
        "note": "Không có tương tác đáng kể. Có thể dùng cùng lúc theo chỉ định.",
    },
    "aspirin|metformin": {
        "level": "CAUTION",
        "note": "Aspirin ức chế kết dính tiểu cầu + Metformin → tăng nguy cơ chảy máu nhẹ. Theo dõi.",
    },
    "amoxicillin|paracetamol": {
        "level": "SAFE",
        "note": "Không có tương tác đáng kể. Có thể dùng cùng lúc.",
    },
    "ibuprofen|metformin": {
        "level": "CAUTION",
        "note": "NSAID (ibuprofen) có thể ảnh hưởng chức năng thận → cần theo dõi khi dùng chung với metformin.",
    },
    "omeprazole|metformin": {
        "level": "MINOR",
        "note": "Omeprazole có thể làm tăng nhẹ nồng độ metformin. Thường không cần điều chỉnh liều.",
    },
    "aspirin|paracetamol": {
        "level": "SAFE",
        "note": "Có thể dùng xen kẽ để giảm đau/hạ sốt hiệu quả hơn. Cách nhau 4 giờ.",
    },
}

# Triệu chứng → phân loại mức độ
SYMPTOM_CLASSIFICATION = {
    "GREEN": [
        "tốt", "khỏe", "ổn", "bình thường", "ok", "good", "đỡ", "giảm",
        "hết đau", "hết sốt", "ngon", "ngủ được", "sinh hoạt bình thường",
    ],
    "YELLOW": [
        "mệt", "mỏi", "đau đầu", "nhức đầu", "buồn nôn", "nôn", "chóng mặt",
        "chong mặt", "xao xuyến", "xây xẩm", "mất ngủ", "ngủ không được",
        "phát ban", "nổi mẩn", "đau bụng nhẹ", "tiêu chảy nhẹ", "nghẹn",
        "đau họng", "ho", "sổ mũi", "hắt hơi", "ngứa", "đau khớp",
    ],
    "RED": [
        "khó thở", "kho tho", "hụt oxy", "sốt cao", "sot cao", "sốt 39",
        "sốt 40", "co giật", "co giat", "đau ngực", "dau nguc", "ngực khó thở",
        "bất tỉnh", "bat tinh", "ngất", "ngat", "xuất huyết", "xuat huyet",
        "chảy máu não", "liệt", "nói khó", "mất ý thức", "mau miệng",
        "da vàng", "nước tiểu sẫm", "phù nề", "dị ứng nặng", "sốc phản vệ",
    ],
}

# Bệnh viện cấp cứu
HOSPITALS = [
    {
        "name": "Vinmec Times City",
        "address": "458 Minh Khai, Hai Bà Trưng, Hà Nội",
        "phone": "024 3974 3556",
        "district": "Hai Bà Trưng",
        "type": "Đa khoa quốc tế",
    },
    {
        "name": "Bệnh viện Bạch Mai",
        "address": "78 Giải Phóng, Đống Đa, Hà Nội",
        "phone": "024 3869 3731",
        "district": "Đống Đa",
        "type": "Bệnh viện tuyến trung ương",
    },
    {
        "name": "BV Việt Đức",
        "address": "40 Tràng Tiền, Hoàn Kiếm, Hà Nội",
        "phone": "024 3823 5213",
        "district": "Hoàn Kiếm",
        "type": "BV ngoại khoa trung ương",
    },
    {
        "name": "BV Nhi Trung Ương",
        "address": "18/879 La Thành, Ba Đình, Hà Nội",
        "phone": "024 6273 8498",
        "district": "Ba Đình",
        "type": "BV nhi khoa tuyến trung ương",
    },
    {
        "name": "BV Đại học Y Hà Nội",
        "address": "1 Tôn Thất Tùng, Đống Đa, Hà Nội",
        "phone": "024 3829 5729",
        "district": "Đống Đa",
        "type": "BV tuyến trung ương",
    },
]


# ============================================================================
# TOOLS
# ============================================================================

@tool
def get_dosage_info(drug_name: str) -> str:
    """
    Lấy thông tin liều lượng chi tiết của một loại thuốc.
    Tham số:
    - drug_name: tên thuốc (VD: 'paracetamol', 'ibuprofen', 'amoxicillin')
    Trả về: Thông tin liều lượng, cách dùng, lưu ý.
    """
    key = drug_name.lower().strip()
    drug = DRUG_DB.get(key)
    if not drug:
        available = ", ".join(DRUG_DB.keys())
        return (
            f"Không tìm thấy thông tin cho '{drug_name}' trong hệ thống.\n"
            f"Các thuốc có sẵn: {available}.\n"
            f"Em khuyên anh/chị hỏi bác sĩ hoặc dược sĩ để được tư vấn chính xác nhất nha!"
        )

    return (
        f"💊 {drug['name']} ({drug['generic']})\n\n"
        f"📌 Liều người lớn: {drug['dosage_adult']}\n"
        f"📌 Liều trẻ em: {drug['dosage_child']}\n"
        f"📌 Tần suất: {drug['frequency']}\n"
        f"📌 Liều tối đa/ngày: {drug['max_daily']}\n"
        f"🍽️ Uống: {drug['take_with']}\n\n"
        f"⚠️ Tác dụng phụ: {drug['side_effects']}\n"
        f"🚫 Chống chỉ định: {drug['contraindications']}\n\n"
        f"💡 Nhớ hỏi bác sĩ/dược sĩ để được tư vấn chính xác nhất nha!"
    )


@tool
def check_drug_interaction(drug_a: str, drug_b: str) -> str:
    """
    Kiểm tra tương tác giữa 2 loại thuốc.
    Tham số:
    - drug_a: tên thuốc thứ nhất (VD: 'paracetamol')
    - drug_b: tên thuốc thứ hai (VD: 'ibuprofen')
    Trả về: Mức độ tương tác và lưu ý.
    """
    key_a = drug_a.lower().strip()
    key_b = drug_b.lower().strip()

    # Tạo key theo 2 chiều
    key_forward = f"{key_a}|{key_b}"
    key_reverse = f"{key_b}|{key_a}"

    interaction = DRUG_INTERACTIONS.get(key_forward) or DRUG_INTERACTIONS.get(key_reverse)

    if not interaction:
        return (
            f"Chưa có dữ liệu về tương tác giữa '{drug_a}' và '{drug_b}' trong hệ thống.\n"
            f"Em khuyên anh/chị hỏi bác sĩ hoặc dược sĩ trước khi dùng chung 2 thuốc nha!"
        )

    level = interaction["level"]
    emoji = {"SAFE": "✅", "CAUTION": "⚠️", "MINOR": "ℹ️"}.get(level, "⚠️")

    return (
        f"{emoji} Tương tác giữa **{drug_a}** và **{drug_b}**: [{level}]\n\n"
        f"{interaction['note']}\n\n"
        f"💡 Hãy hỏi bác sĩ/dược sĩ để được tư vấn an toàn nhất nha!"
    )


@tool
def get_side_effects(drug_name: str) -> str:
    """
    Lấy thông tin tác dụng phụ phổ biến của một loại thuốc.
    Tham số:
    - drug_name: tên thuốc (VD: 'ibuprofen', 'metformin')
    Trả về: Danh sách tác dụng phụ và lưu ý.
    """
    key = drug_name.lower().strip()
    drug = DRUG_DB.get(key)
    if not drug:
        available = ", ".join(DRUG_DB.keys())
        return (
            f"Không tìm thấy thông tin cho '{drug_name}'.\n"
            f"Thuốc có sẵn: {available}.\n"
            f"Em khuyên hỏi dược sĩ để được tư vấn nha!"
        )

    return (
        f"💊 {drug['name']} - Tác dụng phụ:\n\n"
        f"⚠️ {drug['side_effects']}\n\n"
        f"🚫 Chống chỉ định: {drug['contraindications']}\n\n"
        f"💡 Nếu có phản ứng bất thường → gặp bác sĩ ngay nha!"
    )


@tool
def search_hospital(location: str = "") -> str:
    """
    Tìm bệnh viện cấp cứu gần nhất.
    Tham số:
    - location: khu vực/quận (VD: 'Hà Nội', 'Đống Đa'). Để trống = tìm tất cả.
    Trả về: Danh sách bệnh viện cấp cứu với địa chỉ, hotline.
    """
    # Chuẩn hóa location: bỏ dấu, lowercase
    import unicodedata
    loc_nd = ""
    if location:
        loc_nd = unicodedata.normalize("NFD", location.lower())
        loc_nd = "".join(c for c in loc_nd if not unicodedata.combining(c))

    results = []
    if loc_nd:
        for h in HOSPITALS:
            # Chuẩn hóa tất cả trường của bệnh viện để so sánh
            name_nd = "".join(c for c in unicodedata.normalize("NFD", h["name"].lower())
                             if not unicodedata.combining(c))
            addr_nd = "".join(c for c in unicodedata.normalize("NFD", h["address"].lower())
                             if not unicodedata.combining(c))
            dist_nd = "".join(c for c in unicodedata.normalize("NFD", h["district"].lower())
                             if not unicodedata.combining(c))
            if (loc_nd in name_nd or loc_nd in addr_nd or loc_nd in dist_nd or
                    loc_nd in h["phone"]):
                results.append(h)
    else:
        results = HOSPITALS

    if not results:
        return (
            f"Không tìm thấy bệnh viện tại '{location}'.\n"
            f"📞 Gọi 115 để được cấp cứu ngay!\n"
            f"💡 Em khuyên anh/chị đến bệnh viện gần nhất ngay nha!"
        )

    lines = ["🏥 BỆNH VIỆN CẤP CỨU GẦN BẠN:\n"]
    for i, h in enumerate(results, 1):
        lines.append(
            f"{i}. {h['name']}\n"
            f"   📍 {h['address']}\n"
            f"   📞 {h['phone']} | Loại: {h['type']}\n"
        )
    lines.append("\n📞 Gọi 115 nếu cần cấp cứu ngay lập tức!")
    return "\n".join(lines)


@tool
def get_symptom_advice(symptoms: str) -> str:
    """
    Đánh giá mức độ triệu chứng dựa trên mô tả và đưa ra lời khuyên.
    Tham số:
    - symptoms: mô tả triệu chứng của người dùng (VD: 'mệt mỏi, đau đầu nhẹ')
    Trả về: Mức độ (GREEN/YELLOW/RED) + lời khuyên tương ứng.
    """
    # Chuẩn hóa text: bỏ dấu để match không phân biệt có/không dấu
    import unicodedata
    sym_nodiac = unicodedata.normalize("NFD", sym_lower)
    sym_nodiac = "".join(c for c in sym_nodiac if not unicodedata.combining(c))

    # Check RED first (highest priority)
    for kw_raw in SYMPTOM_CLASSIFICATION["RED"]:
        kw_nd = unicodedata.normalize("NFD", kw_raw)
        kw_nd = "".join(c for c in kw_nd if not unicodedata.combining(c))
        if kw_nd in sym_nodiac:
            return (
                "🚨 **CẢNH BÁO NGUY HIỂM!**\n\n"
                "Triệu chứng bạn mô tả có thể nghiêm trọng!\n\n"
                "Hành động NGAY:\n"
                "1. Gọi 115 — cấp cứu ngay lập tức!\n"
                "2. Không tự ý uống thêm thuốc.\n"
                "3. Nếu có người nhà → nhờ hỗ trợ.\n\n"
                "⚠️ Đây là thông tin tham khảo. Hãy gặp bác sĩ ngay!"
            )

    # Check YELLOW
    for kw_raw in SYMPTOM_CLASSIFICATION["YELLOW"]:
        kw_nd = unicodedata.normalize("NFD", kw_raw)
        kw_nd = "".join(c for c in kw_nd if not unicodedata.combining(c))
        if kw_nd in sym_nodiac:
            return (
                "⚠️ **CẦN THEO DÕI** — Triệu chứng của bạn cần chú ý.\n\n"
                "Bạn có thể đánh giá mức độ từ 1 đến 10 không?\n"
                "  • 1-3: Nhẹ, theo dõi tại nhà\n"
                "  • 4-6: Trung bình, nên liên hệ bác sĩ\n"
                "  • 7-10: Nặng, cần khám ngay\n\n"
                "💡 Nếu tình trạng nặng hơn → đừng chờ, đến bệnh viện ngay nha!"
            )

    # Check GREEN
    for kw in SYMPTOM_CLASSIFICATION["GREEN"]:
        if kw in sym_lower:
            return (
                "✅ **TÌNH TRẠNG ỔN ĐỊNH**\n\n"
                "Tuyệt vời! Rất vui khi bạn cảm thấy tốt hơn.\n\n"
                "Nhớ duy trì:\n"
                "  • Uống thuốc đúng giờ như bác sĩ chỉ định\n"
                "  • Ăn uống đầy đủ, nghỉ ngơi hợp lý\n"
                "  • Tái khám đúng lịch\n\n"
                "Nếu có thay đổi gì → báo ngay cho em nha!"
            )

    # Không nhận diện được
    return (
        "📋 Em chưa rõ triệu chứng của bạn lắm.\n\n"
        "Bạn có thể mô tả chi tiết hơn không?\n"
        "Ví dụ: đau ở đâu? mức độ ntn? kéo dài bao lâu rồi?\n\n"
        "Em sẽ hỗ trợ tốt nhất có thể nha!"
    )


def get_tool_list():
    """Trả về danh sách tất cả tools (dùng khi bind vào LLM)."""
    return [
        get_dosage_info,
        check_drug_interaction,
        get_side_effects,
        search_hospital,
        get_symptom_advice,
    ]
