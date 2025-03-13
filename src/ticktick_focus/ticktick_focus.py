import os
import requests
import pytz
from datetime import datetime, timezone, timedelta
from dataclasses import dataclass, fields, asdict
from common_utils.apis.ticktick.habits import TicktickHabitHandler
from common_utils.config import load_dotenv
from common_utils.apis.firebase import FirebaseClient


@dataclass
class TickTickFocusTime:
    id: str
    startTime: str | datetime
    endTime: str | datetime
    status: int
    pauseDuration: int
    type: int
    totalDuration: int | None = None

    def __post_init__(self):
        self.startTime = datetime.fromisoformat(self.startTime) if self.startTime else None
        self.endTime = datetime.fromisoformat(self.endTime) if self.endTime else None
        # convert to berlin timezone
        berlin_tz = pytz.timezone("Europe/Berlin")
        self.startTime = self.startTime.astimezone(berlin_tz)
        self.endTime = self.endTime.astimezone(berlin_tz)
        self.totalDuration = int((self.endTime - self.startTime).total_seconds() / 60)

    def to_dict(self):
        result = asdict(self)
        result["startTime"] = result["startTime"].strftime("%Y-%m-%d %H:%M:%S")
        result["endTime"] = result["endTime"].strftime("%Y-%m-%d %H:%M:%S")
        return result

    @classmethod
    def from_dict(cls, data):
        field_names = {field.name for field in fields(cls)}
        filtered_data = {key: value for key, value in data.items() if key in field_names}
        return TickTickFocusTime(**filtered_data)


class TickTickFocusScraper:
    firebase_path = "/DATA/Arbeitszeiten/TickTick"

    def __init__(self):
        load_dotenv()
        self.habits_handler = TicktickHabitHandler(headless=True, download_driver=True)
        self.headers = self.habits_handler.headers
        self.firebase = FirebaseClient(realtime_db_url=os.environ["FIREBASE_REALTIME_DB_URL"])

    def run(self):
        focus_times = self.get_focus()
        self.store_focus_times_firebase(focus_times)
        return focus_times

    def get_focus(self) -> list[TickTickFocusTime]:
        url = "https://api.ticktick.com/api/v2/pomodoros/timeline"
        response = self._make_get_request(url)
        focus_times = [TickTickFocusTime.from_dict(focus_time) for focus_time in response]
        return focus_times

    def _make_get_request(self, url):
        response = requests.get(url, headers=self.headers)
        return response.json()

    def store_focus_times_firebase(self, focus_times):
        focus_times_data = [focus_time.to_dict() for focus_time in focus_times]
        focus_days = [focus_time["startTime"].split(" ")[0] for focus_time in focus_times_data]
        focus_days = list(set(focus_days))
        focus_days_map = {}
        for focus_day in focus_days:
            focus_times_map = {focus_time['startTime'].split(' ')[1]: focus_time for focus_time in focus_times_data if focus_time["startTime"].split(" ")[0] == focus_day}
            focus_days_map[focus_day] = focus_times_map
        self.firebase.set_entry(ref=self.firebase_path, data=focus_days_map)


if __name__ == "__main__":
    scraper = TickTickFocusScraper()
    focus = scraper.run()
