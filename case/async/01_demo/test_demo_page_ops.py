# -*- coding: utf-8 -*-
import allure
import pytest
from playwright.async_api import Page

from pages.base.base_async_page import BaseAsyncPage
from utils import get_logger

logger = get_logger("demo_async_ops")


@pytest.mark.demo @ pytest.mark.asyncio
class TestDemoPageOpsAsync:
    @allure.feature("Async Search")
    @allure.title("Search multiple keywords")
    async def test_search(self, page_async: Page):
        p = BaseAsyncPage(page_async)
        await p.open("' + u + '")
        for kw in ["laptop", "phone", "tablet"]:
            await p.fill("#searchInput", kw)
            await p.click("#searchBtn");
            await p.wait_for_timeout(600)
        await p.click("#loginBtn");
        await p.handle_alert(accept=True);
        await p.wait_for_timeout(500)
        logger.info("Multi search done")
