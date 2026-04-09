"""
==============================================================================
Lệnh Admin - Test và Debug ứng dụng MedReminder
==============================================================================
File: admin_commands.py

Cách dùng:
    python admin_commands.py <command> [args]

Lệnh:
    python admin_commands.py date              # Hiển thị ngày giờ app đang dùng
    python admin_commands.py set-date "08/04/2026 10:30:00"  # Đặt ngày giờ
    python admin_commands.py reset-date        # Reset về ngày hệ thống
    python admin_commands.py gen-image         # Tạo ảnh đơn thuốc giả lập
    python admin_commands.py show-image       # Mở ảnh đơn thuốc đã tạo
    python admin_commands.py run-app          # Chạy ứng dụng
    python admin_commands.py clear-cache      # Xóa ảnh cache
    python admin_commands.py help             # Hiển thị trợ giúp
==============================================================================
"""

import os
import sys
import datetime
import subprocess

# Thêm thư mục app vào path
APP_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, APP_DIR)

import app_datetime as _app_dt


# ============================================================================
# CÁC LỆNH ADMIN
# ============================================================================

def cmd_date():
    """Hiển thị ngày giờ hiện tại của app."""
    now = _app_dt.get_app_now()
    system_now = datetime.datetime.now()
    is_custom = _app_dt.is_datetime_custom()

    print("=" * 55)
    print("  NGAY GIO CUA APP - MEDREMINDER")
    print("=" * 55)
    print(f"  App dang dung:  {now.strftime('%d/%m/%Y  %H:%M:%S')}")
    print(f"  He thong:       {system_now.strftime('%d/%m/%Y  %H:%M:%S')}")
    print(f"  Che do:         {'TUY CHINH' if is_custom else 'MAC DINH (HE THONG)'}")
    print("=" * 55)


def cmd_set_date(args: list):
    """Đặt ngày giờ cho app."""
    if not args:
        print("[LOI] Thieu tham so ngay.")
        print('Dinh dang: python admin_commands.py set-date "08/04/2026 10:30:00"')
        print()
        print("Format ho tro:")
        print('  "08/04/2026 10:30:00"   (ngay/thang/nam  gio:phut:giay)')
        print('  "08/04/2026 10:30"        (ngay/thang/nam  gio:phut)')
        print('  "08/04/2026"             (ngay/thang/nam)')
        print('  "2026-04-08 10:30:00"    (nam-thang-ngay  gio:phut:giay)')
        return

    date_str = " ".join(args)
    if _app_dt.set_app_datetime(date_str):
        new_dt = _app_dt.get_app_now()
        print(f"[OK] Da dat ngay gio app thanh: {new_dt.strftime('%d/%m/%Y  %H:%M:%S')}")
    else:
        print(f"[LOI] Khong the parse ngay: '{date_str}'")
        print("Format ho tro:")
        print('  "08/04/2026 10:30:00"   (ngay/thang/nam  gio:phut:giay)')
        print('  "08/04/2026 10:30"        (ngay/thang/nam  gio:phut)')
        print('  "08/04/2026"             (ngay/thang/nam)')
        print('  "2026-04-08 10:30:00"    (nam-thang-ngay  gio:phut:giay)')


def cmd_reset_date():
    """Reset ngày giờ về ngày hệ thống."""
    _app_dt.reset_app_datetime()
    print("[OK] Da reset ve ngay gio he thong.")


def cmd_gen_image():
    """Tạo ảnh đơn thuốc giả lập (bỏ qua cache)."""
    print("[...] Dang tao anh don thuoc (force=True)...")
    try:
        from data.prescription_image import create_prescription_image
        path = create_prescription_image(force=True)
        print(f"[OK] Da tao anh: {path}")
    except Exception as e:
        print(f"[LOI] Khong the tao anh: {e}")


