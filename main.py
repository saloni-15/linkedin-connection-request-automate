from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import WebDriverException
from selenium.common.exceptions import TimeoutException
from constants import Constants
from linkedin_message import message_to_recruiter
from dotenv import load_dotenv
import os
import sys

load_dotenv()

linkedin_username = os.getenv('LINKEDIN_USERNAME')
linkedin_password = os.getenv('LINKEDIN_PASSWORD')


company_name = sys.argv[1]
url = f"https://www.linkedin.com/company/{company_name}/people/"

options = Options()
options.add_experimental_option("detach", True)
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

#redirect to company's people section
try:
    driver.get(url)
except WebDriverException as e:
    print(f"Error occurred while navigating to the URL: {e}")

driver.maximize_window()

#login to linkedin
email_field = driver.find_element(By.ID, "username")
email_field.send_keys(linkedin_username)

password_field = driver.find_element(By.ID, "password")
password_field.send_keys(linkedin_password)

sign_in_button = driver.find_element(By.ID, "organic-div")
sign_in_button.click()

#list of keywords
search_keywords = ["software", "talent"]
try:
    WebDriverWait(driver, Constants.PEOPLE_SEARCH_TIMEOUT).until(EC.visibility_of_element_located((By.CLASS_NAME, "org-people__insights-container")))
    keyword_search_field = driver.find_element(By.ID, "people-search-keywords")
except TimeoutException:
    print("Timeout: Search results did not load within the specified time.")

#search people for every keyword
for key in search_keywords:
    keyword_search_field.send_keys(key)
    keyword_search_field.send_keys(Keys.ENTER)
    try:
        WebDriverWait(driver, Constants.KEYWORD_SEARCH_TIMEOUT).until(EC.visibility_of_element_located((By.CLASS_NAME, "scaffold-finite-scroll")))
        pattern = r"\b(\w*connect)\b$"
        connect_buttons = driver.find_elements(By.CSS_SELECTOR, "[aria-label$='connect']")
    except TimeoutException:
        print("Timeout: Search results did not load within the specified time.")

    #send connection to 5 people for every keyword
    sent_connection_counter = 0
    
    for button in connect_buttons:
        if "Connect" in button.get_attribute("innerHTML"):
            sent_connection_counter += 1
            button.click()
            try:
                WebDriverWait(driver, Constants.CONNECT_MODAL_TIMEOUT).until(EC.visibility_of_element_located((By.ID, "send-invite-modal")))
                connection_name = driver.find_element(By.TAG_NAME, "strong")
                # print(connection_name.text)
                connection_message = message_to_recruiter(connection_name.text, company_name)
                add_note_button = driver.find_element(By.CSS_SELECTOR, "[aria-label='Add a note']")
            except TimeoutException:
                print("Timeout: Search results did not load within the specified time.")
            add_note_button.click()

            try:
                WebDriverWait(driver, Constants.CUSTOM_MESSAGE_TIMEOUT).until(EC.visibility_of_element_located((By.ID, "custom-message")))
                custom_note_field = driver.find_element(By.ID, "custom-message")
                custom_note_field.send_keys(connection_message)
            except TimeoutException:
                print("Timeout: Search results did not load within the specified time.")

            
            # cancel_button = driver.find_element(By.CSS_SELECTOR, "[aria-label='Cancel adding a note']")
            # cancel_button.click()
            # dismiss_button = driver.find_element(By.CSS_SELECTOR, "[aria-label='Dismiss']")
            # dismiss_button.click()

            send_button = driver.find_element(By.CSS_SELECTOR, "[aria-label='Send now']")
            send_button.click()
            if(sent_connection_counter == Constants.TOTAL_CONNECTION):
                break


driver.quit()