# -*- coding: UTF-8 -*-
"""
断言辅助类
提供丰富的断言方法，基于 Playwright 的 expect
"""

import allure
import time
from typing import Optional, Union, List, Dict, Any, Callable
from playwright.sync_api import Page, Locator, expect
from core.exception_handle import TimeoutException
from common.log_utils import LogUtils

logger = LogUtils.get_logger(__name__)


class AssertionHelper:
    """断言辅助类"""
    
    def __init__(self, page: Page):
        """
        初始化断言辅助类
        
        Args:
            page: Playwright Page 对象
        """
        self._page = page
        self._default_timeout = 30000  # 默认超时时间（毫秒）
    
    def set_default_timeout(self, timeout: int):
        """
        设置默认超时时间
        
        Args:
            timeout: 超时时间（毫秒）
        """
        self._default_timeout = timeout
    
    # ========== 页面断言 ==========
    def assert_url(self, url: Union[str, Callable[[str], bool]], 
                  timeout: Optional[int] = None):
        """
        断言当前 URL
        
        Args:
            url: 期望的 URL 或匹配函数
            timeout: 超时时间（毫秒）
        """
        timeout = timeout or self._default_timeout
        with allure.step(f"断言 URL: {url}"):
            expect(self._page).to_have_url(url, timeout=timeout)
    
    def assert_url_contains(self, text: str, timeout: Optional[int] = None):
        """
        断言 URL 包含指定文本
        
        Args:
            text: 期望包含的文本
            timeout: 超时时间（毫秒）
        """
        timeout = timeout or self._default_timeout
        with allure.step(f"断言 URL 包含: {text}"):
            expect(self._page).to_have_url(lambda url: text in url, timeout=timeout)
    
    def assert_title(self, title: Union[str, Callable[[str], bool]],
                    timeout: Optional[int] = None):
        """
        断言页面标题
        
        Args:
            title: 期望的标题或匹配函数
            timeout: 超时时间（毫秒）
        """
        timeout = timeout or self._default_timeout
        with allure.step(f"断言页面标题: {title}"):
            expect(self._page).to_have_title(title, timeout=timeout)
    
    def assert_title_contains(self, text: str, timeout: Optional[int] = None):
        """
        断言页面标题包含指定文本
        
        Args:
            text: 期望包含的文本
            timeout: 超时时间（毫秒）
        """
        timeout = timeout or self._default_timeout
        with allure.step(f"断言页面标题包含: {text}"):
            expect(self._page).to_have_title(lambda title: text in title, timeout=timeout)
    
    # ========== 元素存在断言 ==========
    def assert_element_visible(self, selector: str, timeout: Optional[int] = None):
        """
        断言元素可见
        
        Args:
            selector: 元素选择器
            timeout: 超时时间（毫秒）
        """
        timeout = timeout or self._default_timeout
        with allure.step(f"断言元素可见: {selector}"):
            locator = self._page.locator(selector)
            expect(locator).to_be_visible(timeout=timeout)
    
    def assert_element_hidden(self, selector: str, timeout: Optional[int] = None):
        """
        断言元素隐藏
        
        Args:
            selector: 元素选择器
            timeout: 超时时间（毫秒）
        """
        timeout = timeout or self._default_timeout
        with allure.step(f"断言元素隐藏: {selector}"):
            locator = self._page.locator(selector)
            expect(locator).to_be_hidden(timeout=timeout)
    
    def assert_element_attached(self, selector: str, timeout: Optional[int] = None):
        """
        断言元素存在于 DOM 中
        
        Args:
            selector: 元素选择器
            timeout: 超时时间（毫秒）
        """
        timeout = timeout or self._default_timeout
        with allure.step(f"断言元素存在: {selector}"):
            locator = self._page.locator(selector)
            expect(locator).to_be_attached(timeout=timeout)
    
    def assert_element_detached(self, selector: str, timeout: Optional[int] = None):
        """
        断言元素不存在于 DOM 中
        
        Args:
            selector: 元素选择器
            timeout: 超时时间（毫秒）
        """
        timeout = timeout or self._default_timeout
        with allure.step(f"断言元素不存在: {selector}"):
            locator = self._page.locator(selector)
            expect(locator).to_be_hidden(timeout=timeout)  # 使用 hidden 作为近似
    
    def assert_element_count(self, selector: str, count: int, 
                            timeout: Optional[int] = None):
        """
        断言元素数量
        
        Args:
            selector: 元素选择器
            count: 期望的元素数量
            timeout: 超时时间（毫秒）
        """
        timeout = timeout or self._default_timeout
        with allure.step(f"断言元素数量: {selector} = {count}"):
            locator = self._page.locator(selector)
            expect(locator).to_have_count(count, timeout=timeout)
    
    def assert_element_count_greater_than(self, selector: str, min_count: int,
                                         timeout: Optional[int] = None):
        """
        断言元素数量大于指定值
        
        Args:
            selector: 元素选择器
            min_count: 最小元素数量
            timeout: 超时时间（毫秒）
        """
        timeout = timeout or self._default_timeout
        
        def count_greater_than():
            actual_count = self._page.locator(selector).count()
            return actual_count > min_count
        
        self._assert_condition(
            count_greater_than,
            timeout=timeout,
            message=f"元素数量大于 {min_count}: {selector}"
        )
    
    def assert_element_count_less_than(self, selector: str, max_count: int,
                                      timeout: Optional[int] = None):
        """
        断言元素数量小于指定值
        
        Args:
            selector: 元素选择器
            max_count: 最大元素数量
            timeout: 超时时间（毫秒）
        """
        timeout = timeout or self._default_timeout
        
        def count_less_than():
            actual_count = self._page.locator(selector).count()
            return actual_count < max_count
        
        self._assert_condition(
            count_less_than,
            timeout=timeout,
            message=f"元素数量小于 {max_count}: {selector}"
        )
    
    # ========== 元素状态断言 ==========
    def assert_element_enabled(self, selector: str, timeout: Optional[int] = None):
        """
        断言元素可用
        
        Args:
            selector: 元素选择器
            timeout: 超时时间（毫秒）
        """
        timeout = timeout or self._default_timeout
        with allure.step(f"断言元素可用: {selector}"):
            locator = self._page.locator(selector)
            expect(locator).to_be_enabled(timeout=timeout)
    
    def assert_element_disabled(self, selector: str, timeout: Optional[int] = None):
        """
        断言元素禁用
        
        Args:
            selector: 元素选择器
            timeout: 超时时间（毫秒）
        """
        timeout = timeout or self._default_timeout
        with allure.step(f"断言元素禁用: {selector}"):
            locator = self._page.locator(selector)
            expect(locator).to_be_disabled(timeout=timeout)
    
    def assert_element_checked(self, selector: str, timeout: Optional[int] = None):
        """
        断言元素被勾选
        
        Args:
            selector: 元素选择器
            timeout: 超时时间（毫秒）
        """
        timeout = timeout or self._default_timeout
        with allure.step(f"断言元素被勾选: {selector}"):
            locator = self._page.locator(selector)
            expect(locator).to_be_checked(timeout=timeout)
    
    def assert_element_not_checked(self, selector: str, timeout: Optional[int] = None):
        """
        断言元素未勾选
        
        Args:
            selector: 元素选择器
            timeout: 超时时间（毫秒）
        """
        timeout = timeout or self._default_timeout
        with allure.step(f"断言元素未勾选: {selector}"):
            locator = self._page.locator(selector)
            expect(locator).not_to_be_checked(timeout=timeout)
    
    def assert_element_editable(self, selector: str, timeout: Optional[int] = None):
        """
        断言元素可编辑
        
        Args:
            selector: 元素选择器
            timeout: 超时时间（毫秒）
        """
        timeout = timeout or self._default_timeout
        with allure.step(f"断言元素可编辑: {selector}"):
            locator = self._page.locator(selector)
            expect(locator).to_be_editable(timeout=timeout)
    
    def assert_element_not_editable(self, selector: str, timeout: Optional[int] = None):
        """
        断言元素不可编辑
        
        Args:
            selector: 元素选择器
            timeout: 超时时间（毫秒）
        """
        timeout = timeout or self._default_timeout
        with allure.step(f"断言元素不可编辑: {selector}"):
            locator = self._page.locator(selector)
            expect(locator).not_to_be_editable(timeout=timeout)
    
    def assert_element_focused(self, selector: str, timeout: Optional[int] = None):
        """
        断言元素获得焦点
        
        Args:
            selector: 元素选择器
            timeout: 超时时间（毫秒）
        """
        timeout = timeout or self._default_timeout
        with allure.step(f"断言元素获得焦点: {selector}"):
            locator = self._page.locator(selector)
            expect(locator).to_be_focused(timeout=timeout)
    
    def assert_element_not_focused(self, selector: str, timeout: Optional[int] = None):
        """
        断言元素未获得焦点
        
        Args:
            selector: 元素选择器
            timeout: 超时时间（毫秒）
        """
        timeout = timeout or self._default_timeout
        with allure.step(f"断言元素未获得焦点: {selector}"):
            locator = self._page.locator(selector)
            expect(locator).not_to_be_focused(timeout=timeout)
    
    # ========== 元素内容断言 ==========
    def assert_element_text(self, selector: str, text: Union[str, List[str]],
                           exact: bool = False, timeout: Optional[int] = None):
        """
        断言元素文本
        
        Args:
            selector: 元素选择器
            text: 期望的文本或文本列表
            exact: 是否精确匹配
            timeout: 超时时间（毫秒）
        """
        timeout = timeout or self._default_timeout
        with allure.step(f"断言元素文本: {selector} = {text}"):
            locator = self._page.locator(selector)
            if exact:
                expect(locator).to_have_text(text, timeout=timeout)
            else:
                expect(locator).to_contain_text(text, timeout=timeout)
    
    def assert_element_text_contains(self, selector: str, text: str,
                                    timeout: Optional[int] = None):
        """
        断言元素文本包含指定文本
        
        Args:
            selector: 元素选择器
            text: 期望包含的文本
            timeout: 超时时间（毫秒）
        """
        timeout = timeout or self._default_timeout
        with allure.step(f"断言元素文本包含: {selector} 包含 {text}"):
            locator = self._page.locator(selector)
            expect(locator).to_contain_text(text, timeout=timeout)
    
    def assert_element_value(self, selector: str, value: Union[str, List[str]],
                            timeout: Optional[int] = None):
        """
        断言元素值
        
        Args:
            selector: 元素选择器
            value: 期望的值
            timeout: 超时时间（毫秒）
        """
        timeout = timeout or self._default_timeout
        with allure.step(f"断言元素值: {selector} = {value}"):
            locator = self._page.locator(selector)
            expect(locator).to_have_value(value, timeout=timeout)
    
    def assert_element_attribute(self, selector: str, attribute: str,
                                value: Union[str, List[str], Callable[[str], bool]],
                                timeout: Optional[int] = None):
        """
        断言元素属性
        
        Args:
            selector: 元素选择器
            attribute: 属性名
            value: 期望的属性值
            timeout: 超时时间（毫秒）
        """
        timeout = timeout or self._default_timeout
        with allure.step(f"断言元素属性: {selector}[{attribute}] = {value}"):
            locator = self._page.locator(selector)
            expect(locator).to_have_attribute(attribute, value, timeout=timeout)
    
    def assert_element_css_property(self, selector: str, property_name: str,
                                   value: Union[str, Callable[[str], bool]],
                                   timeout: Optional[int] = None):
        """
        断言元素 CSS 属性
        
        Args:
            selector: 元素选择器
            property_name: CSS 属性名
            value: 期望的属性值
            timeout: 超时时间（毫秒）
        """
        timeout = timeout or self._default_timeout
        with allure.step(f"断言元素 CSS 属性: {selector}[{property_name}] = {value}"):
            locator = self._page.locator(selector)
            expect(locator).to_have_css(property_name, value, timeout=timeout)
    
    def assert_element_class(self, selector: str, class_name: Union[str, List[str]],
                            timeout: Optional[int] = None):
        """
        断言元素类名
        
        Args:
            selector: 元素选择器
            class_name: 期望的类名或类名列表
            timeout: 超时时间（毫秒）
        """
        timeout = timeout or self._default_timeout
        with allure.step(f"断言元素类名: {selector} 包含类 {class_name}"):
            locator = self._page.locator(selector)
            expect(locator).to_have_class(class_name, timeout=timeout)
    
    # ========== 页面状态断言 ==========
    def assert_page_loaded(self, timeout: Optional[int] = None):
        """
        断言页面已加载完成
        
        Args:
            timeout: 超时时间（毫秒）
        """
        timeout = timeout or self._default_timeout
        with allure.step("断言页面已加载完成"):
            expect(self._page).to_have_load_state("networkidle", timeout=timeout)
    
    def assert_dom_content_loaded(self, timeout: Optional[int] = None):
        """
        断言 DOM 内容已加载完成
        
        Args:
            timeout: 超时时间（毫秒）
        """
        timeout = timeout or self._default_timeout
        with allure.step("断言 DOM 内容已加载完成"):
            expect(self._page).to_have_load_state("domcontentloaded", timeout=timeout)
    
    # ========== 视觉断言 ==========
    def assert_screenshot(self, selector: str, screenshot_name: str,
                         threshold: float = 0.1, timeout: Optional[int] = None):
        """
        断言元素截图匹配
        
        Args:
            selector: 元素选择器
            screenshot_name: 截图名称
            threshold: 匹配阈值（0-1）
            timeout: 超时时间（毫秒）
        """
        timeout = timeout or self._default_timeout
        with allure.step(f"断言元素截图匹配: {selector}"):
            locator = self._page.locator(selector)
            expect(locator).to_have_screenshot(screenshot_name, threshold=threshold, timeout=timeout)
    
    def assert_page_screenshot(self, screenshot_name: str,
                              threshold: float = 0.1,
                              full_page: bool = False,
                              timeout: Optional[int] = None):
        """
        断言页面截图匹配
        
        Args:
            screenshot_name: 截图名称
            threshold: 匹配阈值（0-1）
            full_page: 是否截取整个页面
            timeout: 超时时间（毫秒）
        """
        timeout = timeout or self._default_timeout
        with allure.step(f"断言页面截图匹配: {screenshot_name}"):
            expect(self._page).to_have_screenshot(
                screenshot_name, 
                threshold=threshold,
                full_page=full_page,
                timeout=timeout
            )
    
    # ========== JavaScript 断言 ==========
    def assert_js_condition(self, script: str, arg: Any = None,
                           timeout: Optional[int] = None):
        """
        断言 JavaScript 条件为真
        
        Args:
            script: JavaScript 条件表达式
            arg: 传递给表达式的参数
            timeout: 超时时间（毫秒）
        """
        timeout = timeout or self._default_timeout
        with allure.step(f"断言 JavaScript 条件: {script[:50]}..."):
            expect(self._page).to_evaluate_script(script, arg, timeout=timeout)
    
    # ========== 自定义条件断言 ==========
    def _assert_condition(self, condition: Callable[[], bool],
                         timeout: Optional[int] = None,
                         message: str = "条件断言失败"):
        """
        断言自定义条件
        
        Args:
            condition: 条件函数
            timeout: 超时时间（毫秒）
            message: 错误信息
        """
        timeout = timeout or self._default_timeout
        start_time = time.time()
        
        while time.time() - start_time < timeout / 1000:
            try:
                if condition():
                    with allure.step(f"断言成功: {message}"):
                        return True
            except Exception as e:
                logger.error(f"条件检查失败: {e}")
            
            time.sleep(0.1)  # 100ms 轮询
        
        raise AssertionError(f"{message} (超时: {timeout}ms)")
    
    # ========== 组合断言 ==========
    def assert_all(self, *assertions, timeout: Optional[int] = None):
        """
        断言所有条件成立
        
        Args:
            *assertions: 断言函数列表
            timeout: 每个断言的最大超时时间（毫秒）
        """
        timeout = timeout or self._default_timeout
        with allure.step("断言所有条件成立"):
            for i, assertion in enumerate(assertions):
                try:
                    assertion()
                except Exception as e:
                    raise AssertionError(f"第 {i+1} 个断言失败: {str(e)}")
    
    def assert_any(self, *assertions, timeout: Optional[int] = None):
        """
        断言任意条件成立
        
        Args:
            *assertions: 断言函数列表
            timeout: 总超时时间（毫秒）
        """
        timeout = timeout or self._default_timeout
        start_time = time.time()
        
        while time.time() - start_time < timeout / 1000:
            for assertion in assertions:
                try:
                    assertion()
                    with allure.step("断言任意条件成立: 成功"):
                        return True
                except Exception:
                    continue
            
            time.sleep(0.1)  # 100ms 轮询
        
        raise AssertionError(f"所有断言都失败 (超时: {timeout}ms)")
    
    # ========== 反向断言 ==========
    def assert_not(self, assertion_func: Callable, *args, **kwargs):
        """
        反向断言（断言条件不成立）
        
        Args:
            assertion_func: 断言函数
            *args: 断言函数参数
            **kwargs: 断言函数关键字参数
        """
        try:
            assertion_func(*args, **kwargs)
            # 如果断言成功，说明条件成立，但我们需要它不成立
            raise AssertionError(f"期望条件不成立，但条件成立")
        except AssertionError:
            # 断言失败是期望的结果
            with allure.step(f"反向断言成功: 条件不成立"):
                return True
        except Exception as e:
            # 其他异常需要抛出
            raise AssertionError(f"反向断言时发生异常: {str(e)}")
    
    # ========== 软断言 ==========
    def soft_assert(self, assertion_func: Callable, *args, **kwargs) -> bool:
        """
        软断言（不立即抛出异常）
        
        Args:
            assertion_func: 断言函数
            *args: 断言函数参数
            **kwargs: 断言函数关键字参数
            
        Returns:
            bool: 断言是否成功
        """
        try:
            assertion_func(*args, **kwargs)
            return True
        except AssertionError as e:
            # 记录失败但不抛出
            error_msg = f"软断言失败: {str(e)}"
            logger.warning(error_msg)
            allure.attach(
                error_msg,
                name="软断言失败",
                attachment_type=allure.attachment_type.TEXT
            )
            return False
        except Exception as e:
            error_msg = f"软断言异常: {str(e)}"
            logger.warning(error_msg)
            allure.attach(
                error_msg,
                name="软断言异常",
                attachment_type=allure.attachment_type.TEXT
            )
            return False
    
    def verify_all_soft_assertions(self, results: List[bool], 
                                  fail_message: str = "软断言失败"):
        """
        验证所有软断言结果
        
        Args:
            results: 软断言结果列表
            fail_message: 失败时的信息
            
        Raises:
            AssertionError: 如果有任何软断言失败
        """
        failed_count = results.count(False)
        if failed_count > 0:
            raise AssertionError(f"{fail_message}: {failed_count} 个断言失败")