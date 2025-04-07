import pytest
import allure
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time


@allure.title("Login Test - Valid Credentials")
@allure.description("Checks login functionality with valid credentials.")
def test_login_valid():
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    driver.maximize_window()

    try:
        with allure.step("Open login page"):
            driver.get("https://stock-sense-fe.onrender.com")
            time.sleep(2)

        with allure.step("Enter valid username"):
            username_input = driver.find_elements(By.XPATH, "//label[contains(text(), 'Username')]/following-sibling::input")[0]
            username_input.send_keys("not_tarang")

        with allure.step("Enter valid password"):
            password_input = driver.find_elements(By.XPATH, "//label[contains(text(), 'Password')]/following-sibling::input")[0]
            password_input.send_keys("not_tarang@123")

        with allure.step("Click Sign In"):
            sign_in_btn = driver.find_element(By.XPATH, "//button[@type='submit']")
            sign_in_btn.click()
            time.sleep(5)

        with allure.step("Check login success"):
            if "chat" in driver.current_url:
                allure.attach(driver.get_screenshot_as_png(), name="login_success", attachment_type=allure.attachment_type.PNG)
                assert True
            else:
                allure.attach(driver.get_screenshot_as_png(), name="login_fail", attachment_type=allure.attachment_type.PNG)
                assert False, "Login failed - Unexpected URL"

    finally:
        driver.quit()


@allure.title("Login Test - Invalid Credentials")
@allure.description("Checks login fails with wrong credentials.")
def test_login_invalid():
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    driver.maximize_window()

    try:
        with allure.step("Open login page"):
            driver.get("https://stock-sense-fe.onrender.com")
            time.sleep(2)

        with allure.step("Enter invalid username"):
            username_input = driver.find_elements(By.XPATH, "//label[contains(text(), 'Username')]/following-sibling::input")[0]
            username_input.send_keys("vyom")

        with allure.step("Enter invalid password"):
            password_input = driver.find_elements(By.XPATH, "//label[contains(text(), 'Password')]/following-sibling::input")[0]
            password_input.send_keys("vyom@1234")

        with allure.step("Click Sign In"):
            sign_in_btn = driver.find_element(By.XPATH, "//button[@type='submit']")
            sign_in_btn.click()
            time.sleep(5)

        with allure.step("Check login failure"):
            if "chat" not in driver.current_url:
                allure.attach(driver.get_screenshot_as_png(), name="login_failure_expected", attachment_type=allure.attachment_type.PNG)
                assert True
            else:
                allure.attach(driver.get_screenshot_as_png(), name="login_unexpected_success", attachment_type=allure.attachment_type.PNG)
                assert False, "Login should have failed but succeeded"

    finally:
        driver.quit()
