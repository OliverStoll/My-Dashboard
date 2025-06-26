import os
from datetime import datetime, timedelta

from common_utils.apis.ticktick.habits import TicktickHabitHandler, TickTickHabitEntry
from common_utils.config import load_dotenv
from common_utils.apis.firebase import FirebaseClient


class TicktickHabitsScraper:
    firebase_path = "/DATA/Habits/Ticktick"

    def __init__(self) -> None:
        load_dotenv()
        self.firebase = FirebaseClient(realtime_db_url=os.environ["FIREBASE_REALTIME_DB_URL"])
        self.habit_handler = TicktickHabitHandler(
            cookies_path="ticktick-cookies.json", headless=True, download_driver=True
        )
        self.habits = None

    def run(self, days_offset=10):
        self.habits, _ = self.habit_handler._get_all_habits_metadata()
        self.save_habits_metadata_to_firebase(self.habits)

        after_stamp = int((datetime.now() - timedelta(days=days_offset)).strftime("%Y%m%d"))
        all_habits_entries = self.habit_handler.get_all_checkins(after_stamp=after_stamp)

        all_habit_entries_flat = []
        for habit_id, habit_entries in all_habits_entries.items():
            all_habit_entries_flat += habit_entries

        self.save_habit_entries_to_firebase(all_habit_entries_flat)

        return all_habits_entries

    def save_habit_entries_to_firebase(self, habit_entries: list[TickTickHabitEntry]) -> None:
        ref = f"{self.firebase_path}/Eintraege"
        payload: dict[str, dict[str, dict]] = {}
        for habit_entry in habit_entries:
            checkin_date_obj = datetime.strptime(str(habit_entry.checkin_stamp), "%Y%m%d")
            checkin_date = checkin_date_obj.strftime("%Y-%m-%d")
            if checkin_date not in payload.keys():
                payload[checkin_date] = {}
            payload[checkin_date][habit_entry.habit_id] = habit_entry.model_dump()
        self.firebase.update(ref=ref, data=payload)

    def save_habits_metadata_to_firebase(self, habits: dict):
        ref = f"{self.firebase_path}/Habits"
        payload = {}
        for habit_id, habit in habits.items():
            payload[habit_id] = habit
        self.firebase.update(ref=ref, data=payload)


if __name__ == "__main__":
    scraper = TicktickHabitsScraper()
    habits_ = scraper.run()
    print(habits_)
