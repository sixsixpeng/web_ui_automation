# -*- coding: utf-8 -*-
"""captcha_util - 验证码处理工具（同步+异步）"""
import base64

from utils.config_util import get as cfg_get
from utils.log_util import get_logger

logger = get_logger("captcha_util")


class CaptchaSyncUtil:
    @staticmethod
    def get_universal():
        """获取万能验证码"""
        return cfg_get("universal_captcha", "")

    @staticmethod
    def is_universal(code):
        """判断是否为万能验证码"""
        return bool(CaptchaSyncUtil.get_universal() and code == CaptchaSyncUtil.get_universal())

    @staticmethod
    def get_image(page, selector):
        """获取验证码图片二进制数据"""
        el = page.locator(selector)
        src = el.get_attribute("src")
        if src and src.startswith("data:image"):
            return base64.b64decode(src.split(",")[1])
        return el.screenshot()


class CaptchaAsyncUtil:
    @staticmethod
    def get_universal():
        """获取万能验证码"""
        return cfg_get("universal_captcha", "")

    @staticmethod
    def is_universal(code):
        """判断是否为万能验证码"""
        return bool(CaptchaAsyncUtil.get_universal() and code == CaptchaAsyncUtil.get_universal())

    @staticmethod
    async def get_image(page, selector):
        """获取验证码图片二进制数据"""
        el = page.locator(selector)
        src = await el.get_attribute("src")
        if src and src.startswith("data:image"):
            return base64.b64decode(src.split(",")[1])
        return await el.screenshot()
