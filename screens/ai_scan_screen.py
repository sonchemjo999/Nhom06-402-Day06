"""
=============================================================================
 AIScanScreen - Màn hình Mô phỏng AI đọc đơn thuốc
=============================================================================
 File: screens/ai_scan_screen.py
 Mô tả: Tích hợp AI core (LangGraph + OpenAI) để đọc đơn thuốc.
         Nếu AI agent không khả dụng (thiếu API key, dependencies),
         tự động fallback về mock data.

         Hiển thị loading spinner trong khi AI xử lý,
         sau đó chuyển sang màn hình xác nhận y khoa.
=============================================================================
"""

import threading
from kivymd.uix.screen import MDScreen
from kivy.clock import Clock
from kivy.properties import BooleanProperty


class AIScanScreen(MDScreen):
    """
    Màn hình quét đơn thuốc bằng AI.
    Sử dụng threading để gọi AI agent không block UI.
    """

    is_scanning = BooleanProperty(False)

    def start_scan(self):
        """
        Bắt đầu quá trình quét đơn thuốc.
        Chạy AI agent trên background thread để không block UI.
        """
        if self.is_scanning:
            return  # Tránh bấm nhiều lần

        self.is_scanning = True

        # Chạy AI trên background thread
        thread = threading.Thread(target=self._run_ai_scan, daemon=True)
        thread.start()

    def _run_ai_scan(self):
        """
        Chạy AI scan trên background thread.
        Gọi ai_core.agent.scan_prescription() rồi schedule kết quả
        về main thread qua Clock.
        """
        try:
            from ai_core.agent import scan_prescription
            result = scan_prescription(case="random")
        except Exception as e:
            print(f"[AIScanScreen] [X] Loi goi AI: {e}")
            # Fallback: import mock data trực tiếp
            import random
            from data.mock_data import MOCK_RESULT_SUCCESS, MOCK_RESULT_FAILURE
            result = random.choice([MOCK_RESULT_SUCCESS, MOCK_RESULT_FAILURE])

        # Schedule callback về main thread (Kivy yêu cầu UI update trên main thread)
        Clock.schedule_once(lambda dt: self._on_scan_complete(result), 0)

    def _on_scan_complete(self, result: dict):
        """
        Callback khi AI xử lý xong (chạy trên main thread).

        Tham số:
            result (dict): Kết quả từ AI core
        """
        self.is_scanning = False

        # Truyền kết quả sang CrossCheckScreen
        crosscheck_screen = self.manager.get_screen("crosscheck")
        crosscheck_screen.receive_ai_result(result)

        # Chuyển màn hình
        self.manager.current = "crosscheck"

    def go_back(self):
        """Quay lại màn hình chính."""
        self.manager.current = "home"
