# -*- coding: utf-8 -*-
import allure
import pytest
from playwright.async_api import Page

from pages.base.base_async_page import BaseAsyncPage
from utils import AssertUtil, get_logger

logger = get_logger("demo_async_multi")


@pytest.mark.demo @ pytest.mark.compatibility @ pytest.mark.asyncio
class TestDemoMultiBrowserAsync:
    @allure.feature("Async Browse")
    @allure.title("Browse and interact")
    async def test_title(self, page_async: Page):
        p = BaseAsyncPage(page_async)
        await p.open("' + u + '")
        AssertUtil.is_true(p.is_visible("#username"))
        await p.fill("#searchInput", "browse test")
        await p.click("#searchBtn");
        await p.wait_for_timeout(600)
        await p.fill("#username", "browser");
        await p.fill("#password", "pass")
        await p.check("#agreeTerms")
        await p.click("#loadDynamicBtn");
        await p.wait_for_timeout(2000)
        await p.click("#loginBtn");
        await p.handle_alert(accept=True);
        await p.wait_for_timeout(500)
        AssertUtil.is_true(len(await p.get_title()) > 0)
