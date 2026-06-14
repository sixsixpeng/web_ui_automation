# -*- coding: utf-8 -*-
"""Product page objects - Sync + Async"""
import allure

from pages.base.base_async_page import BaseAsyncPage
from pages.base.base_sync_page import BaseSyncPage
from utils import get_logger

logger = get_logger("product_page")


class ProductPageSync(BaseSyncPage):
    SEARCH_INPUT = "#searchInput"
    SEARCH_BUTTON = "#searchBtn"
    PRODUCT_NAME = ".product-name"
    PRODUCT_PRICE = ".product-price"
    ADD_TO_CART_BUTTON = ".add-to-cart"
    CART_BADGE = ".cart-badge"
    SORT_SELECT = "#sortSelect"

    def search_product(self, keyword: str):
        """搜索商品"""
        with allure.step(f"search: {keyword}"):
            self.fill(self.SEARCH_INPUT, keyword)
            self.click(self.SEARCH_BUTTON)

    def get_product_names(self) -> list:
        """获取搜索结果商品名称列表"""
        items = self.page.locator(self.PRODUCT_NAME)
        return [items.nth(i).text_content() for i in range(items.count())]

    def add_to_cart(self, index: int = 0):
        """添加商品到购物车"""
        self.page.locator(self.ADD_TO_CART_BUTTON).nth(index).click()

    def get_cart_count(self) -> int:
        """获取购物车数量"""
        return int(self.get_text(self.CART_BADGE) or "0")


class ProductPageAsync(BaseAsyncPage):
    SEARCH_INPUT = "#searchInput"
    SEARCH_BUTTON = "#searchBtn"
    PRODUCT_NAME = ".product-name"
    PRODUCT_PRICE = ".product-price"
    ADD_TO_CART_BUTTON = ".add-to-cart"
    CART_BADGE = ".cart-badge"
    SORT_SELECT = "#sortSelect"

    async def search_product(self, keyword: str):
        with allure.step(f"async search: {keyword}"):
            await self.fill(self.SEARCH_INPUT, keyword)
            await self.click(self.SEARCH_BUTTON)

    async def get_product_names(self) -> list:
        items = self.page.locator(self.PRODUCT_NAME)
        count = await items.count()
        return [await items.nth(i).text_content() for i in range(count)]

    async def add_to_cart(self, index: int = 0):
        await self.page.locator(self.ADD_TO_CART_BUTTON).nth(index).click()

    async def get_cart_count(self) -> int:
        text = await self.get_text(self.CART_BADGE)
        return int(text) if text.isdigit() else 0
