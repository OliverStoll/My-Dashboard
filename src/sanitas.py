from selenium import webdriver
from dotenv import load_dotenv
import os
from datetime import datetime
from datetime import date

from time import sleep
from dataclasses import dataclass
from typing import Literal

from selenium.webdriver.common.by import By


load_dotenv()


@dataclass
class DriverAction:
    action: Literal["url", "sleep", "click", "send_keys"]
    identifier: str | None = None
    input: str | int | None = None


@dataclass
class ScaleData:
    date: datetime
    weight: float
    fat: float = None
    water: float = None
    muscle: float = None




login_actions = [
    DriverAction("url", "https://connect.sanitas-online.de/HealthCoach/Default.aspx"),
    DriverAction("send_keys", "#ContentPlaceHolder1_ctl00_txtUserName", os.environ["SANITAS_EMAIL"]),
    DriverAction("send_keys", "#ContentPlaceHolder1_ctl00_txtPassword", os.environ["SANITAS_PASSWORD"]),
    DriverAction("click", "#ContentPlaceHolder1_ctl00_lnkLogin"),
]

navigate_to_data_actions = [
    DriverAction("url", "https://connect.sanitas-online.de/HealthCoach/Modules/Devices/ScaleDataInfo.aspx"),
    DriverAction("click", "#ui-id-7"),
    DriverAction("sleep", input=4),
    DriverAction("click", "#ContentPlaceHolder1_ctl00_ucBPFilter_lblFiltersYear"),
    DriverAction("sleep", input=4),
    DriverAction("click", "#ContentPlaceHolder1_ctl00_ucBPFilter_lnkBtnFiltersGo"),
]


actions = login_actions + navigate_to_data_actions

# login
driver = webdriver.Chrome()

for action in actions:
    if action.action == "url":
        driver.get(action.identifier)
    if action.action == "send_keys":
        driver.find_element(By.CSS_SELECTOR, action.identifier).send_keys(action.input)
    if action.action == "click":
        driver.find_element(By.CSS_SELECTOR, action.identifier).click()
    if action.action == "sleep":
        sleep(action.input)


selector = "table#ScaleDataTblHeader > tbody > tr > td > table"

table = driver.find_element(By.CSS_SELECTOR, selector)
table_rows = table.text.replace(',', '.').split('\n')

# convert table text to list of dicts
scale_data_list = []
for row in table_rows:
    row_data = row.split(' ')
    scale_data = ScaleData(
        date=datetime.strptime(f"{row_data[0]} {row_data[1]}", '%d.%m.%Y %H:%M'),
        weight=float(row_data[2]),
    )
    if len(row_data) == 6:
        scale_data.fat = float(row_data[3])
        scale_data.water = float(row_data[4])
        scale_data.muscle = float(row_data[5])

    scale_data_list.append(scale_data)
    print(scale_data)


driver.quit()

