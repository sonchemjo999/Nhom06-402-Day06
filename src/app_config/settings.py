"""
==============================================================================
App Settings - Lưu trữ cài đặt ứng dụng (JSON file)
==============================================================================
File: app_settings.py

Lưu trữ:
    - Dark Mode: True/False
    - Âm thanh báo thức: True/False
    - Rung khi báo thức: True/False
    - File: .app_settings.json cùng thư mục main.py
"""

import os
import json

_FILE_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    ".app_settings.json"
)

_DEFAULT_SETTINGS = {
    "dark_mode": False,
    "sound_enabled": True,
    "vibration_enabled": True,
    "alarm_sound_file": "pills.mp3",
}


def _read() -> dict:
    """Đọc settings từ file JSON."""
    if not os.path.exists(_FILE_PATH):
        return _DEFAULT_SETTINGS.copy()
    try:
        with open(_FILE_PATH, "r", encoding="utf-8") as f:
            return {**_DEFAULT_SETTINGS, **json.load(f)}
    except Exception:
        return _DEFAULT_SETTINGS.copy()


def _write(data: dict):
    """Ghi settings ra file JSON — flush + fsync để Windows đảm bảo ghi đĩa."""
    try:
        with open(_FILE_PATH, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
            f.flush()
            os.fsync(f.fileno())
    except Exception as e:
        print(f"[AppSettings] Lỗi ghi settings: {e}")


def get_dark_mode() -> bool:
    return _read().get("dark_mode", False)


def set_dark_mode(value: bool):
    data = _read()
    data["dark_mode"] = bool(value)
    _write(data)


def get_sound_enabled() -> bool:
    return _read().get("sound_enabled", True)


def set_sound_enabled(value: bool):
    data = _read()
    data["sound_enabled"] = bool(value)
    _write(data)


def get_vibration_enabled() -> bool:
    return _read().get("vibration_enabled", True)


def set_vibration_enabled(value: bool):
    data = _read()
    data["vibration_enabled"] = bool(value)
    _write(data)


def get_all() -> dict:
    return _read()


def get_alarm_sound_file() -> str:
    fn = _read().get("alarm_sound_file") or "pills.mp3"
    if not fn.lower().endswith(".mp3"):
        fn = "pills.mp3"
    return fn


def set_alarm_sound_file(filename: str):
    from sound_manager import list_mp3_files, DEFAULT_ALARM_SOUND
    fn = str(filename).strip()
    allowed = list_mp3_files()
    if fn not in allowed:
        fn = DEFAULT_ALARM_SOUND if DEFAULT_ALARM_SOUND in allowed else (allowed[0] if allowed else "pills.mp3")
    data = _read()
    data["alarm_sound_file"] = fn
    _write(data)
