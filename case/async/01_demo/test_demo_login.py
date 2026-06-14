# -*- coding: utf-8 -*-
import allure
import pytest
from playwright.async_api import Page

from pages.base.base_async_page import BaseAsyncPage
from utils import AssertUtil, get_logger

logger = get_logger("demo_async_login")


@pytest.mark.demo @ pytest.mark.login @ pytest.mark.asyncio
class TestDemoLoginAsync:
    @allure.feature("Async Login")
    @allure.title("Async login multi-step")
    @pytest.mark.smoke
    async def test_page_loads(self, page_async: Page):
        p = BaseAsyncPage(page_async)
        await p.open("' + u + '");
        logger.info("Page loaded")
        AssertUtil.is_true("Demo" in await p.get_title())
        await p.fill("#username", "async_user");
        await p.fill("#password", "async_pass")
        await p.check("#rememberMe");
        await p.uncheck("#rememberMe")
        await p.fill("#searchInput", "async test")
        await p.click("#searchBtn");
        await p.wait_for_timeout(600)
        await p.click("#loadDynamicBtn");
        await p.wait_for_timeout(2000)
        await p.click("#loginBtn");
        await p.handle_alert(accept=True);
        await p.wait_for_timeout(500)
        logger.info("Async login done")
