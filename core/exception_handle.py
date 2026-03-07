# -*- coding: UTF-8 -*-
"""
自定义异常类
用于统一处理框架中的各种异常
"""


class FrameworkException(Exception):
    """框架基础异常"""
    pass


class ElementNotFoundException(FrameworkException):
    """元素未找到异常"""
    def __init__(self, locator, page_url=""):
        self.locator = locator
        self.page_url = page_url
        message = f"元素未找到: {locator}"
        if page_url:
            message += f" (页面: {page_url})"
        super().__init__(message)


class TimeoutException(FrameworkException):
    """超时异常"""
    def __init__(self, operation, timeout):
        message = f"操作 '{operation}' 超时，等待时间: {timeout}ms"
        super().__init__(message)


class APICallException(FrameworkException):
    """API 调用异常"""
    def __init__(self, url, status_code, response_text=""):
        self.url = url
        self.status_code = status_code
        self.response_text = response_text
        message = f"API 调用失败: {url} (状态码: {status_code})"
        if response_text:
            message += f"\n响应: {response_text[:200]}"
        super().__init__(message)


class ConfigException(FrameworkException):
    """配置异常"""
    pass


class BrowserException(FrameworkException):
    """浏览器异常"""
    pass