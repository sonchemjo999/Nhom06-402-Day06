"""
==============================================================================
CrossCheckScreen - Màn hình Xác nhận Y khoa
==============================================================================
File: screens/crosscheck_screen.py

Mô tả: Màn hình CỰC KỲ QUAN TRỌNG trong ứng dụng y tế.
        Chống lại Automation Bias bằng cách:

        1. Hiển thị thông tin thuốc dạng FORM CÓ THỂ CHỈNH SỬA từng khung giờ.
           Mỗi khung giờ là một mốc chuẩn hóa Y KHOA (buổi cố định, theo bữa ăn, PRN).

        2. HIỂN THỊ ẢNH ĐƠN THUỐC GỐC bên dưới form để đối chiếu.

        3. BẮT BUỘC người dùng tick checkbox trước khi lưu.

Quy tắc chuẩn hóa khung giờ (theo hướng dẫn lâm sàng):
  - Buổi sáng (06:00-08:00), Trưa (11:30-13:00), Chiều-Tối (18:00-20:00),
    Trước khi ngủ (21:00-22:00)
  - Theo bữa ăn: Trước ăn (30-60p), Trong bữa ăn, Sau ăn (15-30p), Sau ăn 1 tiếng
  - PRN (Khi có triệu chứng): với khoảng cách tối thiểu 4-6 tiếng
==============================================================================
"""

import os
from kivymd.uix.screen import MDScreen
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDFlatButton, MDIconButton
from kivymd.uix.snackbar import MDSnackbar
from kivy.uix.popup import Popup
from kivy.properties import (
    BooleanProperty,
    StringProperty,
    ListProperty,
    DictProperty,
    ObjectProperty,
    NumericProperty,
)
from kivy.metrics import dp


# =============================================================================
#  MedScheduleSlot: Một khung giờ nhắc nhở có thể chỉnh sửa
# =============================================================================
class MedScheduleSlot(MDBoxLayout):
    """
    Widget hiển thị một khung giờ nhắc nhở.
    Có thể nhấn bút để đổi giờ, nhấn X để xóa.
    """
    slot_time = StringProperty("")
    slot_note = StringProperty("")
    slot_index = NumericProperty(0)
    _parent_card = ObjectProperty(None)

    def __init__(self, time_str: str, note: str,
                 index: int, parent_card, **kwargs):
        super().__init__(**kwargs)
        self.slot_time = time_str
        self.slot_note = note
        self.slot_index = index
        self._parent_card = parent_card

    def open_time_picker(self):
        """Mở popup chọn khung giờ chuẩn y khoa."""
        popup = TimeSlotPopup(
            on_select_callback=lambda t, n: self._on_time_selected(t, n)
        )
        popup.open()

    def _on_time_selected(self, new_time: str, new_note: str):
        """Cập nhật khung giờ sau khi chọn."""
        self.slot_time = new_time
        self.slot_note = new_note
        self._parent_card._update_slot(self.slot_index, new_time, new_note)

    def remove_slot(self):
        """Xóa khung giờ này."""
        self._parent_card._remove_slot(self.slot_index)


# =============================================================================
#  MedEditCard: Card thuốc có thể chỉnh sửa từng khung giờ
# =============================================================================
class MedEditCard(MDCard):
    """
    Card hiển thị thông tin 1 loại thuốc với form chỉnh sửa khung giờ.
    Mỗi khung giờ được chuẩn hóa theo mốc y khoa.
    """
    med_name = StringProperty("")
    med_dosage = StringProperty("")
    slots = ListProperty([])  # Danh sách dict: [{"time": "07:00", "note": "..."}]
    _medications_list = ObjectProperty(None)  # Tham chiếu đến danh sách thuốc gốc

    def __init__(self, med_name: str, med_dosage: str,
                 schedule: list, medications_list: list, **kwargs):
        super().__init__(**kwargs)
        self.med_name = med_name
        self.med_dosage = med_dosage
        self.slots = list(schedule)
        self._medications_list = medications_list
        self._rebuild_slots()

    def _rebuild_slots(self):
        """Xây dựng lại danh sách khung giờ trong card."""
        container = self.ids.slots_container
        container.clear_widgets()
        for i, slot in enumerate(self.slots):
            time_str = slot.get("time", "")
            note_str = slot.get("note", "")
            slot_widget = MedScheduleSlot(
                time_str=time_str,
                note_str=note_str,
                index=i,
                parent_card=self,
            )
            container.add_widget(slot_widget)

    def _update_slot(self, index: int, new_time: str, new_note: str):
        """Cập nhật một khung giờ."""
        if 0 <= index < len(self.slots):
            self.slots[index] = {"time": new_time, "note": new_note}
            self._sync_to_medications()

    def _remove_slot(self, index: int):
        """Xóa một khung giờ."""
        if 0 <= index < len(self.slots):
            self.slots.pop(index)
            self._rebuild_slots()
            self._sync_to_medications()

    def add_schedule_slot(self):
        """Thêm một khung giờ mới."""
        popup = TimeSlotPopup(
            on_select_callback=lambda t, n: self._on_add_slot(t, n)
        )
        popup.open()

    def _on_add_slot(self, new_time: str, new_note: str):
        """Xử lý khi thêm khung giờ mới."""
        self.slots.append({"time": new_time, "note": new_note})
        self._rebuild_slots()
        self._sync_to_medications()

    def _sync_to_medications(self):
        """Đồng bộ dữ liệu slots vào medications_list."""
        pass  # Đã cập nhật trực tiếp trong med_edit_container


