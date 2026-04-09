"""
==============================================================================
Hình ảnh giả lập đơn thuốc chữ viết tay - phiên bản rõ ràng
==============================================================================
File: data/prescription_image.py

Mô tả:
    Tạo và cache ảnh giả lập đơn thuốc với phong cách chữ viết tay bác sĩ.
    Điểm khác biệt:
      - DPI cao (300 DPI) để ảnh sắc nét khi AI đọc
      - Font Times New Roman Bold (font đậm) cho chữ rõ ràng
      - Nền trắng sáng, chữ đen đậm, độ tương phản cao
      - Mã hóa UTF-8 rõ ràng cho tiếng Việt có dấu

Cache:
    Ảnh được lưu tại assets/prescription_handwritten.png
    Các lần sau: kiểm tra tồn tại → dùng ngay → bỏ qua bước tạo
    Để tạo lại: xóa file ảnh hoặc gọi create_prescription_image(force=True)
==============================================================================
"""

import os

# Đường dẫn lưu ảnh
_ASSETS_DIR = os.path.join(os.path.dirname(__file__), "..", "assets")
_PRESCRIPTION_PATH = os.path.join(_ASSETS_DIR, "prescription_handwritten.png")


def _try_load_font(size: int, bold: bool = False):
    """
    Thử tải font chữ với độ đậm tùy chọn.
    Ưu tiên Times New Roman Bold để chữ rõ ràng, sắc nét.
    """
    # Font paths có độ đậm khác nhau
    if bold:
        font_paths = [
            "C:\\Windows\\Fonts\\timesbd.ttf",    # Times New Roman Bold
            "C:\\Windows\\Fonts\\TIMESBD.TTF",
            "C:\\Windows\\Fonts\\times.ttf",        # Fallback: Times thường
            "C:\\Windows\\Fonts\\TIMES.TTF",
            "C:\\Windows\\Fonts\\ARIALBD.TTF",     # Arial Bold
            "C:\\Windows\\Fonts\\CAMBRIAB.TTF",    # Cambria Bold
            "C:\\Windows\\Fonts\\calibrib.ttf",    # Calibri Bold
            "C:\\Windows\\Fonts\\CALIBRIL.TTF",
        ]
    else:
        font_paths = [
            "C:\\Windows\\Fonts\\times.ttf",
            "C:\\Windows\\Fonts\\TIMES.TTF",
            "C:\\Windows\\Fonts\\ARIAL.TTF",
            "C:\\Windows\\Fonts\\CAMBRIAB.TTF",
            "C:\\Windows\\Fonts\\calibri.ttf",
        ]

    for path in font_paths:
        try:
            from PIL import ImageFont
            return ImageFont.truetype(path, size)
        except Exception:
            pass

    # Font mặc định hệ thống
    try:
        from PIL import ImageFont
        return ImageFont.load_default()
    except Exception:
        return None


