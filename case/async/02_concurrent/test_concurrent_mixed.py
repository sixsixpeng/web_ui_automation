# -*- coding: utf-8 -*-
import asyncio

import pytest
from playwright.async_api import Browser

from pages.base.base_async_page import BaseAsyncPage
from utils import hash_util, AssertUtil

URL = "file:///E:/code/web_ui_automation/case/test_page.html"


@pytest.mark.demo @ pytest.mark.asyncio
class TestConcurrentMixed:
    async def test_ui_hash(self, browser_async: Browser):
        async def ui():
            c = await browser_async.new_context()
            p = BaseAsyncPage(await c.new_page())
            await p.open(URL);
            await p.wait_for_timeout(300)
            t = await p.get_title();
            await c.close();
            return t

        async def cpu():
            return hash_util.sha256("x" * 5000)[:16]

        title, h = await asyncio.gather(ui(), cpu())
        AssertUtil.not_empty(title)
        AssertUtil.not_empty(h)
