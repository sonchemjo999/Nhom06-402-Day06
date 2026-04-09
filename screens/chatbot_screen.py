"""
==============================================================================
 ChatbotScreen - Màn hình Chatbot AI Y tế (LangGraph Agent)
==============================================================================
 File: screens/chatbot_screen.py

 Giao diện chat giống Messenger/Zalo.
 Tích hợp LangGraph Agent từ ai_core/chatbot_agent.py:
   - Persona y tế miền Nam ngọt ngào
   - 5 tools: tra liều, tương tác thuốc, tác dụng phụ, bệnh viện, triệu chứng
   - MemorySaver: nhớ toàn bộ lịch sử hội thoại
   - Fallback: keyword matching nếu không có API key

 Phân loại phản hồi:
   - RED    : cảnh báo nguy hiểm → hiện nút gọi cấp cứu
   - YELLOW : cần theo dõi → hỏi mức độ 1-10
   - GREEN  : bình thường → động viên
==============================================================================
"""

import re
import uuid
import time as _time

from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDRaisedButton, MDFlatButton
from kivymd.uix.textfield import MDTextField
from kivymd.app import MDApp
from kivy.properties import StringProperty, BooleanProperty, ListProperty, ObjectProperty
from kivy.metrics import dp
from kivy.clock import Clock


# ============================================================================
# DETECT LEVEL TỪ PHẢN HỒI AI
# ============================================================================

# Emoji: Noto Color Emoji chỉ có glyph emoji — không dùng làm font duy nhất (chữ Việt sẽ mất).
_EMOJI_RUN = re.compile(
    "["
    "\U0001F1E6-\U0001F1FF"  # cờ (2 ký tự liên tiếp)
    "\U0001F300-\U0001FAFF"
    "\U00002600-\U000027BF"
    "\U0001F600-\U0001F64F"
    "\U0001F680-\U0001F6FF"
    "\U0000200D\U0000FE0F"
    "\U0001F3FB-\U0001F3FF"  # tông da
    "]+"
)


def _strip_emoji(raw: str) -> str:
    """Bỏ emoji để hiển thị an toàn."""
    return _EMOJI_RUN.sub("", raw) if raw else ""


def _detect_level(text: str) -> str:
    """Tự động phát hiện mức độ phản hồi từ nội dung AI."""
    t = text.lower()
    if any(kw in t for kw in ["cảnh báo", "nguy hiểm", "🚨", "115", "cấp cứu ngay",
                               "gọi 115", "cấp cứu ngay lập tức", "cấp cứu!"]):
        return "danger"
    if any(kw in t for kw in ["theo dõi", "⚠️", "cần chú ý", "mức độ", "1-10",
                               "nên liên hệ bác sĩ", "cần khám"]):
        return "warning"
    return "normal"


# ============================================================================
# CHAT BUBBLE WIDGET
# ============================================================================

class ChatBubble(MDCard):
    """Widget hiển thị 1 tin nhắn trong chat."""
    message_text = StringProperty("")
    display_markup = StringProperty("")
    is_user = BooleanProperty(False)
    bubble_color = ListProperty([0.9, 0.9, 0.9, 1])

    def on_message_text(self, _inst, value):
        self.display_markup = _strip_emoji(value or "")


# ============================================================================
# LOADING BUBBLE
# ============================================================================

class LoadingBubble(MDCard):
    """Widget hiển thị trạng thái 'đang suy nghĩ'."""


# ============================================================================
# CHATBOT SCREEN
# ============================================================================

