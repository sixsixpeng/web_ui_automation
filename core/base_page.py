# -*- coding: UTF-8 -*-
"""
页面基类
封装通用的页面操作方法，所有页面对象类应继承此类
"""

import time
import allure
from pathlib import Path
from typing import Optional, Tuple, Union

from playwright.sync_api import Page, Locator, expect

from config.config_loader import config
from core.exception_handle import ElementNotFoundException, TimeoutException
from core.browser import browser_manager


class BasePage:
    """页面基类"""
    
    def __init__(self, page: Optional[Page] = None):
        """
        初始化页面对象
        
        Args:
            page: Playwright Page 对象，如果为 None 则创建新页面
        """
        self._page = page or browser_manager.new_page()
        self._screenshot_dir = config.get("screenshot_dir")
        
        # 确保截图目录存在
        Path(self._screenshot_dir).mkdir(parents=True, exist_ok=True)
    
    @property
    def page(self) -> Page:
        """获取 Playwright Page 对象"""
        return self._page
    
    def navigate(self, url: str):
        """
        导航到指定 URL
        
        Args:
            url: 目标 URL，可以是绝对路径或相对路径
        """
        if not url.startswith(("http://", "https://")):
            base_url = config.get_base_url()
            url = f"{base_url.rstrip('/')}/{url.lstrip('/')}"
        
        with allure.step(f"导航到: {url}"):
            self._page.goto(url)
            self.wait_for_page_load()
    
    def wait_for_page_load(self, timeout: Optional[int] = None):
        """等待页面加载完成"""
        timeout = timeout or config.get("timeout", 30000)
        self._page.wait_for_load_state("networkidle", timeout=timeout)
    
    def get_element(self, selector: str, timeout: Optional[int] = None) -> Locator:
        """
        获取元素定位器
        
        Args:
            selector: 元素选择器
            timeout: 超时时间（毫秒）
            
        Returns:
            Locator: Playwright 元素定位器
        """
        try:
            timeout = timeout or config.get("timeout", 30000)
            element = self._page.locator(selector)
            element.wait_for(state="visible", timeout=timeout)
            return element
        except Exception as e:
            current_url = self._page.url
            raise ElementNotFoundException(selector, current_url) from e
    
    def click(self, selector: str, timeout: Optional[int] = None):
        """
        点击元素
        
        Args:
            selector: 元素选择器
            timeout: 超时时间（毫秒）
        """
        with allure.step(f"点击元素: {selector}"):
            element = self.get_element(selector, timeout)
            element.click()
    
    def fill(self, selector: str, text: str, timeout: Optional[int] = None):
        """
        填充文本到输入框
        
        Args:
            selector: 元素选择器
            text: 要输入的文本
            timeout: 超时时间（毫秒）
        """
        with allure.step(f"在元素 {selector} 中输入: {text}"):
            element = self.get_element(selector, timeout)
            element.fill(text)
    
    def type(self, selector: str, text: str, delay: int = 100, timeout: Optional[int] = None):
        """
        模拟键盘输入文本（带延迟）
        
        Args:
            selector: 元素选择器
            text: 要输入的文本
            delay: 延迟时间（毫秒）
            timeout: 超时时间（毫秒）
        """
        with allure.step(f"在元素 {selector} 中模拟输入: {text}"):
            element = self.get_element(selector, timeout)
            element.type(text, delay=delay)
    
    def get_text(self, selector: str, timeout: Optional[int] = None) -> str:
        """
        获取元素文本
        
        Args:
            selector: 元素选择器
            timeout: 超时时间（毫秒）
            
        Returns:
            str: 元素文本
        """
        element = self.get_element(selector, timeout)
        return element.text_content()
    
    def get_attribute(self, selector: str, attribute: str, timeout: Optional[int] = None) -> Optional[str]:
        """
        获取元素属性值
        
        Args:
            selector: 元素选择器
            attribute: 属性名
            timeout: 超时时间（毫秒）
            
        Returns:
            Optional[str]: 属性值，如果不存在则返回 None
        """
        element = self.get_element(selector, timeout)
        return element.get_attribute(attribute)
    
    def is_visible(self, selector: str, timeout: Optional[int] = None) -> bool:
        """
        检查元素是否可见
        
        Args:
            selector: 元素选择器
            timeout: 超时时间（毫秒）
            
        Returns:
            bool: 是否可见
        """
        try:
            timeout = timeout or config.get("timeout", 30000)
            element = self._page.locator(selector)
            element.wait_for(state="visible", timeout=timeout)
            return True
        except:
            return False
    
    def is_enabled(self, selector: str, timeout: Optional[int] = None) -> bool:
        """
        检查元素是否可用
        
        Args:
            selector: 元素选择器
            timeout: 超时时间（毫秒）
            
        Returns:
            bool: 是否可用
        """
        element = self.get_element(selector, timeout)
        return element.is_enabled()
    
    def wait_for_selector(self, selector: str, timeout: Optional[int] = None):
        """
        等待元素出现
        
        Args:
            selector: 元素选择器
            timeout: 超时时间（毫秒）
        """
        timeout = timeout or config.get("timeout", 30000)
        self._page.wait_for_selector(selector, timeout=timeout)
    
    def wait_for_element_hidden(self, selector: str, timeout: Optional[int] = None):
        """
        等待元素隐藏
        
        Args:
            selector: 元素选择器
            timeout: 超时时间（毫秒）
        """
        timeout = timeout or config.get("timeout", 30000)
        self._page.wait_for_selector(selector, state="hidden", timeout=timeout)
    
    def screenshot(self, name: str = None):
        """
        截取页面截图并附加到 Allure 报告
        
        Args:
            name: 截图名称，如果为 None 则使用时间戳
        """
        if name is None:
            name = f"screenshot_{int(time.time())}"
        
        screenshot_path = Path(self._screenshot_dir) / f"{name}.png"
        self._page.screenshot(path=str(screenshot_path))
        
        # 附加到 Allure 报告
        allure.attach.file(
            str(screenshot_path),
            name=name,
            attachment_type=allure.attachment_type.PNG
        )
        
        return str(screenshot_path)
    
    def take_screenshot_on_failure(self, test_name: str):
        """
        测试失败时截图（在 conftest.py 中调用）
        
        Args:
            test_name: 测试用例名称
        """
        screenshot_name = f"failure_{test_name}_{int(time.time())}"
        self.screenshot(screenshot_name)
    
    def switch_to_frame(self, selector: str, timeout: Optional[int] = None):
        """
        切换到 iframe
        
        Args:
            selector: iframe 选择器
            timeout: 超时时间（毫秒）
        """
        with allure.step(f"切换到 iframe: {selector}"):
            frame = self.get_element(selector, timeout)
            self._page.frame_locator(selector)
    
    def switch_to_default_content(self):
        """切换回主文档"""
        with allure.step("切换回主文档"):
            self._page.main_frame
    
    def execute_script(self, script: str, *args):
        """
        执行 JavaScript 脚本
        
        Args:
            script: JavaScript 代码
            *args: 传递给脚本的参数
            
        Returns:
            script 执行结果
        """
        return self._page.evaluate(script, args)
    
    def refresh(self):
        """刷新页面"""
        with allure.step("刷新页面"):
            self._page.reload()
            self.wait_for_page_load()
    
    def go_back(self):
        """后退"""
        with allure.step("页面后退"):
            self._page.go_back()
            self.wait_for_page_load()
    
    def go_forward(self):
        """前进"""
        with allure.step("页面前进"):
            self._page.go_forward()
            self.wait_for_page_load()
    
    def get_current_url(self) -> str:
        """获取当前页面 URL"""
        return self._page.url
    
    def get_title(self) -> str:
        """获取页面标题"""
        return self._page.title()
    
    def close(self):
        """关闭当前页面"""
        self._page.close()