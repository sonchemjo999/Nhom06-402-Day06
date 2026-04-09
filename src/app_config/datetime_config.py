"""
==============================================================================
App Datetime - Quản lý ngày giờ của ứng dụng
==============================================================================
File: app_datetime.py

Mô tả:
    Quản lý ngày giờ của app để test alarm.
    - Mặc định: dùng ngày giờ hệ thống
    - Admin có thể set ngày giờ tùy chỉnh để test alarm ở các mốc khác
    - Ngày giờ tùy chỉnh được LƯU VÀO FILE vào/ra app

Cách dùng:
    from app_datetime import get_app_now, set_app_datetime, reset_app_datetime

    now = get_app_now()           # datetime object
    set_app_datetime("08/04/2026 07:00:00")  # Lưu file
    reset_app_datetime()          # Xóa file
==============================================================================
"""

import os
import time as _time
import datetime as _datetime

# ============================================================================
# FILE LƯU TRỮ: Lưu ngày giờ tùy chỉnh giữa các lần chạy
# ============================================================================
# File nằm cùng thư mục với main.py
_FILE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".app_datetime")

# Khi có override: neo thời gian ảo tại lần đọc đầu + cộng dồn giây thực (time.time)
# → đồng hồ app vẫn “chạy” giống timenow, không bị đứng im
_anchor_virtual: _datetime.datetime | None = None
_anchor_monotonic: float | None = None


def _read_override() -> _datetime.datetime:
    """Đọc ngày giờ từ file cache. Trả về None nếu chưa set."""
    if not os.path.exists(_FILE_PATH):
        return None
    try:
        with open(_FILE_PATH, "r", encoding="utf-8") as f:
            content = f.read().strip()
        if not content:
            return None
        # Thử nhiều format
        for fmt in ["%d/%m/%Y %H:%M:%S", "%d/%m/%Y %H:%M", "%d/%m/%Y",
                    "%Y-%m-%d %H:%M:%S", "%Y-%m-%d"]:
            try:
                return _datetime.datetime.strptime(content, fmt)
            except ValueError:
                continue
        return None
    except Exception:
        return None


def _write_override(dt: _datetime.datetime):
    """Ghi ngày giờ vào file cache."""
    try:
        with open(_FILE_PATH, "w", encoding="utf-8") as f:
            f.write(dt.strftime("%d/%m/%Y %H:%M:%S"))
    except Exception as e:
        print(f"[WARN] Khong the ghi file datetime: {e}")


def _clear_override_file():
    """Xóa file cache."""
    if os.path.exists(_FILE_PATH):
        try:
            os.remove(_FILE_PATH)
        except Exception:
            pass


# ============================================================================
# HÀM CHÍNH
# ============================================================================

def _reset_time_anchor():
    """Xóa neo thời gian (gọi khi reset override hoặc đổi file)."""
    global _anchor_virtual, _anchor_monotonic
    _anchor_virtual = None
    _anchor_monotonic = None


def get_app_now() -> _datetime.datetime:
    """
    Lấy ngày giờ hiện tại của app.

    - Không có file .app_datetime: dùng datetime.now() (thời gian thật, luôn tăng).
    - Có file: lấy mốc ảo trong file, rồi cộng thêm thời gian thực đã trôi qua
      kể từ lần đọc đầu tiên trong tiến trình → đồng hồ vẫn chạy từng giây.

    Returns:
        datetime: Ngày giờ hiện tại của app.
    """
    global _anchor_virtual, _anchor_monotonic
    cached = _read_override()
    if cached is None:
        _reset_time_anchor()
        return _datetime.datetime.now()
    if _anchor_virtual is None:
        _anchor_virtual = cached
        _anchor_monotonic = _time.time()
    elapsed = _time.time() - _anchor_monotonic
    return _anchor_virtual + _datetime.timedelta(seconds=elapsed)


def set_app_datetime(date_str: str) -> bool:
    """
    Đặt ngày giờ tùy chỉnh cho app và LƯU VÀO FILE.
    Giá trị này sẽ được dùng khi app khởi chạy (qua nhiều lần chạy).

    Format hỗ trợ:
        "08/04/2026 10:30:00"   -> ngày/tháng/năm giờ:phút:giây
        "08/04/2026 10:30"      -> ngày/tháng/năm giờ:phút
        "08/04/2026"            -> ngày/tháng/năm (giờ mặc định 00:00:00)
        "2026-04-08 10:30:00"   -> năm-tháng-ngày giờ:phút:giây
        "2026-04-08"            -> năm-tháng-ngày (giờ mặc định 00:00:00)

    Returns:
        True nếu parse thành công, False nếu thất bại
    """
    formats = [
        "%d/%m/%Y %H:%M:%S",
        "%d/%m/%Y %H:%M",
        "%d/%m/%Y",
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d",
    ]

    for fmt in formats:
        try:
            dt = _datetime.datetime.strptime(date_str.strip(), fmt)
            _write_override(dt)
            _reset_time_anchor()
            return True
        except ValueError:
            continue

    return False


def reset_app_datetime():
    """
    Reset ngày giờ về ngày hệ thống.
    Xóa file cache để app dùng ngày thực.
    """
    _clear_override_file()
    _reset_time_anchor()


def is_datetime_custom() -> bool:
    """Kiểm tra xem app có đang dùng ngày tùy chỉnh không."""
    return _read_override() is not None
