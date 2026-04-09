"""
==============================================================================
 ChatbotScreen - Màn hình Chatbot AI Triage
==============================================================================
 File: screens/chatbot_screen.py

 Mô tả: Giao diện chat giống Messenger/Zalo để hỏi triệu chứng.
        Tách riêng send_message() và receive_message() để sau này
        dễ dàng cắm module TTS (Text-to-Speech) và STT (Speech-to-Text).

 Logic Triage (theo spec):
   - GREEN: từ khóa bình thường -> ghi nhận
   - YELLOW: từ khóa mờ hỏi -> hỏi thêm mức độ 1-10
   - RED: từ khóa nguy hiểm -> cảnh báo ĐỎ + nút gọi cấp cứu
==============================================================================
"""

from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDRaisedButton, MDFlatButton
from kivymd.uix.textfield import MDTextField
from kivymd.app import MDApp
from kivy.properties import StringProperty, BooleanProperty, ListProperty
from kivy.metrics import dp
from kivy.clock import Clock


# === TỪ KHÓA PHÂN LOẠI TRIỆU CHỨNG ===

# RED - Nguy hiểm, cần cấp cứu ngay
RED_KEYWORDS = [
    "kho tho", "khó thở",
    "sot cao", "sốt cao",
    "co giat", "co giật",
    "dau nguc", "đau ngực",
    "bat tinh", "bất tỉnh",
    "xuat huyet", "xuất huyết",
    "ngat", "ngất",
    "sot 40", "sốt 40",
    "sot 41", "sốt 41",
]

# YELLOW - Cần theo dõi, hỏi thêm
YELLOW_KEYWORDS = [
    "met", "mệt",
    "dau dau", "đau đầu",
    "buon non", "buồn nôn",
    "chong mat", "chóng mặt",
    "mat ngu", "mất ngủ",
    "phat ban", "phát ban",
    "dau bung", "đau bụng",
    "tieu chay", "tiêu chảy",
]

# GREEN - Bình thường
GREEN_KEYWORDS = [
    "tot", "tốt",
    "binh thuong", "bình thường",
    "on", "ổn",
    "khoe", "khỏe",
    "ok", "good",
    "duoc", "được",
]


class ChatBubble(MDCard):
    """Widget hiển thị 1 tin nhắn trong chat."""
    message_text = StringProperty("")
    is_user = BooleanProperty(False)
    bubble_color = ListProperty([0.9, 0.9, 0.9, 1])


