"""
==============================================================================
 AIScanScreen - Màn hình Quét đơn thuốc (Mock Mode)
==============================================================================
 File: screens/ai_scan_screen.py

 Chế độ: Mock — không dùng camera thực.
 Người dùng chọn loại case để mô phỏng AI đọc đơn.
 Sau đó chuyển sang CrossCheckScreen để xác nhận.

 Luồng:
   Chọn case (Clear / Mờ / Card / Viết tay / Vết bẩn)
   → confirm_and_scan()
   → Background thread: scan_prescription()
   → CrossCheckScreen (xác nhận)
==============================================================================
"""

import os
import threading
import random

from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDRaisedButton, MDFlatButton
from kivymd.uix.label import MDLabel
from kivymd.uix.progressbar import MDProgressBar
from kivymd.uix.dialog import MDDialog
from kivymd.uix.snackbar import Snackbar

from kivy.clock import Clock
from kivy.properties import BooleanProperty, NumericProperty, StringProperty


class AIScanScreen(MDScreen):
    """
    Màn hình quét đơn thuốc — mock mode (không camera).
    """

    is_scanning = BooleanProperty(False)
    scan_progress = NumericProperty(0)

    # Danh sách case để chọn
    CASES = [
        ("Đơn rõ ràng", "clear", "Đơn điện tử, chữ in rõ"),
        ("Đơn mờ / nhòe", "blurry", "Chữ mờ, khó đọc"),
        ("Đơn trên card nhỏ", "card", "Đơn viết tay trên card"),
        ("Đơn viết tay", "handwritten", "Chữ viết nguệch ngoạc"),
        ("Đơn có vết bẩn", "stain", "Có vết nước/dầu trên ảnh"),
        ("Ngẫu nhiên", "random", "AI tự chọn case phù hợp"),
    ]

    def on_enter(self):
        self.is_scanning = False
        self.scan_progress = 0
        # Tránh gọi scan đồng bộ ngay trong on_enter (tranh xung đột layout)
        Clock.schedule_once(lambda dt: self.start_scan("random"), 0.1)

    # =========================================================================
    # SCAN — chạy trên background thread
    # =========================================================================
    def start_scan(self, case: str = "random"):
        """
        Bắt đầu mock scan với case đã chọn.
        """
        if self.is_scanning:
            return

        self.is_scanning = True
        self.scan_progress = 0

        # Animate progress bar
        Clock.schedule_interval(self._animate_progress, 0.05)

        # Chạy AI trên thread riêng
        thread = threading.Thread(
            target=self._run_mock_scan,
            args=(case,),
            daemon=True
        )
        thread.start()

    def _animate_progress(self, dt):
        if not self.is_scanning:
            Clock.unschedule(self._animate_progress)
            return False
        if self.scan_progress < 90:
            self.scan_progress += random.uniform(2.0, 5.0)
        return True

    def _run_mock_scan(self, case: str):
        """Gọi agent.scan_prescription() rồi callback về main thread."""
        try:
            from ai_core.agent import scan_prescription
            result = scan_prescription(image_path=None, case=case)
            Clock.schedule_once(
                lambda dt: self._on_scan_complete(result), 0
            )
        except Exception as e:
            print(f"[AIScan] Loi: {e}")
            Clock.schedule_once(
                lambda dt: self._on_scan_error(str(e)), 0
            )

    def _on_scan_complete(self, result: dict):
        self.is_scanning = False
        self.scan_progress = 100
        Clock.unschedule(self._animate_progress)

        confidence = result.get("confidence", 0)
        if confidence < 0.6:
            self._show_dialog(
                title="Cảnh báo",
                text=(f"Độ tự tin: {confidence:.0%}.\n"
                      "Một số thông tin có thể không chính xác.\n"
                      "Vui lòng kiểm tra kỹ trước khi lưu."),
                actions=[
                    {"text": "Đã hiểu", "callback": lambda r=result: self._navigate_to_crosscheck(r)},
                    {"text": "Thử lại", "callback": self._retry},
                ]
            )
        else:
            self._navigate_to_crosscheck(result)

    def _on_scan_error(self, msg: str):
        self.is_scanning = False
        self.scan_progress = 0
        Clock.unschedule(self._animate_progress)
        try:
            Snackbar(text=f"Lỗi: {msg}", duration=3).open()
        except Exception:
            pass

    def _navigate_to_crosscheck(self, result: dict):
        """Chuyển màn sau frame tiếp theo (tránh xung đột với dialog / animation)."""
        Clock.schedule_once(lambda dt: self._do_navigate_to_crosscheck(result), 0)

    def _do_navigate_to_crosscheck(self, result: dict):
        try:
            crosscheck = self.manager.get_screen("crosscheck")
            crosscheck.receive_ai_result(result)
            self.manager.current = "crosscheck"
        except Exception as e:
            print(f"[AIScan] Loi chuyen man: {e}")
            import traceback
            traceback.print_exc()
            try:
                Snackbar(text=f"Lỗi màn hình xác nhận: {e}", duration=4).open()
            except Exception:
                pass

    def _retry(self, *args):
        self.is_scanning = False
        self.scan_progress = 0
        Clock.schedule_once(lambda dt: self.start_scan("random"), 0)

    # =========================================================================
    # HELPER
    # =========================================================================
    def _dialog_dismiss_then(self, callback):
        """Đóng dialog hiện tại rồi gọi callback (self._dialog đã gán trước khi mở)."""
        dlg = getattr(self, "_dialog", None)
        if dlg is not None:
            try:
                dlg.dismiss()
            except Exception:
                pass
        self._dialog = None
        if callback:
            callback()

    def _show_dialog(self, title: str, text: str, actions: list):
        try:
            btn_list = []
            for act in actions:
                cb = act.get("callback")
                btn_list.append(
                    MDFlatButton(
                        text=act.get("text", "OK"),
                        on_release=lambda x, c=cb: self._dialog_dismiss_then(c),
                    )
                )
            self._dialog = MDDialog(
                title=title,
                text=text,
                buttons=btn_list,
                auto_dismiss=False,
            )
            self._dialog.open()
        except Exception as e:
            print(f"[AIScan] Dialog error: {e}")
            import traceback
            traceback.print_exc()

    def go_back(self):
        self.manager.current = "home"
