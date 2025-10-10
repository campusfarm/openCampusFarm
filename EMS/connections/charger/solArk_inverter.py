from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
import chromedriver_autoinstaller
import time
import undetected_chromedriver as uc
from dotenv import load_dotenv
import os
from from_root import from_root

load_dotenv(from_root(".env"))

# # Disable the __del__ method to prevent errors from being printed
# uc.Chrome.__del__ = lambda self: None


def get_inverter_data():
    #driver = uc.Chrome()
    chromdriver_path = chromedriver_autoinstaller.install()
    service = Service(chromdriver_path)
    driver = webdriver.Chrome(service=service)

    # Open the webpage
    driver.get('https://www.solarkcloud.com/login')
    time.sleep(5)

    try:
        # Increment attempt counter
        email_field = WebDriverWait(driver, 60).until(
            EC.presence_of_element_located((By.XPATH, "//input[@placeholder='Please input your E-mail']"))
        )
        email_field.send_keys(os.environ.get("SOLARKCLOUD_EMAIL"))

        password_field = WebDriverWait(driver, 60).until(
            EC.presence_of_element_located((By.XPATH, "//input[@placeholder='Please re-enter password']"))
        )
        password_field.send_keys(os.environ.get("SOLARKCLOUD_PASSWORD"))

        checkbox = driver.find_element(By.CLASS_NAME, "el-checkbox__input")
        checkbox.click()  # Click the checkbox

        sign_in_button = WebDriverWait(driver, 60).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "button.sunmit"))
        )
        sign_in_button.click()

    except Exception as e:
        print("Error during login:", e)

    time.sleep(5)

    try:
        campus_farm_link = driver.find_element(By.LINK_TEXT, "campus farm")
        campus_farm_link.click() 
    except Exception as e:
        print("An error occurred:", e)

    time.sleep(2)

    # Define keys for each wattage value
    keys = ["Solar W", "Battery W", "Grid W", "Consumed W"]
    wattage_dict = {}

    # Find all elements with the class name "txt" and store each wattage value in the dictionary
    try:
        wattage_elements = driver.find_elements(By.CLASS_NAME, "txt")
        for i, element in enumerate(wattage_elements):
            if i < len(keys): 
                wattage_text = element.text  
                wattage_dict[keys[i]] = wattage_text  

        print("Wattage Dictionary:", wattage_dict)

    except Exception as e:
        print("An error occurred:", e)

    driver.quit()
    return wattage_dict
