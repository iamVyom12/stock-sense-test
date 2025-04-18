import pytest
import allure
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
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

@allure.title("Login Test - Empty Username")
@allure.description("Checks validation when username field is empty.")
def test_empty_username():
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    driver.maximize_window()

    try:
        with allure.step("Open login page"):
            driver.get("https://stock-sense-fe.onrender.com")
            time.sleep(2)
            
        with allure.step("Fill password only"):
            password_input = driver.find_element(By.CSS_SELECTOR, "input[type='password'][required]")
            password_input.send_keys("password123")
            
        with allure.step("Try to submit form"):
            sign_in_btn = driver.find_element(By.XPATH, "//button[text()='Sign in']")
            sign_in_btn.click()
            time.sleep(1)
            
        with allure.step("Check username validation message"):
            username_input = driver.find_element(By.CSS_SELECTOR, "input[type='text'][required]")
            validation_message = username_input.get_property("validationMessage")
            allure.attach(driver.get_screenshot_as_png(), name="empty_username_validation", attachment_type=allure.attachment_type.PNG)
            assert "fill out this field" in validation_message.lower(), f"Unexpected validation message: {validation_message}"
    finally:
        driver.quit()

@allure.title("Login Test - Empty Password")
@allure.description("Checks validation when password field is empty.")
def test_empty_password():
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    driver.maximize_window()

    try:
        with allure.step("Open login page"):
            driver.get("https://stock-sense-fe.onrender.com")
            time.sleep(2)
            
        with allure.step("Fill username only"):
            username_input = driver.find_element(By.CSS_SELECTOR, "input[type='text'][required]")
            username_input.send_keys("testuser")
            
        with allure.step("Try to submit form"):
            sign_in_btn = driver.find_element(By.XPATH, "//button[text()='Sign in']")
            sign_in_btn.click()
            time.sleep(1)
            
        with allure.step("Check password validation message"):
            password_input = driver.find_element(By.CSS_SELECTOR, "input[type='password'][required]")
            validation_message = password_input.get_property("validationMessage")
            allure.attach(driver.get_screenshot_as_png(), name="empty_password_validation", attachment_type=allure.attachment_type.PNG)
            assert "fill out this field" in validation_message.lower(), f"Unexpected validation message: {validation_message}"
    finally:
        driver.quit()

@allure.title("Login Test - Both Fields Empty")
@allure.description("Checks validation when both fields are empty.")
def test_both_fields_empty():
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    driver.maximize_window()

    try:
        with allure.step("Open login page"):
            driver.get("https://stock-sense-fe.onrender.com")
            time.sleep(2)
            
        with allure.step("Try to submit empty form"):
            sign_in_btn = driver.find_element(By.XPATH, "//button[text()='Sign in']")
            sign_in_btn.click()
            time.sleep(1)
            
        with allure.step("Check validation message on first required field"):
            # Browser will typically show validation on the first required field only
            username_input = driver.find_element(By.CSS_SELECTOR, "input[type='text'][required]")
            validation_message = username_input.get_property("validationMessage")
            allure.attach(driver.get_screenshot_as_png(), name="both_empty_validation", attachment_type=allure.attachment_type.PNG)
            assert "fill out this field" in validation_message.lower(), f"Unexpected validation message: {validation_message}"
    finally:
        driver.quit()

@allure.title("Login Test - SQL Injection")
@allure.description("Tests SQL injection protection in login form.")
def test_login_sql_injection():
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    driver.maximize_window()

    try:
        with allure.step("Open login page"):
            driver.get("https://stock-sense-fe.onrender.com")
            time.sleep(2)

        with allure.step("Enter SQL injection in username"):
            username_input = driver.find_elements(By.XPATH, "//label[contains(text(), 'Username')]/following-sibling::input")[0]
            username_input.send_keys("' OR '1'='1")

        with allure.step("Enter SQL injection in password"):
            password_input = driver.find_elements(By.XPATH, "//label[contains(text(), 'Password')]/following-sibling::input")[0]
            password_input.send_keys("' OR '1'='1")

        with allure.step("Click Sign In"):
            sign_in_btn = driver.find_element(By.XPATH, "//button[@type='submit']")
            sign_in_btn.click()
            time.sleep(5)

        with allure.step("Check login failure"):
            if "chat" not in driver.current_url:
                allure.attach(driver.get_screenshot_as_png(), name="sql_injection_blocked", attachment_type=allure.attachment_type.PNG)
                assert True
            else:
                allure.attach(driver.get_screenshot_as_png(), name="sql_injection_successful", attachment_type=allure.attachment_type.PNG)
                assert False, "SQL Injection attempt succeeded - security risk detected"

    finally:
        driver.quit()

