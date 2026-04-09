"""
==============================================================================
 Icon Loader - Hệ thống tải và quản lý icon thuốc
==============================================================================
 File: icon_loader.py

 Mô tả:
   Tải SVG icons thuốc và cung cấp API để sử dụng trong app.
   Dựa trên Mewdicate decompile - 40+ loại biểu tượng thuốc.

 Sử dụng:
   from icon_loader import IconLoader
   icons = IconLoader()
   svg_data = icons.get_icon("capsule_standard")
   icons.save_icon("tablet_round", "output.svg")
==============================================================================
"""

import os
from typing import Optional

# ============================================================================
# ICON REGISTRY - Ánh xạ loại thuốc → icon
# ============================================================================

# Ánh xạ tên thuốc thông dụng → icon phù hợp nhất
MEDICATION_TO_ICON = {
    # --- Viên nén ---
    "paracetamol": "tablet_round_scored",
    "acetaminophen": "tablet_round_scored",
    "panadol": "tablet_round_scored",
    "doliprane": "tablet_round_scored",
    "aspirin": "tablet_round_unscored",
    "ibuprofen": "tablet_caplet_scored",
    "brufen": "tablet_caplet_scored",
    "naproxen": "tablet_rhombus",

    # --- Kháng sinh ---
    "amoxicillin": "capsule_standard",
    "azithromycin": "capsule_standard",
    "ciprofloxacin": "capsule_beads",
    "metronidazole": "capsule_mono",
    "cephalexin": "capsule_standard",

    # --- Vitamin ---
    "vitamin c": "vitamin_complex",
    "vitamin b": "vitamin_complex",
    "vitamin d": "vitamin_complex",
    "multivitamin": "vitamin_complex",
    "vitamin_complex": "vitamin_complex",

    # --- Thuốc nhỏ ---
    "眼药水": "drop_eye_drops",
    "nước mắt": "drop_eye_drops",
    "eye drops": "drop_eye_drops",

    # --- Thuốc xịt ---
    "inhaler": "spray_inhaler",
    "salbutamol": "spray_inhaler",
    "ventolin": "spray_inhaler",
    "xịt mũi": "nose_spray",
    "nose spray": "nose_spray",

    # --- Thuốc tiêm ---
    "tiêm": "injection_standard",
    "injection": "injection_standard",
    "insulin": "insulin_pen",
    "insuline": "insulin_pen",

    # --- Dán da ---
    "dán": "patch_transdermal",
    "patch": "patch_transdermal",
    "nicotine": "patch_transdermal",

    # --- Kem/Gel ---
    "kem": "creamgel_standard",
    "gel": "creamgel_standard",
    "cream": "creamgel_standard",

    # --- Thuốc nước ---
    "syrup": "syrup_standard",
    "xi rô": "syrup_standard",
    "nước": "liquid_standard",
    "liquid": "liquid_standard",

    # --- Bổ sung ---
    "sữa": "snack_milk",
    "milk": "snack_milk",
    "protein": "snack_protein",
    "supper": "snack_protein",
    "súp": "snack_soup",
    "soup": "snack_soup",

    # --- Đo lường ---
    "đo huyết áp": "blood_pressure",
    "blood pressure": "blood_pressure",
    "đo đường huyết": "glucose_meter",
    "glucose": "glucose_meter",
    "nhiệt kế": "thermometer",
    "thermometer": "thermometer",

    # --- Sơ cứu ---
    "sơ cứu": "first_aid_kit",
    "first aid": "first_aid_kit",
    "băng": "patch_cross_bandage",
    "bandage": "patch_cross_bandage",

    # --- Thảo mộc ---
    "thảo mộc": "herbal_leaf",
    "herbal": "herbal_leaf",

    # --- Mặc định ---
    "default": "tablet_round_scored",
}


# ============================================================================
# ICON LOADER CLASS
# ============================================================================


