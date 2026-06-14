# -*- coding: utf-8 -*-
import asyncio

import pytest
from playwright.async_api import Browser

from pages.base.base_async_page import BaseAsyncPage

URL = "file:///E:/code/web_ui_automation/case/test_page.html"


@pytest.mark.demo @ pytest.mark.asyncio
class TestConcurrentBatch:
    async def test_gather_5(self, browser_async: Browser):
        async def go(i):
            c = await browser_async.new_context()
            p = BaseAsyncPage(await c.new_page())
            await p.open(URL);
            await p.wait_for_timeout(300)
            await p.fill("#searchInput", f"g-{i}")
            await p.click("#searchBtn");
            await p.wait_for_timeout(400)
            await c.close();
            return await p.get_title()

        rs = await asyncio.gather(*[go(i) for i in range(5)])
        assert len(rs) == 5

    async def test_semaphore_8(self, browser_async: Browser):
        sem = asyncio.Semaphore(3)

        async def go(i):
            async with sem:
                c = await browser_async.new_context()
                p = BaseAsyncPage(await c.new_page())
                await p.open(URL);
                await p.wait_for_timeout(300)
                await p.fill("#searchInput", f"s-{i}")
                await p.fill("#username", f"u-{i}")
                await p.click("#loginBtn");
                await p.handle_alert(accept=True);
                await p.wait_for_timeout(300)
                await c.close();
                return await p.get_title()

        rs = await asyncio.gather(*[go(i) for i in range(8)])
        assert len(rs) == 8
