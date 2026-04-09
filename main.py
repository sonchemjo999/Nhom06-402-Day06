"""
=============================================================================
 MedReminder - Ứng dụng Nhắc nhở Uống Thuốc
=============================================================================
 File: main.py
 Mô tả: Entry point chính của ứng dụng. Khởi tạo App, ScreenManager
         và kết nối các màn hình lại với nhau.
         Hỗ trợ Light / Dark Mode.

 Kiến trúc:
   - UI (KV Language)  -> kv/*.kv
   - Logic (Python)    -> screens/*.py
   - Theme Manager     -> app_core/theme_manager.py (màu động Light/Dark)
   - Services          -> services/*.py (alarm, notification)
   - AI Core           -> ai_core/*.py (LangGraph agent)
   - Data              -> data/*.py (mock data)
   - Entry point       -> main.py
=============================================================================
"""

import os
import sys

# --- Cấu hình KivyMD trước khi import ---
os.environ["KIVY_LOG_LEVEL"] = "info"

# ============================================================================
# Fix Kivy 2.3.x + KivyMD 1.2.0: BoxShadow border_radius crash
# Đã sửa trong site-packages:
#   kivymd/uix/behaviors/elevation.py
#   - shadow_radius default [0] -> [0,0,0,0]
#   - border_radius KV rule -> [1,1,1,1] thay vì so sánh phức tạp
# ============================================================================

from kivy.lang import Builder
from kivy.core.window import Window
from kivy.properties import ListProperty
from kivymd.app import MDApp

# Import theme manager
from app_core.theme_manager import ThemeManager
from app_core.app_settings import get_dark_mode, get_sound_enabled, get_vibration_enabled

# Import cac man hinh
from screens.home_screen import HomeScreen
from screens.ai_scan_screen import AIScanScreen
from screens.crosscheck_screen import CrossCheckScreen
from screens.chatbot_screen import ChatbotScreen
from screens.settings_screen import SettingsScreen

# Giả lập kích thước điện thoại khi chạy trên Desktop
Window.size = (400, 720)


