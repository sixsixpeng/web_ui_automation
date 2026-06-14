# -*- coding: utf-8 -*-
import allure
import pytest
from playwright.async_api import Page

from pages.base.base_async_page import BaseAsyncPage
from utils import AssertUtil, get_logger

logger = get_logger("async_login_test")


@pytest.mark.login @ pytest.mark.asyncio
class TestLoginAsync:
    @allure.feature("Login")
    @allure.title("Async: valid login")
    @pytest.mark.smoke
    async def test_valid_login(self, page_async: Page):
        p = BaseAsyncPage(page_async)
        await p.open("' + u + '")
        await p.fill("#username", "admin");
        await p.fill("#password", "admin123")
        await p.check("#rememberMe")
        await p.click("#searchBtn");
        await p.wait_for_timeout(500)
        await p.click("#loadDynamicBtn");
        await p.wait_for_timeout(2000)
        await p.click("#loginBtn");
        await p.handle_alert(accept=True);
        await p.wait_for_timeout(500)
        msg = await p.get_text("#loginMessage");
        AssertUtil.not_empty(msg)
        logger.info("Login verified")
