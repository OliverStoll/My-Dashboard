import os
from dataclasses import dataclass
from datetime import datetime
from typing import Literal

from common_utils.logger import create_logger
from common_utils.web.scraper import DriverAction, SeleniumHandler
from common_utils.apis.firebase import FirebaseClient
from common_utils.config import load_dotenv


@dataclass
class DiaroEntry:
    text: str
    date: datetime
    title: str | None = None
    mood: Literal["Awesome", "Happy", "Neutral", "Sad", "Awful"] | None = None
    weather: str | None = None
    location: str | None = None



class DiaroScraper:
    log = create_logger("DiaroScraper")
    firebase_path = "/DATA/Tagebuch/Diaro"

    def __init__(self) -> None:
        load_dotenv()
        self.scraper = SeleniumHandler(headless=False)
        self.firebase = FirebaseClient(realtime_db_url=os.environ["FIREBASE_REALTIME_DB_URL"])

    def run(self):
        diary_entry_strings = self.get_diaro_data()
        diary_entries = self.clean_diaro_data(diary_entry_strings)
        self.store_data_firestore(diary_entries)
        return diary_entries

    def get_diaro_data(self) -> list[str]:
        actions = [
            DriverAction("url", "https://www.diaroapp.com/login"),
            DriverAction("send_keys", "input[name='email']", os.environ["DIARO_EMAIL"]),
            DriverAction("send_keys", "input[name='password']", os.environ["DIARO_PASSWORD"]),
            DriverAction("click", "button.signin-button"),
            DriverAction("sleep", input=30),
            DriverAction("get_texts", "a.EntryListItem"),
        ]
        diary_entry_strings = self.scraper.run_actions(actions)[0]
        return diary_entry_strings

    def clean_diaro_data(self, diary_entry_strings: list[str]) -> list[dict]:
        diary_entries = []
        for entry_string in diary_entry_strings:
            entry_parts = entry_string.split("\n")
            day = entry_parts[1]
            time = entry_parts[2]
            text = entry_parts[3]

            entry = DiaroEntry(


            )

        print(diary_entry_strings)
        return []


if __name__ == '__main__':
    scraper = DiaroScraper()
    scraper.run()