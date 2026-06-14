# -*- coding: utf-8 -*-
import allure
import pytest
import time

from pages.base.base_sync_page import BaseSyncPage
from utils import AssertUtil, ScreenshotSyncUtil, get_logger

logger = get_logger("demo_sync_ops")


@pytest.mark.demo
class TestDemoPageOpsSync:
    @allure.feature("Shopping")
    @allure.story("Full shop flow")
    @allure.title("Search - sort - cart - submit")
    def test_full_shopping(self, page_sync):
        p = BaseSyncPage(page_sync)
        p.open("' + u + '");
        time.sleep(0.5)
        p.fill("#searchInput", "gaming laptop")
        p.select_option("#sortSelect", "price_desc");
        p.wait_for_timeout(300)
        p.click("#searchBtn");
        p.wait_for_timeout(600)
        p.click(".add-to-cart");
        p.wait_for_timeout(400)
        p.click(".add-to-cart");
        p.wait_for_timeout(400)
        p.click("#loadDynamicBtn");
        p.wait_for_timeout(2000)
        p.fill("#username", "buyer");
        p.fill("#password", "pass123")
        p.check("#rememberMe")
        p.click("#loginBtn");
        p.wait_for_timeout(300)
        p.handle_alert(accept=True);
        p.wait_for_timeout(500)
        msg = p.get_text("#loginMessage")
        AssertUtil.is_true(len(msg) > 0)
        ScreenshotSyncUtil.take_window_screenshot(p.page, name="shop_done")
