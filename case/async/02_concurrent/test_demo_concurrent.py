# -*- coding: utf-8 -*-
import asyncio

import pytest
from playwright.async_api import Browser

from pages.base.base_async_page import BaseAsyncPage

URL = "file:///E:/code/web_ui_automation/case/test_page.html"


@pytest.mark.demo
@pytest.mark.asyncio
class TestDemoConcurrentAsync:
    @pytest.mark.smoke
    async def test_concurrent(self, browser_async: Browser):
        async def session(i):
            ctx = await browser_async.new_context()
            pg = await ctx.new_page()
            p = BaseAsyncPage(pg)
            await p.open(URL);
            await p.wait_for_timeout(300)
            await p.fill("#searchInput", f"s-{i}")
            await p.click("#searchBtn");
            await p.wait_for_timeout(400)
            await p.fill("#username", f"u-{i}");
            await p.fill("#password", f"p-{i}")
            await p.check("#rememberMe")
            await p.click("#loginBtn");
            await p.handle_alert(accept=True);
            await p.wait_for_timeout(300)
            t = await p.get_title()
            await ctx.close()
            return t

        rs = await asyncio.gather(*[session(i) for i in range(3)])
        assert len(rs) == 3
