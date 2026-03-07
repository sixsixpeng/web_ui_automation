# -*- coding: UTF-8 -*-
"""
登录页面对象封装
"""

from typing import Optional
from core.base_page import BasePage
from common.log_utils import LogUtils


class LoginPage(BasePage):
    """登录页面"""
    
    # 元素定位器
    USERNAME_INPUT = "#username"
    PASSWORD_INPUT = "#password"
    LOGIN_BUTTON = "#login-button"
    REMEMBER_ME_CHECKBOX = "#remember-me"
    FORGOT_PASSWORD_LINK = "a.forgot-password"
    ERROR_MESSAGE = ".error-message"
    SUCCESS_MESSAGE = ".success-message"
    REGISTER_LINK = "a.register-link"
    
    def __init__(self, page=None):
        super().__init__(page)
        self.logger = LogUtils.get_logger(__name__)
    
    def navigate_to_login(self):
        """导航到登录页面"""
        self.logger.info("导航到登录页面")
        self.navigate("/login")
    
    def enter_username(self, username: str):
        """
        输入用户名
        
        Args:
            username: 用户名
        """
        self.logger.info(f"输入用户名: {username}")
        self.fill(self.USERNAME_INPUT, username)
    
    def enter_password(self, password: str):
        """
        输入密码
        
        Args:
            password: 密码
        """
        self.logger.info("输入密码")
        self.fill(self.PASSWORD_INPUT, password)
    
    def click_login(self):
        """点击登录按钮"""
        self.logger.info("点击登录按钮")
        self.click(self.LOGIN_BUTTON)
    
    def click_remember_me(self):
        """点击记住我复选框"""
        self.logger.info("点击记住我复选框")
        self.click(self.REMEMBER_ME_CHECKBOX)
    
    def click_forgot_password(self):
        """点击忘记密码链接"""
        self.logger.info("点击忘记密码链接")
        self.click(self.FORGOT_PASSWORD_LINK)
    
    def click_register(self):
        """点击注册链接"""
        self.logger.info("点击注册链接")
        self.click(self.REGISTER_LINK)
    
    def login(self, username: str, password: str, remember_me: bool = False):
        """
        执行登录操作
        
        Args:
            username: 用户名
            password: 密码
            remember_me: 是否记住我
        """
        self.logger.info(f"执行登录操作，用户名: {username}")
        
        self.navigate_to_login()
        self.enter_username(username)
        self.enter_password(password)
        
        if remember_me:
            self.click_remember_me()
        
        self.click_login()
    
    def get_error_message(self) -> Optional[str]:
        """
        获取错误消息
        
        Returns:
            Optional[str]: 错误消息文本，如果不存在则返回 None
        """
        try:
            error_text = self.get_text(self.ERROR_MESSAGE)
            self.logger.info(f"获取到错误消息: {error_text}")
            return error_text
        except Exception:
            return None
    
    def get_success_message(self) -> Optional[str]:
        """
        获取成功消息
        
        Returns:
            Optional[str]: 成功消息文本，如果不存在则返回 None
        """
        try:
            success_text = self.get_text(self.SUCCESS_MESSAGE)
            self.logger.info(f"获取到成功消息: {success_text}")
            return success_text
        except Exception:
            return None
    
    def is_login_button_enabled(self) -> bool:
        """
        检查登录按钮是否可用
        
        Returns:
            bool: 是否可用
        """
        return self.is_enabled(self.LOGIN_BUTTON)
    
    def is_username_field_visible(self) -> bool:
        """
        检查用户名输入框是否可见
        
        Returns:
            bool: 是否可见
        """
        return self.is_visible(self.USERNAME_INPUT)
    
    def is_password_field_visible(self) -> bool:
        """
        检查密码输入框是否可见
        
        Returns:
            bool: 是否可见
        """
        return self.is_visible(self.PASSWORD_INPUT)
    
    def clear_username(self):
        """清空用户名输入框"""
        self.logger.info("清空用户名输入框")
        self.fill(self.USERNAME_INPUT, "")
    
    def clear_password(self):
        """清空密码输入框"""
        self.logger.info("清空密码输入框")
        self.fill(self.PASSWORD_INPUT, "")
    
    def wait_for_login_success(self, timeout: int = 10000):
        """
        等待登录成功（页面跳转或显示成功消息）
        
        Args:
            timeout: 超时时间（毫秒）
        """
        self.logger.info("等待登录成功")
        
        # 等待页面跳转到首页或显示成功消息
        try:
            # 方法1：等待 URL 变化（假设登录后跳转到首页）
            self.page.wait_for_url("**/dashboard**", timeout=timeout)
        except:
            # 方法2：等待成功消息出现
            self.wait_for_selector(self.SUCCESS_MESSAGE, timeout=timeout)
    
    def wait_for_login_error(self, timeout: int = 5000):
        """
        等待登录错误消息出现
        
        Args:
            timeout: 超时时间（毫秒）
        """
        self.logger.info("等待登录错误消息")
        self.wait_for_selector(self.ERROR_MESSAGE, timeout=timeout)
    
    def take_login_screenshot(self, prefix: str = "login"):
        """
        截取登录页面截图
        
        Args:
            prefix: 截图前缀
        """
        screenshot_name = f"{prefix}_{int(time.time())}"
        self.screenshot(screenshot_name)