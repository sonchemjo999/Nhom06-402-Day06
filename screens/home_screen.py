"""
==============================================================================
 HomeScreen - Trang chủ + Alarm + Logic khóa/mở nút
==============================================================================
 File: screens/home_screen.py

 - Đồng hồ: cập nhật mỗi giây qua StringProperty (KV tự bind → luôn vẽ lại).
 - Thời gian: get_app_now() (có file .app_datetime thì mốc ảo + thời gian thực trôi).
==============================================================================
"""

import os
from app_core.app_datetime import get_app_now
from app_core.app_settings import get_sound_enabled, get_vibration_enabled, get_alarm_sound_file
from app_core.sound_manager import play_alarm, stop_alarm
from kivymd.uix.screen import MDScreen
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDRaisedButton, MDFlatButton
from kivy.uix.image import Image
from kivy.uix.popup import Popup
from kivy.properties import StringProperty, BooleanProperty
from kivy.metrics import dp
from kivy.clock import Clock
from kivymd.uix.snackbar import MDSnackbar
from kivymd.uix.boxlayout import MDBoxLayout

from data.schedule_store import schedule_store
from services.alarm_service import AlarmService


_WEEKDAYS_VI = (
    "Thứ Hai",
    "Thứ Ba",
    "Thứ Tư",
    "Thứ Năm",
    "Thứ Sáu",
    "Thứ Bảy",
    "Chủ nhật",
)


def _get_icon_path(icon_name):
    """Trả về đường dẫn tuyệt đối đến file icon PNG."""
    if not icon_name:
        return ""
    base = os.path.dirname(os.path.abspath(__file__))
    icon_dir = os.path.join(base, "..", "assets", "icons", "medications")
    path = os.path.join(icon_dir, icon_name)
    if os.path.exists(path):
        return path
    return ""


class IconImage(MDBoxLayout):
    """Widget hiển thị icon thuốc bên trái MedCard."""
    med_icon = StringProperty("")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size_hint_x = None
        self.width = "56dp"
        self.padding = ["4dp", "4dp", "4dp", "4dp"]
        self._img = None

    def on_med_icon(self, *args):
        self._update_icon()

    def on_kv_post(self, *args):
        super().on_kv_post(*args)
        self._img = Image(
            size_hint=(1, 1),
            allow_stretch=True,
            keep_ratio=True,
        )
        self.add_widget(self._img)
        self._update_icon()

    def _update_icon(self):
        if self._img:
            self._img.source = _get_icon_path(self.med_icon)


class MedCard(MDCard):
    med_time = StringProperty("")
    med_name = StringProperty("")
    med_dosage = StringProperty("")
    med_note = StringProperty("")
    med_taken = BooleanProperty(False)
    med_unlocked = BooleanProperty(False)
    med_icon = StringProperty("")


class AlarmPopup(Popup):
    alarm_time = StringProperty("")
    alarm_med_name = StringProperty("")
    alarm_dosage = StringProperty("")
    alarm_note = StringProperty("")
    alarm_count_text = StringProperty("")
    alarm_med_icon = StringProperty("")

    def __init__(self, med_info, reminder_count,
                 on_confirm_cb=None, on_snooze_cb=None, **kwargs):
        super().__init__(**kwargs)
        self.alarm_time = med_info.get("time", "")
        self.alarm_med_name = med_info.get("name", "")
        self.alarm_dosage = med_info.get("dosage", "")
        self.alarm_note = med_info.get("note", "")
        self.alarm_count_text = f"Lần nhắc: {reminder_count}/5"
        self.alarm_med_icon = med_info.get("icon", "")
        self._med_info = med_info
        self._on_confirm_cb = on_confirm_cb
        self._on_snooze_cb = on_snooze_cb

    def on_confirm(self):
        self.dismiss()
        if self._on_confirm_cb:
            self._on_confirm_cb(self._med_info)

    def on_snooze(self):
        self.dismiss()
        if self._on_snooze_cb:
            self._on_snooze_cb(self._med_info)


