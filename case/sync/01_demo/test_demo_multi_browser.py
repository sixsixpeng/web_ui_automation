# -*- coding: utf-8 -*-
import allure
import pytest
import time

from pages.base.base_sync_page import BaseSyncPage
from utils import AssertUtil, ScreenshotSyncUtil, get_logger

logger = get_logger("demo_sync_multi")


@pytest.mark.demo @ pytest.mark.compatibility
class TestDemoMultiBrowserSync:
    @allure.feature("Roaming")
    @allure.story("Full interaction")
    @allure.title("Scroll - alerts - form")
    def test_page_roaming(self, page_sync):
        p = BaseSyncPage(page_sync)
        p.open("' + u + '");
        time.sleep(0.5)
        AssertUtil.is_true(p.is_visible("#username"))
        p.handle_alert(accept=True)
        p.fill("#username", "roamer");
        p.fill("#password", "roam_pass")
        p.fill("#searchInput", "explore");
        p.fill("#captcha", "CODE")
        p.check("#rememberMe");
        p.uncheck("#rememberMe")
        p.click("#loadDynamicBtn");
        p.wait_for_timeout(2000)
        p.click("#loginBtn");
        p.wait_for_timeout(300)
        p.handle_alert(accept=True);
        p.wait_for_timeout(500)
        ScreenshotSyncUtil.take_window_screenshot(p.page, name="roam_done")
