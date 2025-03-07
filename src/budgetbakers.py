import os
from itertools import count
from dataclasses import dataclass
from datetime import datetime, date as Date, timedelta

from common_utils.web.scraper import DriverAction, SeleniumHandler
from common_utils.apis.firebase import FirebaseClient
from common_utils.config import load_dotenv



@dataclass
class PaymentRecord:
    category: str
    amount: float
    account: str
    recipient: str
    note: str
    date: Date

    def to_dict(self):
        return {
            "category": self.category,
            "amount": self.amount,
            "account": self.account,
            "recipient": self.recipient,
            "note": self.note,
            "date": self.date.strftime("%d.%m.%Y"),
        }

    def __str__(self):
        return f"[{self.date.strftime('%d.%m.%Y')}] {self.account}: {self.amount}€ | {self.category} | {self.recipient} | {self.note}"


class BudgetBakersDataScraper:
    scraper = SeleniumHandler(headless=True)
    firebase = FirebaseClient(realtime_db_url=os.environ["FIREBASE_REALTIME_DB_URL"])
    firebase_path = "/DATA/BudgetBakers"
    account_map = {
        '.': 'Alltag',
        'Fixkosten': 'Fixkosten',
    }

    def __init__(self) -> None:
        load_dotenv()
        self.current_date: Date = datetime.today()

    def run(self):
        raw_data = self.get_data()
        payments_data = self.clean_data(raw_data)
        self.save_to_firestore(payments_data)
        return payments_data

    def get_data(self):
        actions = [
            DriverAction("url", "https://web.budgetbakers.com/login"),
            DriverAction("sleep", input=4),
            DriverAction("send_keys", "input[name='email']", os.environ["BUDGETBAKERS_EMAIL"]),
            DriverAction("send_keys", "input[name='password']", os.environ["BUDGETBAKERS_PASSWORD"]),
            DriverAction("click", "button[type='submit']"),
            DriverAction("sleep", input=15),
            DriverAction("url", "https://web.budgetbakers.com/records"),
            DriverAction("sleep", input=3),
            DriverAction("get_texts", "main > div > div:nth-child(2) > div:nth-child(2) > div > div > div"),
        ]
        payments_data = self.scraper.run_actions(actions)[0]
        return payments_data

    def clean_data(self, data_rows: list[str]):
        data_rows = data_rows[4:]
        data_entries = []
        for row in data_rows:
            entry_vals = row.split("\n")
            if len(entry_vals) == 2:
                self.current_date = self._get_current_date(entry_vals[0])
            if len(entry_vals) < 5:
                continue
            try:
                record = self.convert_to_record(entry_vals)
            except ValueError:
                continue
            data_entries.append(record)
        return data_entries

    def _get_current_date(self, date_str: str) -> Date:
        if date_str == "Yesterday":
            return datetime.today().date() - timedelta(days=1)
        date = datetime.strptime(date_str, "%B %d").date()
        current_year = datetime.today().year
        year = current_year if date.month <= datetime.today().month else current_year - 1
        return date.replace(year=year)


    def convert_to_record(self, entry_vals: list[str]) -> PaymentRecord:
        amount = entry_vals[4].replace("€", "").replace(",", ".")
        if amount.count(".") > 1:
            amount = amount.replace(".", "", 1)
        record = PaymentRecord(
            category=entry_vals[0],
            account=self.account_map[entry_vals[1].strip()],
            amount=float(amount),
            recipient=entry_vals[2],
            note=entry_vals[3],
            date=self.current_date,
        )
        return record

    def save_to_firestore(self, payment_records: list[PaymentRecord]):
        for rec in payment_records:
            entry_key = f"{rec.amount}|{rec.category}|{rec.recipient}".replace('/', '').replace('.', ',')
            entry_date = rec.date.strftime('%Y-%m-%d')
            entry_ref = f"{self.firebase_path}/{rec.account}/{entry_date}/{entry_key}"
            self.firebase.set_entry(ref=entry_ref, data=rec.to_dict())


if __name__ == "__main__":
    data = BudgetBakersDataScraper().run()
    for entry in data:
        print(entry)