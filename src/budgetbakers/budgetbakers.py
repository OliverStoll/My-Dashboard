import os
from dataclasses import dataclass
from datetime import datetime, date as Date, timedelta

from common_utils.web.selenium import DriverAction as Action, SeleniumHandler
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
        return (f"[{self.date.strftime('%d.%m.%Y')}] {self.account}: {self.amount}€ |"
                f" {self.category} | {self.recipient} | {self.note}")


@dataclass
class BalanceRecord:
    account: str
    balance: float
    date: Date

    def to_dict(self):
        return {
            "account": self.account,
            "balance": self.balance,
            "date": self.date.strftime("%d.%m.%Y"),
        }

    def __str__(self):
        return f"[{self.date.strftime('%d.%m.%Y')}] {self.account}: {self.balance}€"


class BudgetBakersDataScraper:
    scraper = SeleniumHandler(headless=True, download_driver=True)
    firebase_path = "/DATA/Finanzen/BudgetBakers"
    account_map = {
        '.': 'Alltag',
        'Fixkosten': 'Fixkosten',
    }

    def __init__(self) -> None:
        load_dotenv()
        self.firebase = FirebaseClient(realtime_db_url=os.environ["FIREBASE_REALTIME_DB_URL"])
        self.current_date: Date = datetime.today()

    def run(self) -> list[BalanceRecord]:
        raw_payments, raw_balances = self.get_data()
        payments_data = self.clean_payments_data(raw_payments)
        balances = self.clean_balances_data(raw_balances)
        self.save_payments_to_firestore(payments_data)
        self.save_balances_to_firestore(balances)
        return balances

    def get_data(self) -> tuple[list[str], list[str]]:
        actions = [
            Action("url", "https://web.budgetbakers.com/login"),
            Action("sleep", input=4),
            Action("send_keys", "input[name='email']", os.environ["BUDGETBAKERS_EMAIL"]),
            Action("send_keys", "input[name='password']", os.environ["BUDGETBAKERS_PASSWORD"]),
            Action("click", "button[type='submit']"),
            Action("sleep", input=15),
            Action("url", "https://web.budgetbakers.com/records"),
            Action("sleep", input=5),
            Action("get_texts", "main > div > div:nth-child(2) > div:nth-child(2) > div > div > div", key="records"),
            Action("sleep", input=2),
            Action("url", "https://web.budgetbakers.com/accounts"),
            Action("sleep", input=5),
            Action("get_texts", "main > div > div:nth-child(2) > div:nth-child(2) > div > div", key="balances"),
        ]
        payments_data = self.scraper.run_actions(actions)['records']
        balance_data = self.scraper.run_actions(actions)['balances']
        return payments_data, balance_data

    def clean_payments_data(self, data_rows: list[str]):
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

    def clean_balances_data(self, balance_rows: list[str]):
        balance_records = []
        for row in balance_rows:
            row_entries = row.split("\n")
            record = BalanceRecord(
                account=self.account_map[row_entries[0].strip()],
                balance=self._clean_amount(row_entries[4]),
                date=datetime.today().date(),
            )
            balance_records.append(record)
        return balance_records

    def _clean_amount(self, amount_str: str) -> float:
        amount = amount_str.replace("€", "").replace(",", ".")
        if amount.count(".") > 1:
            amount = amount.replace(".", "", 1)
        return float(amount)

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

    def save_payments_to_firestore(self, payment_records: list[PaymentRecord]):
        for rec in payment_records:
            entry_key = f"{rec.amount}|{rec.category}|{rec.recipient}".replace('/', '').replace('.', ',')
            entry_date = rec.date.strftime('%Y-%m-%d')
            entry_ref = f"{self.firebase_path}/records/{rec.account}/{entry_date}/{entry_key}"
            self.firebase.set_entry(ref=entry_ref, data=rec.to_dict())

    def save_balances_to_firestore(self, balance_records: list[BalanceRecord]):
        for rec in balance_records:
            entry_ref = f"{self.firebase_path}/balances/{rec.account}/{rec.date.strftime('%Y-%m-%d')}"
            self.firebase.set_entry(ref=entry_ref, data=rec.to_dict())


if __name__ == "__main__":
    data = BudgetBakersDataScraper().run()
    for entry in data:
        print(entry)