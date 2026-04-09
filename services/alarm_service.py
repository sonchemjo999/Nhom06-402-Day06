"""
=============================================================================
 AlarmService - He thong bao thuc nhac uong thuoc
=============================================================================
 File: services/alarm_service.py
 Mo ta: Service chay nen kiem tra gio uong thuoc moi 10 giay.
        Khi den gio uong thuoc ma chua confirm "Da uong":
          - Bat popup bao thuc toan man hinh (giong alarm dien thoai)
          - Phat am thanh canh bao (beep)
          - Neu user khong tick "Da uong" -> lap lai toi da 5 lan
          - Khoang cach giua cac lan: 1 phut, 5 phut, 10 phut, 15 phut

 Theo spec-draft.md:
   - Feature 1: "AI gui thong bao len Web/App moi 5 phut
     -> Cho user nhan 'Da uong'"
   - "Nut 'Tri hoan 15 phut' (Snooze) la bat buoc"
   - Low-confidence path: sau 3 lan nhac -> hoi user gap kho khan gi
=============================================================================
"""

import time
from datetime import datetime
from kivy.clock import Clock

from app_core.app_datetime import get_app_now
from data.schedule_store import schedule_store


# Khoang cach giua cac lan nhac (giay)
# Lan 1: ngay lap tuc, Lan 2: +1 phut, Lan 3: +5 phut,
# Lan 4: +10 phut, Lan 5: +15 phut
REMINDER_INTERVALS_SECONDS = [0, 60, 300, 600, 900]
MAX_REMINDERS = 5

# Cho demo: dung intervals ngan hon (giay) de test nhanh
DEMO_INTERVALS_SECONDS = [0, 10, 20, 30, 40]


class AlarmService:
    """
    Service quan ly alarm nhac uong thuoc.

    Theo doi:
      - Cu thuoc nao da duoc nhac (va nhac bao nhieu lan)
      - Cu thuoc nao da duoc confirm
      - Khi nao can nhac lai (dua tren intervals)
    """

    def __init__(self, demo_mode=True):
        self.demo_mode = demo_mode
        self.intervals = DEMO_INTERVALS_SECONDS if demo_mode else REMINDER_INTERVALS_SECONDS
        self._reminder_state = {}
        self._on_alarm_callback = None
        self._check_event = None
        self._grace_period_minutes = 60

    def start(self, on_alarm_callback):
        """Bat dau service kiem tra gio uong thuoc."""
        self._on_alarm_callback = on_alarm_callback
        interval = 10 if self.demo_mode else 30
        self._check_event = Clock.schedule_interval(self._check_medications, interval)
        print(f"[AlarmService] Started (demo_mode={self.demo_mode}, check every {interval}s)")

    def stop(self):
        """Dung service."""
        if self._check_event:
            self._check_event.cancel()
            self._check_event = None
        print("[AlarmService] Stopped")

    def confirm_taken(self, med_time: str, med_name: str):
        """Xac nhan da uong thuoc -> dung alarm cho cu nay."""
        key = f"{med_time}|{med_name}"
        if key in self._reminder_state:
            self._reminder_state[key]["dismissed"] = True
        print(f"[AlarmService] Confirmed: {med_name} at {med_time}")

    def snooze(self, med_time: str, med_name: str):
        """Tri hoan alarm (Snooze) -> se nhac lai o interval tiep theo."""
        key = f"{med_time}|{med_name}"
        state = self._reminder_state.get(key)
        if state and state["count"] < MAX_REMINDERS:
            count = state["count"]
            delay = self.intervals[min(count, len(self.intervals) - 1)]
            state["next_time"] = time.time() + delay
            print(f"[AlarmService] Snooze {med_name}: retry in {delay}s "
                  f"(attempt {count + 1}/{MAX_REMINDERS})")

    def get_reminder_count(self, med_time: str, med_name: str) -> int:
        """Lay so lan da nhac cho mot cu thuoc."""
        key = f"{med_time}|{med_name}"
        state = self._reminder_state.get(key)
        return state["count"] if state else 0

    def _check_medications(self, dt):
        """
        Kiem tra dinh ky: co cu thuoc nao den gio chua uong khong?
        Duoc goi boi Clock.schedule_interval.
        """
        # Dùng cùng nguồn thời gian với đồng hồ UI (get_app_now có thể là mốc test + thời gian thực trôi)
        now = get_app_now()

        for item in schedule_store.load():
            if item.get("taken", False):
                continue

            med_time = item["time"]
            med_name = item["name"]
            key = f"{med_time}|{med_name}"

            try:
                med_dt = now.replace(
                    hour=int(med_time.split(":")[0]),
                    minute=int(med_time.split(":")[1]),
                    second=0, microsecond=0
                )
            except (ValueError, IndexError):
                continue

            time_diff = (now - med_dt).total_seconds()
            if time_diff < 0 or time_diff > self._grace_period_minutes * 60:
                continue

            if key not in self._reminder_state:
                self._reminder_state[key] = {
                    "count": 0,
                    "next_time": time.time(),
                    "dismissed": False,
                    "first_trigger": time.time(),
                }

            state = self._reminder_state[key]

            if state["dismissed"] or state["count"] >= MAX_REMINDERS:
                continue

            if time.time() >= state["next_time"]:
                state["count"] += 1
                count = state["count"]

                if count < MAX_REMINDERS:
                    delay = self.intervals[min(count, len(self.intervals) - 1)]
                    state["next_time"] = time.time() + delay

                print(f"[AlarmService] ALARM #{count}/{MAX_REMINDERS}: "
                      f"{med_name} at {med_time}")

                if self._on_alarm_callback:
                    self._on_alarm_callback(item, count)
