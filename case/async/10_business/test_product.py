# -*- coding: utf-8 -*-
import allure
import pytest
from playwright.async_api import Page

from pages.base.base_async_page import BaseAsyncPage
from utils import get_logger

logger = get_logger("async_product_test")


@pytest.mark.product @ pytest.mark.asyncio
class TestProductAsync:
    @allure.feature("Product")
    @allure.title("Async: search + cart")
    @pytest.mark.smoke
    async def test_search_product(self, page_async: Page):
        p = BaseAsyncPage(page_async)
        await p.open("' + u + '")
        await p.fill("#searchInput", "phone")
        await p.click("#searchBtn");
        await p.wait_for_timeout(600)
        await p.click(".add-to-cart");
        await p.wait_for_timeout(400)
        await p.click("#loadDynamicBtn");
        await p.wait_for_timeout(2000)
        await p.fill("#username", "buyer");
        await p.fill("#password", "pass")
        await p.check("#rememberMe")
        await p.click("#loginBtn");
        p.handle_alert(accept=True);
        await p.wait_for_timeout(500)
        logger.info("Product done")
