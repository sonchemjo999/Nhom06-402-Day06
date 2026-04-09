"""
==============================================================================
 Theme Manager - Hệ thống màu động Light / Dark Mode
==============================================================================
 File: theme_manager.py

 Mô tả:
   Quản lý màu sắc tập trung cho toàn bộ app.
   THAY ĐỔI MÀU Ở ĐÂY → TỰ ĐỘNG ÁP DỤNG CHO TẤT CẢ MÀN HÌNH.
   Dựa trên màu sắc từ Mewdicate APK decompile.

 Sử dụng:
   from app_core.theme_manager import AppColors, ThemeManager
   from kivy.properties import ListProperty

   # Trong class Widget:
   text_color: AppColors.text_primary()
==============================================================================
"""

from kivy.properties import ListProperty, BooleanProperty
from kivy.event import EventDispatcher

# ============================================================================
# BẢNG MÀU SẮC - THAY ĐỔI TẠI ĐÂY
# ============================================================================
# Màu sắc được chia thành 2 nhóm: Light Mode và Dark Mode
# Inspiration từ Mewdicate APK (values-night/colors.xml)
# ============================================================================


class AppColors:
    """
    Lớp tĩnh chứa tất cả màu sắc của ứng dụng.
    Mỗi method trả về màu phù hợp với chế độ hiện tại.
    """

    # ==========================================================================
    # TRẠNG THÁI CHẾ ĐỘ (Light/Dark) - THAY ĐỔI TẠI ĐÂY
    # ==========================================================================
    _is_dark_mode: bool = False

    @classmethod
    def set_dark_mode(cls, enabled: bool):
        """Bật/tắt Dark Mode."""
        cls._is_dark_mode = enabled

    @classmethod
    def is_dark(cls) -> bool:
        """Kiểm tra có đang ở Dark Mode không."""
        return cls._is_dark_mode

    # ==========================================================================
    # MÀU NỀN
    # ==========================================================================

    @staticmethod
    def background() -> list:
        """Màu nền chính."""
        if AppColors._is_dark_mode:
            return [0.06, 0.06, 0.1, 1]     # #0F0F1A - Tím đen đậm
        return [1.0, 1.0, 1.0, 1]            # Trắng

    @staticmethod
    def surface() -> list:
        """Màu nền card/panel."""
        if AppColors._is_dark_mode:
            return [0.1, 0.1, 0.16, 1]      # #1A1A29 - Tím đen nhạt
        return [0.97, 0.97, 0.97, 1]         # Xám nhạt

    @staticmethod
    def surface_variant() -> list:
        """Màu nền phụ (header, divider)."""
        if AppColors._is_dark_mode:
            return [0.12, 0.12, 0.18, 1]    # #1F1F2E
        return [0.96, 0.96, 0.96, 1]        # Xám rất nhạt

    @staticmethod
    def card_taken() -> list:
        """Màu nền thẻ thuốc ĐÃ uống."""
        if AppColors._is_dark_mode:
            return [0.08, 0.18, 0.1, 1]      # Xanh lá đậm tối
        return [0.95, 1.0, 0.95, 1]         # Xanh lá nhạt

    @staticmethod
    def card_normal() -> list:
        """Màu nền thẻ thuốc BÌNH THƯỜNG."""
        if AppColors._is_dark_mode:
            return [0.12, 0.12, 0.18, 1]     # Tím đen nhạt
        return [1.0, 1.0, 1.0, 1]           # Trắng

    @staticmethod
    def card_unlocked() -> list:
        """Màu nền thẻ thuốc ĐẾN GIỜ (đã mở khóa)."""
        if AppColors._is_dark_mode:
            return [0.22, 0.1, 0.08, 1]      # Đỏ cam tối
        return [1.0, 0.97, 0.93, 1]          # Cam nhạt

    # ==========================================================================
    # MÀU CHỮ
    # ==========================================================================

    @staticmethod
    def text_primary() -> list:
        """Màu chữ chính."""
        if AppColors._is_dark_mode:
            return [0.95, 0.95, 0.97, 1]    # Trắng mờ
        return [0.1, 0.1, 0.15, 1]          # Đen nhạt

    @staticmethod
    def text_secondary() -> list:
        """Màu chữ phụ (subtitle, ghi chú)."""
        if AppColors._is_dark_mode:
            return [0.6, 0.6, 0.65, 1]      # Xám sáng
        return [0.4, 0.4, 0.45, 1]          # Xám đậm

    @staticmethod
    def text_disabled() -> list:
        """Màu chữ bị vô hiệu hóa."""
        if AppColors._is_dark_mode:
            return [0.35, 0.35, 0.4, 1]      # Xám tối
        return [0.6, 0.6, 0.6, 1]            # Xám trung

    @staticmethod
    def text_on_primary() -> list:
        """Màu chữ trên nền primary (nút, toolbar)."""
        return [1.0, 1.0, 1.0, 1]            # Trắng

    @staticmethod
    def text_time() -> list:
        """Màu chữ giờ (hiển thị giờ uống thuốc)."""
        if AppColors._is_dark_mode:
            return [0.4, 0.6, 0.95, 1]      # Xanh dương nhạt
        return [0.1, 0.1, 0.5, 1]           # Xanh dương đậm

    # ==========================================================================
    # TRẠNG THÁI THUỐC
    # ==========================================================================

    @staticmethod
    def status_taken() -> list:
        """Màu trạng thái: ĐÃ UỐNG."""
        if AppColors._is_dark_mode:
            return [0.2, 0.75, 0.4, 1]       # Xanh lá sáng
        return [0.0, 0.6, 0.3, 1]            # Xanh lá

    @staticmethod
    def status_pending() -> list:
        """Màu trạng thái: CHƯA ĐẾN GIỜ."""
        if AppColors._is_dark_mode:
            return [0.35, 0.35, 0.4, 1]      # Xám tối
        return [0.6, 0.6, 0.6, 1]            # Xám trung

    @staticmethod
    def status_unlocked() -> list:
        """Màu trạng thái: ĐẾN GIỜ (cần uống)."""
        if AppColors._is_dark_mode:
            return [1.0, 0.5, 0.2, 1]        # Cam sáng
        return [0.9, 0.3, 0.0, 1]           # Cam đỏ

    # ==========================================================================
    # MÀU NÚT
    # ==========================================================================

    @staticmethod
    def btn_taken() -> list:
        """Màu nút ĐÃ UỐNG."""
        if AppColors._is_dark_mode:
            return [0.15, 0.7, 0.4, 1]        # Xanh lá đậm sáng
        return [0.0, 0.6, 0.4, 1]            # Xanh lá

    @staticmethod
    def btn_disabled() -> list:
        """Màu nút bị vô hiệu hóa."""
        if AppColors._is_dark_mode:
            return [0.2, 0.2, 0.25, 1]       # Xám tối
        return [0.75, 0.75, 0.75, 1]         # Xám trung

    @staticmethod
    def btn_snooze() -> list:
        """Màu nút TRÌ HOÃN."""
        if AppColors._is_dark_mode:
            return [0.8, 0.5, 0.15, 1]        # Cam đậm sáng
        return [0.8, 0.4, 0.0, 1]            # Cam đỏ

    @staticmethod
    def btn_chatbot() -> list:
        """Màu nút Chat AI."""
        if AppColors._is_dark_mode:
            return [0.25, 0.45, 0.8, 1]      # Xanh dương tối sáng
        return [0.2, 0.6, 0.9, 1]            # Xanh dương

    @staticmethod
    def btn_scan() -> list:
        """Màu nút QUÉT ĐƠN THUỐC (dùng primary)."""
        # Trả về màu primary của theme_cls - gán ở KV
        return None  # Sẽ dùng app.theme_cls.primary_color

    # ==========================================================================
    # ALARM POPUP
    # ==========================================================================

    @staticmethod
    def alarm_background() -> list:
        """Màu nền popup báo thức."""
        if AppColors._is_dark_mode:
            return [0.04, 0.04, 0.07, 1]     # Tím đen cực đậm
        return [0.02, 0.02, 0.05, 1]        # Đen mờ

    @staticmethod
    def alarm_header() -> list:
        """Màu header cảnh báo."""
        if AppColors._is_dark_mode:
            return [0.8, 0.2, 0.15, 1]      # Đỏ sáng
        return [0.95, 0.25, 0.2, 1]          # Đỏ cam

    @staticmethod
    def alarm_time() -> list:
        """Màu hiển thị giờ alarm."""
        if AppColors._is_dark_mode:
            return [1.0, 0.4, 0.3, 1]        # Cam đỏ sáng
        return [0.9, 0.2, 0.15, 1]           # Đỏ cam

    @staticmethod
    def alarm_med_card() -> list:
        """Màu card thông tin thuốc trong alarm."""
        if AppColors._is_dark_mode:
            return [0.12, 0.1, 0.1, 1]      # Nâu tối
        return [1.0, 0.97, 0.93, 1]          # Cam nhạt

    @staticmethod
    def alarm_warning() -> list:
        """Màu cảnh báo trong alarm."""
        if AppColors._is_dark_mode:
            return [0.9, 0.55, 0.2, 1]      # Cam sáng
        return [0.8, 0.4, 0.0, 1]           # Cam đỏ

    # ==========================================================================
    # CHATBOT
    # ==========================================================================

    @staticmethod
    def bubble_user() -> list:
        """Màu bong bóng người dùng."""
        if AppColors._is_dark_mode:
            return [0.25, 0.45, 0.8, 1]      # Xanh dương tối
        return [0.2, 0.6, 0.9, 1]            # Xanh dương

    @staticmethod
    def bubble_ai_danger() -> list:
        """Màu bong bóng AI - nguy hiểm (đỏ)."""
        if AppColors._is_dark_mode:
            return [0.6, 0.1, 0.08, 1]      # Đỏ đậm sáng
        return [0.95, 0.2, 0.15, 1]          # Đỏ

    @staticmethod
    def bubble_ai_warning() -> list:
        """Màu bong bóng AI - cảnh báo (cam)."""
        if AppColors._is_dark_mode:
            return [0.7, 0.45, 0.1, 1]      # Cam đậm sáng
        return [1.0, 0.7, 0.2, 1]            # Cam

    @staticmethod
    def bubble_ai_safe() -> list:
        """Màu bong bóng AI - an toàn (xanh)."""
        if AppColors._is_dark_mode:
            return [0.15, 0.25, 0.18, 1]    # Xanh lá tối sáng
        return [0.85, 0.93, 0.85, 1]        # Xanh lá nhạt

    @staticmethod
    def btn_emergency() -> list:
        """Màu nút khẩn cấp."""
        if AppColors._is_dark_mode:
            return [0.8, 0.15, 0.1, 1]      # Đỏ sáng
        return [0.9, 0.15, 0.1, 1]           # Đỏ

    # ==========================================================================
    # CROSSCHECK / ĐỐI CHIẾU
    # ==========================================================================

    @staticmethod
    def crosscheck_form_bg() -> list:
        """Màu nền form chỉnh sửa."""
        if AppColors._is_dark_mode:
            return [0.08, 0.1, 0.18, 1]     # Xanh tím tối
        return [0.97, 0.97, 1.0, 1]         # Xanh nhạt

    @staticmethod
    def crosscheck_success_bg() -> list:
        """Màu nền thành công."""
        if AppColors._is_dark_mode:
            return [0.1, 0.22, 0.12, 1]     # Xanh lá tối
        return [0.9, 1.0, 0.9, 1]            # Xanh lá nhạt

    @staticmethod
    def crosscheck_image_bg() -> list:
        """Màu nền vùng ảnh gốc."""
        if AppColors._is_dark_mode:
            return [0.1, 0.1, 0.12, 1]      # Tím đen
        return [0.97, 0.97, 0.95, 1]        # Xám ngà

    @staticmethod
    def crosscheck_confirm_bg() -> list:
        """Màu nền vùng xác nhận."""
        if AppColors._is_dark_mode:
            return [0.15, 0.12, 0.08, 1]    # Nâu tối
        return [1.0, 0.98, 0.9, 1]          # Vàng nhạt

    # ==========================================================================
    # THEME TRIGGER - THAY ĐỔI CHẾ ĐỘ
    # ==========================================================================

    @classmethod
    def toggle(cls) -> bool:
        """Chuyển đổi Light/Dark mode. Trả về trạng thái mới."""
        cls._is_dark_mode = not cls._is_dark_mode
        return cls._is_dark_mode


