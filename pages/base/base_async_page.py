# -*- coding: utf-8 -*-

"""base_async_page - 异步 BasePage 父类"""
import asyncio
from typing import List, Union

import allure

from utils.log_util import get_logger

logger = get_logger("base_async_page")


def _screenshot_wrapper(method):
    """装饰器：方法执行前后自动截图"""
    async def wrapper(self, *args, **kwargs):
        method_name = method.__name__
        try:
            from utils.config_util import get as cfg
            if str(cfg("screenshot.auto_attach_allure", "false")).lower() == "true":
                await self.attach_window_screenshot(name=f"before_{method_name}")
        except:
            pass
        result = await method(self, *args, **kwargs)
        try:
            from utils.config_util import get as cfg
            if str(cfg("screenshot.auto_attach_allure", "false")).lower() == "true":
                await self.attach_window_screenshot(name=f"after_{method_name}")
        except:
            pass
        return result
    return wrapper


def _log_call():
    import traceback, asyncio
    try:
        task = asyncio.current_task()
        task_id = id(task)
        st = traceback.extract_stack(limit=4)
        if len(st) >= 2:
            f2 = st[-3]
            logger.debug(f"[T:{task_id}][{f2.name}] {f2.filename}:{f2.lineno}")
    except:
        pass


class BaseAsyncPage:
    """异步页面父类，所有 async_pages 继承此类"""

    def __init__(self, page, base_url: str = "", step_delay_ms: int = 0):
        self.page = page
        self.base_url = base_url
        from utils.config_util import get as cfg
        self.timeout = int(cfg("timeout.default", 30000))
        self.element_timeout = int(cfg("timeout.element", 10000))
        self.step_delay_ms = step_delay_ms

    async def _step_delay(self):
        """步骤间异步延时"""
        if self.step_delay_ms:
            await asyncio.sleep(self.step_delay_ms / 1000.0)

    async def _auto_step_screenshot(self, name: str = ""):
        """自动步骤截图（受 config.yaml screenshot.auto_attach_allure 控制）"""
        try:
            from utils.config_util import get as cfg
            if str(cfg("screenshot.auto_attach_allure", "false")).lower() == "true":
                await self.attach_window_screenshot(name=name)
        except:
            pass

    # ====== 导航 ======

    async def open(self, url: str = ""):
        _log_call()
        target = url if url else self.base_url
        with allure.step(f"异步打开页面: {target}"):
            await self.page.goto(target, timeout=self.timeout)
        await self._auto_step_screenshot(name=f"open_{target[:30]}")

    async def refresh(self):
        _log_call()
        """刷新页面"""
        with allure.step("异步刷新页面"):
            await self.page.reload(timeout=self.timeout)
        await self._auto_step_screenshot(name="after_refresh")

    async def go_back(self):
        _log_call()
        with allure.step("异步后退"):
            await self.page.go_back()
        await self._auto_step_screenshot(name="after_go_back")

    async def go_forward(self):
        _log_call()
        with allure.step("异步前进"):
            await self.page.go_forward()
        await self._auto_step_screenshot(name="after_go_forward")

    def locator(self, selector: str):
        _log_call()
        return self.page.locator(selector)

    async def click(self, selector: str, timeout: int = None, **kwargs):
        _log_call()
        with allure.step(f"异步点击: {selector}"):
            t = timeout or self.timeout
            await self.page.locator(selector).click(timeout=t, **kwargs)
            logger.debug(f"异步已点击: {selector}")
            await self._auto_step_screenshot(name=f"click_{selector}")
            await self._step_delay()

    async def fill(self, selector: str, text: str, timeout: int = None):
        _log_call()
        with allure.step(f"异步输入: {selector}"):
            await self.page.locator(selector).fill(text, timeout=timeout)
            logger.debug(f"异步已输入: {selector}")
            await self._auto_step_screenshot(name=f"fill_{selector}")
            await self._step_delay()

    async def type_text(self, selector: str, text: str, delay: int = 50):
        _log_call()
        await self.page.locator(selector).press_sequentially(text, delay=delay)
        await self._auto_step_screenshot(name=f"type_{selector}")

    async def select_option(self, selector: str, value):
        _log_call()
        await self.page.locator(selector).select_option(value)
        await self._auto_step_screenshot(name=f"select_{selector}")

    async def check(self, selector: str):
        _log_call()
        await self.page.locator(selector).check()
        await self._auto_step_screenshot(name=f"check_{selector}")
        await self._step_delay()

    async def uncheck(self, selector: str):
        _log_call()
        await self.page.locator(selector).uncheck()
        await self._auto_step_screenshot(name=f"uncheck_{selector}")

    async def hover(self, selector: str):
        _log_call()
        await self.page.locator(selector).hover()
        await self._auto_step_screenshot(name=f"hover_{selector}")

    async def double_click(self, selector: str):
        _log_call()
        await self.page.locator(selector).dblclick()
        await self._auto_step_screenshot(name=f"dblclick_{selector}")

    async def right_click(self, selector: str):
        _log_call()
        await self.page.locator(selector).click(button="right")
        await self._auto_step_screenshot(name=f"rightclick_{selector}")

    async def press_key(self, key: str):
        _log_call()
        await self.page.keyboard.press(key)
        await self._auto_step_screenshot(name=f"press_{key}")

    async def is_visible(self, selector: str, timeout: int = None) -> bool:
        _log_call()
        return await self.page.locator(selector).is_visible(timeout=timeout or self.element_timeout)

    async def is_enabled(self, selector: str) -> bool:
        _log_call()
        return await self.page.locator(selector).is_enabled()

    async def is_checked(self, selector: str) -> bool:
        _log_call()
        return await self.page.locator(selector).is_checked()

    async def get_text(self, selector: str, timeout: int = None) -> str:
        _log_call()
        return await self.page.locator(selector).text_content(timeout=timeout or self.element_timeout)

    async def get_inner_text(self, selector: str) -> str:
        _log_call()
        return await self.page.locator(selector).inner_text()

    async def get_attribute(self, selector: str, attr: str) -> str:
        _log_call()
        return await self.page.locator(selector).get_attribute(attr)

    async def get_input_value(self, selector: str) -> str:
        _log_call()
        return await self.page.locator(selector).input_value()

    async def get_count(self, selector: str) -> int:
        _log_call()
        return await self.page.locator(selector).count()

    async def wait_for_visible(self, selector: str, timeout: int = None):
        _log_call()
        await self.page.locator(selector).wait_for(state="visible", timeout=timeout or self.timeout)

    async def wait_for_hidden(self, selector: str, timeout: int = None):
        _log_call()
        await self.page.locator(selector).wait_for(state="hidden", timeout=timeout or self.timeout)

    async def wait_for_load_state(self, state: str = "networkidle"):
        _log_call()
        await self.page.wait_for_load_state(state, timeout=self.timeout)

    async def wait_for_timeout(self, ms: int):
        await asyncio.sleep(ms / 1000.0)

    async def get_title(self) -> str:
        _log_call()
        return await self.page.title()

    async def get_url(self) -> str:
        _log_call()
        return self.page.url

    async def attach_window_screenshot(self, name: str = None):
        _log_call()
        from utils.screenshot_util import ScreenshotAsyncUtil
        util = ScreenshotAsyncUtil()
        await util.take_window_screenshot(self.page, name=name)

    async def attach_full_screenshot(self, name: str = None):
        _log_call()
        from utils.screenshot_util import ScreenshotAsyncUtil
        util = ScreenshotAsyncUtil()
        await util.take_full_page_screenshot(self.page, name=name)

    async def attach_element_screenshot(self, selector: str, name: str = None):
        _log_call()
        from utils.screenshot_util import ScreenshotAsyncUtil
        util = ScreenshotAsyncUtil()
        await util.take_element_screenshot(self.page, selector, name=name)

    async def handle_alert(self, accept: bool = True):
        _log_call()
        try:
            dialog = await self.page.wait_for_event("dialog", timeout=2000)
            if accept:
                await dialog.accept()
            else:
                await dialog.dismiss()
            await self._auto_step_screenshot(name="alert")
        except:
            pass

    async def scroll_to_top(self):
        _log_call()
        await self.page.evaluate("window.scrollTo(0,0)")
        await self._auto_step_screenshot(name="scroll_top")

    async def scroll_to_bottom(self):
        _log_call()
        await self.page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        await self._auto_step_screenshot(name="scroll_bottom")

    async def scroll_to_element(self, selector: str):
        _log_call()
        await self.page.locator(selector).scroll_into_view_if_needed()
        await self._auto_step_screenshot(name=f"scroll_{selector}")

    async def press_sequentially(self, selector: str, text: str, delay: int = 50):
        _log_call()
        await self.page.locator(selector).press_sequentially(text, delay=delay)

    async def click_position(self, x: int, y: int):
        _log_call()
        await self.page.mouse.click(x, y)
        await self._auto_step_screenshot(name=f"click_pos_{x}_{y}")

    async def double_click_position(self, x: int, y: int):
        _log_call()
        await self.page.mouse.dblclick(x, y)
        await self._auto_step_screenshot(name=f"dblclick_pos_{x}_{y}")

    async def hover_position(self, x: int, y: int):
        _log_call()
        await self.page.mouse.move(x, y)
        await self._auto_step_screenshot(name=f"hover_pos_{x}_{y}")

    async def wait_for_response(self, url_pattern: str, timeout: int = None):
        _log_call()
        timeout = timeout or self.timeout
        return await self.page.wait_for_response(url_pattern, timeout=timeout)

    async def reload_and_wait(self):
        _log_call()
        await self.page.reload(wait_until="networkidle", timeout=self.timeout)
        await self._auto_step_screenshot(name="reload")

    async def copy_to_clipboard(self, text: str):
        _log_call()
        await self.page.evaluate(f"navigator.clipboard.writeText('{text}')")
        await self._auto_step_screenshot(name="clipboard")

    async def new_tab(self, url: str = ""):
        _log_call()
        pg = await self.page.context.new_page()
        if url:
            await pg.goto(url, timeout=self.timeout)
        await self._auto_step_screenshot(name="new_tab")
        return pg

    async def tab_count(self) -> int:
        _log_call()
        return len(self.page.context.pages)

    def current_tab(self):
        _log_call()
        pages = self.page.context.pages
        for i, p in enumerate(pages):
            if p == self.page:
                return i
        return 0

    async def wait_for_new_tab(self, timeout: int = None):
        _log_call()
        timeout = timeout or self.element_timeout
        import time
        start = time.time()
        pages_before = len(self.page.context.pages)
        while time.time() - start < timeout / 1000:
            pages = self.page.context.pages
            if len(pages) > pages_before:
                new_page = pages[-1]
                await new_page.wait_for_load_state()
                await self._auto_step_screenshot(name="new_tab_waited")
                return new_page
            await asyncio.sleep(0.1)
        raise TimeoutError(f"No new tab within {timeout}ms")

    async def close_ad_popups(self, timeout: int = None) -> bool:
        _log_call()
        timeout = timeout or self.element_timeout
        import time
        start = time.time()
        while time.time() - start < timeout / 1000:
            try:
                dialogs = self.page.context.pages
                if len(dialogs) > 1:
                    for d in dialogs:
                        if d != self.page:
                            await d.close()
                    await self._auto_step_screenshot(name="popup_closed")
                    return True
            except:
                pass
            await asyncio.sleep(0.2)
        return False

    async def handler(self):
        _log_call()
        pass
