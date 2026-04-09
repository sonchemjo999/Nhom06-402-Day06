"""
SettingsScreen - Cài đặt: theme, âm thanh, chọn file chuông, rung.
"""

from kivy.metrics import dp
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView
from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDFlatButton
from kivymd.uix.label import MDLabel


class SettingsScreen(MDScreen):

    def _get_app(self):
        from kivymd.app import MDApp
        return MDApp.get_running_app()

    def on_enter(self):
        self.update_all_toggles()
        self.refresh_alarm_sound_label()

    def on_leave(self):
        """Luôn refresh label khi quay lại — đảm bảo label cập nhật sau khi đổi âm thanh."""
        pass

    def refresh_alarm_sound_label(self):
        from app_core.app_settings import get_alarm_sound_file
        from app_core.sound_manager import get_sound_label
        try:
            if self.ids.get("alarm_sound_value"):
                self.ids.alarm_sound_value.text = get_sound_label(get_alarm_sound_file())
        except Exception:
            pass

    def update_all_toggles(self):
        from app_core.app_settings import get_dark_mode, get_sound_enabled, get_vibration_enabled
        try:
            ids = self.ids
            if ids.get("dark_mode_switch"):
                ids.dark_mode_switch.active = get_dark_mode()
            if ids.get("sound_switch"):
                ids.sound_switch.active = get_sound_enabled()
            if ids.get("vibration_switch"):
                ids.vibration_switch.active = get_vibration_enabled()
        except Exception:
            pass

    def toggle_dark_mode(self, *args):
        active = bool(args[1]) if len(args) >= 2 else False
        self._get_app().set_dark_mode(active)

    def toggle_sound(self, *args):
        from app_core.app_settings import set_sound_enabled
        active = bool(args[1]) if len(args) >= 2 else False
        set_sound_enabled(active)

    def toggle_vibration(self, *args):
        from app_core.app_settings import set_vibration_enabled
        active = bool(args[1]) if len(args) >= 2 else False
        set_vibration_enabled(active)

    def open_sound_picker(self):
        from app_core.app_settings import get_alarm_sound_file, set_alarm_sound_file
        from app_core.sound_manager import get_sound_choices, stop_alarm

        stop_alarm()
        choices = get_sound_choices()
        current = get_alarm_sound_file()
        app = self._get_app()
        # Popup mặc định của Kivy tối; MD widget theo theme — light mode dễ thành chữ tối trên nền tối.
        surface = list(app.surface_color)
        primary_text = list(app.text_primary_color)
        secondary_text = list(app.text_secondary_color)

        box = MDBoxLayout(
            orientation="vertical",
            spacing=dp(4),
            size_hint_y=None,
            adaptive_height=True,
            padding=dp(8),
            md_bg_color=surface,
        )
        for fn, label in choices:
            txt = ("• " if fn == current else "") + label
            b = MDFlatButton(
                text=txt,
                size_hint_y=None,
                height=dp(44),
                theme_text_color="Custom",
                text_color=primary_text,
            )

            def make_handler(filename):
                def _h(*_a):
                    set_alarm_sound_file(filename)
                    self.refresh_alarm_sound_label()
                    popup.dismiss()

                return _h

            b.bind(on_release=make_handler(fn))
            box.add_widget(b)

        scroll = ScrollView(
            size_hint_y=1,
            bar_color=(*secondary_text[:3], 0.45),
            bar_inactive_color=(*secondary_text[:3], 0.2),
        )
        scroll.add_widget(box)

        content = MDBoxLayout(
            orientation="vertical",
            spacing=dp(8),
            padding=dp(8),
            md_bg_color=surface,
        )
        content.add_widget(
            MDLabel(
                text="Chọn âm thanh báo thức",
                font_style="Subtitle1",
                bold=True,
                size_hint_y=None,
                height=dp(36),
                theme_text_color="Custom",
                text_color=primary_text,
            )
        )
        content.add_widget(scroll)

        popup = Popup(
            title="",
            content=content,
            size_hint=(0.88, 0.62),
            separator_height=0,
            # Nền popup sáng khi Light / tối khi Dark — khớp bảng màu app
            background_color=surface,
        )
        popup.open()

    def preview_alarm_sound(self):
        from app_core.app_settings import get_alarm_sound_file
        from app_core.sound_manager import play_preview, stop_alarm

        stop_alarm()
        play_preview(get_alarm_sound_file(), duration_sec=2.5)

    def go_back(self):
        self.manager.current = "home"