class HomeScreen(MDScreen):
    """StringProperty cho đồng hồ: KV bind text → mỗi giây đổi property là UI cập nhật."""

    clock_display = StringProperty("--:--:--")
    date_display = StringProperty("")
    day_display = StringProperty("")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.alarm_service = AlarmService(demo_mode=True)
        self._current_popup = None
        self._clock_event = None

    def on_enter(self, *args):
        if self._clock_event is not None:
            self._clock_event.cancel()
            self._clock_event = None
        self._tick_clock(0)
        self._clock_event = Clock.schedule_interval(self._tick_clock, 1.0)
        Clock.schedule_once(lambda dt: self.load_schedule(), 0)
        Clock.schedule_once(lambda dt: self._start_alarm(), 0.5)

    def on_leave(self, *args):
        if self._clock_event is not None:
            self._clock_event.cancel()
            self._clock_event = None

    def _tick_clock(self, dt):
        now = get_app_now()
        self.clock_display = now.strftime("%H:%M:%S")
        self.date_display = now.strftime("%d/%m/%Y")
        self.day_display = _WEEKDAYS_VI[now.weekday()]

    def _start_alarm(self):
        self.alarm_service.start(on_alarm_callback=self._on_alarm_triggered)

    def load_schedule(self):
        container = self.ids.get("med_list_container")
        if not container:
            return
        container.clear_widgets()
        for item in schedule_store.load():
            card = MedCard(
                med_time=item["time"],
                med_name=item["name"],
                med_dosage=item["dosage"],
                med_note=item.get("note", ""),
                med_taken=item.get("taken", False),
                med_unlocked=False,
                med_icon=item.get("icon", ""),
            )
            container.add_widget(card)

    def mark_as_taken(self, card):
        card.med_taken = True
        current = schedule_store.load()
        for item in current:
            if item["time"] == card.med_time and item["name"] == card.med_name:
                item["taken"] = True
                break
        schedule_store.save(current)
        self.alarm_service.confirm_taken(card.med_time, card.med_name)
        MDSnackbar(
            MDLabel(
                text="Đã ghi nhận: {} lúc {}".format(card.med_name, card.med_time)
            ),
            y=dp(24),
            pos_hint={"center_x": 0.5},
            size_hint_x=0.95,
        ).open()

    def _on_alarm_triggered(self, med_info, reminder_count):
        self._unlock_med_button(med_info["time"], med_info["name"])
        if self._current_popup:
            try:
                self._current_popup.dismiss()
            except Exception:
                pass
        self._play_alarm_sound()
        self._current_popup = AlarmPopup(
            med_info=med_info,
            reminder_count=reminder_count,
            on_confirm_cb=self._on_alarm_confirm,
            on_snooze_cb=self._on_alarm_snooze,
        )
        self._current_popup.open()

    def _unlock_med_button(self, med_time, med_name):
        container = self.ids.get("med_list_container")
        if not container:
            return
        for child in container.children:
            if isinstance(child, MedCard):
                if child.med_time == med_time and child.med_name == med_name:
                    child.med_unlocked = True
                    break

    def _on_alarm_confirm(self, med_info):
        stop_alarm()
        self._current_popup = None
        current = schedule_store.load()
        for item in current:
            if item["time"] == med_info["time"] and item["name"] == med_info["name"]:
                item["taken"] = True
                break
        schedule_store.save(current)
        self.alarm_service.confirm_taken(med_info["time"], med_info["name"])
        self.load_schedule()
        MDSnackbar(
            MDLabel(
                text="Đã uống: {} lúc {}".format(med_info["name"], med_info["time"])
            ),
            y=dp(24),
            pos_hint={"center_x": 0.5},
            size_hint_x=0.95,
        ).open()

    def _on_alarm_snooze(self, med_info):
        stop_alarm()
        self._current_popup = None
        self.alarm_service.snooze(med_info["time"], med_info["name"])
        count = self.alarm_service.get_reminder_count(med_info["time"], med_info["name"])
        remaining = 5 - count
        MDSnackbar(
            MDLabel(
                text="Trì hoãn: {} - còn {} lần nhắc".format(med_info["name"], remaining)
            ),
            y=dp(24),
            pos_hint={"center_x": 0.5},
            size_hint_x=0.95,
        ).open()

    def _play_alarm_sound(self):
        play_alarm(
            get_alarm_sound_file(),
            sound_enabled=get_sound_enabled(),
            vibrate_enabled=get_vibration_enabled(),
        )

    def go_to_settings(self):
        self.manager.current = "settings"

    def nav_home(self):
        """Đang ở trang chủ — có thể mở rộng cuộn về đầu."""
        pass

    def go_to_scan(self):
        self.manager.current = "ai_scan"

    def go_to_chatbot(self):
        self.manager.current = "chatbot"
