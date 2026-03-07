# -*- coding: UTF-8 -*-
"""
等待辅助类
封装各种等待条件，提供灵活的等待机制
"""

import time
import allure
from typing import Optional, Callable, Any, Union
from playwright.sync_api import Page, Locator, expect

from config.config_loader import config
from core.exception_handle import TimeoutException


class WaitHelper:
    """等待辅助类"""
    
    def __init__(self, page: Page):
        """
        初始化等待辅助类
        
        Args:
            page: Playwright Page 对象
        """
        self._page = page
        self._default_timeout = config.get("timeout", 30000)
    
    def set_default_timeout(self, timeout: int):
        """
        设置默认超时时间
        
        Args:
            timeout: 超时时间（毫秒）
        """
        self._default_timeout = timeout
    
    # ========== 基础等待 ==========
    def wait_for_timeout(self, milliseconds: int):
        """
        等待指定时间
        
        Args:
            milliseconds: 等待时间（毫秒）
        """
        time.sleep(milliseconds / 1000)
    
    def wait_for_condition(self, condition: Callable[[], bool], 
                          timeout: Optional[int] = None,
                          message: str = "等待条件超时",
                          poll_frequency: int = 100):
        """
        等待自定义条件成立
        
        Args:
            condition: 条件函数，返回布尔值
            timeout: 超时时间（毫秒）
            message: 超时错误信息
            poll_frequency: 轮询频率（毫秒）
        """
        timeout = timeout or self._default_timeout
        start_time = time.time()
        
        while time.time() - start_time < timeout / 1000:
            if condition():
                return True
            time.sleep(poll_frequency / 1000)
        
        raise TimeoutException(message, timeout)
    
    # ========== 页面状态等待 ==========
    def wait_for_page_load(self, timeout: Optional[int] = None):
        """
        等待页面加载完成
        
        Args:
            timeout: 超时时间（毫秒）
        """
        timeout = timeout or self._default_timeout
        with allure.step("等待页面加载完成"):
            self._page.wait_for_load_state("networkidle", timeout=timeout)
    
    def wait_for_dom_content_loaded(self, timeout: Optional[int] = None):
        """
        等待 DOM 内容加载完成
        
        Args:
            timeout: 超时时间（毫秒）
        """
        timeout = timeout or self._default_timeout
        with allure.step("等待 DOM 内容加载完成"):
            self._page.wait_for_load_state("domcontentloaded", timeout=timeout)
    
    def wait_for_url(self, url: Union[str, Callable[[str], bool]], 
                    timeout: Optional[int] = None):
        """
        等待 URL 匹配
        
        Args:
            url: 期望的 URL 或匹配函数
            timeout: 超时时间（毫秒）
        """
        timeout = timeout or self._default_timeout
        with allure.step(f"等待 URL 匹配: {url}"):
            self._page.wait_for_url(url, timeout=timeout)
    
    def wait_for_url_contains(self, text: str, timeout: Optional[int] = None):
        """
        等待 URL 包含指定文本
        
        Args:
            text: 期望包含的文本
            timeout: 超时时间（毫秒）
        """
        timeout = timeout or self._default_timeout
        
        def url_contains():
            return text in self._page.url
        
        self.wait_for_condition(
            url_contains,
            timeout=timeout,
            message=f"等待 URL 包含 '{text}' 超时"
        )
    
    def wait_for_title(self, title: Union[str, Callable[[str], bool]],
                      timeout: Optional[int] = None):
        """
        等待页面标题匹配
        
        Args:
            title: 期望的标题或匹配函数
            timeout: 超时时间（毫秒）
        """
        timeout = timeout or self._default_timeout
        
        def check_title():
            actual_title = self._page.title()
            if callable(title):
                return title(actual_title)
            return actual_title == title
        
        self.wait_for_condition(
            check_title,
            timeout=timeout,
            message=f"等待标题匹配 '{title}' 超时"
        )
    
    def wait_for_title_contains(self, text: str, timeout: Optional[int] = None):
        """
        等待页面标题包含指定文本
        
        Args:
            text: 期望包含的文本
            timeout: 超时时间（毫秒）
        """
        timeout = timeout or self._default_timeout
        
        def title_contains():
            return text in self._page.title()
        
        self.wait_for_condition(
            title_contains,
            timeout=timeout,
            message=f"等待标题包含 '{text}' 超时"
        )
    
    # ========== 元素等待 ==========
    def wait_for_selector(self, selector: str, 
                         state: str = "visible",
                         timeout: Optional[int] = None):
        """
        等待选择器匹配的元素达到指定状态
        
        Args:
            selector: 元素选择器
            state: 状态，"visible", "hidden", "attached", "detached"
            timeout: 超时时间（毫秒）
        """
        timeout = timeout or self._default_timeout
        with allure.step(f"等待元素 {selector} 状态变为 {state}"):
            self._page.wait_for_selector(selector, state=state, timeout=timeout)
    
    def wait_for_selector_visible(self, selector: str, timeout: Optional[int] = None):
        """
        等待元素可见
        
        Args:
            selector: 元素选择器
            timeout: 超时时间（毫秒）
        """
        self.wait_for_selector(selector, "visible", timeout)
    
    def wait_for_selector_hidden(self, selector: str, timeout: Optional[int] = None):
        """
        等待元素隐藏
        
        Args:
            selector: 元素选择器
            timeout: 超时时间（毫秒）
        """
        self.wait_for_selector(selector, "hidden", timeout)
    
    def wait_for_selector_enabled(self, selector: str, timeout: Optional[int] = None):
        """
        等待元素可用
        
        Args:
            selector: 元素选择器
            timeout: 超时时间（毫秒）
        """
        timeout = timeout or self._default_timeout
        locator = self._page.locator(selector)
        
        def is_enabled():
            try:
                return locator.is_enabled()
            except:
                return False
        
        self.wait_for_condition(
            is_enabled,
            timeout=timeout,
            message=f"等待元素可用 {selector} 超时"
        )
    
    def wait_for_selector_disabled(self, selector: str, timeout: Optional[int] = None):
        """
        等待元素禁用
        
        Args:
            selector: 元素选择器
            timeout: 超时时间（毫秒）
        """
        timeout = timeout or self._default_timeout
        locator = self._page.locator(selector)
        
        def is_disabled():
            try:
                return locator.is_disabled()
            except:
                return False
        
        self.wait_for_condition(
            is_disabled,
            timeout=timeout,
            message=f"等待元素禁用 {selector} 超时"
        )
    
    def wait_for_element_count(self, selector: str, count: int, 
                              timeout: Optional[int] = None):
        """
        等待匹配选择器的元素数量达到指定值
        
        Args:
            selector: 元素选择器
            count: 期望的元素数量
            timeout: 超时时间（毫秒）
        """
        timeout = timeout or self._default_timeout
        
        def element_count_matches():
            try:
                return self._page.locator(selector).count() == count
            except:
                return False
        
        self.wait_for_condition(
            element_count_matches,
            timeout=timeout,
            message=f"等待元素数量为 {count} {selector} 超时"
        )
    
    def wait_for_element_count_greater_than(self, selector: str, min_count: int,
                                           timeout: Optional[int] = None):
        """
        等待匹配选择器的元素数量大于指定值
        
        Args:
            selector: 元素选择器
            min_count: 最小元素数量
            timeout: 超时时间（毫秒）
        """
        timeout = timeout or self._default_timeout
        
        def element_count_greater():
            try:
                return self._page.locator(selector).count() > min_count
            except:
                return False
        
        self.wait_for_condition(
            element_count_greater,
            timeout=timeout,
            message=f"等待元素数量大于 {min_count} {selector} 超时"
        )
    
    # ========== 文本等待 ==========
    def wait_for_text(self, selector: str, text: str,
                     exact: bool = False,
                     timeout: Optional[int] = None):
        """
        等待元素包含指定文本
        
        Args:
            selector: 元素选择器
            text: 期望的文本
            exact: 是否精确匹配
            timeout: 超时时间（毫秒）
        """
        timeout = timeout or self._default_timeout
        with allure.step(f"等待元素 {selector} 包含文本: {text}"):
            locator = self._page.locator(selector)
            if exact:
                locator.get_by_text(text, exact=True).wait_for(state="visible", timeout=timeout)
            else:
                locator.get_by_text(text).wait_for(state="visible", timeout=timeout)
    
    def wait_for_text_to_disappear(self, selector: str, text: str,
                                  exact: bool = False,
                                  timeout: Optional[int] = None):
        """
        等待元素不再包含指定文本
        
        Args:
            selector: 元素选择器
            text: 期望消失的文本
            exact: 是否精确匹配
            timeout: 超时时间（毫秒）
        """
        timeout = timeout or self._default_timeout
        
        def text_disappeared():
            try:
                locator = self._page.locator(selector)
                if exact:
                    return locator.get_by_text(text, exact=True).count() == 0
                else:
                    return locator.get_by_text(text).count() == 0
            except:
                return True
        
        self.wait_for_condition(
            text_disappeared,
            timeout=timeout,
            message=f"等待文本消失 '{text}' {selector} 超时"
        )
    
    # ========== 属性等待 ==========
    def wait_for_attribute(self, selector: str, attribute: str,
                          value: Optional[str] = None,
                          timeout: Optional[int] = None):
        """
        等待元素具有指定属性
        
        Args:
            selector: 元素选择器
            attribute: 属性名
            value: 期望的属性值（如果为 None 则只检查属性是否存在）
            timeout: 超时时间（毫秒）
        """
        timeout = timeout or self._default_timeout
        
        def attribute_matches():
            try:
                locator = self._page.locator(selector)
                actual_value = locator.get_attribute(attribute)
                
                if actual_value is None:
                    return False
                
                if value is not None:
                    return actual_value == value
                
                return True
            except:
                return False
        
        self.wait_for_condition(
            attribute_matches,
            timeout=timeout,
            message=f"等待属性 {attribute}={value} {selector} 超时"
        )
    
    # ========== 值等待 ==========
    def wait_for_value(self, selector: str, value: str,
                      timeout: Optional[int] = None):
        """
        等待输入框具有指定值
        
        Args:
            selector: 元素选择器
            value: 期望的值
            timeout: 超时时间（毫秒）
        """
        timeout = timeout or self._default_timeout
        
        def value_matches():
            try:
                locator = self._page.locator(selector)
                actual_value = locator.input_value()
                return actual_value == value
            except:
                return False
        
        self.wait_for_condition(
            value_matches,
            timeout=timeout,
            message=f"等待值 '{value}' {selector} 超时"
        )
    
    # ========== 复选框等待 ==========
    def wait_for_checked(self, selector: str, checked: bool = True,
                        timeout: Optional[int] = None):
        """
        等待复选框的勾选状态
        
        Args:
            selector: 元素选择器
            checked: 期望的勾选状态
            timeout: 超时时间（毫秒）
        """
        timeout = timeout or self._default_timeout
        
        def checked_state_matches():
            try:
                locator = self._page.locator(selector)
                return locator.is_checked() == checked
            except:
                return False
        
        self.wait_for_condition(
            checked_state_matches,
            timeout=timeout,
            message=f"等待勾选状态 {checked} {selector} 超时"
        )
    
    # ========== JavaScript 条件等待 ==========
    def wait_for_function(self, script: str, arg: Any = None,
                         timeout: Optional[int] = None):
        """
        等待 JavaScript 函数返回真值
        
        Args:
            script: JavaScript 函数
            arg: 传递给函数的参数
            timeout: 超时时间（毫秒）
        """
        timeout = timeout or self._default_timeout
        with allure.step(f"等待 JavaScript 条件: {script[:50]}..."):
            self._page.wait_for_function(script, arg, timeout=timeout)
    
    def wait_for_ajax(self, timeout: Optional[int] = None):
        """
        等待 AJAX 请求完成（jQuery）
        
        Args:
            timeout: 超时时间（毫秒）
        """
        timeout = timeout or self._default_timeout
        script = """
            (function() {
                if (window.jQuery) {
                    return jQuery.active === 0;
                }
                return true;
            })();
        """
        self.wait_for_function(script, timeout=timeout)
    
    # ========== 框架等待 ==========
    def wait_for_frame(self, frame_selector: str,
                      timeout: Optional[int] = None):
        """
        等待 iframe 加载
        
        Args:
            frame_selector: iframe 选择器
            timeout: 超时时间（毫秒）
        """
        timeout = timeout or self._default_timeout
        with allure.step(f"等待 iframe 加载: {frame_selector}"):
            self._page.wait_for_selector(frame_selector, state="attached", timeout=timeout)
    
    # ========== 网络请求等待 ==========
    def wait_for_request(self, url_pattern: str,
                        timeout: Optional[int] = None):
        """
        等待匹配指定模式的请求
        
        Args:
            url_pattern: URL 模式（正则表达式或字符串）
            timeout: 超时时间（毫秒）
            
        Returns:
            匹配的 Request 对象
        """
        timeout = timeout or self._default_timeout
        with allure.step(f"等待请求: {url_pattern}"):
            return self._page.wait_for_request(lambda req: url_pattern in req.url, timeout=timeout)
    
    def wait_for_response(self, url_pattern: str,
                         timeout: Optional[int] = None):
        """
        等待匹配指定模式的响应
        
        Args:
            url_pattern: URL 模式（正则表达式或字符串）
            timeout: 超时时间（毫秒）
            
        Returns:
            匹配的 Response 对象
        """
        timeout = timeout or self._default_timeout
        with allure.step(f"等待响应: {url_pattern}"):
            return self._page.wait_for_response(lambda res: url_pattern in res.url, timeout=timeout)
    
    # ========== 组合等待 ==========
    def wait_for_all(self, *conditions, timeout: Optional[int] = None):
        """
        等待所有条件成立
        
        Args:
            *conditions: 条件函数列表
            timeout: 超时时间（毫秒）
        """
        timeout = timeout or self._default_timeout
        start_time = time.time()
        
        for condition in conditions:
            remaining_time = timeout - (time.time() - start_time) * 1000
            if remaining_time <= 0:
                raise TimeoutException("等待所有条件超时", timeout)
            
            self.wait_for_condition(
                condition,
                timeout=remaining_time,
                message="组合等待条件超时"
            )
    
    def wait_for_any(self, *conditions, timeout: Optional[int] = None):
        """
        等待任意条件成立
        
        Args:
            *conditions: 条件函数列表
            timeout: 超时时间（毫秒）
            
        Returns:
            第一个成立的条件的索引，如果超时则抛出异常
        """
        timeout = timeout or self._default_timeout
        start_time = time.time()
        
        while time.time() - start_time < timeout / 1000:
            for i, condition in enumerate(conditions):
                try:
                    if condition():
                        return i
                except:
                    continue
            
            time.sleep(0.1)  # 100ms 轮询
        
        raise TimeoutException("等待任意条件超时", timeout)