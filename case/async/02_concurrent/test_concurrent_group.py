# -*- coding: utf-8 -*-
"""Demo: ConcurrentGroup auto-discovers and runs steps concurrently"""
import pytest
from playwright.async_api import async_playwright

from utils import get_logger
from utils.async_runner import ConcurrentGroup, set_max_concurrency

logger = get_logger("demo_concurrent_group")
URL = "file:///E:/code/web_ui_automation/case/test_page.html"
# Set global max concurrency
set_max_concurrency(3)


class LoginSteps(ConcurrentGroup):
    """Login-related steps, auto-discovered and run concurrently"""
    max_concurrency = 2  # optional override

    async def step_valid_login(self):
        async with async_playwright() as p:
            b = await p.chromium.launch()
            pg = await (await b.new_context()).new_page()
            await pg.goto(URL)
            await pg.fill("#username", "admin")
            await pg.fill("#password", "admin123")
            logger.info("  valid login done")
            await b.close()

    async def step_wrong_password(self):
        async with async_playwright() as p:
            b = await p.chromium.launch()
            pg = await (await b.new_context()).new_page()
            await pg.goto(URL)
            await pg.fill("#username", "admin")
            await pg.fill("#password", "wrong")
            logger.info("  wrong password done")
            await b.close()

    async def step_empty_form(self):
        async with async_playwright() as p:
            b = await p.chromium.launch()
            pg = await (await b.new_context()).new_page()
            await pg.goto(URL)
            await pg.click("#loginBtn")
            logger.info("  empty form done")
            await b.close()


@pytest.mark.asyncio
async def test_login_concurrent_group():
    """
    Single pytest test that auto-runs all Step methods concurrently.
    No manual gather() needed - ConcurrentGroup handles it.
    """
    steps = LoginSteps()
    results = await steps.run()
    for name, ok, err in results:
        logger.info(f"Result: {name} = {'PASS' if ok else 'FAIL'}")
        assert ok, f"{name}: {err}"
