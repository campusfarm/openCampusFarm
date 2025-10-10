from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import undetected_chromedriver as uc
from dotenv import load_dotenv
import os
from from_root import from_root

load_dotenv(from_root(".env"))

# Disable the __del__ method to prevent errors from being printed
uc.Chrome.__del__ = lambda self: None

def check_battery():

    driver = None  # Initialize driver as None

    try:
        battery = {}
        driver = uc.Chrome()
        
        driver.get('https://www.ford.com/myaccount/account-dashboard')

        # Wait for the page to load and email input field to be present
        wait = WebDriverWait(driver, 20)  # Set maximum wait time (in seconds)

        # Wait for the email input field to become available
        email_field = wait.until(EC.presence_of_element_located((By.ID, 'signInName')))
        email_field.send_keys(os.environ.get("FORD_EMAIL")) 
        
        # Wait for the password input field to become available
        password_field = wait.until(EC.presence_of_element_located((By.ID, 'password')))
        password_field.send_keys(os.environ.get("FORD_PASSWORD"))  

        # Wait for the sign-in button to be clickable and click it
        sign_in_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'button[type="submit"]')))
        sign_in_button.click()

        print("Logged in successfully!")

    except Exception as e:
        print("Error during login:", e)
        driver.quit()
        return

    time.sleep(25)
    # Wait for the next page to load and the Charge Level element to be visible

    try:

        go_to_vehicle_button = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, '[data-testid="go-to-vehicle-button"]')))

        # Click the "Go to Vehicle" button
        go_to_vehicle_button.click()

        # Wait for the vehicle details section to load
        time.sleep(10)

        print("Extracting charge level...")
        charge_level_element = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '.fm-connected-vehicle.fm-battery-charge span'))
        )
        charge_level = charge_level_element.text.strip('%')  # Remove the % sign if present
        print(f"Charge Level Found: {charge_level}%")

        print("Extracting range...")
        range_element = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '.fm-connected-vehicle.charge-level span'))
        )
        est_distance = range_element.text.split()[0]  # Extract only the number
        print(f"Estimated Range Found: {est_distance} miles")

        # Print the results
        print(f"Charge Level: {charge_level}")
        print(f"Range: {est_distance} miles")

        # Update battery dictionary
        battery['miles_left'] = est_distance
        battery['percentage'] = charge_level
        
        # Close the driver and return data
        driver.quit()
        return battery

    except Exception as e:
        print(f"Attempt failed. Error extracting data: {e}")
    finally:
        if driver:
            driver.quit()
