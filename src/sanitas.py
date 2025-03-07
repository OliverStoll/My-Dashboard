from dotenv import load_dotenv
import os
from datetime import datetime
from dataclasses import dataclass

from common_utils.web.scraper import DriverAction, SeleniumHandler
from common_utils.apis.firebase import FirebaseClient

from selenium.webdriver.chrome.service import Service
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
service = Service(ChromeDriverManager().install())
options = webdriver.ChromeOptions()
options.add_argument("--headless")
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

DRIVER = webdriver.Chrome(service=service, options=options)


@dataclass
class WeightEntry:
    date: datetime
    weight: float
    fat: float | None = None
    water: float | None = None
    muscle: float | None = None

    def __str__(self):
        return f"Date: {self.date.strftime('%d.%m.%Y %H:%M')}, Weight: {self.weight}, Fat: {self.fat}, Water: {self.water}, Muscle: {self.muscle}"

    def to_dict(self):
        return {
            "date": self.date.strftime('%d.%m.%Y %H:%M'),
            "weight": self.weight,
            "fat": self.fat,
            "water": self.water,
            "muscle": self.muscle,
        }


class SanitasDataScraper:
    firebase_path = "/DATA/Gewichtsdaten/Sanitas"
    scraper = SeleniumHandler(headless=True, download_driver=True)

    def __init__(self):
        load_dotenv()
        self.firebase = FirebaseClient(realtime_db_url=os.environ["FIREBASE_REALTIME_DB_URL"])

    def run(self):
        table_rows = self.get_sanitas_data()
        weight_data = self.clean_sanitas_data(table_rows)
        self.store_data_firestore(weight_data)
        return weight_data

    def get_sanitas_data(self) -> list[str]:
        sanitas_actions = [
            # login
            DriverAction("url", "https://connect.sanitas-online.de/HealthCoach/Default.aspx"),
            DriverAction("send_keys", "#ContentPlaceHolder1_ctl00_txtUserName", os.environ["SANITAS_EMAIL"]),
            DriverAction("send_keys", "#ContentPlaceHolder1_ctl00_txtPassword", os.environ["SANITAS_PASSWORD"]),
            DriverAction("click", "#ContentPlaceHolder1_ctl00_lnkLogin"),
            # navigate to data
            DriverAction("url", "https://connect.sanitas-online.de/HealthCoach/Modules/Devices/ScaleDataInfo.aspx"),
            DriverAction("click", "#ui-id-7"),
            DriverAction("sleep", input=4),
            DriverAction("click", "#ContentPlaceHolder1_ctl00_ucBPFilter_lblFiltersYear"),
            DriverAction("sleep", input=4),
            DriverAction("click", "#ContentPlaceHolder1_ctl00_ucBPFilter_lnkBtnFiltersGo"),
            DriverAction("get_text", "table#ScaleDataTblHeader > tbody > tr > td > table"),
        ]

        table_text = self.scraper.run_actions(sanitas_actions)[0]
        table_rows = table_text.replace(',', '.').split('\n')
        return table_rows


    def clean_sanitas_data(self, table_rows: list[str]) -> list[WeightEntry]:
        """ Convert table text to list of dicts """
        scale_data_list = []
        for row in table_rows:
            row_data = row.split(' ')
            scale_data = WeightEntry(
                date=datetime.strptime(f"{row_data[0]} {row_data[1]}", '%d.%m.%Y %H:%M'),
                weight=float(row_data[2]),
            )
            if len(row_data) == 6:
                scale_data.fat = float(row_data[3])
                scale_data.water = float(row_data[4])
                scale_data.muscle = float(row_data[5])
            scale_data_list.append(scale_data)
        return scale_data_list


    def store_data_firestore(self, weight_data: list[WeightEntry]):
        for entry in weight_data:
            entry_ref = f"{self.firebase_path}/{entry.date.strftime('%Y-%m-%d %H:%M')}"
            self.firebase.set_entry(ref=entry_ref, data=entry.to_dict())


if __name__ == "__main__":
    scraper = SanitasDataScraper()
    scraper.run()