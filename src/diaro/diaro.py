import os
from dataclasses import dataclass
from datetime import datetime
from typing import Literal

from common_utils.logger import create_logger
from common_utils.web.selenium import DriverAction, SeleniumHandler
from common_utils.apis.firebase import FirebaseClient
from common_utils.config import load_dotenv


@dataclass
class DiaroEntry:
    text: str
    date: datetime
    title: str | None = None
    mood: Literal["Awesome", "Happy", "Neutral", "Sad", "Awful"] | None = None
    location: str | None = None

    def to_dict(self):
        return {
            "text": self.text,
            "date": self.date.strftime("%Y-%m-%d %H:%M"),
            "title": self.title,
            "mood": self.mood,
            "location": self.location,
        }

    def __str__(self):
        return f"[{self.date.strftime('%d.%m.%Y %H:%M')}] {self.title}: {self.text[:50]}"



class DiaroScraper:
    log = create_logger("DiaroScraper")
    firebase_path = "/DATA/Tagebuch/Diaro"
    entry_limit = 10

    def __init__(self) -> None:
        load_dotenv()
        self.scraper = SeleniumHandler(headless=True, raise_exceptions=False, verbose=True, download_driver=True)
        self.firebase = FirebaseClient(realtime_db_url=os.environ["FIREBASE_REALTIME_DB_URL"])
        self.driver = self.scraper.get_driver()

    def run(self) -> list[DiaroEntry]:
        diary_entries = self.get_diaro_data()
        return diary_entries

    def get_diaro_data(self) -> list[DiaroEntry]:
        actions = [
            DriverAction("url", "https://www.diaroapp.com/login"),
            DriverAction("send_keys", "input[name='email']", os.environ["DIARO_EMAIL"]),
            DriverAction("send_keys", "input[name='password']", os.environ["DIARO_PASSWORD"]),
            DriverAction("sleep", input=2),
            DriverAction("click", "button.signin-button"),
            DriverAction("sleep", input=2),
            DriverAction("click", "a.EntryListItem"),
            DriverAction("sleep", input=2),
        ]
        self.scraper.run_actions(actions, driver=self.driver)
        diary_entries = []
        for i in range(self.entry_limit):
            try:
                diary_entry = self.get_single_diaro_entry(self.driver)
                diary_entries.append(diary_entry)
                self.log.info(f"{diary_entry.date}:\n\n{diary_entry.text}\n\n\n")
                self.save_entry_to_firebase(diary_entry)
            except Exception as e:
                self.log.error(f"Error in entry {i}: {e}")
                continue
        return diary_entries

    def get_single_diaro_entry(self, driver) -> DiaroEntry:
        actions = [
            DriverAction("get_text", ".InnerContent > div > div:nth-child(1) > div:nth-child(1)", key="date"),
            DriverAction("get_text", ".InnerContent > div > div:nth-child(2)", key="title"),
            DriverAction("get_text", ".InnerContent > div > div:nth-child(3)", key="text"),
            DriverAction("get_class", ".InnerContent > div > table tr:nth-child(3) .mood_button > i", key="mood"),  # dm-1 = awesome
            DriverAction("get_text", ".InnerContent > div > table tr:nth-child(4)", key="location"),
            DriverAction("click", "a[title='Next']"),
            DriverAction("sleep", input=2),
        ]
        entry_data = self.scraper.run_actions(actions, driver=driver)
        date = datetime.strptime(entry_data['date'], "%A, %d %B %Y, %H:%M")
        location = entry_data.get('location', None).replace("Location:\n", "")
        location = location if location != "No location" else None
        return DiaroEntry(
            title=entry_data.get('title', None),
            text=entry_data['text'],
            date=date,
            mood=self._get_mood(entry_data.get('mood', '')),
            location=location,
        )

    @staticmethod
    def _get_mood(mood_class: str) -> Literal["Awesome", "Happy", "Neutral", "Sad", "Awful"] | None:
        if 'dm-1' in mood_class:
            return "Awesome"
        elif 'dm-2' in mood_class:
            return "Happy"
        elif 'dm-3' in mood_class:
            return "Neutral"
        elif 'dm-4' in mood_class:
            return "Sad"
        elif 'dm-5' in mood_class:
            return "Awful"
        else:
            return None

    def save_entry_to_firebase(self, entry: DiaroEntry):
        entry_ref = f"{self.firebase_path}/{entry.date.strftime('%Y-%m-%d %H:%M')}"
        self.firebase.set_entry(entry_ref, entry.to_dict())


if __name__ == '__main__':
    scraper = DiaroScraper()
    scraper.run()