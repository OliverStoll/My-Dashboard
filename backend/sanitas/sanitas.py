from dotenv import load_dotenv
import os
from datetime import datetime
from pydantic import BaseModel

from common_utils.web.selenium import DriverAction, SeleniumHandler
from common_utils.apis.firebase import FirebaseClient


class WeightEntry(BaseModel):
    date: datetime
    weight: float
    fat: float | None = None
    water: float | None = None
    muscle: float | None = None

    def __str__(self):
        return (
            f"Date: {self.date.strftime('%d.%m.%Y %H:%M')}, Weight: {self.weight}, "
            f"Fat: {self.fat}, Water: {self.water}, Muscle: {self.muscle}"
        )


class SanitasDataScraper:
    firebase_path = "/DATA/Gewicht/Sanitas"
    headless = bool(os.getenv("DEBUG", True))
    scraper = SeleniumHandler(headless=headless, download_driver=True)

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
            DriverAction("url", value="https://connect.sanitas-online.de/HealthCoach/Default.aspx"),
            DriverAction(
                "send_keys",
                css_identifier="#ContentPlaceHolder1_ctl00_txtUserName",
                value=os.environ["SANITAS_EMAIL"],
            ),
            DriverAction(
                "send_keys",
                css_identifier="#ContentPlaceHolder1_ctl00_txtPassword",
                value=os.environ["SANITAS_PASSWORD"],
            ),
            DriverAction("sleep", value=1),
            DriverAction("click", css_identifier="#ContentPlaceHolder1_ctl00_lnkLogin"),
            DriverAction("sleep", value=1),
            # navigate to data
            DriverAction(
                "url",
                value="https://connect.sanitas-online.de/HealthCoach/Modules/Devices/ScaleDataInfo.aspx",
            ),
            DriverAction("sleep", value=3),
            DriverAction("click", css_identifier="#ui-id-7"),
            DriverAction("sleep", value=3),
            DriverAction(
                "click", css_identifier="#ContentPlaceHolder1_ctl00_ucBPFilter_lblFiltersYear"
            ),
            DriverAction("sleep", value=3),
            DriverAction(
                "click", css_identifier="#ContentPlaceHolder1_ctl00_ucBPFilter_lnkBtnFiltersGo"
            ),
            DriverAction("sleep", value=3),
            DriverAction(
                "get_text",
                css_identifier="table#ScaleDataTblHeader > tbody > tr > td > table",
                result_key="table_text_start",
            ),
            DriverAction("scroll_down", value=1000, css_identifier=".fht-tbody.ps-container"),
            DriverAction("sleep", value=1),
            DriverAction(
                "get_text",
                css_identifier="table#ScaleDataTblHeader > tbody > tr > td > table",
                result_key="table_text_end",
            ),
        ]

        results: dict[str, str | list[str] | None] = self.scraper.run_actions(sanitas_actions)
        table_text = str(results.get("table_text_start", "")) + str(
            results.get("table_text_end", "")
        )
        table_rows = table_text.replace(",", ".").split("\n")
        return table_rows

    @staticmethod
    def clean_sanitas_data(table_rows: list[str]) -> list[WeightEntry]:
        """Convert table text to list of dicts"""
        scale_data_list = []
        for row in table_rows:
            row_data = row.split(" ")
            if len(row_data) < 3:
                continue
            weight_date = datetime.strptime(f"{row_data[0]} {row_data[1]}", "%d.%m.%Y %H:%M")
            scale_data = WeightEntry(date=weight_date, weight=float(row_data[2]))
            if len(row_data) == 6:
                scale_data.fat = float(row_data[3])
                scale_data.water = float(row_data[4])
                scale_data.muscle = float(row_data[5])
            scale_data_list.append(scale_data)
        return scale_data_list

    def store_data_firestore(self, weight_data: list[WeightEntry]):
        payload = {}
        for weight_entry in weight_data:
            weight_date = weight_entry.date.strftime("%Y-%m-%d %H:%M")
            payload[weight_date] = weight_entry.model_dump(mode="json")

        self.firebase.update(ref=self.firebase_path, data=payload)


if __name__ == "__main__":
    scraper = SanitasDataScraper()
    scraper.run()
