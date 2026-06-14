# -*- coding: utf-8 -*-
import allure
import pytest
import time

from pages.base.base_sync_page import BaseSyncPage
from utils import AssertUtil, ScreenshotSyncUtil, get_logger

logger = get_logger("demo_sync_login")


@pytest.mark.demo @ pytest.mark.login
class TestDemoLoginSync:
    @allure.feature("Login Module")
    @allure.story("Full login flow")
    @allure.title("Complete login flow")
    @pytest.mark.smoke
    def test_full_login_flow(self, page_sync):
        p = BaseSyncPage(page_sync)
        logger.info("=== Login flow ===")
        p.open("' + u + '");
        time.sleep(0.5)
        AssertUtil.is_true("Demo" in p.get_title())
        p.fill("#username", "admin");
        p.fill("#password", "admin123")
        p.check("#rememberMe")
        p.fill("#searchInput", "headphone")
        p.click("#searchBtn");             # 搜索触发 alert
        p.handle_alert(accept=True);                         # 处理搜索弹窗
        p.wait_for_timeout(600)
        p.check("#agreeTerms")
        p.click("#loginBtn");                                # 登录无 alert
        p.wait_for_timeout(300)
        p.wait_for_timeout(500)
        msg = p.get_text("#loginMessage")
        AssertUtil.not_empty(msg)
        ScreenshotSyncUtil.take_window_screenshot(p.page, name="login_done")
        logger.info("Login completed: " + msg)
