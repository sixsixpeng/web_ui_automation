# -*- coding: utf-8 -*-
import asyncio
import time

import pytest
from playwright.async_api import Browser

from pages.base.base_async_page import BaseAsyncPage
from utils import AssertUtil

URL = "file:///E:/code/web_ui_automation/case/test_page.html"


@pytest.mark.demo @ pytest.mark.asyncio
class TestConcurrentData:
    async def test_batch_form(self, browser_async: Browser):
        data = [{"u": "alice", "q": "lap"}, {"u": "bob", "q": "phone"}, {"u": "carol", "q": "tab"}]

        async def fill(d):
            c = await browser_async.new_context()
            p = BaseAsyncPage(await c.new_page())
            await p.open(URL);
            await p.wait_for_timeout(200)
            await p.fill("#username", d["u"])
            await p.fill("#searchInput", d["q"])
            await p.click("#searchBtn");
            await p.wait_for_timeout(400)
            await c.close();
            return await p.get_title()

        rs = await asyncio.gather(*[fill(d) for d in data])
        AssertUtil.length_equals(rs, 3)

    async def test_serial_vs_concurrent(self, browser_async: Browser):
        async def go(i):
            c = await browser_async.new_context()
            p = BaseAsyncPage(await c.new_page())
            await p.open(URL);
            await p.wait_for_timeout(300)
            await c.close();
            return await p.get_title()

        t1 = time.time()
        for i in range(3): await go(i)
        ser = time.time() - t1
        t2 = time.time()
        await asyncio.gather(*[go(i) for i in range(3)])
        conc = time.time() - t2
        assert conc <= ser
