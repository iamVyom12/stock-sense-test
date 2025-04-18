venv\Scripts\activate
pytest --alluredir=allure-results
allure serve allure-results
allure generate allure-results --clean -o allure-report
allure open allure-report

Empty Fields	Try to submit with empty username, password, or both
🚫 SQL Injection	Try using ' OR '1'='1 as input to check basic validation
⏰ Login Delay	Enter credentials and wait before clicking Sign in – check if session expires
🔒 Password Mask	Check if the password field hides characters (type = "password")
🖱️ Remember Me	Check if “Remember Me” checkbox retains login info after logout/refresh
🧹 Form Reset	Click "Sign up" then return — check if login form resets 