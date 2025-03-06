from selenium import webdriver
from dotenv import load_dotenv
import os
from time import sleep

from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.options import Options



load_dotenv()

options = webdriver.ChromeOptions()
prefs = {
    "download.default_directory": "C:/CODE/My-Dashboard",
    "download.prompt_for_download": False,
    "safebrowsing.enabled": True
}
options.add_experimental_option("prefs", prefs)


login = {
    "url": "https://connect.sanitas-online.de/HealthCoach/Default.aspx",
    "username_selector": "input#ContentPlaceHolder1_ctl00_txtUserName",
    "password_selector": "input#ContentPlaceHolder1_ctl00_txtPassword",
    "submit_selector": "#ContentPlaceHolder1_ctl00_lnkLogin",
    "username_env": "SANITAS_EMAIL",
    "password_env": "SANITAS_PASSWORD",
}
print(os.environ[login["username_env"]])
print(os.environ[login["password_env"]])

# login
driver = webdriver.Chrome(options=options)
driver.get(login["url"])
username_input = (driver.find_element(By.CSS_SELECTOR, login["username_selector"]))
username_input.send_keys(
    os.environ[login["username_env"]]
)
driver.find_element(By.CSS_SELECTOR, login["password_selector"]).send_keys(
    os.environ[login["password_env"]]
)
driver.find_element(By.CSS_SELECTOR, login["submit_selector"]).click()
sleep(1)



# get csv
url = "https://connect.sanitas-online.de/HealthCoach/Modules/Devices/ScaleDataInfo.aspx"
nav_selector = "#ui-id-7"
selector = "#ContentPlaceHolder1_ctl00_ScaleData_lnkBtnExcelExport"

driver.get(url)
# download csv by clicking the download button
driver.find_element(By.CSS_SELECTOR, nav_selector).click()
sleep(1)
driver.find_element(By.CSS_SELECTOR, selector).click()
sleep(5)
driver.quit()

