# -*- coding: utf-8 -*-
import allure
import pytest

from pages.base.base_sync_page import BaseSyncPage
from utils import ScreenshotSyncUtil, get_logger

logger = get_logger("sync_product_test")


@pytest.mark.product
class TestProductSync:
    @allure.feature("Product")
    @allure.story("Search")
    @allure.title("Sync: search + cart")
    @pytest.mark.smoke
    def test_search_product(self, page_sync):
        p = BaseSyncPage(page_sync)
        p.open("' + u + '")
        p.fill("#searchInput", "phone")
        p.select_option("#sortSelect", "price_desc")
        p.click("#searchBtn");
        p.wait_for_timeout(600)
        p.click(".add-to-cart");
        p.wait_for_timeout(400)
        p.click("#loadDynamicBtn");
        p.wait_for_timeout(2000)
        p.fill("#username", "buyer");
        p.fill("#password", "pass")
        p.check("#rememberMe")
        p.click("#loginBtn");                                # 登录无 alert
        p.wait_for_timeout(300)
        p.wait_for_timeout(500)
        ScreenshotSyncUtil.take_window_screenshot(p.page, name="biz_product")
