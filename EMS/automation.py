from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
import undetected_chromedriver as uc
from selenium import webdriver
import chromedriver_autoinstaller
from selenium.webdriver.chrome.service import Service
import time
from dotenv import load_dotenv
import os
from from_root import from_root

load_dotenv(from_root(".env"))
# # Disable the __del__ method to prevent errors from being printed
# uc.Chrome.__del__ = lambda self: None

def change_value(value):
    try:
        chromdriver_path = chromedriver_autoinstaller.install()
        service = Service(chromdriver_path)
        driver = webdriver.Chrome(service=service)
        url = "https://cb.storeitcold.com/#/login"
        driver.get(url)

        wait = WebDriverWait(driver, 20)
        login = wait.until(EC.visibility_of_element_located((By.XPATH, "/html/body/ion-app/ng-component/ion-nav/page-login/single-page/ion-content/div[2]/ion-grid/ion-row/ion-col/div/form/ion-row[1]/ion-col/ion-list/ion-item[1]/div[1]")))

        email = driver.find_element(By.XPATH, "/html/body/ion-app/ng-component/ion-nav/page-login/single-page/ion-content/div[2]/ion-grid/ion-row/ion-col/div/form/ion-row[1]/ion-col/ion-list/ion-item[1]/div[1]/div/ion-input/input")
        email.send_keys(os.getenv('SIT_EMAIL'))

        password = driver.find_element(By.XPATH, "/html/body/ion-app/ng-component/ion-nav/page-login/single-page/ion-content/div[2]/ion-grid/ion-row/ion-col/div/form/ion-row[1]/ion-col/ion-list/ion-item[2]/div[1]/div/ion-input/input")
        password.send_keys(os.getenv('SIT_PASSWORD'))

        button = driver.find_element(By.XPATH, "/html/body/ion-app/ng-component/ion-nav/page-login/single-page/ion-content/div[2]/ion-grid/ion-row/ion-col/div/form/ion-row[2]/ion-col/button[1]")
        button.click()

        main_page = wait.until(EC.visibility_of_element_located((By.XPATH, '//*[@id="statusGrid"]/ion-row[1]/ion-col/span')))
        button_account = driver.find_element(By.XPATH, '//*[@id="tab-t0-1"]')
        button_account.click()

        button_setting = driver.find_element(By.XPATH, '//*[@id="tabpanel-t0-1"]/page-devices/ion-content/div[2]/div/ion-list/ion-grid/ion-row/ion-col[2]/div/expanding-list-item/div/ion-list-header/div[1]/ion-icon')
        if not button_setting.is_enabled():
            button_setting.click()

        set_page = wait.until(EC.visibility_of_element_located((By.XPATH, '//*[@id="tabpanel-t0-1"]/page-devices/ion-content/div[2]/div/ion-list/ion-grid/ion-row/ion-col[2]/div/expanding-list-item/div/div/div/button')))
        buttion_edit = driver.find_element(By.XPATH, '//*[@id="tabpanel-t0-1"]/page-devices/ion-content/div[2]/div/ion-list/ion-grid/ion-row/ion-col[2]/div/expanding-list-item/div/div/div/button')
        buttion_edit.click()

        # Change the temperature setpoint
        slider = driver.find_element(By.CLASS_NAME, 'range-knob-handle')
        min_value = int(slider.get_attribute('aria-valuemin'))
        max_value = int(slider.get_attribute('aria-valuemax'))
        current_value = int(slider.get_attribute('aria-valuenow'))

        desired_value = value

        # if the desired value is greater than max_value, or smaller than min_value, let it be the extreme
        if desired_value > max_value:
            desired_value = max_value
        elif desired_value < min_value:
            desired_value = min_value

        # Handle the situation when the current_value == desired_value
        if current_value == desired_value:
            button_cancel = driver.find_element(By.XPATH, '//*[@id="tabpanel-t0-1"]/page-devices/ion-content/div[2]/div/ion-list/ion-grid/ion-row/ion-col[2]/div/expanding-list-item/div/div/div/button[3]')
            button_cancel.click()
        else:
            percentage = 0
            if max_value != min_value:
                percentage = (desired_value - min_value) / (max_value - min_value)
            slider_size = slider.size
            offset = int(slider_size['width'] * percentage * 10)
            action_chains = ActionChains(driver)
            remains = (slider_size['width'] * (current_value - min_value) / (max_value - min_value)) * 10
            action_chains.click_and_hold(slider).move_by_offset(offset - remains,0).release().perform()

            # Save the updated values
            current_value = int(slider.get_attribute('aria-valuenow'))

            # Save the value
            save_tag = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="tabpanel-t0-1"]/page-devices/ion-content/div[2]/div/ion-list/ion-grid/ion-row/ion-col[2]/div/expanding-list-item/div/div/div/button[1]')))
            save_bottom = driver.find_element(By.XPATH, '//*[@id="tabpanel-t0-1"]/page-devices/ion-content/div[2]/div/ion-list/ion-grid/ion-row/ion-col[2]/div/expanding-list-item/div/div/div/button[1]')
            save_bottom.click()
        driver.quit()
        return current_value
    except Exception as e:
        print(f"An error occurred in automation/change_value function:\n {e}")
        driver.quit()