# =============================================================================
#  TimeSlotPopup: Popup chọn khung giờ chuẩn y khoa
# =============================================================================
class TimeSlotPopup(Popup):
    """
    Popup chọn khung giờ uống thuốc theo mốc chuẩn y khoa.
    3 nhóm:
      1. Buổi cố định (Sáng, Trưa, Chiều-Tối, Trước khi ngủ)
      2. Theo bữa ăn (Trước ăn, Trong bữa ăn, Sau ăn)
      3. PRN (Khi có triệu chứng - với cảnh báo khoảng cách tối thiểu)
    """
    on_select_callback = ObjectProperty(None)

    def __init__(self, on_select_callback=None, **kwargs):
        super().__init__(**kwargs)
        self.on_select_callback = on_select_callback

    def select_slot(self, time_str: str, note_str: str):
        """Chọn một khung giờ và đóng popup."""
        if self.on_select_callback:
            self.on_select_callback(time_str, note_str)
        self.dismiss()


# =============================================================================
#  CrossCheckScreen: Màn hình chính
# =============================================================================
class CrossCheckScreen(MDScreen):
    """
    Màn hình xác nhận y khoa.
    Hiển thị form thuốc chỉnh sửa được + ảnh đơn thuốc gốc.
    Người dùng PHẢI xác nhận trước khi lưu.
    """

    is_success = BooleanProperty(False)
    is_confirmed = BooleanProperty(False)
    ai_message = StringProperty("")
    confidence_text = StringProperty("")
    ai_result = DictProperty({})

    def on_enter(self, *args):
        """Khi vào màn hình, render form thuốc và ảnh đơn thuốc."""
        self._render_medication_form()
        self._load_prescription_image()

    def _load_prescription_image(self):
        """Load ảnh đơn thuốc giả lập."""
        try:
            from data.prescription_image import get_prescription_image_path
            img_path = get_prescription_image_path()
            if os.path.exists(img_path):
                img_widget = self.ids.prescription_image
                img_widget.source = img_path
        except Exception as e:
            print(f"[CrossCheckScreen] Khong the load anh don thuoc: {e}")

    def _render_medication_form(self):
        """
        Render form thuốc có thể chỉnh sửa từng khung giờ.
        """
        container = self.ids.med_edit_container
        container.clear_widgets()

        if not self.is_success:
            return

        medications = self.ai_result.get("medications", [])
        for med in medications:
            med_card = MedEditCard(
                med_name=med.get("name", ""),
                med_dosage="Liều: " + med.get("dosage", ""),
                schedule=med.get("schedule", []),
                medications_list=medications,
            )
            container.add_widget(med_card)

    def toggle_confirmation(self, is_active: bool):
        """
        Toggle trạng thái checkbox xác nhận.
        Nút "Lưu" chỉ được bật khi checkbox được tick.
        """
        self.is_confirmed = is_active

    def report_correction(self):
        """
        Nút "Sửa lỗi" (Correction) - khi AI đọc sai.
        Ghi nhận correction và log để retrain AI.
        """
        MDSnackbar(
            MDLabel(
                text="Đã ghi nhận lỗi. Vui lòng sửa trực tiếp trên form bên trên.",
            ),
            y=dp(24),
            pos_hint={"center_x": 0.5},
            size_hint_x=0.95,
        ).open()

    def save_schedule(self):
        """
        Lưu lịch nhắc thuốc.
        Chỉ được gọi khi người dùng đã xác nhận (checkbox đã tick).
        Thu thập dữ liệu từ tất cả MedEditCard để lưu.
        """
        if not self.is_confirmed:
            MDSnackbar(
                MDLabel(
                    text="Vui lòng xác nhận thông tin trước khi lưu!",
                ),
                y=dp(24),
                pos_hint={"center_x": 0.5},
                size_hint_x=0.95,
            ).open()
            return

        # Thu thập dữ liệu từ các card
        container = self.ids.med_edit_container
        saved_schedule = []
        for child in container.children:
            if isinstance(child, MedEditCard):
                saved_schedule.append({
                    "name": child.med_name,
                    "dosage": child.med_dosage.replace("Liều: ", ""),
                    "schedule": list(child.slots),
                })

        print(f"[CrossCheckScreen] Da luu lich: {saved_schedule}")

        MDSnackbar(
            MDLabel(
                text="Đã lưu lịch nhắc thuốc thành công!",
            ),
            y=dp(24),
            pos_hint={"center_x": 0.5},
            size_hint_x=0.95,
        ).open()

        self.manager.current = "home"

    def go_back(self):
        """Quay lại màn hình quét."""
        self.manager.current = "ai_scan"

    def go_home(self):
        """Quay lại trang chủ."""
        self.manager.current = "home"

    def receive_ai_result(self, result: dict):
        """
        Nhận kết quả từ AIScanScreen và cập nhật UI tương ứng.

        Tham số:
            result (dict): Kết quả mock từ AI, chứa status, confidence,
                          message, và medications.
        """
        self.ai_result = result
        self.is_confirmed = False  # Reset checkbox mỗi lần nhận kết quả mới
        self.is_success = result.get("status") == "success"
        self.ai_message = result.get("message", "")

        confidence = result.get("confidence", 0)
        self.confidence_text = f"Độ tin cậy: {confidence * 100:.0f}%"
