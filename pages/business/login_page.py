# -*- coding: utf-8 -*-
"""Login page objects - Sync + Async"""
import allure

from pages.base.base_async_page import BaseAsyncPage
from pages.base.base_sync_page import BaseSyncPage
from utils import get_logger

logger = get_logger("login_page")


class LoginPageSync(BaseSyncPage):
    USERNAME_INPUT = "#username"
    PASSWORD_INPUT = "#password"
    LOGIN_BUTTON = "#loginBtn"
    CAPTCHA_INPUT = "#captcha"
    CAPTCHA_IMAGE = "#captchaImg"
    ERROR_MSG = ".error-message"
    WELCOME_TEXT = ".welcome-text"

    def login(self, username: str, password: str, captcha: str = ""):
        """执行登录操作"""
        with allure.step(f"login: {username}"):
            self.fill(self.USERNAME_INPUT, username)
            self.fill(self.PASSWORD_INPUT, password)
            if captcha:
                self.fill(self.CAPTCHA_INPUT, captcha)
            self.click(self.LOGIN_BUTTON)
            self.wait_for_load_state("networkidle")

    def get_error_message(self) -> str:
        """获取登录错误提示"""
        return self.get_text(self.ERROR_MSG)

    def is_login_success(self) -> bool:
        """判断登录是否成功"""
        return self.is_visible(self.WELCOME_TEXT)


class LoginPageAsync(BaseAsyncPage):
    USERNAME_INPUT = "#username"
    PASSWORD_INPUT = "#password"
    LOGIN_BUTTON = "#loginBtn"
    CAPTCHA_INPUT = "#captcha"
    CAPTCHA_IMAGE = "#captchaImg"
    ERROR_MSG = ".error-message"
    WELCOME_TEXT = ".welcome-text"

    async def login(self, username: str, password: str, captcha: str = ""):
        with allure.step(f"async login: {username}"):
            await self.fill(self.USERNAME_INPUT, username)
            await self.fill(self.PASSWORD_INPUT, password)
            if captcha:
                await self.fill(self.CAPTCHA_INPUT, captcha)
            await self.click(self.LOGIN_BUTTON)
            await self.wait_for_load_state("networkidle")

    async def get_error_message(self) -> str:
        return await self.get_text(self.ERROR_MSG)

    async def is_login_success(self) -> bool:
        return await self.is_visible(self.WELCOME_TEXT)