def get_sensor_temp():
    try:
        chromdriver_path = chromedriver_autoinstaller.install()
        service = Service(chromdriver_path)
        driver = webdriver.Chrome(service=service)
        url = "https://www.easylogcloud.com/devices.aspx"
        driver.get(url)

        wait = WebDriverWait(driver, 20)
        login = wait.until(EC.visibility_of_element_located((By.XPATH, '//*[@id="cph1_username1"]')))

        email = driver.find_element(By.XPATH, '//*[@id="cph1_username1"]')
        email.send_keys(os.environ.get('ELC_EMAIL'))

        password = driver.find_element(By.XPATH, '//*[@id="cph1_password"]')
        password.send_keys(os.environ.get('ELC_PASSWORD'))

        button = driver.find_element(By.XPATH, '//*[@id="cph1_signin"]')
        button.click()

        main_page = wait.until(EC.visibility_of_element_located((By.XPATH, '//*[@id="deviceokpanel"]')))
        button_device = driver.find_element(By.XPATH, '//*[@id="deviceokpanel"]')
        button_device.click()

        device_page = wait.until(EC.visibility_of_element_located((By.XPATH, '//*[@id="cph1_devicesupdatepanel"]/div[1]/div[2]/div[1]/div[4]')))
        temp_container = driver.find_element(By.XPATH, '//*[@id="channelreading_0_0"]')
        current_temp = float(temp_container.text)
        driver.quit()
        return float(current_temp)
    except Exception as e:
        print(f"An error occurred in automation/get_sensor_temp function:\n {e}")
        driver.quit()


def get_coolbot_temp():
    try:
        chromdriver_path = chromedriver_autoinstaller.install()
        service = Service(chromdriver_path)
        driver = webdriver.Chrome(service=service)
        url = "https://cb.storeitcold.com/#/login"
        driver.get(url)

        wait = WebDriverWait(driver, 20)
        login = wait.until(EC.visibility_of_element_located((By.XPATH, "/html/body/ion-app/ng-component/ion-nav/page-login/single-page/ion-content/div[2]/ion-grid/ion-row/ion-col/div/form/ion-row[1]/ion-col/ion-list/ion-item[1]/div[1]")))

        email = driver.find_element(By.XPATH, "/html/body/ion-app/ng-component/ion-nav/page-login/single-page/ion-content/div[2]/ion-grid/ion-row/ion-col/div/form/ion-row[1]/ion-col/ion-list/ion-item[1]/div[1]/div/ion-input/input")
        email.send_keys(os.environ.get('SIT_EMAIL'))

        password = driver.find_element(By.XPATH, "/html/body/ion-app/ng-component/ion-nav/page-login/single-page/ion-content/div[2]/ion-grid/ion-row/ion-col/div/form/ion-row[1]/ion-col/ion-list/ion-item[2]/div[1]/div/ion-input/input")
        password.send_keys(os.environ.get('SIT_PASSWORD'))

        button = driver.find_element(By.XPATH, "/html/body/ion-app/ng-component/ion-nav/page-login/single-page/ion-content/div[2]/ion-grid/ion-row/ion-col/div/form/ion-row[2]/ion-col/button[1]")
        button.click()

        main_page = wait.until(EC.visibility_of_element_located((By.XPATH, '//*[@id="statusGrid"]/ion-row[1]/ion-col/span')))

        button_account = driver.find_element(By.XPATH, '//*[@id="tab-t0-1"]')
        button_account.click()
        time.sleep(3) # wait until the command is fully displayed and clickable

        button_click = driver.find_element(By.XPATH, '//*[@id="tabpanel-t0-1"]/page-devices/ion-content/div[2]/div/ion-list/ion-grid/ion-row/ion-col[3]/expanding-list-item[2]/div/ion-list-header/div[1]/ion-icon')
        button_click.click()
        time.sleep(3)

        element = driver.find_element(By.XPATH, '//*[@id="tabpanel-t0-1"]/page-devices/ion-content/div[2]/div/ion-list/ion-grid/ion-row/ion-col[3]/expanding-list-item[2]/div/div/ion-item[1]/div[1]/span')
        temp = element.text
        temp = temp.split('°')[0]
        driver.quit()
        return float(temp)
    except Exception as e:
        print(f"An error occurred in automation/get_coolbot_temp function:\n {e}")
        driver.quit()

def change_setpoint(updated_value):
    from real_time_ems import send_temp_to_automation
    """Function that access the CoolBot website and temperature sensor website and change the temperature based on the input value."""
    try:
        current_value = None
        temp = send_temp_to_automation()
        # if the current temperature is within the updated setpoint range
        if updated_value - 2 <= temp and temp <= updated_value + 2:
            print(f"Temperature is within the range of the updated setpoint: {updated_value} - 2 <= {temp} <= {updated_value} + 2")
        
        while updated_value != current_value:
            try:
                # For test purposes
                print(f"Temperature setpoint changed to {updated_value}")
                current_value = change_value(updated_value)
                time.sleep(5) # wait until the command fully changed
            except Exception as e:
                print(f"An Error has occurred for Cooler Web Automation: {e}")
    except Exception as e:
        print(f"An error occurred in automation/change_setpoint function:\n {e}")

    