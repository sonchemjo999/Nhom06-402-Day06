"""
==============================================================================
 Icon Painter - Ve icon thuoc truc tiep bang Pillow (khong can Cairo)
==============================================================================
 File: icon_painter.py

 Ve 42 icon PNG truc tiep bang Pillow Draw.
 Mỗi icon là 64x64 PNG - hien thi duoc trong Kivy Image widget.

 Chạy: python icon_painter.py
 Output: assets/icons/medications_png/*.png
==============================================================================
"""

import os
from PIL import Image, ImageDraw, ImageFont

PNG_DIR = os.path.join(os.path.dirname(__file__), "assets", "icons", "medications_png")
os.makedirs(PNG_DIR, exist_ok=True)

SIZE = 64


def draw_pill(draw, cx, cy, rx, ry, fill, outline, scored=False, scored_v=False):
    """Ve viên thuốc hình tròn/oval."""
    draw.ellipse([cx - rx, cy - ry, cx + rx, cy + ry], fill=fill, outline=outline, width=2)
    if scored:
        if scored_v:
            draw.line([cx, cy - ry + 2, cx, cy + ry - 2], fill=outline, width=2)
        else:
            draw.line([cx - rx + 2, cy, cx + rx - 2, cy], fill=outline, width=2)


def draw_capsule(draw, cx, cy, w, h, top_color, bottom_color, outline="#555555"):
    """Ve viên nang (2 màu)."""
    # Bottom half
    draw.rounded_rectangle([cx - w // 2, cy, cx + w // 2, cy + h // 2], radius=w // 2, fill=bottom_color, outline=outline, width=2)
    # Top half
    draw.rounded_rectangle([cx - w // 2, cy - h // 2, cx + w // 2, cy], radius=w // 2, fill=top_color, outline=outline, width=2)
    # Center line
    draw.line([cx - w // 2 + 2, cy, cx + w // 2 - 2, cy], fill=outline, width=2)


def draw_drop(draw, cx, cy, rx, ry, fill, outline):
    """Ve giọt thuốc."""
    # Tam giác bo tròn
    draw.ellipse([cx - rx, cy, cx + rx, cy + ry], fill=fill, outline=outline, width=2)
    draw.polygon([(cx, cy - ry + 4), (cx - rx * 0.7, cy + 4), (cx + rx * 0.7, cy + 4)], fill=fill, outline=outline, width=0)
    draw.ellipse([cx - rx * 0.5, cy + ry * 0.3, cx + rx * 0.5, cy + ry * 0.3 + ry * 0.4], fill=fill, outline=outline, width=0)
    draw.polygon([(cx, cy - ry + 4), (cx - rx * 0.7, cy + 4), (cx + rx * 0.7, cy + 4)], fill=fill)


def draw_bottle(draw, cx, cy, w, h, fill, outline):
    """Ve lo thuoc nuoc."""
    draw.rounded_rectangle([cx - w // 2, cy - h // 2 + 12, cx + w // 2, cy + h // 2], radius=6, fill=fill, outline=outline, width=2)
    draw.rounded_rectangle([cx - w // 4, cy - h // 2, cx + w // 4, cy - h // 2 + 14], radius=3, fill="#cccccc", outline="#999999", width=2)


def draw_rect(draw, cx, cy, w, h, fill, outline, radius=4):
    """Ve hinh chu nhat bo tròn."""
    draw.rounded_rectangle([cx - w // 2, cy - h // 2, cx + w // 2, cy + h // 2], radius=radius, fill=fill, outline=outline, width=2)


# ============================================================================
# 42 ICONS
# ============================================================================

def icon_tablet_round_scored(draw, cx=32, cy=32):
    draw_pill(draw, cx, cy, 22, 22, "#d8eef8", "#3a8fc7", scored=True, scored_v=True)
    draw.ellipse([cx - 16, cy - 16, cx + 16, cy + 16], outline="#a8d4f0", width=1)

def icon_tablet_round_unscored(draw, cx=32, cy=32):
    draw_pill(draw, cx, cy, 22, 22, "#d8eef8", "#3a8fc7")
    draw.ellipse([cx - 16, cy - 16, cx + 16, cy + 16], outline="#a8d4f0", width=1)

def icon_tablet_triangle(draw, cx=32, cy=32):
    draw.polygon([(cx, 8), (56, 54), (8, 54)], fill="#ffe8e8", outline="#c73a3a", width=2)

def icon_tablet_rhombus(draw, cx=32, cy=32):
    draw.polygon([(cx, 6), (58, 32), (cx, 58), (6, 32)], fill="#ffe0a8", outline="#c7883a", width=2)
    draw.line([cx, 6, cx, 58], fill="#c7883a", width=2)

def icon_tablet_caplet_scored(draw, cx=32, cy=32):
    draw.rounded_rectangle([8, 18, 56, 46], radius=14, fill="#d8eef8", outline="#3a8fc7", width=2)
    draw.line([cx, 18, cx, 46], fill="#3a8fc7", width=2)

def icon_tablet_caplet_unscored(draw, cx=32, cy=32):
    draw.rounded_rectangle([8, 18, 56, 46], radius=14, fill="#d8eef8", outline="#3a8fc7", width=2)

def icon_capsule_standard(draw, cx=32, cy=32):
    draw_capsule(draw, cx, cy, 24, 44, "#3a8fc7", "#c73a3a")

def icon_capsule_mono(draw, cx=32, cy=32):
    draw_capsule(draw, cx, cy, 24, 44, "#c73a3a", "#c73a3a")

def icon_capsule_beads(draw, cx=32, cy=32):
    draw_capsule(draw, cx, cy, 24, 44, "#3a8fc7", "#c73a3a")
    # Hạt trắng
    for bx, by in [(22, 24), (28, 22), (38, 25), (26, 38), (35, 40)]:
        draw.ellipse([bx - 3, by - 3, bx + 3, by + 3], fill=(255, 255, 255, 200))

def icon_drop_standard(draw, cx=32, cy=32):
    draw_drop(draw, cx, cy + 8, 10, 20, "#a8d4f0", "#3a8fc7")
    draw.ellipse([cx - 4, cy + 16, cx + 4, cy + 24], fill=(255, 255, 255, 100))

def icon_drop_dropper(draw, cx=32, cy=32):
    draw.rounded_rectangle([25, 4, 39, 30], radius=4, fill="#cccccc", outline="#999999", width=2)
    draw_drop(draw, cx, cy + 14, 12, 22, "#a8d4f0", "#3a8fc7")

def icon_drop_eye_drops(draw, cx=32, cy=32):
    draw.rounded_rectangle([20, 4, 44, 36], radius=4, fill="#4a90d9", outline="#2a6099", width=2)
    draw.rounded_rectangle([20, 4, 44, 14], radius=4, fill="#cccccc", outline="#999999", width=2)
    draw.polygon([(24, 36), (24, 54), (40, 54), (40, 36)], fill="#4a90d9", outline="#2a6099", width=2)

def icon_liquid_standard(draw, cx=32, cy=32):
    draw_bottle(draw, cx, cy, 28, 36, "#a8d4f0", "#3a8fc7")
    draw.rounded_rectangle([25, 6, 39, 20], radius=3, fill="#cccccc", outline="#999999", width=2)

def icon_liquid_bottle_small(draw, cx=32, cy=32):
    draw.rounded_rectangle([18, 18, 46, 56], radius=4, fill="#c8f0c8", outline="#3ac73a", width=2)
    draw.rounded_rectangle([25, 8, 39, 18], radius=3, fill="#cccccc", outline="#999999", width=2)

def icon_creamgel_standard(draw, cx=32, cy=32):
    draw.rounded_rectangle([12, 20, 52, 56], radius=8, fill="#f0e8d0", outline="#c7a83a", width=2)
    draw.rounded_rectangle([22, 8, 42, 20], radius=4, fill="#cccccc", outline="#999999", width=2)

def icon_spray_standard(draw, cx=32, cy=32):
    draw.rounded_rectangle([16, 22, 48, 56], radius=6, fill="#d8f0f8", outline="#3aaac7", width=2)
    draw.rounded_rectangle([24, 8, 40, 22], radius=4, fill="#cccccc", outline="#999999", width=2)
    draw.ellipse([cx - 2, 4, cx + 2, 8], fill="#cccccc", outline="#999999", width=1)
    # Tia xịt
    for tx, ty in [(6, 24), (4, 30), (8, 36)]:
        draw.ellipse([tx - 2, ty - 2, tx + 2, ty + 2], fill="#3aaac7")

def icon_spray_inhaler(draw, cx=32, cy=32):
    draw.rounded_rectangle([14, 12, 50, 56], radius=6, fill="#e8f0e8", outline="#3ac7a8", width=2)
    draw.polygon([(22, 12), (22, 2), (42, 2), (42, 12)], fill="#dddddd", outline="#888888", width=2)
    draw.rounded_rectangle([24, 6, 40, 14], radius=3, fill="#bbbbbb", outline="#888888", width=2)

def icon_injection_standard(draw, cx=32, cy=32):
    draw.rounded_rectangle([27, 4, 37, 44], radius=2, fill="#dddddd", outline="#999999", width=2)
    draw.polygon([(cx, 44), (27, 58), (37, 58)], fill="#bbbbbb", outline="#888888", width=2)
    draw.rounded_rectangle([22, 8, 42, 28], radius=2, fill="#ffffff", outline="#999999", width=2)

def icon_patch_transdermal(draw, cx=32, cy=32):
    draw.rounded_rectangle([6, 18, 58, 46], radius=6, fill="#f8e8d0", outline="#c78a3a", width=2)
    for dotx in [18, 32, 46]:
        draw.ellipse([dotx - 4, 28, dotx + 4, 36], fill="#c78a3a", outline=None)

def icon_patch_cross_bandage(draw, cx=32, cy=32):
    draw.rounded_rectangle([20, 4, 44, 60], radius=4, fill="#ffffff", outline="#cccccc", width=2)
    draw.rounded_rectangle([4, 20, 60, 44], radius=4, fill="#ffffff", outline="#cccccc", width=2)
    for coords in [(28, 8, 36, 16), (28, 48, 36, 56), (8, 26, 16, 34), (48, 26, 56, 34)]:
        draw.line(coords, fill="#e8c8a8", width=3)

def icon_patch_knuckle_bandage(draw, cx=32, cy=32):
    draw.rounded_rectangle([8, 22, 56, 42], radius=10, fill="#ffffff", outline="#cccccc", width=2)
    draw.rounded_rectangle([16, 26, 48, 38], radius=6, fill="#f8e8e8", width=0)

def icon_snack_milk(draw, cx=32, cy=32):
    draw.polygon([(16, 18), (32, 4), (48, 18)], fill="#fff8e8", outline="#c7a83a", width=2)
    draw.rounded_rectangle([16, 18, 48, 56], radius=2, fill="#fff8e8", outline="#c7a83a", width=2)

def icon_snack_soup(draw, cx=32, cy=32):
    draw.ellipse([8, 30, 56, 50], fill="#f8e8d0", outline="#c7a83a", width=2)
    draw.ellipse([14, 34, 50, 46], fill="#f0d090", width=0)
    for bx, by in [(24, 38), (36, 36), (30, 44)]:
        draw.ellipse([bx - 5, by - 4, bx + 5, by + 4], fill="#c8783a")

def icon_snack_dessert(draw, cx=32, cy=32):
    draw.ellipse([10, 28, 54, 52], fill="#f8e0f0", outline="#c73ac7", width=2)
    draw.ellipse([14, 24, 50, 42], fill="#f0d0f0", outline="#c73ac7", width=2)
    draw.ellipse([cx - 7, cy - 3, cx + 7, cy + 7], fill="#e8a0d0", outline="#c73ac7", width=1)

def icon_snack_protein(draw, cx=32, cy=32):
    draw.rounded_rectangle([12, 14, 52, 54], radius=6, fill="#e8f0e8", outline="#3ac73a", width=2)
    draw.rounded_rectangle([18, 8, 46, 14], radius=3, fill="#bbbbbb", outline="#999999", width=2)

def icon_snack_veggie(draw, cx=32, cy=32):
    draw.ellipse([10, 22, 54, 52], fill="#f0f8e8", outline="#7ac73a", width=2)
    for ex, ey, rx, ry in [(22, 28, 7, 10), (38, 26, 6, 9), (28, 42, 9, 5)]:
        draw.ellipse([ex - rx, ey - ry, ex + rx, ey + ry], fill="#80c83a")

def icon_suppository_standard(draw, cx=32, cy=32):
    draw.ellipse([12, 18, 52, 46], fill="#f8f0e0", outline="#c7a83a", width=2)
    draw.arc([12, 18, 52, 46], start=180, end=360, fill="#e8d8a0", width=2)

def icon_eye_drops_multi(draw, cx=32, cy=32):
    draw.rounded_rectangle([14, 14, 50, 54], radius=6, fill="#a8d4f0", outline="#3a8fc7", width=2)
    draw.rounded_rectangle([24, 4, 40, 14], radius=3, fill="#cccccc", outline="#999999", width=2)
    draw.rounded_rectangle([14, 14, 50, 26], radius=6, fill="#3a8fc7", outline="", width=0)
    draw.ellipse([20, 38, 28, 46], fill=(255, 255, 255, 150))
    draw.ellipse([36, 38, 44, 46], fill=(255, 255, 255, 150))

def icon_inhaler_breath(draw, cx=32, cy=32):
    draw.ellipse([12, 24, 52, 48], fill="#e8f0f8", outline="#3a8fc7", width=2)
    draw.rounded_rectangle([26, 6, 38, 30], radius=4, fill="#cccccc", outline="#999999", width=2)
    draw.ellipse([cx - 4, 6, cx + 4, 14], fill="#bbbbbb", outline="#999999", width=1)

def icon_pill_box_daily(draw, cx=32, cy=32):
    draw.rounded_rectangle([8, 14, 56, 54], radius=6, fill="#e8f8e8", outline="#3ac73a", width=2)
    draw.rounded_rectangle([8, 14, 56, 26], radius=6, fill="#3ac73a", outline="", width=0)
    for lx in [20, 32, 44]:
        draw.line([lx, 14, lx, 54], fill="#3ac73a", width=1)
    draw.line([8, 34, 56, 34], fill="#3ac73a", width=1)
    for px, py, pc in [(12, 22, "#c73a3a"), (44, 22, "#3a8fc7"), (12, 44, "#c7a83a"), (44, 44, "#3ac73a")]:
        draw.ellipse([px - 4, py - 4, px + 4, py + 4], fill=pc)

def icon_syrup_standard(draw, cx=32, cy=32):
    draw.polygon([(20, 20), (18, 52), (46, 52), (44, 20)], fill="#f0e8e8", outline="#c73a3a", width=2)
    draw.rounded_rectangle([22, 6, 42, 20], radius=4, fill="#cccccc", outline="#999999", width=2)

def icon_powder_sachet(draw, cx=32, cy=32):
    draw.rounded_rectangle([10, 14, 54, 54], radius=4, fill="#f8f0e8", outline="#c7a83a", width=2)
    draw.line([10, 24, 54, 24], fill="#c7a83a", width=1)

def icon_lozenge_standard(draw, cx=32, cy=32):
    draw.ellipse([8, 16, 56, 48], fill="#f8e8e8", outline="#c73a3a", width=2)
    draw.ellipse([14, 21, 50, 43], outline="#f0a8a8", width=1)

def icon_vitamin_complex(draw, cx=32, cy=32):
    draw.ellipse([12, 16, 32, 40], fill="#ffe8a8", outline="#c7a83a", width=2)
    draw.ellipse([32, 16, 52, 40], fill="#f8e8a8", outline="#c7a83a", width=2)
    draw.ellipse([18, 36, 46, 52], fill="#e8f8e8", outline="#3ac73a", width=2)
    draw.text((20, 24), "A", fill="#c7a83a")
    draw.text((40, 24), "B", fill="#c7a83a")
    draw.text((28, 41), "C", fill="#3ac73a")

def icon_herbal_leaf(draw, cx=32, cy=32):
    draw.ellipse([8, 4, 56, 60], fill="#a8e8a8", outline="#3ac73a", width=2)
    draw.line([cx, 8, cx, 56], fill="#3ac73a", width=1)
    for coords in [(cx, 18, 20, 24), (cx, 28, 22, 34), (cx, 38, 24, 42), (cx, 18, 44, 24), (cx, 28, 42, 34), (cx, 38, 40, 42)]:
        draw.line(coords, fill="#3ac73a", width=1)

def icon_insulin_pen(draw, cx=32, cy=32):
    draw.rounded_rectangle([22, 6, 42, 56], radius=6, fill="#e8f0f8", outline="#3a8fc7", width=2)
    draw.rounded_rectangle([22, 6, 42, 18], radius=6, fill="#3a8fc7", outline="", width=0)
    draw.line([22, 28, 42, 28], fill="#3a8fc7", width=2)
    draw.rounded_rectangle([22, 32, 42, 48], radius=2, fill="#3a8fc7", outline="", width=0)
    draw.rounded_rectangle([26, 56, 38, 60], radius=1, fill="#bbbbbb", outline="#999999", width=1)

def icon_ear_drops(draw, cx=32, cy=32):
    draw.rounded_rectangle([24, 4, 40, 24], radius=4, fill="#cccccc", outline="#999999", width=2)
    draw.polygon([(28, 24), (28, 40), (36, 40), (36, 24)], fill="#f0e8d0", outline="#c7a83a", width=2)
    draw.ellipse([22, 42, 42, 54], fill="#f0e8d0", outline="#c7a83a", width=2)

def icon_nose_spray(draw, cx=32, cy=32):
    draw.rounded_rectangle([22, 14, 42, 54], radius=4, fill="#e8f8f8", outline="#3a8fc7", width=2)
    draw.rounded_rectangle([26, 4, 38, 16], radius=3, fill="#cccccc", outline="#999999", width=2)
    draw.polygon([(30, 54), (26, 60), (38, 60), (34, 54)], fill="#cccccc", outline="#999999", width=2)
    draw.rounded_rectangle([26, 28, 38, 44], radius=2, fill="#3a8fc7", outline="", width=0)

def icon_thermometer(draw, cx=32, cy=32):
    draw.rounded_rectangle([27, 6, 37, 50], radius=5, fill="#f8e8e8", outline="#c73a3a", width=2)
    draw.ellipse([cx - 5, 50, cx + 5, 60], fill="#f8e8e8", outline="#c73a3a", width=2)
    draw.rounded_rectangle([28, 18, 36, 46], radius=4, fill="#c73a3a", outline="", width=0)

def icon_blood_pressure(draw, cx=32, cy=32):
    draw.ellipse([14, 6, 50, 30], fill="#e8f0f8", outline="#3a8fc7", width=2)
    draw.rounded_rectangle([14, 28, 50, 54], radius=4, fill="#e8f0f8", outline="#3a8fc7", width=2)
    draw.rounded_rectangle([18, 32, 46, 48], radius=2, fill="#3a8fc7", outline="", width=0)

def icon_glucose_meter(draw, cx=32, cy=32):
    draw.rounded_rectangle([14, 8, 50, 58], radius=6, fill="#e8f8e8", outline="#3ac73a", width=2)
    draw.rounded_rectangle([18, 14, 46, 34], radius=3, fill="#3ac73a", outline="", width=0)

def icon_first_aid_kit(draw, cx=32, cy=32):
    draw.rounded_rectangle([8, 16, 56, 54], radius=6, fill="#f8e8e8", outline="#c73a3a", width=3)
    draw.rounded_rectangle([28, 10, 36, 18], radius=2, fill="#c73a3a", outline="#a02020", width=2)
    draw.rounded_rectangle([26, 28, 38, 42], radius=2, fill="#c73a3a", outline="", width=0)
    draw.line([cx, 30, cx, 40], fill="white", width=2)
    draw.line([29, 34, 35, 34], fill="white", width=2)


# ============================================================================
# REGISTRY - map tên icon → hàm vẽ
# ============================================================================

ICON_DRAWERS = {
    "tablet_round_scored": icon_tablet_round_scored,
    "tablet_round_unscored": icon_tablet_round_unscored,
    "tablet_triangle": icon_tablet_triangle,
    "tablet_rhombus": icon_tablet_rhombus,
    "tablet_caplet_scored": icon_tablet_caplet_scored,
    "tablet_caplet_unscored": icon_tablet_caplet_unscored,
    "capsule_standard": icon_capsule_standard,
    "capsule_mono": icon_capsule_mono,
    "capsule_beads": icon_capsule_beads,
    "drop_standard": icon_drop_standard,
    "drop_dropper": icon_drop_dropper,
    "drop_eye_drops": icon_drop_eye_drops,
    "liquid_standard": icon_liquid_standard,
    "liquid_bottle_small": icon_liquid_bottle_small,
    "creamgel_standard": icon_creamgel_standard,
    "spray_standard": icon_spray_standard,
    "spray_inhaler": icon_spray_inhaler,
    "injection_standard": icon_injection_standard,
    "patch_transdermal": icon_patch_transdermal,
    "patch_cross_bandage": icon_patch_cross_bandage,
    "patch_knuckle_bandage": icon_patch_knuckle_bandage,
    "snack_milk": icon_snack_milk,
    "snack_soup": icon_snack_soup,
    "snack_dessert": icon_snack_dessert,
    "snack_protein": icon_snack_protein,
    "snack_veggie": icon_snack_veggie,
    "suppository_standard": icon_suppository_standard,
    "eye_drops_multi": icon_eye_drops_multi,
    "inhaler_breath": icon_inhaler_breath,
    "pill_box_daily": icon_pill_box_daily,
    "syrup_standard": icon_syrup_standard,
    "powder_sachet": icon_powder_sachet,
    "lozenge_standard": icon_lozenge_standard,
    "vitamin_complex": icon_vitamin_complex,
    "herbal_leaf": icon_herbal_leaf,
    "insulin_pen": icon_insulin_pen,
    "ear_drops": icon_ear_drops,
    "nose_spray": icon_nose_spray,
    "thermometer": icon_thermometer,
    "blood_pressure": icon_blood_pressure,
    "glucose_meter": icon_glucose_meter,
    "first_aid_kit": icon_first_aid_kit,
}


def paint_icon(name: str) -> bool:
    """Vẽ một icon và lưu thành PNG."""
    if name not in ICON_DRAWERS:
        return False
    try:
        img = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        ICON_DRAWERS[name](draw)
        png_path = os.path.join(PNG_DIR, f"{name}.png")
        img.save(png_path)
        return True
    except Exception as e:
        print(f"[IconPainter] Loi ve {name}: {e}")
        return False


def paint_all():
    """Vẽ tất cả icon."""
    count = 0
    for name in ICON_DRAWERS:
        if paint_icon(name):
            count += 1
    print(f"[IconPainter] Da ve {count}/{len(ICON_DRAWERS)} icons PNG tai: {PNG_DIR}")
    return count


if __name__ == "__main__":
    paint_all()
