"""
==============================================================================
 Shared Data Store — lưu trữ lịch thuốc giữa các màn hình
==============================================================================
 File: data/schedule_store.py

 Cơ chế:
   - Module-level singleton `_store` giữ lịch thuốc hiện tại.
   - Kivy EventDispatcher để các widget subscribe thay đổi.
   - CrossCheckScreen  gọi  schedule_store.save(medications)
   - HomeScreen       gọi  schedule_store.load()  trong load_schedule()
   - AlarmService     đọc   schedule_store.get_all() để lên lịch alarm.
==============================================================================
"""

from kivy.event import EventDispatcher
from kivy.properties import ListProperty

# Giá trị mặc định ban đầu (đọc từ mock_data để khởi tạo)
from data.mock_data import SAMPLE_SCHEDULE
from data.med_icons import resolve_med_icon


def _normalize_schedule_row(item: dict) -> dict:
    """Đảm bảo mỗi dòng có icon để MedCard / AlarmPopup hiển thị."""
    row = dict(item)
    icon = row.get("icon") or ""
    if not str(icon).strip():
        row["icon"] = resolve_med_icon(row.get("name", ""))
    return row


class ScheduleStore(EventDispatcher):
    """
    Shared store: lưu trữ lịch thuốc hiện tại và thông báo khi thay đổi.
    """
    medications = ListProperty([])

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.medications = [
                _normalize_schedule_row(x) for x in SAMPLE_SCHEDULE
            ]
        return cls._instance

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def save(self, medications: list):
        """
        Lưu lịch thuốc mới (từ CrossCheckScreen).
        Tự động kích hoạt property on_change để UI cập nhật.
        """
        self.medications = [
            _normalize_schedule_row(x) for x in medications
        ]
        print(f"[ScheduleStore] Da luu {len(self.medications)} muc lich")

    def load(self) -> list:
        """Trả về danh sách thuốc hiện tại (mỗi dòng đã có icon nếu thiếu)."""
        return [_normalize_schedule_row(x) for x in self.medications]

    def get_all(self) -> list:
        """Alias cho load()."""
        return list(self.medications)

    def reset(self):
        """Reset về mock data ban đầu."""
        self.medications = [
            _normalize_schedule_row(x) for x in SAMPLE_SCHEDULE
        ]


# =============================================================================
# Singleton instance
# =============================================================================
schedule_store = ScheduleStore.get_instance()