class MedReminderApp(MDApp):
    """
    Lớp ứng dụng chính.
    Quản lý theme, load KV files, và khởi tạo ScreenManager.
    Hỗ trợ Light / Dark Mode với bảng màu tập trung.
    """

    # ==========================================================================
    # COLOR PROPERTIES - Dùng trong KV Language (app.xxx)
    # Thay đổi ở ĐÂY → tự động cập nhật toàn bộ màn hình.
    # ==========================================================================

    # Màu nền
    bg_color = ListProperty([1, 1, 1, 1])
    surface_color = ListProperty([0.97, 0.97, 0.97, 1])
    surface_variant_color = ListProperty([0.96, 0.96, 0.96, 1])

    # Màu card thuốc
    card_taken_color = ListProperty([0.95, 1, 0.95, 1])
    card_normal_color = ListProperty([1, 1, 1, 1])
    card_unlocked_color = ListProperty([1, 0.97, 0.93, 1])

    # Màu chữ
    text_primary_color = ListProperty([0.1, 0.1, 0.15, 1])
    text_secondary_color = ListProperty([0.4, 0.4, 0.45, 1])
    text_disabled_color = ListProperty([0.6, 0.6, 0.6, 1])
    text_time_color = ListProperty([0.1, 0.1, 0.5, 1])

    # Màu trạng thái
    status_taken_color = ListProperty([0.0, 0.6, 0.3, 1])
    status_pending_color = ListProperty([0.6, 0.6, 0.6, 1])
    status_unlocked_color = ListProperty([0.9, 0.3, 0.0, 1])

    # Màu nút
    btn_taken_color = ListProperty([0.0, 0.6, 0.4, 1])
    btn_disabled_color = ListProperty([0.75, 0.75, 0.75, 1])
    btn_chatbot_color = ListProperty([0.2, 0.6, 0.9, 1])

    # Màu alarm popup
    alarm_bg_color = ListProperty([0.02, 0.02, 0.05, 1])
    alarm_header_color = ListProperty([0.95, 0.25, 0.2, 1])
    alarm_time_color = ListProperty([0.9, 0.2, 0.15, 1])
    alarm_med_card_color = ListProperty([1, 0.97, 0.93, 1])
    alarm_warning_color = ListProperty([0.8, 0.4, 0.0, 1])

    # Màu chatbot
    bubble_user_color = ListProperty([0.2, 0.6, 0.9, 1])
    bubble_ai_danger_color = ListProperty([0.95, 0.2, 0.15, 1])
    bubble_ai_warning_color = ListProperty([1.0, 0.7, 0.2, 1])
    bubble_ai_safe_color = ListProperty([0.85, 0.93, 0.85, 1])
    btn_emergency_color = ListProperty([0.9, 0.15, 0.1, 1])

    # Màu crosscheck
    crosscheck_form_bg_color = ListProperty([0.97, 0.97, 1, 1])
    crosscheck_success_bg_color = ListProperty([0.9, 1, 0.9, 1])
    crosscheck_image_bg_color = ListProperty([0.97, 0.97, 0.95, 1])
    crosscheck_confirm_bg_color = ListProperty([1, 0.98, 0.9, 1])

    # Màu settings
    settings_card_bg = ListProperty([0.95, 0.95, 0.95, 1])
    settings_title_color = ListProperty([0.5, 0.5, 0.5, 1])
    settings_text_color = ListProperty([0.1, 0.1, 0.15, 1])

    # ==========================================================================
    # LIFECYCLE
    # ==========================================================================

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Đọc Dark Mode từ file settings (lưu qua các lần chạy)
        saved_dark = get_dark_mode()
        # Khởi tạo ThemeManager (singleton)
        self.theme_manager = ThemeManager()
        # Đăng ký callback trước khi set_theme để đồng bộ AppColors + is_dark với setting đã lưu
        self.theme_manager.bind(on_theme_changed=self._on_theme_changed)
        # set_theme cập nhật theme_manager.is_dark + AppColors + gọi _apply_colors qua callback
        self.theme_manager.set_theme(saved_dark)

    def build(self):
        # --- Cấu hình Theme Material Design ---
        self.theme_cls.theme_style = "Dark" if get_dark_mode() else "Light"
        self.theme_cls.primary_palette = "Teal"
        self.title = "MedReminder - Nhắc nhở Uống thuốc"

        # --- Load tất cả file KV (UI) ---
        kv_dir = os.path.join(os.path.dirname(__file__), "kv")
        for kv_file in sorted(os.listdir(kv_dir)):
            if kv_file.endswith(".kv"):
                Builder.load_file(os.path.join(kv_dir, kv_file))

        # --- Load layout chính (chứa ScreenManager) ---
        return Builder.load_file(os.path.join(kv_dir, "app_root.kv"))

    def _on_theme_changed(self, *args):
        """Callback khi ThemeManager thay đổi → cập nhật MDApp theme + màu."""
        is_dark = self.theme_manager.is_dark
        self.theme_cls.theme_style = "Dark" if is_dark else "Light"
        self._apply_colors(is_dark=is_dark)

    def toggle_theme(self):
        """Chuyển đổi Light ↔ Dark mode."""
        self.theme_manager.toggle()

    def set_dark_mode(self, enabled: bool):
        """Đặt chế độ Dark Mode cụ thể."""
        from app_core.app_settings import set_dark_mode
        set_dark_mode(enabled)
        self.theme_manager.set_theme(enabled)

    def on_stop(self):
        """Dọn dẹp khi app đóng: dừng alarm service."""
        try:
            home = self.root.get_screen("home")
            if hasattr(home, "alarm_service"):
                home.alarm_service.stop()
        except Exception:
            pass

    # ==========================================================================
    # ÁP DỤNG BẢNG MÀU
    # ==========================================================================

    def _apply_colors(self, is_dark: bool):
        """Áp dụng bảng màu dựa trên chế độ Light/Dark."""
        if is_dark:
            # --- DARK MODE ---
            self.bg_color = [0.06, 0.06, 0.1, 1]
            self.surface_color = [0.1, 0.1, 0.16, 1]
            self.surface_variant_color = [0.12, 0.12, 0.18, 1]
            self.card_taken_color = [0.08, 0.18, 0.1, 1]
            self.card_normal_color = [0.12, 0.12, 0.18, 1]
            self.card_unlocked_color = [0.22, 0.1, 0.08, 1]
            self.text_primary_color = [0.95, 0.95, 0.97, 1]
            self.text_secondary_color = [0.6, 0.6, 0.65, 1]
            self.text_disabled_color = [0.35, 0.35, 0.4, 1]
            self.text_time_color = [0.4, 0.6, 0.95, 1]
            self.status_taken_color = [0.2, 0.75, 0.4, 1]
            self.status_pending_color = [0.35, 0.35, 0.4, 1]
            self.status_unlocked_color = [1.0, 0.5, 0.2, 1]
            self.btn_taken_color = [0.15, 0.7, 0.4, 1]
            self.btn_disabled_color = [0.2, 0.2, 0.25, 1]
            self.btn_chatbot_color = [0.25, 0.45, 0.8, 1]
            self.alarm_bg_color = [0.04, 0.04, 0.07, 1]
            self.alarm_header_color = [0.8, 0.2, 0.15, 1]
            self.alarm_time_color = [1.0, 0.4, 0.3, 1]
            self.alarm_med_card_color = [0.12, 0.1, 0.1, 1]
            self.alarm_warning_color = [0.9, 0.55, 0.2, 1]
            self.bubble_user_color = [0.25, 0.45, 0.8, 1]
            self.bubble_ai_danger_color = [0.6, 0.1, 0.08, 1]
            self.bubble_ai_warning_color = [0.7, 0.45, 0.1, 1]
            self.bubble_ai_safe_color = [0.15, 0.25, 0.18, 1]
            self.btn_emergency_color = [0.8, 0.15, 0.1, 1]
            self.crosscheck_form_bg_color = [0.08, 0.1, 0.18, 1]
            self.crosscheck_success_bg_color = [0.1, 0.22, 0.12, 1]
            self.crosscheck_image_bg_color = [0.1, 0.1, 0.12, 1]
            self.crosscheck_confirm_bg_color = [0.15, 0.12, 0.08, 1]
            self.settings_card_bg = [0.15, 0.15, 0.2, 1]
            self.settings_title_color = [0.6, 0.6, 0.65, 1]
            self.settings_text_color = [0.95, 0.95, 0.97, 1]
        else:
            # --- LIGHT MODE ---
            self.bg_color = [1, 1, 1, 1]
            self.surface_color = [0.97, 0.97, 0.97, 1]
            self.surface_variant_color = [0.96, 0.96, 0.96, 1]
            self.card_taken_color = [0.95, 1, 0.95, 1]
            self.card_normal_color = [1, 1, 1, 1]
            self.card_unlocked_color = [1, 0.97, 0.93, 1]
            self.text_primary_color = [0.1, 0.1, 0.15, 1]
            self.text_secondary_color = [0.4, 0.4, 0.45, 1]
            self.text_disabled_color = [0.6, 0.6, 0.6, 1]
            self.text_time_color = [0.1, 0.1, 0.5, 1]
            self.status_taken_color = [0.0, 0.6, 0.3, 1]
            self.status_pending_color = [0.6, 0.6, 0.6, 1]
            self.status_unlocked_color = [0.9, 0.3, 0.0, 1]
            self.btn_taken_color = [0.0, 0.6, 0.4, 1]
            self.btn_disabled_color = [0.75, 0.75, 0.75, 1]
            self.btn_chatbot_color = [0.2, 0.6, 0.9, 1]
            self.alarm_bg_color = [0.02, 0.02, 0.05, 1]
            self.alarm_header_color = [0.95, 0.25, 0.2, 1]
            self.alarm_time_color = [0.9, 0.2, 0.15, 1]
            self.alarm_med_card_color = [1, 0.97, 0.93, 1]
            self.alarm_warning_color = [0.8, 0.4, 0.0, 1]
            self.bubble_user_color = [0.2, 0.6, 0.9, 1]
            self.bubble_ai_danger_color = [0.95, 0.2, 0.15, 1]
            self.bubble_ai_warning_color = [1.0, 0.7, 0.2, 1]
            self.bubble_ai_safe_color = [0.85, 0.93, 0.85, 1]
            self.btn_emergency_color = [0.9, 0.15, 0.1, 1]
            self.crosscheck_form_bg_color = [0.97, 0.97, 1, 1]
            self.crosscheck_success_bg_color = [0.9, 1, 0.9, 1]
            self.crosscheck_image_bg_color = [0.97, 0.97, 0.95, 1]
            self.crosscheck_confirm_bg_color = [1, 0.98, 0.9, 1]
            self.settings_card_bg = [0.95, 0.95, 0.95, 1]
            self.settings_title_color = [0.5, 0.5, 0.5, 1]
            self.settings_text_color = [0.1, 0.1, 0.15, 1]


if __name__ == "__main__":
    MedReminderApp().run()
