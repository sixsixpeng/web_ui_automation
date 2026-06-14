"""allure_plugin - Allure report enhancement"""
import json
import os

from _pytest.config import Config

from utils.log_util import get_logger
from utils.path_util import path_util

logger = get_logger("allure_plugin")


def pytest_configure(config: Config):
    """Set Allure environment info"""
    raw = str(path_util.allure_raw_dir)
    os.makedirs(raw, exist_ok=True)
    env_file = os.path.join(raw, "environment.properties")
    env = cfg_get("run.env", "test")
    browser = cfg_get("browser_type", "chromium")
    headless = cfg_get("headless", "false")
    with open(env_file, "w", encoding="utf-8") as f:
        f.write(f"Environment={env}\nBrowser={browser}\nHeadless={headless}\n")
    logger.info(f"Allure env written: {env_file}")


def pytest_sessionfinish(session, exitstatus):
    """Generate executor.json and categories.json"""
    raw = str(path_util.allure_raw_dir)
    try:
        data = {"name": "Local", "type": "local", "reportName": "Web UI Test Report"}
        with open(os.path.join(raw, "executor.json"), "w") as f:
            json.dump(data, f, indent=2)
        cats = [
            {"name": "Assertion", "messageRegex": ".*AssertionError.*", "matchedStatuses": ["failed"]},
            {"name": "Timeout", "messageRegex": ".*Timeout.*", "matchedStatuses": ["broken"]},
        ]
        with open(os.path.join(raw, "categories.json"), "w") as f:
            json.dump(cats, f, indent=2)
        logger.info("Allure extra data generated")
    except Exception as e:
        logger.warning(f"Allure post error: {e}")
