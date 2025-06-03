import os
from datetime import datetime, date, timedelta
from pydantic import BaseModel, ConfigDict

from common_utils.web.selenium import DriverAction as Action, SeleniumHandler
from common_utils.apis.firebase import FirebaseClient
from common_utils.config import load_dotenv
from common_utils.logger import create_logger


class PaymentRecord(BaseModel):
    category: str
    amount: float
    account: str
    recipient: str
    note: str
    date: date

    model_config = ConfigDict(from_attributes=True)

    def to_dict(self):
        data = self.model_dump()
        data["date"] = self.date.strftime("%d.%m.%Y")
        return data

    def __str__(self):
        return (
            f"[{self.date.strftime('%d.%m.%Y')}] {self.account}: {self.amount}€ |"
            f" {self.category} | {self.recipient} | {self.note}"
        )


class BalanceRecord(BaseModel):
    account: str
    balance: float
    date: date

    def to_dict(self):
        data = self.model_dump()
        data["date"] = self.date.strftime("%d.%m.%Y")
        return data

    def __str__(self):
        return f"[{self.date.strftime('%d.%m.%Y')}] {self.account}: {self.balance}€"


class BudgetBakersDataScraper:
    log = create_logger("BudgetBakers Scraper")
    debug = bool(os.getenv("DEBUG", False))
    scraper = SeleniumHandler(headless=not debug, download_driver=True)
    firebase_path = "/DATA/Finanzen/BudgetBakers"
    account_map = {
        ".": "Alltag",
        "Fixkosten": "Fixkosten",
    }

    def __init__(self) -> None:
        load_dotenv()
        self.firebase = FirebaseClient(realtime_db_url=os.environ["FIREBASE_REALTIME_DB_URL"])
        self.current_date: date = datetime.today()

    def run(self) -> dict[str, list[PaymentRecord] | list[BalanceRecord]]:
        data = self.get_data()
        raw_payments = data.get("records", [])
        raw_balances = data.get("balances", [])
        payments_data = self.clean_payments_data(raw_payments)
        balances = self.clean_balances_data(raw_balances)
        self.save_payments_to_firestore(payments_data)
        self.save_balances_to_firestore(balances)
        return {"payments": payments_data, "balances": balances}

    def get_data(self) -> dict[str, list[str]]:
        actions = [
            Action("url", value="https://web.budgetbakers.com/login"),
            Action("sleep", value=10),
            Action(
                "send_keys",
                css_identifier="input[name='email']",
                value=os.environ["BUDGETBAKERS_EMAIL"],
            ),
            Action(
                "send_keys",
                css_identifier="input[name='password']",
                value=os.environ["BUDGETBAKERS_PASSWORD"],
            ),
            Action("click", css_identifier="button[type='submit']"),
            Action("sleep", value=60),
            Action("url", value="https://web.budgetbakers.com/records"),
            Action("sleep", value=10),
            Action(
                "get_texts",
                result_key="records",
                css_identifier="main > div > div:nth-child(2) > div:nth-child(2) > div > div > div",
            ),
            Action("sleep", value=10),
            Action("url", value="https://web.budgetbakers.com/accounts"),
            Action("sleep", value=10),
            Action(
                "get_texts",
                result_key="balances",
                css_identifier="main > div > div:nth-child(2) > div:nth-child(2) > div > div",
            ),
        ]
        results = self.scraper.run_actions(actions)
        # records, balances
        return results

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

    @staticmethod
    def _clean_amount(amount_str: str) -> float:
        amount = amount_str.replace("€", "").replace(",", ".")
        if amount.count(".") > 1:
            amount = amount.replace(".", "", 1)
        return float(amount)

    @staticmethod
    def _get_current_date(date_str: str) -> date:
        if date_str == "Yesterday":
            return datetime.today().date() - timedelta(days=1)
        date_ = datetime.strptime(date_str, "%B %d").date()
        current_year = datetime.today().year
        year = current_year if date_.month <= datetime.today().month else current_year - 1
        return date_.replace(year=year)

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
        self.log.info(f"Saving {len(payment_records)} payments to firebase")
        for rec in payment_records:
            entry_key = f"{rec.amount}|{rec.category}|{rec.recipient}".replace("/", "").replace(
                ".", ","
            )
            entry_date = rec.date.strftime("%Y-%m-%d")
            entry_ref = f"{self.firebase_path}/records/{rec.account}/{entry_date}/{entry_key}"
            self.firebase.set_entry(ref=entry_ref, data=rec.to_dict())

    def save_balances_to_firestore(self, balance_records: list[BalanceRecord]):
        self.log.info(f"Saving {len(balance_records)} balances to firebase")
        for rec in balance_records:
            entry_ref = (
                f"{self.firebase_path}/balances/{rec.account}/{rec.date.strftime('%Y-%m-%d')}"
            )
            self.firebase.set_entry(ref=entry_ref, data=rec.to_dict())


if __name__ == "__main__":
    data_ = BudgetBakersDataScraper().run()
    for entry in data_:
        print(entry)
