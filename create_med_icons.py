"""
==============================================================================
 Tạo icons thuốc - 40+ icon SVG dựa trên Mewdicate decompile
==============================================================================
 Chạy: python create_med_icons.py
 Tạo: assets/icons/medications/*.svg
"""

import os

# Thư mục lưu icons
ICONS_DIR = os.path.join(
    os.path.dirname(__file__), "assets", "icons", "medications"
)
os.makedirs(ICONS_DIR, exist_ok=True)


# ============================================================================
# ICON SVG TEMPLATES
# Mỗi icon là SVG vector - scale tốt trên mọi kích thước
# ============================================================================


def svg_template(content: str, size=64) -> str:
    """Gói nội dung SVG với header chuẩn."""
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 64 64">
{content}
</svg>'''


# ============================================================================
# 1. TABLET ICONS (Viên nén)
# ============================================================================

ICONS = {

    # --- Viên tròn có vạch chia ---
    "tablet_round_scored": svg_template('''
    <circle cx="32" cy="32" r="24" fill="#e8f4fd" stroke="#3a8fc7" stroke-width="3"/>
    <line x1="32" y1="8" x2="32" y2="56" stroke="#3a8fc7" stroke-width="2.5"/>
    <circle cx="32" cy="32" r="20" fill="none" stroke="#a8d4f0" stroke-width="1"/>
    '''),

    # --- Viên tròn không vạch chia ---
    "tablet_round_unscored": svg_template('''
    <circle cx="32" cy="32" r="24" fill="#e8f4fd" stroke="#3a8fc7" stroke-width="3"/>
    <circle cx="32" cy="32" r="18" fill="none" stroke="#a8d4f0" stroke-width="1.5"/>
    '''),

    # --- Viên tam giác ---
    "tablet_triangle": svg_template('''
    <polygon points="32,6 58,54 6,54" fill="#ffe8e8" stroke="#c73a3a" stroke-width="3" stroke-linejoin="round"/>
    <polygon points="32,14 50,48 14,48" fill="none" stroke="#f0a8a8" stroke-width="1.5"/>
    '''),

    # --- Viên nang (dạng viên con nhộng) ---
    "capsule_standard": svg_template('''
    <rect x="16" y="10" width="32" height="44" rx="16" fill="#c73a3a"/>
    <rect x="16" y="10" width="32" height="22" rx="16" fill="#3a8fc7"/>
    <rect x="16" y="10" width="32" height="44" rx="16" fill="none" stroke="#555" stroke-width="2"/>
    <line x1="16" y1="32" x2="48" y2="32" stroke="#555" stroke-width="2"/>
    '''),

    # --- Viên nang một màu ---
    "capsule_mono": svg_template('''
    <rect x="16" y="10" width="32" height="44" rx="16" fill="#c73a3a"/>
    <rect x="16" y="10" width="32" height="44" rx="16" fill="none" stroke="#555" stroke-width="2"/>
    <line x1="16" y1="32" x2="48" y2="32" stroke="#8a2020" stroke-width="1.5"/>
    '''),

    # --- Viên nang có hạt ---
    "capsule_beads": svg_template('''
    <rect x="16" y="10" width="32" height="44" rx="16" fill="#c73a3a"/>
    <rect x="16" y="10" width="32" height="22" rx="16" fill="#3a8fc7"/>
    <rect x="16" y="10" width="32" height="44" rx="16" fill="none" stroke="#555" stroke-width="2"/>
    <circle cx="24" cy="26" r="3" fill="#fff" opacity="0.7"/>
    <circle cx="32" cy="24" r="2.5" fill="#fff" opacity="0.7"/>
    <circle cx="40" cy="26" r="3" fill="#fff" opacity="0.7"/>
    <circle cx="28" cy="40" r="2" fill="#fff" opacity="0.5"/>
    <circle cx="36" cy="42" r="2.5" fill="#fff" opacity="0.5"/>
    '''),

    # --- Viên hình thoi ---
    "tablet_rhombus": svg_template('''
    <polygon points="32,4 58,32 32,60 6,32" fill="#ffe0a8" stroke="#c7883a" stroke-width="3" stroke-linejoin="round"/>
    <line x1="32" y1="4" x2="32" y2="60" stroke="#c7883a" stroke-width="2"/>
    '''),

    # --- Viên nửa tròn (caplet có vạch) ---
    "tablet_caplet_scored": svg_template('''
    <rect x="8" y="20" width="48" height="24" rx="12" fill="#e8f4fd" stroke="#3a8fc7" stroke-width="3"/>
    <line x1="32" y1="20" x2="32" y2="44" stroke="#3a8fc7" stroke-width="2.5"/>
    '''),

    # --- Viên nửa tròn không vạch ---
    "tablet_caplet_unscored": svg_template('''
    <rect x="8" y="20" width="48" height="24" rx="12" fill="#e8f4fd" stroke="#3a8fc7" stroke-width="3"/>
    '''),

    # =========================================================================
    # 2. DROP ICONS (Thuốc nhỏ)
    # =========================================================================

    # --- Giọt chuẩn ---
    "drop_standard": svg_template('''
    <path d="M32 6 C32 6 12 32 12 44 A20 20 0 1 0 52 44 C52 32 32 6 32 6Z" fill="#a8d4f0" stroke="#3a8fc7" stroke-width="2.5"/>
    <ellipse cx="26" cy="38" rx="5" ry="7" fill="white" opacity="0.4"/>
    '''),

    # --- Ống nhỏ giọt (dropper) ---
    "drop_dropper": svg_template('''
    <rect x="26" y="4" width="12" height="28" rx="4" fill="#ddd" stroke="#999" stroke-width="2"/>
    <path d="M20 32 C20 32 14 44 14 50 A18 14 0 1 0 50 50 C50 44 44 32 44 32Z" fill="#a8d4f0" stroke="#3a8fc7" stroke-width="2"/>
    <line x1="26" y1="32" x2="38" y2="32" stroke="#999" stroke-width="1.5"/>
    '''),

    # --- Nhỏ mắt ---
    "drop_eye_drops": svg_template('''
    <rect x="22" y="2" width="20" height="34" rx="4" fill="#4a90d9" stroke="#2a6099" stroke-width="2"/>
    <rect x="22" y="2" width="20" height="10" rx="4" fill="#ddd" stroke="#999" stroke-width="2"/>
    <path d="M26 36 L26 48 A6 6 0 0 0 38 48 L38 36Z" fill="#4a90d9" stroke="#2a6099" stroke-width="2"/>
    <ellipse cx="32" cy="22" rx="5" ry="4" fill="white" opacity="0.5"/>
    '''),

    # =========================================================================
    # 3. LIQUID ICONS (Thuốc nước)
    # =========================================================================

    # --- Lọ thuốc nước ---
    "liquid_standard": svg_template('''
    <rect x="16" y="24" width="32" height="36" rx="4" fill="#a8d4f0" stroke="#3a8fc7" stroke-width="2.5"/>
    <rect x="24" y="8" width="16" height="16" rx="3" fill="#ddd" stroke="#999" stroke-width="2"/>
    <rect x="24" y="8" width="16" height="6" rx="3" fill="#bbb" stroke="#999" stroke-width="1.5"/>
    <rect x="20" y="36" width="24" height="16" rx="2" fill="#3a8fc7" opacity="0.3"/>
    <line x1="22" y1="42" x2="42" y2="42" stroke="#3a8fc7" stroke-width="1.5"/>
    '''),

    # --- Lọ nhỏ có nắp ---
    "liquid_bottle_small": svg_template('''
    <rect x="20" y="18" width="24" height="40" rx="4" fill="#c8f0c8" stroke="#3ac73a" stroke-width="2.5"/>
    <rect x="26" y="6" width="12" height="12" rx="3" fill="#ddd" stroke="#999" stroke-width="2"/>
    <rect x="24" y="34" width="16" height="12" rx="2" fill="#3ac73a" opacity="0.3"/>
    '''),

    # =========================================================================
    # 4. CREAM / GEL ICONS
    # =========================================================================

    # --- Kem / Gel chuẩn ---
    "creamgel_standard": svg_template('''
    <rect x="12" y="22" width="40" height="36" rx="8" fill="#f0e8d0" stroke="#c7a83a" stroke-width="2.5"/>
    <rect x="22" y="8" width="20" height="14" rx="4" fill="#ddd" stroke="#999" stroke-width="2"/>
    <rect x="16" y="32" width="32" height="18" rx="3" fill="#e8d8a0" opacity="0.6"/>
    '''),

    # =========================================================================
    # 5. SPRAY ICONS
    # =========================================================================

    # --- Xịt chuẩn ---
    "spray_standard": svg_template('''
    <rect x="18" y="24" width="28" height="36" rx="6" fill="#d8f0f8" stroke="#3aaac7" stroke-width="2.5"/>
    <rect x="26" y="8" width="12" height="16" rx="4" fill="#ddd" stroke="#999" stroke-width="2"/>
    <circle cx="32" cy="4" r="3" fill="#ddd" stroke="#999" stroke-width="1.5"/>
    <circle cx="12" cy="28" r="2" fill="#3aaac7" opacity="0.5"/>
    <circle cx="8" cy="36" r="1.5" fill="#3aaac7" opacity="0.3"/>
    '''),

    # --- Hít mũi (inhaler) ---
    "spray_inhaler": svg_template('''
    <rect x="16" y="14" width="32" height="44" rx="6" fill="#e8f0e8" stroke="#3ac7a8" stroke-width="2.5"/>
    <rect x="24" y="4" width="16" height="10" rx="4" fill="#bbb" stroke="#888" stroke-width="2"/>
    <path d="M22 22 L22 6 L42 6 L42 22Z" fill="#ddd" stroke="#888" stroke-width="2"/>
    <rect x="20" y="36" width="24" height="14" rx="2" fill="#3ac7a8" opacity="0.3"/>
    '''),

    # =========================================================================
    # 6. INJECTION ICONS
    # =========================================================================

    # --- Tiêm chuẩn ---
    "injection_standard": svg_template('''
    <rect x="28" y="4" width="8" height="40" rx="2" fill="#ddd" stroke="#999" stroke-width="2"/>
    <polygon points="32,44 28,56 36,56" fill="#bbb" stroke="#888" stroke-width="1.5"/>
    <rect x="24" y="8" width="16" height="20" rx="3" fill="#fff" stroke="#999" stroke-width="2"/>
    <line x1="28" y1="14" x2="36" y2="14" stroke="#ddd" stroke-width="1"/>
    <line x1="28" y1="18" x2="36" y2="18" stroke="#ddd" stroke-width="1"/>
    <line x1="28" y1="22" x2="36" y2="22" stroke="#ddd" stroke-width="1"/>
    '''),

    # =========================================================================
    # 7. PATCH / DÁN
    # =========================================================================

    # --- Dán da (miếng dán thuốc) ---
    "patch_transdermal": svg_template('''
    <rect x="6" y="18" width="52" height="28" rx="6" fill="#f8e8d0" stroke="#c78a3a" stroke-width="3"/>
    <rect x="12" y="24" width="40" height="16" rx="3" fill="#e8d0a8" opacity="0.6"/>
    <circle cx="18" cy="32" r="3" fill="#c78a3a" opacity="0.4"/>
    <circle cx="32" cy="32" r="3" fill="#c78a3a" opacity="0.4"/>
    <circle cx="46" cy="32" r="3" fill="#c78a3a" opacity="0.4"/>
    '''),

    # --- Băng keo chéo ---
    "patch_cross_bandage": svg_template('''
    <rect x="22" y="6" width="20" height="52" rx="4" fill="#fff" stroke="#ccc" stroke-width="2"/>
    <rect x="6" y="22" width="52" height="20" rx="4" fill="#fff" stroke="#ccc" stroke-width="2"/>
    <line x1="26" y1="10" x2="38" y2="10" stroke="#e8c8a8" stroke-width="3"/>
    <line x1="26" y1="54" x2="38" y2="54" stroke="#e8c8a8" stroke-width="3"/>
    <line x1="10" y1="26" x2="10" y2="38" stroke="#e8c8a8" stroke-width="3"/>
    <line x1="54" y1="26" x2="54" y2="38" stroke="#e8c8a8" stroke-width="3"/>
    '''),

    # --- Băng keo ngón ---
    "patch_knuckle_bandage": svg_template('''
    <rect x="8" y="24" width="48" height="20" rx="10" fill="#fff" stroke="#ccc" stroke-width="2"/>
    <rect x="16" y="28" width="32" height="12" rx="6" fill="#f8e8e8" opacity="0.6"/>
    '''),

    # =========================================================================
    # 8. SNACK / THỨC ĂN (Uống thuốc kèm thức ăn)
    # =========================================================================

    # --- Sữa ---
    "snack_milk": svg_template('''
    <path d="M16 18 L16 56 L48 56 L48 18 Z" fill="#fff8e8" stroke="#c7a83a" stroke-width="2.5"/>
    <polygon points="16,18 32,4 48,18" fill="#fff8e8" stroke="#c7a83a" stroke-width="2.5"/>
    <rect x="20" y="28" width="24" height="20" rx="2" fill="#e8d8a0" opacity="0.4"/>
    <text x="32" y="42" font-size="10" text-anchor="middle" fill="#c7a83a" font-family="sans-serif">MILK</text>
    '''),

    # --- Súp ---
    "snack_soup": svg_template('''
    <ellipse cx="32" cy="44" rx="24" ry="14" fill="#f8e8d0" stroke="#c7a83a" stroke-width="2.5"/>
    <ellipse cx="32" cy="44" rx="18" ry="10" fill="#f0d090" opacity="0.5"/>
    <ellipse cx="26" cy="42" rx="4" ry="3" fill="#c8783a" opacity="0.6"/>
    <ellipse cx="36" cy="40" rx="3" ry="2" fill="#c8783a" opacity="0.6"/>
    <ellipse cx="32" cy="46" rx="5" ry="2" fill="#c8f080" opacity="0.4"/>
    '''),

    # --- Tráng miệng ---
    "snack_dessert": svg_template('''
    <ellipse cx="32" cy="44" rx="22" ry="14" fill="#f8e0f0" stroke="#c73ac7" stroke-width="2.5"/>
    <ellipse cx="32" cy="36" rx="18" ry="10" fill="#f0d0f0" stroke="#c73ac7" stroke-width="2"/>
    <circle cx="32" cy="32" r="6" fill="#e8a0d0" stroke="#c73ac7" stroke-width="1.5"/>
    '''),

    # --- Protein ---
    "snack_protein": svg_template('''
    <rect x="12" y="14" width="40" height="40" rx="6" fill="#e8f0e8" stroke="#3ac73a" stroke-width="2.5"/>
    <rect x="18" y="8" width="28" height="6" rx="3" fill="#bbb" stroke="#999" stroke-width="2"/>
    <text x="32" y="38" font-size="9" text-anchor="middle" fill="#3ac73a" font-family="sans-serif" font-weight="bold">PROTEIN</text>
    '''),

    # --- Rau củ ---
    "snack_veggie": svg_template('''
    <ellipse cx="32" cy="40" rx="22" ry="18" fill="#f0f8e8" stroke="#7ac73a" stroke-width="2.5"/>
    <ellipse cx="24" cy="36" rx="6" ry="8" fill="#80c83a" opacity="0.6" transform="rotate(-20 24 36)"/>
    <ellipse cx="38" cy="34" rx="5" ry="7" fill="#80c83a" opacity="0.6" transform="rotate(15 38 34)"/>
    <ellipse cx="30" cy="46" rx="7" ry="4" fill="#c8803a" opacity="0.5"/>
    '''),

    # =========================================================================
    # 9. SUPPOSITORY / THUỐC ĐẠN
    # =========================================================================

    "suppository_standard": svg_template('''
    <path d="M16 32 C16 24 22 18 32 18 C42 18 48 24 48 32 C48 40 42 46 32 46 C22 46 16 40 16 32Z" fill="#f8f0e0" stroke="#c7a83a" stroke-width="2.5"/>
    <path d="M20 32 C20 26 24 22 32 22 C40 22 44 26 44 32" fill="none" stroke="#e8d8a0" stroke-width="1.5"/>
    '''),

    # =========================================================================
    # 10. EYE DROPS (Nước mắt nhân tạo)
    # =========================================================================

    "eye_drops_multi": svg_template('''
    <rect x="14" y="16" width="36" height="40" rx="6" fill="#a8d4f0" stroke="#3a8fc7" stroke-width="2.5"/>
    <rect x="24" y="6" width="16" height="10" rx="3" fill="#ddd" stroke="#999" stroke-width="2"/>
    <rect x="14" y="16" width="36" height="12" rx="6" fill="#3a8fc7" opacity="0.3"/>
    <circle cx="22" cy="42" r="5" fill="#fff" opacity="0.5"/>
    <circle cx="42" cy="42" r="5" fill="#fff" opacity="0.5"/>
    '''),

    # =========================================================================
    # 11. INHALER / HÍT
    # =========================================================================

    "inhaler_breath": svg_template('''
    <ellipse cx="32" cy="40" rx="20" ry="16" fill="#e8f0f8" stroke="#3a8fc7" stroke-width="2.5"/>
    <rect x="26" y="6" width="12" height="24" rx="4" fill="#ddd" stroke="#999" stroke-width="2"/>
    <circle cx="32" cy="8" r="4" fill="#bbb" stroke="#999" stroke-width="1.5"/>
    <path d="M20 36 Q24 28 32 32 Q40 36 44 28" fill="none" stroke="#3a8fc7" stroke-width="2" opacity="0.5"/>
    '''),

    # =========================================================================
    # 12. PILL BOX / HỘP THUỐC
    # =========================================================================

    "pill_box_daily": svg_template('''
    <rect x="8" y="16" width="48" height="40" rx="6" fill="#e8f8e8" stroke="#3ac73a" stroke-width="2.5"/>
    <rect x="8" y="16" width="48" height="10" rx="6" fill="#3ac73a" opacity="0.3"/>
    <line x1="24" y1="16" x2="24" y2="56" stroke="#3ac73a" stroke-width="1.5"/>
    <line x1="40" y1="16" x2="40" y2="56" stroke="#3ac73a" stroke-width="1.5"/>
    <line x1="8" y1="36" x2="56" y2="36" stroke="#3ac73a" stroke-width="1.5"/>
    <circle cx="16" cy="26" r="4" fill="#c73a3a" opacity="0.6"/>
    <circle cx="48" cy="26" r="4" fill="#3a8fc7" opacity="0.6"/>
    <circle cx="16" cy="48" r="4" fill="#c7a83a" opacity="0.6"/>
    <circle cx="48" cy="48" r="4" fill="#3ac73a" opacity="0.6"/>
    '''),

    # =========================================================================
    # 13. SYRUP (Xi rô)
    # =========================================================================

    "syrup_standard": svg_template('''
    <path d="M20 20 L18 52 C18 56 22 58 32 58 C42 58 46 56 46 52 L44 20Z" fill="#f0e8e8" stroke="#c73a3a" stroke-width="2.5"/>
    <rect x="22" y="6" width="20" height="14" rx="4" fill="#ddd" stroke="#999" stroke-width="2"/>
    <rect x="22" y="6" width="20" height="5" rx="3" fill="#bbb" stroke="#999" stroke-width="1.5"/>
    <rect x="24" y="30" width="16" height="18" rx="2" fill="#c73a3a" opacity="0.2"/>
    <text x="32" y="42" font-size="8" text-anchor="middle" fill="#c73a3a" font-family="sans-serif">SYRUP</text>
    '''),

    # =========================================================================
    # 14. POWDER (Bột)
    # =========================================================================

    "powder_sachet": svg_template('''
    <rect x="10" y="14" width="44" height="40" rx="4" fill="#f8f0e8" stroke="#c7a83a" stroke-width="2.5"/>
    <line x1="10" y1="24" x2="54" y2="24" stroke="#c7a83a" stroke-width="1.5"/>
    <rect x="16" y="30" width="32" height="18" rx="2" fill="#e8d8a0" opacity="0.4"/>
    <text x="32" y="42" font-size="8" text-anchor="middle" fill="#c7a83a" font-family="sans-serif">POWDER</text>
    '''),

    # =========================================================================
    # 15. LOZENGE / KẸO NGậM
    # =========================================================================

    "lozenge_standard": svg_template('''
    <ellipse cx="32" cy="32" rx="24" ry="16" fill="#f8e8e8" stroke="#c73a3a" stroke-width="3"/>
    <ellipse cx="32" cy="32" rx="18" ry="11" fill="none" stroke="#f0a8a8" stroke-width="1.5"/>
    '''),

    # =========================================================================
    # 16. MULTI-VITAMIN (Vitamin tổng hợp)
    # =========================================================================

    "vitamin_complex": svg_template('''
    <circle cx="22" cy="28" r="12" fill="#ffe8a8" stroke="#c7a83a" stroke-width="2.5"/>
    <circle cx="42" cy="28" r="12" fill="#f8e8a8" stroke="#c7a83a" stroke-width="2.5"/>
    <circle cx="32" cy="44" r="12" fill="#e8f8e8" stroke="#3ac73a" stroke-width="2.5"/>
    <text x="22" y="32" font-size="8" text-anchor="middle" fill="#c7a83a" font-family="sans-serif">A</text>
    <text x="42" y="32" font-size="8" text-anchor="middle" fill="#c7a83a" font-family="sans-serif">B</text>
    <text x="32" y="48" font-size="8" text-anchor="middle" fill="#3ac73a" font-family="sans-serif">C</text>
    '''),

    # =========================================================================
    # 17. HERBAL / THUỐC THẢO MỘC
    # =========================================================================

    "herbal_leaf": svg_template('''
    <path d="M32 6 Q56 20 50 38 Q44 52 32 58 Q20 52 14 38 Q8 20 32 6Z" fill="#a8e8a8" stroke="#3ac73a" stroke-width="2.5"/>
    <line x1="32" y1="10" x2="32" y2="54" stroke="#3ac73a" stroke-width="1.5"/>
    <line x1="32" y1="20" x2="20" y2="26" stroke="#3ac73a" stroke-width="1"/>
    <line x1="32" y1="28" x2="22" y2="34" stroke="#3ac73a" stroke-width="1"/>
    <line x1="32" y1="36" x2="24" y2="40" stroke="#3ac73a" stroke-width="1"/>
    <line x1="32" y1="20" x2="44" y2="26" stroke="#3ac73a" stroke-width="1"/>
    <line x1="32" y1="28" x2="42" y2="34" stroke="#3ac73a" stroke-width="1"/>
    <line x1="32" y1="36" x2="40" y2="40" stroke="#3ac73a" stroke-width="1"/>
    '''),

    # =========================================================================
    # 18. INSULIN / TIÊM INSULIN
    # =========================================================================

    "insulin_pen": svg_template('''
    <rect x="22" y="6" width="20" height="50" rx="6" fill="#e8f0f8" stroke="#3a8fc7" stroke-width="2.5"/>
    <rect x="22" y="6" width="20" height="12" rx="6" fill="#3a8fc7" opacity="0.3"/>
    <rect x="22" y="32" width="20" height="16" rx="2" fill="#3a8fc7" opacity="0.2"/>
    <line x1="22" y1="28" x2="42" y2="28" stroke="#3a8fc7" stroke-width="2"/>
    <rect x="26" y="56" width="12" height="4" rx="1" fill="#bbb" stroke="#999" stroke-width="1.5"/>
    '''),

    # =========================================================================
    # 19. EAR DROPS / NHỖ TAI
    # =========================================================================

    "ear_drops": svg_template('''
    <rect x="24" y="4" width="16" height="20" rx="4" fill="#ddd" stroke="#999" stroke-width="2"/>
    <path d="M28 24 L28 40 A4 4 0 0 0 36 40 L36 24Z" fill="#f0e8d0" stroke="#c7a83a" stroke-width="2"/>
    <ellipse cx="32" cy="48" rx="10" ry="6" fill="#f0e8d0" stroke="#c7a83a" stroke-width="2"/>
    <ellipse cx="32" cy="48" rx="6" ry="3" fill="#e8d8a0" opacity="0.5"/>
    '''),

    # =========================================================================
    # 20. NOSE SPRAY / XỊT MŨI
    # =========================================================================

    "nose_spray": svg_template('''
    <rect x="22" y="16" width="20" height="40" rx="4" fill="#e8f8f8" stroke="#3a8fc7" stroke-width="2.5"/>
    <rect x="26" y="4" width="12" height="12" rx="3" fill="#ddd" stroke="#999" stroke-width="2"/>
    <path d="M30 56 L26 62 L38 62 L34 56Z" fill="#ddd" stroke="#999" stroke-width="2"/>
    <rect x="26" y="28" width="12" height="16" rx="2" fill="#3a8fc7" opacity="0.2"/>
    '''),

    # =========================================================================
    # 21. THERMOMETER / NHIỆT KẾ
    # =========================================================================

    "thermometer": svg_template('''
    <rect x="28" y="6" width="8" height="44" rx="4" fill="#f8e8e8" stroke="#c73a3a" stroke-width="2.5"/>
    <circle cx="32" cy="56" r="6" fill="#f8e8e8" stroke="#c73a3a" stroke-width="2.5"/>
    <rect x="29" y="18" width="6" height="36" rx="3" fill="#c73a3a" opacity="0.6"/>
    <line x1="28" y1="16" x2="36" y2="16" stroke="#c73a3a" stroke-width="1"/>
    <line x1="28" y1="26" x2="34" y2="26" stroke="#c73a3a" stroke-width="1"/>
    <line x1="28" y1="36" x2="34" y2="36" stroke="#c73a3a" stroke-width="1"/>
    <line x1="28" y1="46" x2="34" y2="46" stroke="#c73a3a" stroke-width="1"/>
    '''),

    # =========================================================================
    # 22. BLOOD PRESSURE / ĐO HUYẾT ÁP
    # =========================================================================

    "blood_pressure": svg_template('''
    <ellipse cx="32" cy="20" rx="18" ry="14" fill="#e8f0f8" stroke="#3a8fc7" stroke-width="2.5"/>
    <rect x="14" y="32" width="36" height="24" rx="4" fill="#e8f0f8" stroke="#3a8fc7" stroke-width="2.5"/>
    <rect x="18" y="36" width="28" height="16" rx="2" fill="#3a8fc7" opacity="0.2"/>
    <text x="32" y="48" font-size="10" text-anchor="middle" fill="#3a8fc7" font-family="sans-serif">120/80</text>
    '''),

    # =========================================================================
    # 23. GLUCOMETER / ĐO ĐƯỜNG HUYẾT
    # =========================================================================

    "glucose_meter": svg_template('''
    <rect x="14" y="10" width="36" height="50" rx="6" fill="#e8f8e8" stroke="#3ac73a" stroke-width="2.5"/>
    <rect x="18" y="16" width="28" height="20" rx="3" fill="#3ac73a" opacity="0.2"/>
    <text x="32" y="30" font-size="12" text-anchor="middle" fill="#3ac73a" font-family="sans-serif">5.4</text>
    <text x="32" y="38" font-size="6" text-anchor="middle" fill="#3ac73a" font-family="sans-serif">mmol/L</text>
    <circle cx="32" cy="50" r="6" fill="#ddd" stroke="#999" stroke-width="2"/>
    <circle cx="32" cy="50" r="3" fill="#3ac73a" opacity="0.5"/>
    '''),

    # =========================================================================
    # 24. FIRST AID / SƠ CỨU
    # =========================================================================

    "first_aid_kit": svg_template('''
    <rect x="8" y="18" width="48" height="38" rx="6" fill="#f8e8e8" stroke="#c73a3a" stroke-width="3"/>
    <rect x="28" y="12" width="8" height="6" rx="2" fill="#c73a3a" stroke="#a02020" stroke-width="2"/>
    <rect x="26" y="30" width="12" height="14" rx="2" fill="#c73a3a"/>
    <line x1="32" y1="32" x2="32" y2="42" stroke="white" stroke-width="2"/>
    <line x1="27" y1="37" x2="37" y2="37" stroke="white" stroke-width="2"/>
    '''),
}


def create_all_icons():
    """Tạo tất cả icon SVG và lưu vào thư mục assets."""
    count = 0
    for name, content in ICONS.items():
        path = os.path.join(ICONS_DIR, f"{name}.svg")
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        count += 1

    print(f"[OK] Da tao {count} icon SVG tai: {ICONS_DIR}")
    return count


def create_index_file():
    """Tao file index.py de de import."""
    index_path = os.path.join(ICONS_DIR, "__init__.py")
    with open(index_path, "w", encoding="utf-8") as f:
        f.write('"""\nIcon thuoc - 40+ SVG icons\n"""\n\n')
        f.write("MED_ICON_NAMES = [\n")
        for name in sorted(ICONS.keys()):
            f.write(f'    "{name}",\n')
        f.write("]\n\n")
        f.write("def get_all_icon_names():\n")
        f.write('    """Tra ve danh sach ten tat ca icon."""\n')
        f.write("    return list(MED_ICON_NAMES)\n")
    print(f"[OK] Da tao index: {index_path}")


if __name__ == "__main__":
    n = create_all_icons()
    create_index_file()
    print(f"\nTong cong: {n} icons thuoc")
    print(f"Thu muc: {ICONS_DIR}")
