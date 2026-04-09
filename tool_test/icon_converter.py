"""
==============================================================================
 Icon Converter - Chuyển SVG → PNG để hiển thị trong Kivy
==============================================================================
 File: icon_converter.py

 Kivy không hỗ trợ SVG trực tiếp.
 Script này chuyển SVG → PNG để MedCard có thể hiển thị icon.

 Chạy: python icon_converter.py
 Output: assets/icons/medications_png/*.png
==============================================================================
"""

import os
import sys

# Cài đặt cairoly nếu chưa có
try:
    import cairosvg
except ImportError:
    print("[IconConverter] Dang cai dat cairosvg...")
    os.system(f'"{sys.executable}" -m pip install cairosvg pillow -q')
    import cairosvg

_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ICONS_DIR = os.path.join(_PROJECT_ROOT, "assets", "icons", "medications")
PNG_DIR = os.path.join(_PROJECT_ROOT, "assets", "icons", "medications_png")
os.makedirs(PNG_DIR, exist_ok=True)


def svg_to_png(svg_path: str, png_path: str, size: int = 64):
    """Chuyển một file SVG sang PNG."""
    try:
        cairosvg.svg2png(url=svg_path, write_to=png_path, output_width=size, output_height=size)
        return True
    except Exception as e:
        print(f"[IconConverter] Loi chuyen {svg_path}: {e}")
        return False


def convert_all():
    """Chuyển tất cả SVG trong thư mục icons sang PNG."""
    if not os.path.exists(ICONS_DIR):
        print(f"[IconConverter] Khong tim thay thu muc: {ICONS_DIR}")
        return 0

    files = [f for f in os.listdir(ICONS_DIR) if f.endswith(".svg")]
    if not files:
        print(f"[IconConverter] Khong co file SVG nao trong: {ICONS_DIR}")
        return 0

    count = 0
    for f in files:
        svg_path = os.path.join(ICONS_DIR, f)
        png_name = f[:-4] + ".png"  # .svg → .png
        png_path = os.path.join(PNG_DIR, png_name)
        if svg_to_png(svg_path, png_path):
            count += 1

    print(f"[IconConverter] Da chuyen {count}/{len(files)} SVG → PNG tai: {PNG_DIR}")
    return count


if __name__ == "__main__":
    convert_all()