@allure.title("Login Test - Session Timeout")
@allure.description("Tests if login session expires after a delay.")
def test_login_delay():
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
            
        with allure.step("Wait for potential session timeout"):
            # Wait for 2 minutes - adjust based on expected session timeout
            time.sleep(60)
            
        with allure.step("Click Sign In after delay"):
            sign_in_btn = driver.find_element(By.XPATH, "//button[@type='submit']")
            sign_in_btn.click()
            time.sleep(10)
            
        with allure.step("Check if login still works after delay"):
            if "chat" in driver.current_url:
                allure.attach(driver.get_screenshot_as_png(), name="login_after_delay_success", attachment_type=allure.attachment_type.PNG)
                assert True
            else:
                allure.attach(driver.get_screenshot_as_png(), name="login_after_delay_fail", attachment_type=allure.attachment_type.PNG)
                assert False, "Login failed after delay - session might have expired"

    finally:
        driver.quit()

@allure.title("Login Test - Form Reset")
@allure.description("Verifies that user can logout and login form is reset.")
def test_login_form_reset():
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    driver.maximize_window()
    
    try:
        # Login first
        with allure.step("Login with valid credentials"):
            driver.get("https://stock-sense-fe.onrender.com")
            username_input = driver.find_element(By.CSS_SELECTOR, "input[type='text'][required]")
            password_input = driver.find_element(By.CSS_SELECTOR, "input[type='password'][required]")
            username_input.send_keys("not_tarang")
            password_input.send_keys("not_tarang@123")
            sign_in_btn = driver.find_element(By.XPATH, "//button[text()='Sign in']")
            sign_in_btn.click()
            
            # Wait for navigation to complete
            WebDriverWait(driver, 10).until(
                EC.url_contains("chat")
            )
        
        # Logout process
        with allure.step("Navigate back to login by logging out"):
            # First click on the user profile
            user_profile = driver.find_element(By.XPATH, "//div[contains(@class, 'user-dropdown')]//div[contains(@class, 'cursor-pointer')]")
            user_profile.click()
            
            # Wait for logout button to appear
            logout_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(@class, 'text-red-600')]//span[text()='Logout']"))
            )
            
            # Click logout
            logout_button.click()
            
            # Wait for redirect to login page
            WebDriverWait(driver, 10).until(
                EC.url_contains("login")
            )
        
        # Verify form is reset
        with allure.step("Verify login form is reset"):
          username_input = driver.find_element(By.CSS_SELECTOR, "input[type='text'][required]")
          password_input = driver.find_element(By.CSS_SELECTOR, "input[type='password'][required]")

           # Check that fields are empty
          assert username_input.get_attribute("value") == "", "Username field is not empty after logout"
          assert password_input.get_attribute("value") == "", "Password field is not empty after logout"

    # Check the custom 'Remember me' checkbox (based on presence of checked class or SVG)
          remember_me_div = driver.find_element(By.XPATH, "//label[contains(text(), 'Remember me')]/parent::div")

          checkbox_inner = remember_me_div.find_element(By.XPATH, ".//div[contains(@class, 'h-5 w-5')]")

    # Check if the checkbox is "checked" based on its classes (adjust this according to your styles)
          is_checked = "bg-blue-600" in checkbox_inner.get_attribute("class")  # or check if SVG is present

          assert is_checked, "Remember me checkbox is still checked after logout"

          allure.attach(driver.get_screenshot_as_png(), name="reset_form_after_logout", attachment_type=allure.attachment_type.PNG)

    
    finally:
        driver.quit()
