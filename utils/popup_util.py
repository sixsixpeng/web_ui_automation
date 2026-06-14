# -*- coding: utf-8 -*-
"""popup_util - Popup handler (Sync + Async)"""
from utils.log_util import get_logger

logger = get_logger("popup_util")


class PopupSyncUtil:
    def __init__(self, page=None):
        self._page = page

    def set_page(self, page):
        """设置弹窗处理的页面对象"""
        self._page = page

    def close_popup_ads(self, timeout=3000):
        """自动关闭页面广告弹窗"""
        if not self._page: return False
        # 关闭前截图
        try:
            from utils.screenshot_util import ScreenshotSyncUtil
            ScreenshotSyncUtil.take_window_screenshot(self._page, name="before_close_popup", attach_allure=True)
        except:
            pass
        for sel in ["div[class*='ad']", "div[class*='modal']", "div[class*='popup']"]:
            try:
                el = self._page.locator(sel).first
                if el.is_visible(timeout=timeout):
                    cb = el.locator("button,[class*='close'],[class*='dismiss']").first
                    if cb.is_visible(timeout=1000): cb.click()
                    # 关闭后截图
                    try:
                        ScreenshotSyncUtil.take_window_screenshot(self._page, name="after_close_popup", attach_allure=True)
                    except:
                        pass
                    return True
            except:
                continue
        return False


class PopupAsyncUtil:
    def __init__(self, page=None):
        self._page = page

    def set_page(self, page):
        """设置弹窗处理的页面对象"""
        self._page = page

    async def close_popup_ads(self, timeout=3000):
        if not self._page: return False
        # 关闭前截图
        try:
            from utils.screenshot_util import ScreenshotAsyncUtil
            util = ScreenshotAsyncUtil()
            await util.take_window_screenshot(self._page, name="before_close_popup_async", attach_allure=True)
        except:
            pass
        for sel in ["div[class*='ad']", "div[class*='modal']", "div[class*='popup']"]:
            try:
                el = self._page.locator(sel).first
                if await el.is_visible(timeout=timeout):
                    cb = el.locator("button,[class*='close'],[class*='dismiss']").first
                    if await cb.is_visible(timeout=1000): await cb.click()
                    # 关闭后截图
                    try:
                        await util.take_window_screenshot(self._page, name="after_close_popup_async", attach_allure=True)
                    except:
                        pass
                    return True
            except:
                continue
        return False
