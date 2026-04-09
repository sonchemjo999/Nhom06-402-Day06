"""
Sound Manager - Phát âm thanh báo thức lặp đến khi stop_alarm + rung lặp.
"""

import os
import sys

from kivy.clock import Clock

from app_core.paths import PROJECT_ROOT

_SOUNDS_DIR = os.path.join(PROJECT_ROOT, "assets", "sounds")

# Nhãn hiển thị (tiếng Việt) — bổ sung theo tên file
_SOUND_LABELS = {
    "pills.mp3": "Thuốc (meo)",
    "bell.mp3": "Chuông",
    "cabin_chime.mp3": "Chuông tàu",
    "notification_sound_1.mp3": "Thông báo 1",
    "notification_sound_2.mp3": "Thông báo 2",
    "notification_sound_3.mp3": "Thông báo 3",
    "ringtone_1.mp3": "Nhạc chuông 1",
    "ringtone_2.mp3": "Nhạc chuông 2",
    "ringtone_3.mp3": "Nhạc chuông 3",
    "iphone_notification.mp3": "Kiểu iPhone",
    "messenger.mp3": "Messenger",
    "mews_sunrise_serenade.mp3": "Mews bình minh",
    "mews_sunrise_serenade_long.mp3": "Mews bình minh (dài)",
    "samsung_ringtone_trap.mp3": "Samsung trap",
    "samsung_ringtone_trap_long.mp3": "Samsung trap (dài)",
    "silent.mp3": "Im lặng",
    "sweetie_girl.mp3": "Sweetie girl",
    "sweetie_girl_long.mp3": "Sweetie girl (dài)",
    "arigato.mp3": "Arigato",
    "awoo.mp3": "Awoo",
    "ayaya.mp3": "Ayaya",
    "cat.mp3": "Mèo",
    "chicken.mp3": "Gà",
    "dog.mp3": "Chó",
    "facebook.mp3": "Facebook",
    "instagram.mp3": "Instagram",
    "oh_my_gah.mp3": "Oh my gah",
    "pikachu.mp3": "Pikachu",
    "wait_wait_wait.mp3": "Wait wait",
    "the_amazing_digital_circus.mp3": "Digital circus",
    "the_amazing_digital_circus_long.mp3": "Digital circus (dài)",
    "cat_creep_radiohead.mp3": "Cat creep",
}

DEFAULT_ALARM_SOUND = "pills.mp3"

_alarm_active = False
_scheduled_events = []
_pygame_ready = False


def get_sound_path(filename: str) -> str:
    return os.path.join(_SOUNDS_DIR, filename)


def list_mp3_files():
    if not os.path.isdir(_SOUNDS_DIR):
        return []
    return sorted(
        f for f in os.listdir(_SOUNDS_DIR)
        if f.lower().endswith(".mp3")
    )


def get_sound_label(filename: str) -> str:
    return _SOUND_LABELS.get(filename, filename.replace(".mp3", "").replace("_", " "))


def get_sound_choices():
    """[(filename, label_vn), ...]"""
    return [(f, get_sound_label(f)) for f in list_mp3_files()]


def _clear_scheduled():
    global _scheduled_events
    for ev in _scheduled_events:
        try:
            ev.cancel()
        except Exception:
            pass
    _scheduled_events = []


def _ensure_pygame_init():
    """Khởi tạo pygame mixer đúng 1 lần duy nhất — tránh lỗi trạng thái trên Windows."""
    global _pygame_ready
    if _pygame_ready:
        return True
    try:
        import pygame
        pygame.mixer.init()
        _pygame_ready = True
        return True
    except Exception:
        _pygame_ready = False
        return False


def _play_pygame(filepath: str, volume: float, loops: int) -> bool:
    if not _ensure_pygame_init():
        return False
    try:
        import pygame
        pygame.mixer.music.load(filepath)
        pygame.mixer.music.set_volume(volume)
        pygame.mixer.music.play(loops=loops)
        return True
    except Exception as e:
        print(f"[SoundManager] pygame play: {e}")
        _pygame_ready = False
        return False


def _stop_pygame_music():
    """Dừng pygame music — chỉ gọi khi mixer đã init thành công."""
    try:
        import pygame
        if _pygame_ready:
            pygame.mixer.music.stop()
    except Exception:
        pass


def stop_alarm():
    """Dừng mọi âm thanh / lịch lặp báo thức."""
    global _alarm_active
    _alarm_active = False
    _clear_scheduled()
    _stop_pygame_music()
    try:
        import winsound
        winsound.PlaySound(None, winsound.SND_PURGE)
    except Exception:
        pass


def play_preview(sound_file: str, duration_sec: float = 2.0, volume: float = 0.85):
    """Nghe thử vài giây rồi tự dừng."""
    stop_alarm()
    filepath = get_sound_path(sound_file)
    if not os.path.exists(filepath):
        print(f"[SoundManager] Preview: khong co file {filepath}")
        return
    if _play_pygame(filepath, volume, loops=0):
        Clock.schedule_once(lambda dt: _stop_pygame_music(), duration_sec)
    else:
        try:
            import winsound
            winsound.Beep(880, 300)
        except Exception:
            pass


def _winsound_beep_tick(_dt):
    if not _alarm_active:
        return False
    try:
        import winsound
        winsound.Beep(1100, 180)
    except Exception:
        pass


def _vibrate_tick(_dt):
    if not _alarm_active:
        return False
    try:
        import winsound
        winsound.Beep(280, 120)
    except Exception:
        pass


def play_alarm(
    sound_file: str = None,
    volume: float = 0.9,
    loops: int = -1,
    sound_enabled: bool = True,
    vibrate_enabled: bool = True,
    vibrate_interval: float = 2.0,
):
    """
    Báo thức: âm thanh lặp (loops=-1) và/hoặc rung lặp cho đến stop_alarm().
    """
    global _alarm_active
    stop_alarm()
    _alarm_active = True

    if sound_file is None:
        sound_file = DEFAULT_ALARM_SOUND
    filepath = get_sound_path(sound_file)

    if sound_enabled:
        if os.path.exists(filepath) and _play_pygame(filepath, volume, loops):
            pass
        else:
            if not os.path.exists(filepath):
                print(f"[SoundManager] Khong tim thay: {filepath}")
            ev = Clock.schedule_interval(_winsound_beep_tick, 0.85)
            _scheduled_events.append(ev)

    if vibrate_enabled:
        ev2 = Clock.schedule_interval(_vibrate_tick, vibrate_interval)
        _scheduled_events.append(ev2)


def vibrate_once():
    if sys.platform == "win32":
        try:
            import winsound
            winsound.Beep(320, 200)
        except Exception:
            pass
    else:
        try:
            from jnius import autoclass
            Vibrator = autoclass("android.os.Vibrator")
            v = Vibrator()
            if v.hasVibrator():
                v.vibrate(400)
        except Exception as e:
            print(f"[SoundManager] Rung Android: {e}")


def vibrate(duration_ms: int = 1000):
    vibrate_once()