def cmd_show_image():
    """Hiển thị thông tin ảnh đơn thuốc."""
    try:
        from data.prescription_image import get_prescription_image_path
        path = get_prescription_image_path()
        if os.path.exists(path):
            size_kb = os.path.getsize(path) // 1024
            print(f"[OK] Anh don thuoc: {path}")
            print(f"     Kich thuoc: {size_kb} KB")
            print(f"     Trang thai: DA CO (tu cache)")
            # Mở ảnh bằng trình xem mặc định
            try:
                os.startfile(path)
                print("     [Da mo bang trinh xem mac dinh]")
            except Exception:
                pass
        else:
            print(f"[LOI] Anh chua ton tai. Chay 'gen-image' truoc.")
    except Exception as e:
        print(f"[LOI] {e}")


def cmd_clear_cache():
    """Xóa ảnh đơn thuốc đã cache."""
    try:
        from data.prescription_image import clear_prescription_cache
        clear_prescription_cache()
    except Exception as e:
        print(f"[LOI] {e}")


def cmd_run_app():
    """Chạy ứng dụng MedReminder."""
    main_path = os.path.join(APP_DIR, "main.py")
    if not os.path.exists(main_path):
        print(f"[LOI] Khong tim thay main.py tai: {main_path}")
        return
    print("[...] Dang chay ung dung MedReminder...")
    subprocess.run([sys.executable, main_path], cwd=APP_DIR)


def cmd_help():
    """Hiển thị trợ giúp."""
    print("""
================================================================================
  LENH ADMIN - MEDREMINDER
================================================================================

  Cach dung:  python admin_commands.py <command> [args]

  LENH NGAY GIO:
    date              Hien thi ngay gio hien tai cua app
    set-date <str>    Dat ngay gio tuy chinh cho app (de test alarm)
    reset-date        Reset ngay gio ve ngay he thong

  LENH ANH:
    gen-image         Tao anh don thuoc gia lap (bo qua cache, tao lai)
    show-image        Hien thi thong tin + mo anh
    clear-cache       Xoa anh da cache

  LENH CHUNG:
    run-app           Chay ung dung MedReminder
    help              Hien thi tro giup nay

================================================================================
  VI DU TEST ALARM:
================================================================================
  # Buoc 1: Kiem tra ngay gio hien tai
  python admin_commands.py date

  # Buoc 2: Dat gio muon test (vi du trigger alarm 07:00)
  python admin_commands.py set-date "08/04/2026 06:59:00"

  # Buoc 3: Chay app -> alarm se trigger o 07:00
  python admin_commands.py run-app

  # Reset ve binh thuong
  python admin_commands.py reset-date

================================================================================
  VI DU TEST ẢNH:
================================================================================
  # Tao anh (lan dau hoac tao lai)
  python admin_commands.py gen-image

  # Mo xem anh
  python admin_commands.py show-image

  # Xoa cache -> lan sau se tao lai
  python admin_commands.py clear-cache
================================================================================
""")


# ============================================================================
# ĐIỂM VÀO CHÍNH
# ============================================================================
COMMANDS = {
    "date":        (cmd_date,       "Hien thi ngay gio app"),
    "set-date":    (cmd_set_date,   "Dat ngay gio app"),
    "reset-date":  (cmd_reset_date, "Reset ve ngay he thong"),
    "gen-image":   (cmd_gen_image,  "Tao anh don thuoc (force)"),
    "show-image":  (cmd_show_image, "Hien thi thong tin anh"),
    "clear-cache": (cmd_clear_cache, "Xoa anh cache"),
    "run-app":     (cmd_run_app,    "Chay ung dung"),
    "help":        (cmd_help,       "Hien thi tro giup"),
}


def main():
    if len(sys.argv) < 2:
        cmd_date()
        print()
        cmd_help()
        return

    cmd = sys.argv[1].lower()

    if cmd not in COMMANDS:
        print(f"[LOI] Lenh khong ton tai: '{cmd}'")
        print("Go 'python admin_commands.py help' de xem danh sach lenh.")
        return

    func, _ = COMMANDS[cmd]

    if cmd == "set-date":
        func(sys.argv[2:])
    elif cmd == "help":
        func()
    else:
        func()


if __name__ == "__main__":
    main()
