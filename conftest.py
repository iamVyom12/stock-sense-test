import pytest
import os
import json
import allure
from datetime import datetime

# Environment configuration
@pytest.fixture(scope="session")
def env_config():
    """Load environment configuration"""
    env = os.environ.get("TEST_ENV", "dev")
    config_file = f"config.{env}.json"
    
    if os.path.exists(config_file):
        with open(config_file, 'r') as f:
            return json.load(f)
    return {}

# JWT token fixture
@pytest.fixture(scope="session")
def jwt_token(env_config):
    """Get JWT token for API calls"""
    return env_config.get("jwt_token", "default_token")

# Setup allure environment info
@pytest.hookimpl(tryfirst=True)
def pytest_configure(config):
    """Configure test environment"""
    # Create results directory if it doesn't exist
    if not os.path.exists("allure-results"):
        os.makedirs("allure-results")
    
    # Write environment info for Allure report
    env_data = {
        "Environment": os.environ.get("TEST_ENV", "dev"),
        "Python Version": os.popen("python --version").read().strip(),
        "Test Run Date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "Bot API URL": "https://stocksense-backend.onrender.com/api",
        "Tester": "vyom"
    }
    
    with open(os.path.join("allure-results", "environment.properties"), 'w') as f:
        for key, value in env_data.items():
            f.write(f"{key}={value}\n")

# Custom logging for testimport pytest
@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    result = outcome.get_result()

    # Only run this on the 'call' phase of the test (not setup/teardown)
    if result.when == "call":
        test_path = item.nodeid
        metadata = f"Test: {test_path}\nExecution time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        
        allure.attach(
            metadata,
            name="Test Metadata",
            attachment_type=allure.attachment_type.TEXT
        )
