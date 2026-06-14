# -*- coding: utf-8 -*-
"""Global popup handler - Sync + Async"""
from pages.base.base_async_page import BaseAsyncPage
from pages.base.base_sync_page import BaseSyncPage
from utils import get_logger

logger = get_logger("global_popup")


class GlobalPopupSync(BaseSyncPage):
    CLOSE_BUTTON = "button[class*='close'], button[aria-label='close']"

    def close_modal(self):
        """关闭模态框"""
        if self.is_visible(self.CLOSE_BUTTON):
            self.click(self.CLOSE_BUTTON)


class GlobalPopupAsync(BaseAsyncPage):
    CLOSE_BUTTON = "button[class*='close'], button[aria-label='close']"

    async def close_modal(self):
        if await self.is_visible(self.CLOSE_BUTTON):
            await self.click(self.CLOSE_BUTTON)
