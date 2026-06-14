# -*- coding: utf-8 -*-
"""storage_util - Browser storage (Sync + Async)"""
import json

from utils.log_util import get_logger

logger = get_logger("storage_util")


class StorageSyncUtil:
    @staticmethod
    def get_cookies(page):
        """获取所有 Cookie"""
        return page.context.cookies()

    @staticmethod
    def clear_cookies(page):
        """清除所有 Cookie"""
        page.context.clear_cookies()

    @staticmethod
    def get_local_storage(page):
        """获取 LocalStorage 数据"""
        return json.loads(page.evaluate("()=>JSON.stringify(window.localStorage)") or "{}")

    @staticmethod
    def clear_local_storage(page):
        """清空 LocalStorage"""
        page.evaluate("window.localStorage.clear()")


class StorageAsyncUtil:
    @staticmethod
    async def get_cookies(page): return await page.context.cookies()

    @staticmethod
    async def clear_cookies(page): await page.context.clear_cookies()

    @staticmethod
    async def get_local_storage(page):
        s = await page.evaluate("()=>JSON.stringify(window.localStorage)")
        return json.loads(s) if s else {}

    @staticmethod
    async def clear_local_storage(page): await page.evaluate("window.localStorage.clear()")
