import os
from dataclasses import dataclass
from datetime import datetime, date, timedelta

from common_utils.apis.ticktick.habits import TicktickHabitHandler
from common_utils.config import load_dotenv
from common_utils.apis.firebase import FirebaseClient


@dataclass
class HabitEntry:
    id: str
    habit_id: str
    checkin_stamp: int
    value: int
    goal: int
    status: int
    checkin_time: str | None = None

    def to_dict(self):
        return {
            "id": self.id,
            "habit_id": self.habit_id,
            "checkin_stamp": self.checkin_stamp,
            "checkin_time": self.checkin_time,
            "value": self.value,
            "goal": self.goal,
            "status": self.status
        }






class TicktickHabitsScraper:
    firebase_path = "/DATA/Habits/Ticktick"

    def __init__(self) -> None:
        load_dotenv()
        self.firebase = FirebaseClient(realtime_db_url=os.environ["FIREBASE_REALTIME_DB_URL"])
        self.habit_handler = TicktickHabitHandler(cookies_path='ticktick-cookies.json')
        self.habits = None

    def run(self, days_offset=30):
        self.habits, _ = self.habit_handler._get_all_habits_metadata()
        self.save_habits_metadata_to_firebase(self.habits)
        after_stamp = int((datetime.now() - timedelta(days=days_offset)).strftime("%Y%m%d"))
        habit_entries_data = self.habit_handler.get_all_checkins(after_stamp=after_stamp)
        habit_entries = []
        for data in habit_entries_data:
            habit_entry = HabitEntry(
                id=data['id'],
                habit_id=data['habitId'],
                checkin_stamp=data['checkinStamp'],
                checkin_time=data.get('checkinTime'),
                value=data['value'],
                goal=data['goal'],
                status=data['status']
            )
            habit_entries.append(habit_entry)
            self.save_habit_entry_to_firebase(habit_entry)

    def get_habit_name(self, habit_id: str) -> str:
        return self.habits[habit_id]['name']

    def save_habit_entry_to_firebase(self, habit_entry: HabitEntry) -> None:
        habit_name = self.get_habit_name(habit_entry.habit_id)
        ref = f"{self.firebase_path}/Einträge/{habit_name}/{habit_entry.checkin_stamp}"
        self.firebase.set_entry(ref, habit_entry.to_dict())

    def save_habits_metadata_to_firebase(self, habits: dict):
        for id, habit in habits.items():
            self.firebase.set_entry(ref=f"{self.firebase_path}/Habits/{id}", data=habit)



if __name__ == "__main__":
    scraper = TicktickHabitsScraper()
    habits = scraper.run()
    print(habits)