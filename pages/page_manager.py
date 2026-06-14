# -*- coding: utf-8 -*-
"""PageManager - Unified page object manager with auto-loading and caching"""
import importlib

PAGES_MODULE = "pages.business"
PAGE_SUFFIX_SYNC = "PageSync"
PAGE_SUFFIX_ASYNC = "PageAsync"


class PageManager:
    """
    Auto-loads and caches page objects by name convention.

    Usage:
        login_page: LoginPageSync = pages.login
        login_page.login("admin", "admin123")

        # Async
        login_page: LoginPageAsync = pages.login
        await login_page.login("admin", "admin123")
    """

    def __init__(self, page, is_async: bool = False):
        self._page = page
        self._is_async = is_async
        self._cache = {}

    def __getattr__(self, name: str):
        if name in self._cache:
            return self._cache[name]

        suffix = PAGE_SUFFIX_ASYNC if self._is_async else PAGE_SUFFIX_SYNC
        class_name = name.capitalize() + suffix

        try:
            module = importlib.import_module(f"{PAGES_MODULE}.{name}_page")
            page_cls = getattr(module, class_name)
        except (ModuleNotFoundError, AttributeError) as e:
            raise AttributeError(
                f"Page object not found: {name} -> {class_name}. "
                f"Expected {PAGES_MODULE}.{name}_page to define class {class_name}. Error: {e}"
            )

        instance = page_cls(self._page)
        self._cache[name] = instance
        return instance


class SyncPageManager(PageManager):
    """Sync page manager (auto-detects sync suffix)"""

    def __init__(self, page):
        super().__init__(page, is_async=False)


class AsyncPageManager(PageManager):
    """Async page manager (auto-detects async suffix)"""

    def __init__(self, page):
        super().__init__(page, is_async=True)
