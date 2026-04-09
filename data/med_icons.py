"""
==============================================================================
 med_icons — gán icon PNG theo tên thuốc (HomeScreen / AlarmPopup)
==============================================================================
 Dùng khi lưu lịch từ CrossCheck không kèm trường icon.
 File PNG nằm trong assets/icons/medications/ (cùng tên như mock_data).
==============================================================================
"""


def resolve_med_icon(med_name: str) -> str:
    """
    Trả về tên file icon dựa trên tên thuốc (không dấu / có dấu đều được).
    """
    if not med_name or not str(med_name).strip():
        return "icon_tablets.png"
    n = str(med_name).lower()
    if "vitamin" in n:
        return "icon_tablets.png"
    if "amoxicillin" in n or "omeprazole" in n:
        return "ic_med_capsule_standard.png"
    if "paracetamol" in n or "metformin" in n or "aspirin" in n:
        return "ic_med_tablet_round_scored.png"
    return "icon_tablets.png"