# ============================================================================
# THEME MANAGER - QUẢN LÝ SỰ KIỆN THAY ĐỔI THEME
# ============================================================================


class ThemeManager(EventDispatcher):
    """
    Quản lý theme của ứng dụng.
    Khi theme thay đổi → thông báo cho tất cả widget lắng nghe.
    """
    is_dark = BooleanProperty(False)

    _instance = None

    def __new__(cls):
        """Singleton pattern - chỉ có 1 instance."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        super().__init__()
        self.is_dark = AppColors.is_dark()
        # Đăng ký event type trước khi dispatch (bắt buộc của EventDispatcher)
        self.register_event_type("on_theme_changed")

    def toggle(self):
        """Chuyển đổi theme."""
        AppColors.toggle()
        self.is_dark = AppColors.is_dark()
        self.dispatch("on_theme_changed")

    def set_theme(self, is_dark: bool):
        """Đặt theme cụ thể."""
        AppColors.set_dark_mode(is_dark)
        self.is_dark = is_dark
        self.dispatch("on_theme_changed")

    def bind_theme_callback(self, callback):
        """Đăng ký callback khi theme thay đổi."""
        self.bind(on_theme_changed=callback)

    # Sự kiện thay đổi theme
    def on_theme_changed(self, *args):
        """Sự kiện được gọi khi theme thay đổi."""
        pass