class ChatbotScreen(MDScreen):
    """
    Màn hình Chatbot AI - Giao diện chat triage triệu chứng.
    Tách riêng send/receive để cắm TTS/STT sau này.
    """

    show_emergency_button = BooleanProperty(False)

    def on_enter(self, *args):
        """Khi vào màn hình, chatbot tự động chào."""
        Clock.schedule_once(lambda dt: self._auto_greet(), 0.5)

    def _auto_greet(self):
        """Chatbot chào hỏi - trigger daily check."""
        container = self.ids.chat_container
        # Chỉ chào nếu chưa có tin nhắn nào
        if len(container.children) == 0:
            self.receive_message(
                "Xin chào! Tôi là trợ lý y tế ảo của bạn.\n"
                "Hôm nay sức khỏe của bạn sau khi dùng thuốc thế nào?"
            )

    def send_message(self, text: str):
        """
        GỬI TIN NHẮN TỪ USER.
        Tách riêng để sau này cắm STT (Speech-to-Text):
          stt_result = stt_module.recognize()
          send_message(stt_result)

        Tham số:
            text: Nội dung tin nhắn của user
        """
        if not text.strip():
            return

        # Hiển thị tin nhắn user lên UI
        container = self.ids.chat_container
        _app = MDApp.get_running_app()
        bubble = ChatBubble(
            message_text=text.strip(),
            is_user=True,
            # Màu user bubble từ app
            bubble_color=_app.bubble_user_color,
        )
        container.add_widget(bubble)

        # Xóa textfield
        self.ids.chat_input.text = ""

        # Scroll xuống cuối
        self.ids.chat_scroll.scroll_y = 0

        # Xử lý và trả lời sau 0.5s (giả lập "đang suy nghĩ")
        Clock.schedule_once(lambda dt: self._process_user_input(text.strip()), 0.5)

    def receive_message(self, text: str, level: str = "normal"):
        """
        NHẬN TIN NHẮN TỪ AI BOT.
        Tách riêng để sau này cắm TTS (Text-to-Speech):
          tts_module.speak(text)

        Tham số:
            text: Nội dung phản hồi của AI
            level: "normal", "warning", "danger"
        """
        container = self.ids.chat_container

        # Màu sắc theo mức độ
        _app = MDApp.get_running_app()
        if level == "danger":
            color = _app.bubble_ai_danger_color
        elif level == "warning":
            color = _app.bubble_ai_warning_color
        else:
            color = _app.bubble_ai_safe_color

        bubble = ChatBubble(
            message_text=text,
            is_user=False,
            bubble_color=color,
        )
        container.add_widget(bubble)

        # Scroll xuống cuối
        Clock.schedule_once(lambda dt: self._scroll_bottom(), 0.1)

    def _scroll_bottom(self):
        """Scroll chat xuống tin nhắn mới nhất."""
        try:
            self.ids.chat_scroll.scroll_y = 0
        except Exception:
            pass

    def _process_user_input(self, text: str):
        """
        Phân tích input của user và phân loại triệu chứng.
        """
        text_lower = text.lower()

        # === CHECK RED (nguy hiểm) ===
        is_red = False
        for kw in RED_KEYWORDS:
            if kw in text_lower:
                is_red = True
                break

        if is_red:
            self._respond_red(text)
            return

        # === CHECK YELLOW (cần theo dõi) ===
        is_yellow = False
        for kw in YELLOW_KEYWORDS:
            if kw in text_lower:
                is_yellow = True
                break

        if is_yellow:
            self._respond_yellow(text)
            return

        # === CHECK GREEN (bình thường) ===
        is_green = False
        for kw in GREEN_KEYWORDS:
            if kw in text_lower:
                is_green = True
                break

        if is_green:
            self._respond_green()
            return

        # === DEFAULT: Không nhận diện được ===
        self.receive_message(
            "Cảm ơn bạn đã chia sẻ. Bạn có thể mô tả chi tiết hơn "
            "triệu chứng của mình được không?\n\n"
            "Ví dụ: mệt mỏi, đau đầu, buồn nôn, khó thở..."
        )

    def _respond_green(self):
        """Phản hồi khi user bình thường."""
        self.show_emergency_button = False
        self.receive_message(
            "Tuyệt vời! Rất vui khi bạn cảm thấy tốt.\n"
            "Hãy tiếp tục duy trì uống thuốc đúng giờ nhé!\n\n"
            "Nếu có bất kỳ thay đổi nào, hãy báo cho tôi biết.",
            level="normal"
        )

    def _respond_yellow(self, text: str):
        """Phản hồi khi triệu chứng cần theo dõi (YELLOW)."""
        self.show_emergency_button = False
        self.receive_message(
            "Tôi ghi nhận triệu chứng của bạn.\n\n"
            "Bạn có thể đánh giá mức độ từ 1 đến 10 không?\n"
            "  - 1-3: Nhẹ, có thể theo dõi tại nhà\n"
            "  - 4-6: Trung bình, nên liên hệ bác sĩ\n"
            "  - 7-10: Nặng, cần khám ngay\n\n"
            "Nếu tình trạng nặng hơn, đừng ngại ngại "
            "nhấn nút 'Gọi cấp cứu' bên dưới.",
            level="warning"
        )

    def _respond_red(self, text: str):
        """
        Phản hồi khi triệu chứng NGUY HIỂM (RED).
        Hiện nút gọi cấp cứu.
        """
        self.show_emergency_button = True
        self.receive_message(
            "CẢNH BÁO! Triệu chứng bạn mô tả có thể NGUY HIỂM.\n\n"
            "Bạn cần được hỗ trợ y tế NGAY LẬP TỨC!\n\n"
            "Vui lòng:\n"
            "1. Giữ bình tĩnh\n"
            "2. Nhấn nút 'Tìm bệnh viện cấp cứu' bên dưới\n"
            "3. Hoặc gọi 115 (Cấp cứu) ngay",
            level="danger"
        )

    def find_emergency_hospital(self):
        """
        Nút 'Tìm bệnh viện cấp cứu gần nhất'.
        Trong MVP: hiển thị thông tin mock.
        Production: gọi Google Maps API + GPS.
        """
        self.receive_message(
            "BỆNH VIỆN GẦN BẠN NHẤT:\n\n"
            "1. Vinmec Times City\n"
            "   458 Minh Khai, Hai Bà Trưng, Hà Nội\n"
            "   Hotline: 024 3974 3556\n"
            "   Khoảng cách: ~2.5km\n\n"
            "2. Bệnh viện Bạch Mai\n"
            "   78 Giải Phóng, Đống Đa, Hà Nội\n"
            "   Cấp cứu: 024 3869 3731\n"
            "   Khoảng cách: ~4km\n\n"
            "Gọi 115 để được cấp cứu ngay!",
            level="danger"
        )

    def go_back(self):
        """Quay lại trang chủ."""
        self.manager.current = "home"
