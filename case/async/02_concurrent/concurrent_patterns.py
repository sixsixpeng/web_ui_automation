# -*- coding: utf-8 -*-
import asyncio
import pytest
import time

from playwright.async_api import Browser

from pages.base.base_async_page import BaseAsyncPage

URL = "file:///E:/code/web_ui_automation/case/test_page.html"


@pytest.mark.demo
@pytest.mark.asyncio
class TestAsyncConcurrent:
    async def test_gather(self, browser_async: Browser):
        async def ctx(i):
            c = await browser_async.new_context()
            p = BaseAsyncPage(await c.new_page())
            await p.open(URL);
            await p.wait_for_timeout(300)
            await p.fill("#searchInput", f"g-{i}")
            await p.click("#searchBtn");               # 搜索按钮触发 alert
            await p.handle_alert(accept=True);         # 处理搜索弹窗
            await p.wait_for_timeout(400)
            await p.fill("#username", f"u-{i}");
            await p.fill("#password", f"p-{i}")
            await p.check("#rememberMe")               # 勾选记住我
            await p.check("#agreeTerms")               # 勾选同意条款
            await p.click("#loginBtn");                # 登录按钮只显示 div 消息，无 alert
            await p.wait_for_timeout(500)              # 等待登录反馈
            t = await p.get_title();
            await c.close();
            return t

        r1, r2, r3 = await asyncio.gather(ctx(1), ctx(2), ctx(3))
        assert r1 and r2 and r3

    async def test_semaphore(self, browser_async: Browser):
        sem = asyncio.Semaphore(2)

        async def task(i):
            async with sem:
                c = await browser_async.new_context()
                p = BaseAsyncPage(await c.new_page())
                await p.open(URL);
                await p.wait_for_timeout(300)
                await p.fill("#searchInput", f"s-{i}")
                await p.click("#searchBtn");               # 搜索触发 alert
                await p.handle_alert(accept=True);         # 处理搜索弹窗
                await p.fill("#username", f"u-{i}")
                await p.check("#agreeTerms")               # 先勾选同意条款
                await p.check("#rememberMe")
                await p.click("#loginBtn");                # 登录无 alert
                await p.wait_for_timeout(500)
                t = await p.get_title();
                await c.close();
                return t

        rs = await asyncio.gather(*[task(i) for i in range(6)])
        assert len(rs) == 6

    async def test_compare(self, browser_async: Browser):
        async def go(i):
            c = await browser_async.new_context()
            p = BaseAsyncPage(await c.new_page())
            await p.open(URL);
            await p.wait_for_timeout(300)
            await p.fill("#searchInput", f"c-{i}")
            await p.click("#searchBtn");               # 搜索触发 alert
            await p.handle_alert(accept=True);         # 处理搜索弹窗
            await p.wait_for_timeout(400)
            t = await p.get_title();
            await c.close();
            return t

        t1 = time.time()
        for i in range(4): await go(i)
        ser = time.time() - t1
        t2 = time.time()
        await asyncio.gather(*[go(i) for i in range(4)])
        conc = time.time() - t2
        assert conc <= ser

    async def test_practical(self, browser_async: Browser):
        async def a():
            c = await browser_async.new_context()
            p = BaseAsyncPage(await c.new_page())
            await p.open(URL);
            await p.fill("#searchInput", "A")
            await p.click("#searchBtn");               # 搜索触发 alert
            await p.handle_alert(accept=True);         # 处理搜索弹窗
            await p.wait_for_timeout(400)
            t = await p.get_title();
            await c.close();
            return t

        async def b():
            c = await browser_async.new_context()
            p = BaseAsyncPage(await c.new_page())
            await p.open(URL);
            await p.fill("#username", "B")
            await p.check("#agreeTerms")               # 勾选同意条款
            await p.fill("#password", "pwd")
            await p.click("#loginBtn");                # 登录无 alert
            await p.wait_for_timeout(500)
            t = await p.get_title();
            await c.close();
            return t

        ra, rb = await asyncio.gather(a(), b())
        assert ra and rb