class ChatbotScreen(MDScreen):
    """
    Màn hình Chatbot AI Y tế.
    Dùng LangGraph Agent từ ai_core/chatbot_agent.py.
    """

    show_emergency_button = BooleanProperty(False)
    chat_input = ObjectProperty(None)

    # Session ID cho MemorySaver (nhớ hội thoại)
    _session_id = ""
    _loading_bubble = None

    def on_enter(self, *args):
        """Khi vào màn hình, khởi tạo session và chatbot tự chào."""
        if not self._session_id:
            self._session_id = f"user_{uuid.uuid4().hex[:8]}_{int(_time.time() * 1000)}"
        Clock.schedule_once(lambda dt: self._auto_greet(), 0.5)

    def on_pre_leave(self, *args):
        """Khi rời màn hình, dừng loading."""
        self._hide_loading()

    # -------------------------------------------------------------------------
    # AUTO GREETING
    # -------------------------------------------------------------------------

    def _auto_greet(self):
        """Chatbot tự chào khi mở màn hình."""
        container = self.ids.chat_container
        if len(container.children) == 0:
            self.receive_message(GREETING_TEXT, level="normal")

    # -------------------------------------------------------------------------
    # GỬI TIN NHẮN
    # -------------------------------------------------------------------------

    def send_message(self, text: str = None):
        """
        GỬI TIN NHẮN TỪ USER.
        Chạy AI trong thread riêng để không block UI.
        """
        if text is None:
            text = self.ids.chat_input.text if self.ids.chat_input else ""

        if not text.strip():
            return

        # Hiển thị tin nhắn user lên UI
        self._add_user_bubble(text.strip())

        # Xóa input
        if self.ids.chat_input:
            self.ids.chat_input.text = ""

        # Scroll xuống cuối
        self.ids.chat_scroll.scroll_y = 0

        # Show loading
        self._show_loading()

        # Chạy AI trong thread (non-blocking)
        _run_ai_async(text.strip(), self._session_id,
                      on_result=self._on_ai_result,
                      on_error=self._on_ai_error)

    def _add_user_bubble(self, text: str):
        """Thêm bubble của user vào chat."""
        container = self.ids.chat_container
        app = MDApp.get_running_app()
        bubble = ChatBubble(
            message_text=text,
            is_user=True,
            bubble_color=app.bubble_user_color,
        )
        container.add_widget(bubble)

    # -------------------------------------------------------------------------
    # NHẬN TIN NHẮN AI
    # -------------------------------------------------------------------------

    def receive_message(self, text: str, level: str = "normal"):
        """
        NHẬN TIN NHẮN TỪ AI BOT.
        Tham số:
            text : nội dung phản hồi
            level: "normal" | "warning" | "danger"
        """
        container = self.ids.chat_container
        app = MDApp.get_running_app()

        if level == "danger":
            color = app.bubble_ai_danger_color
            self.show_emergency_button = True
        elif level == "warning":
            color = app.bubble_ai_warning_color
            self.show_emergency_button = False
        else:
            color = app.bubble_ai_safe_color
            self.show_emergency_button = False

        bubble = ChatBubble(
            message_text=text,
            is_user=False,
            bubble_color=color,
        )
        container.add_widget(bubble)
        Clock.schedule_once(lambda dt: self._scroll_bottom(), 0.05)

    # -------------------------------------------------------------------------
    # CALLBACK TỪ AI THREAD
    # -------------------------------------------------------------------------

    def _on_ai_result(self, result: str):
        """Callback khi AI trả kết quả."""
        self._hide_loading()

        # Auto-detect level từ nội dung
        level = _detect_level(result)
        self.receive_message(result, level=level)

        # Scroll xuống cuối
        Clock.schedule_once(lambda dt: self._scroll_bottom(), 0.1)

    def _on_ai_error(self, error: str):
        """Callback khi AI có lỗi."""
        self._hide_loading()
        self.receive_message(
            "Xin lỗi bạn, đã có lỗi xảy ra nha! 😅\n"
            "Em sẽ trả lời lại ngay khi hệ thống ổn định.\n\n"
            "Nếu cần cấp cứu → gọi 115 ngay!",
            level="warning",
        )

    # -------------------------------------------------------------------------
    # LOADING INDICATOR
    # -------------------------------------------------------------------------

    def _show_loading(self):
        """Hiện bubble 'đang suy nghĩ'."""
        if self._loading_bubble is not None:
            return
        container = self.ids.chat_container
        app = MDApp.get_running_app()
        lb = LoadingBubble(
            size_hint=(0.65, None),
            height=dp(48),
            radius=[4, 12, 12, 4],
            padding=dp(12),
            md_bg_color=app.bubble_ai_safe_color,
            pos_hint={"right": 0.9},
        )
        dot_label = MDLabel(
            text="MedReminder đang suy nghĩ...",
            font_style="Caption",
            theme_text_color="Custom",
            text_color=app.text_secondary_color,
            halign="left",
        )
        lb.add_widget(dot_label)
        container.add_widget(lb)
        self._loading_bubble = lb
        Clock.schedule_once(lambda dt: self._scroll_bottom(), 0.05)

    def _hide_loading(self):
        """Ẩn bubble loading."""
        lb = self._loading_bubble
        if lb is not None:
            try:
                self.ids.chat_container.remove_widget(lb)
            except Exception:
                pass
            self._loading_bubble = None

    # -------------------------------------------------------------------------
    # SCROLL
    # -------------------------------------------------------------------------

    def _scroll_bottom(self):
        """Scroll chat xuống tin nhắn mới nhất."""
        try:
            self.ids.chat_scroll.scroll_y = 0
        except Exception:
            pass

    # -------------------------------------------------------------------------
    # HÀNH ĐỘNG
    # -------------------------------------------------------------------------

    def find_emergency_hospital(self):
        """
        Tìm bệnh viện cấp cứu — gọi tool qua AI.
        """
        self.receive_message(
            "Em đang tìm bệnh viện cấp cứu gần bạn nhất nha...",
            level="warning",
        )
        _run_ai_async(
            "Tìm bệnh viện cấp cứu gần nhất",
            self._session_id,
            on_result=self._on_ai_result,
            on_error=self._on_ai_error,
        )

    def go_back(self):
        """Quay lại trang chủ."""
        self.manager.current = "home"


# ============================================================================
# AI ENGINE — GỌI TỪ THREAD RIÊNG
# ============================================================================

def _run_ai_async(user_message: str, session_id: str,
                  on_result=None, on_error=None):
    """
    Chạy chatbot agent trong thread riêng, gọi callback khi xong.
    """
    def _execute():
        try:
            from ai_core.chatbot_agent import chatbot_reply_sync
            result = chatbot_reply_sync(user_message, session_id)
            Clock.schedule_once(lambda dt: on_result(result), 0)
        except Exception as e:
            print(f"[ChatbotScreen] AI error: {e}")
            err_msg = str(e)
            if on_error:
                Clock.schedule_once(lambda dt: on_error(err_msg), 0)

    import threading
    t = threading.Thread(target=_execute, daemon=True)
    t.start()


# ============================================================================
# GREETING TEXT
# ============================================================================

GREETING_TEXT = (
    "Xin chào! 🌸 Em là trợ lý y tế của MedReminder nè!\n\n"
    "Hôm nay sức khỏe của anh/chị sau khi dùng thuốc thế nào rồi, có triệu chứng gì không?\n\n"
    "Em lắng nghe anh/chị nha! 😊"
)