class IconLoader:
    """
    Lớp quản lý việc tải và truy xuất icon thuốc.
    """

    def __init__(self):
        """Khởi tạo - tìm thư mục icons."""
        # Tìm thư mục icons
        base = os.path.dirname(os.path.abspath(__file__))
        self.icons_dir = os.path.join(base, "assets", "icons", "medications")
        self._icon_cache = {}

        # Tạo thư mục nếu chưa có
        if not os.path.exists(self.icons_dir):
            os.makedirs(self.icons_dir, exist_ok=True)
            print(f"[IconLoader] Đã tạo thư mục: {self.icons_dir}")

    def get_icon_path(self, icon_name: str) -> Optional[str]:
        """
        Trả về đường dẫn đầy đủ đến file icon SVG.

        Tham số:
            icon_name: Tên icon (ví dụ: "capsule_standard")

        Trả về:
            Đường dẫn đầy đủ hoặc None nếu không tìm thấy.
        """
        # Kiểm tra cache
        if icon_name in self._icon_cache:
            return self._icon_cache[icon_name]

        path = os.path.join(self.icons_dir, f"{icon_name}.svg")
        if os.path.exists(path):
            self._icon_cache[icon_name] = path
            return path

        return None

    def get_icon_data(self, icon_name: str) -> Optional[str]:
        """
        Trả về nội dung SVG của icon dưới dạng string.

        Tham số:
            icon_name: Tên icon

        Trả về:
            Nội dung SVG string hoặc None.
        """
        path = self.get_icon_path(icon_name)
        if path:
            try:
                with open(path, "r", encoding="utf-8") as f:
                    return f.read()
            except Exception as e:
                print(f"[IconLoader] Lỗi đọc icon {icon_name}: {e}")
        return None

    def suggest_icon(self, medication_name: str) -> str:
        """
        Đề xuất icon phù hợp nhất dựa trên tên thuốc.

        Tham số:
            medication_name: Tên thuốc (ví dụ: "Amoxicillin 500mg")

        Trả về:
            Tên icon được đề xuất.
        """
        name_lower = medication_name.lower()

        # Tìm trong registry
        for key, icon in MEDICATION_TO_ICON.items():
            if key in name_lower:
                return icon

        # Fallback: phân tích từ khóa
        if any(w in name_lower for w in ["viên", "tablet", "pill"]):
            return "tablet_round_scored"
        elif any(w in name_lower for w in ["nang", "capsule", "viên nang"]):
            return "capsule_standard"
        elif any(w in name_lower for w in ["nhỏ", "giọt", "drop", "mắt"]):
            return "drop_standard"
        elif any(w in name_lower for w in ["xịt", "spray", "hít"]):
            return "spray_standard"
        elif any(w in name_lower for w in ["tiêm", "injection", "kim"]):
            return "injection_standard"
        elif any(w in name_lower for w in ["kem", "gel", "bôi"]):
            return "creamgel_standard"
        elif any(w in name_lower for w in ["dán", "patch", "miếng"]):
            return "patch_transdermal"
        elif any(w in name_lower for w in ["vitamin", "tổng hợp"]):
            return "vitamin_complex"

        # Mặc định
        return "tablet_round_scored"

    def list_available_icons(self) -> list:
        """
        Trả về danh sách tất cả icon có sẵn.

        Trả về:
            Danh sách tên các icon.
        """
        if not os.path.exists(self.icons_dir):
            return []

        icons = []
        for f in os.listdir(self.icons_dir):
            if f.endswith(".svg"):
                icons.append(f[:-4])  # Bỏ .svg
        return sorted(icons)

    def count_icons(self) -> int:
        """Đếm số lượng icon có sẵn."""
        return len(self.list_available_icons())

    def icon_exists(self, icon_name: str) -> bool:
        """Kiểm tra icon có tồn tại không."""
        return self.get_icon_path(icon_name) is not None


# ============================================================================
# SINGLETON INSTANCE
# ============================================================================
_icon_loader = None


def get_icon_loader() -> IconLoader:
    """Trả về singleton instance của IconLoader."""
    global _icon_loader
    if _icon_loader is None:
        _icon_loader = IconLoader()
    return _icon_loader
