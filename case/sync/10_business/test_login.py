# -*- coding: utf-8 -*-
import allure
import pytest

from pages.base.base_sync_page import BaseSyncPage
from utils import AssertUtil, ScreenshotSyncUtil, get_logger

logger = get_logger("sync_login_test")


@pytest.mark.login
class TestLoginSync:
    @allure.feature("Login")
    @allure.story("Valid login")
    @allure.title("Sync: valid login")
    @pytest.mark.smoke @ pytest.mark.critical
    def test_valid_login(self, page_sync):
        p = BaseSyncPage(page_sync)
        p.open("' + u + '")
        p.fill("#username", "admin");
        p.fill("#password", "admin123")
        p.check("#rememberMe");
        p.check("#agreeTerms")
        p.fill("#searchInput", "phone");
        p.click("#searchBtn");
        p.wait_for_timeout(600)
        p.click("#loadDynamicBtn");
        p.wait_for_timeout(2000)
        p.click("#loginBtn");
        p.wait_for_timeout(300)
        p.handle_alert(accept=True);
        p.wait_for_timeout(500)
        msg = p.get_text("#loginMessage");
        AssertUtil.not_empty(msg)
        ScreenshotSyncUtil.take_window_screenshot(p.page, name="biz_login")

    @allure.feature("Login")
    @allure.story("Form fill")
    @allure.title("Fill wrong password")
    def test_fill_wrong_pass(self, page_sync):
        p = BaseSyncPage(page_sync)
        p.open("' + u + '")
        p.fill("#username", "admin");
        p.fill("#password", "wrong")
        p.click("#loginBtn")
        msg = p.get_text("#loginMessage");
        AssertUtil.is_true(len(msg) > 0)
        ScreenshotSyncUtil.take_window_screenshot(p.page, name="biz_wrong")
