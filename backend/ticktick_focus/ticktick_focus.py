import os

from common_utils.apis.ticktick.focus import TicktickFocusHandler, TickTickFocusTime
from common_utils.config import load_dotenv
from common_utils.apis.firebase import FirebaseClient


class TickTickFocusScraper:
    firebase_path = "/DATA/Arbeitszeiten/TickTick"

    def __init__(self):
        load_dotenv()

        self.focus_handler = TicktickFocusHandler(
            headless=True, download_driver=True, cookies_path="ticktick-cookies.json"
        )
        self.headers = self.focus_handler.headers
        self.firebase = FirebaseClient(realtime_db_url=os.environ["FIREBASE_REALTIME_DB_URL"])

    def run(self):
        focus_times = self.get_focus()
        self.store_focus_times_firebase(focus_times)
        return focus_times

    def get_focus(self) -> list[TickTickFocusTime]:
        all_focus_times = []
        for total_months in range(10):
            days_offset = total_months * 30
            focus_times = self.focus_handler.get_all_focus_times(days_offset=days_offset)
            all_focus_times.extend(focus_times)
        return all_focus_times

    def store_focus_times_firebase(self, focus_times):
        payload = {}
        for focus_time in focus_times:
            date_str = focus_time.start_time.strftime("%Y-%m-%d")
            time_str = focus_time.start_time.strftime("%H:%M:%S")
            if date_str not in payload.keys():
                payload[date_str] = {}
            payload[date_str][time_str] = focus_time.model_dump(mode="json", by_alias=True)

        self.firebase.update(ref=self.firebase_path, data=payload)


if __name__ == "__main__":
    scraper = TickTickFocusScraper()
    focus = scraper.run()