def _draw_prescription(draw, img_width: int, img_height: int):
    """
    Vẽ nội dung đơn thuốc lên đối tượng ImageDraw.
    Sử dụng font đậm, DPI cao để chữ sắc nét.
    """
    # Font đậm cho nội dung chính
    font_title = _try_load_font(32, bold=True)
    font_header = _try_load_font(20, bold=True)
    font_body = _try_load_font(19, bold=True)
    font_small = _try_load_font(17, bold=True)
    font_signature = _try_load_font(22, bold=True)
    font_note = _try_load_font(16, bold=True)
    font_label = _try_load_font(15, bold=True)

    y = 30  # Vị trí y hiện tại

    # === 1. Header: Tên phòng khám ===
    draw.text((img_width // 2, y),
              "PHONG KHAM DAI KHOA VINMEC TIMES CITY",
              font=font_header, fill="#0D2B4E", anchor="mt")
    y += 30

    draw.text((img_width // 2, y),
              "458 Minh Khai, Hai Ba Trung, Ha Noi",
              font=font_note, fill="#444444", anchor="mt")
    y += 24

    draw.text((img_width // 2, y),
              "Hotline: 024 3974 3556",
              font=font_note, fill="#444444", anchor="mt")
    y += 35

    # === 2. Đường kẻ ngang đậm ===
    draw.line([(40, y), (img_width - 40, y)], fill="#0D2B4E", width=3)
    y += 18

    # === 3. Thông tin bác sĩ và bệnh nhân ===
    draw.text((60, y),
              "Bac si: TS.BS Nguyen Van An",
              font=font_label, fill="#111111")
    draw.text((img_width - 60, y), "Ngay ke: 08/04/2026",
              font=font_label, fill="#111111", anchor="rt")
    y += 26

    draw.text((60, y),
              "Benh nhan: Tran Thi Binh (Nu, 45 tuoi)",
              font=font_label, fill="#111111")
    draw.text((img_width - 60, y), "Ma BN: VNM-2026-00462",
              font=font_label, fill="#111111", anchor="rt")
    y += 26

    draw.text((60, y),
              "Chan doan: Viem hong cap, sot nhe",
              font=font_label, fill="#111111")
    y += 32

    # === 4. Đường kẻ ngang ===
    draw.line([(40, y), (img_width - 40, y)], fill="#0D2B4E", width=2)
    y += 20

    # === 5. Tiêu đề ĐƠN THUỐC ===
    draw.text((img_width // 2, y), "DON THUOC",
              font=font_title, fill="#8B0000", anchor="mt")
    y += 38

    # === 6. Danh sách thuốc ===
    # ---- Thuốc 1: Paracetamol ----
    draw.text((60, y), "1.", font=font_body, fill="#000000")
    draw.text((90, y), "Paracetamol 500mg",
              font=font_body, fill="#000000")
    y += 28

    draw.text((90, y), "Uong 1 vien x 3 lan/ngay",
              font=font_small, fill="#333333")
    y += 24

    draw.text((90, y), "   Sang 7h, Trua 13h, Toi 19h - Sau an",
              font=font_small, fill="#444444")
    y += 24

    draw.text((90, y), "   Thoi gian: 5 ngay",
              font=font_small, fill="#555555")
    y += 38

    # ---- Thuốc 2: Amoxicillin ----
    draw.text((60, y), "2.", font=font_body, fill="#000000")
    draw.text((90, y), "Amoxicillin 500mg",
              font=font_body, fill="#000000")
    y += 28

    draw.text((90, y), "Uong 1 vien x 2 lan/ngay",
              font=font_small, fill="#333333")
    y += 24

    draw.text((90, y), "   Sang 8h, Toi 20h - Sau an 1 tieng",
              font=font_small, fill="#444444")
    y += 24

    draw.text((90, y), "   Thoi gian: 7 ngay",
              font=font_small, fill="#555555")
    y += 38

    # ---- Thuốc 3: Vitamin C ----
    draw.text((60, y), "3.", font=font_body, fill="#000000")
    draw.text((90, y), "Vitamin C 1000mg (vien sui)",
              font=font_body, fill="#000000")
    y += 28

    draw.text((90, y), "Uong 1 vien x 1 lan/ngay",
              font=font_small, fill="#333333")
    y += 24

    draw.text((90, y), "   Sang 9h - Hoa nuoc",
              font=font_small, fill="#444444")
    y += 24

    draw.text((90, y), "   Thoi gian: 10 ngay",
              font=font_small, fill="#555555")
    y += 42

    # === 7. Lưu ý ===
    draw.line([(40, y), (img_width - 40, y)], fill="#AAAAAA", width=1)
    y += 16

    draw.text((60, y), "Luu y:",
              font=font_label, fill="#8B4513")
    y += 24

    notes = [
        "   - Uong du nuoc, nghi ngoi",
        "   - Tai kham sau 5 ngay neu trieu chung khong giam",
        "   - Trai thuc an, khong uong ruou",
    ]
    for note in notes:
        draw.text((60, y), note, font=font_note, fill="#555555")
        y += 24

    y += 32

    # === 8. Chữ ký bác sĩ ===
    draw.line([(img_width - 200, y + 35), (img_width - 60, y + 35)],
              fill="#000000", width=2)
    draw.text((img_width - 130, y + 45), "Ky ten BS",
              font=font_note, fill="#555555", anchor="mt")
    draw.text((img_width - 130, y),
              "TS.BS Nguyen Van An",
              font=font_signature, fill="#000000", anchor="mt")

    # === 9. Đóng dấu "DA KE DON" ===
    draw.ellipse([(img_width - 185, img_height - 135),
                  (img_width - 60, img_height - 50)],
                 outline="#CC0000", width=4)
    draw.text((img_width - 122, img_height - 95), "DA KE",
              font=font_label, fill="#CC0000", anchor="mt")
    draw.text((img_width - 122, img_height - 75), "DON",
              font=font_label, fill="#CC0000", anchor="mt")

    # === 10. Đường viền giấy ===
    draw.rectangle([(5, 5), (img_width - 5, img_height - 5)],
                   outline="#AAAAAA", width=2)


def create_prescription_image(force: bool = False) -> str:
    """
    Tao anh gia lap don thuoc chu viet tay - PHIEN BAN ROI RAC.

    Thay doi (so voi phien ban cu):
      - DPI cao (300 DPI) de anh sac net khi AI doc
      - Font Times New Roman Bold cho chu roi rang
      - Size lon hon (800x1050) de AI de dang nhan dien

    Cache:
        Neu anh da ton tai tai assets/prescription_handwritten.png
        → tra ve duong dan ngay, KHONG tao lai.
        De tao lai: goi create_prescription_image(force=True)
        Hoac xoa file anh bang tay.

    Tham so:
        force: True = bo qua cache, tao lai anh moi
               False = kiem tra cache truoc (mac dinh)

    Tra ve:
        Duong dan den anh da tao / da cache.
    """
    # Kiem tra cache: neu anh da ton tai → dung luon
    if not force and os.path.exists(_PRESCRIPTION_PATH):
        return _PRESCRIPTION_PATH

    # Dam bao thu muc assets ton tai
    os.makedirs(_ASSETS_DIR, exist_ok=True)

    # Kich thuoc anh lon hon, DPI cao hon
    img_width = 800
    img_height = 1050

    from PIL import Image, ImageDraw

    img = Image.new("RGB", (img_width, img_height), color="#FFFFFF")
    draw = ImageDraw.Draw(img)

    _draw_prescription(draw, img_width, img_height)

    # Luu voi DPI cao (300 DPI) de AI doc duoc ro rang
    img.save(_PRESCRIPTION_PATH, "PNG", quality=95, dpi=(300, 300))
    return _PRESCRIPTION_PATH


def get_prescription_image_path() -> str:
    """
    Tra ve duong dan anh don thuoc.
    Tu dong tao anh neu chua co (dung cache).

    Tra ve:
        Duong dan den anh da tao / da cache.
    """
    return create_prescription_image(force=False)


def clear_prescription_cache():
    """
    Xoa anh don thuoc da cache.
    Lan goi tiep theo se tao anh moi.
    """
    if os.path.exists(_PRESCRIPTION_PATH):
        os.remove(_PRESCRIPTION_PATH)
        print(f"[OK] Da xoa anh cache: {_PRESCRIPTION_PATH}")
    else:
        print(f"[INFO] Khong co anh de xoa.")


if __name__ == "__main__":
    path = create_prescription_image(force=True)
    print(f"[Prescription Image] Da tao: {path}")
