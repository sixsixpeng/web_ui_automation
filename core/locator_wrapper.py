# -*- coding: UTF-8 -*-
"""
元素定位器包装器
封装 Playwright Locator 对象，提供丰富的元素操作方法
包括元素操作、属性获取、状态检查、断言等
"""

import allure
import time
from typing import Optional, List, Dict, Any, Union
from playwright.sync_api import Locator, Page


from core.exception_handle import ElementNotFoundException, TimeoutException


class LocatorWrapper:
    """元素定位器包装器"""
    
    def __init__(self, locator: Locator, description: str = ""):
        """
        初始化定位器包装器
        
        Args:
            locator: Playwright Locator 对象
            description: 元素描述，用于日志和报告
        """
        self._locator = locator
        self._description = description or str(locator)
    
    @property
    def locator(self) -> Locator:
        """获取原始的 Locator 对象"""
        return self._locator
    
    @property
    def description(self) -> str:
        """获取元素描述"""
        return self._description
    
    def with_description(self, description: str) -> 'LocatorWrapper':
        """
        设置元素描述并返回新的包装器
        
        Args:
            description: 新的元素描述
            
        Returns:
            LocatorWrapper: 新的包装器实例
        """
        return LocatorWrapper(self._locator, description)
    
    # ========== 基础操作 ==========
    def click(self, **kwargs):
        """
        点击元素
        
        Args:
            **kwargs: 点击选项，如 button, click_count, delay, force, modifiers, position 等
        """
        with allure.step(f"点击元素: {self._description}"):
            self._locator.click(**kwargs)
    
    def dblclick(self, **kwargs):
        """
        双击元素
        
        Args:
            **kwargs: 双击选项
        """
        with allure.step(f"双击元素: {self._description}"):
            self._locator.dblclick(**kwargs)
    
    def fill(self, value: str, **kwargs):
        """
        填充文本
        
        Args:
            value: 要填充的文本
            **kwargs: 填充选项，如 force, noWaitAfter, timeout 等
        """
        with allure.step(f"在元素 {self._description} 中填充: {value}"):
            self._locator.fill(value, **kwargs)
    
    def type(self, text: str, delay: int = 0, **kwargs):
        """
        模拟键盘输入文本
        
        Args:
            text: 要输入的文本
            delay: 延迟时间（毫秒）
            **kwargs: 其他选项
        """
        with allure.step(f"在元素 {self._description} 中输入: {text}"):
            self._locator.type(text, delay=delay, **kwargs)
    
    def press(self, key: str, **kwargs):
        """
        按下键盘键
        
        Args:
            key: 按键名称
            **kwargs: 其他选项
        """
        with allure.step(f"在元素 {self._description} 上按下: {key}"):
            self._locator.press(key, **kwargs)
    
    def hover(self, **kwargs):
        """
        鼠标悬停
        
        Args:
            **kwargs: 悬停选项
        """
        with allure.step(f"鼠标悬停在元素上: {self._description}"):
            self._locator.hover(**kwargs)
    
    def focus(self, **kwargs):
        """
        聚焦元素
        
        Args:
            **kwargs: 聚焦选项
        """
        with allure.step(f"聚焦元素: {self._description}"):
            self._locator.focus(**kwargs)
    
    def blur(self):
        """
        移除焦点
        """
        with allure.step(f"移除元素焦点: {self._description}"):
            # 通过聚焦其他元素来移除焦点
            self.evaluate("this.blur()")
    
    def clear(self, **kwargs):
        """
        清空输入框
        
        Args:
            **kwargs: 清空选项
        """
        with allure.step(f"清空元素: {self._description}"):
            self._locator.clear(**kwargs)
    
    def select_option(self, value: Union[str, List[str]], **kwargs):
        """
        选择选项
        
        Args:
            value: 选项值或标签
            **kwargs: 选择选项
        """
        with allure.step(f"在元素 {self._description} 中选择: {value}"):
            self._locator.select_option(value, **kwargs)
    
    def check(self, **kwargs):
        """
        勾选复选框或单选按钮
        
        Args:
            **kwargs: 勾选选项
        """
        with allure.step(f"勾选元素: {self._description}"):
            self._locator.check(**kwargs)
    
    def uncheck(self, **kwargs):
        """
        取消勾选
        
        Args:
            **kwargs: 取消勾选选项
        """
        with allure.step(f"取消勾选元素: {self._description}"):
            self._locator.uncheck(**kwargs)
    
    def set_checked(self, checked: bool, **kwargs):
        """
        设置勾选状态
        
        Args:
            checked: 是否勾选
            **kwargs: 其他选项
        """
        with allure.step(f"设置元素勾选状态为: {checked}"):
            self._locator.set_checked(checked, **kwargs)
    
    # ========== 拖放操作 ==========
    def drag_to(self, target: Union['LocatorWrapper', Locator], **kwargs):
        """
        拖放到目标元素
        
        Args:
            target: 目标元素或定位器包装器
            **kwargs: 拖放选项
        """
        if isinstance(target, LocatorWrapper):
            target_locator = target.locator
            target_desc = target.description
        else:
            target_locator = target
            target_desc = str(target)
        
        with allure.step(f"拖放元素 {self._description} 到 {target_desc}"):
            self._locator.drag_to(target_locator, **kwargs)
    
    # ========== 属性获取 ==========
    def get_attribute(self, name: str, **kwargs) -> Optional[str]:
        """
        获取元素属性
        
        Args:
            name: 属性名
            **kwargs: 其他选项
            
        Returns:
            Optional[str]: 属性值
        """
        return self._locator.get_attribute(name, **kwargs)
    
    def get_text(self, **kwargs) -> str:
        """
        获取元素文本
        
        Args:
            **kwargs: 其他选项
            
        Returns:
            str: 元素文本
        """
        return self._locator.text_content(**kwargs)
    
    def get_inner_text(self, **kwargs) -> str:
        """
        获取元素内部文本（包括隐藏文本）
        
        Args:
            **kwargs: 其他选项
            
        Returns:
            str: 内部文本
        """
        return self._locator.inner_text(**kwargs)
    
    def get_inner_html(self, **kwargs) -> str:
        """
        获取元素内部 HTML
        
        Args:
            **kwargs: 其他选项
            
        Returns:
            str: 内部 HTML
        """
        return self._locator.inner_html(**kwargs)
    
    def get_outer_html(self, **kwargs) -> str:
        """
        获取元素外部 HTML
        
        Args:
            **kwargs: 其他选项
            
        Returns:
            str: 外部 HTML
        """
        return self._locator.outer_html(**kwargs)
    
    def get_value(self, **kwargs) -> str:
        """
        获取输入框的值
        
        Args:
            **kwargs: 其他选项
            
        Returns:
            str: 输入框的值
        """
        return self._locator.input_value(**kwargs)
    
    # ========== 状态检查 ==========
    def is_visible(self, **kwargs) -> bool:
        """
        检查元素是否可见
        
        Args:
            **kwargs: 其他选项
            
        Returns:
            bool: 是否可见
        """
        return self._locator.is_visible(**kwargs)
    
    def is_hidden(self, **kwargs) -> bool:
        """
        检查元素是否隐藏
        
        Args:
            **kwargs: 其他选项
            
        Returns:
            bool: 是否隐藏
        """
        return self._locator.is_hidden(**kwargs)
    
    def is_enabled(self, **kwargs) -> bool:
        """
        检查元素是否可用
        
        Args:
            **kwargs: 其他选项
            
        Returns:
            bool: 是否可用
        """
        return self._locator.is_enabled(**kwargs)
    
    def is_disabled(self, **kwargs) -> bool:
        """
        检查元素是否禁用
        
        Args:
            **kwargs: 其他选项
            
        Returns:
            bool: 是否禁用
        """
        return self._locator.is_disabled(**kwargs)
    
    def is_checked(self, **kwargs) -> bool:
        """
        检查元素是否被勾选
        
        Args:
            **kwargs: 其他选项
            
        Returns:
            bool: 是否被勾选
        """
        return self._locator.is_checked(**kwargs)
    
    def is_editable(self, **kwargs) -> bool:
        """
        检查元素是否可编辑
        
        Args:
            **kwargs: 其他选项
            
        Returns:
            bool: 是否可编辑
        """
        return self._locator.is_editable(**kwargs)
    
    # ========== 等待操作 ==========
    def wait_for(self, state: str = "visible", **kwargs):
        """
        等待元素达到指定状态
        
        Args:
            state: 状态，"visible", "hidden", "attached", "detached"
            **kwargs: 其他选项，如 timeout
        """
        with allure.step(f"等待元素 {self._description} 状态变为 {state}"):
            self._locator.wait_for(state=state, **kwargs)
    
    def wait_for_visible(self, timeout: Optional[int] = None):
        """
        等待元素可见
        
        Args:
            timeout: 超时时间（毫秒）
        """
        self.wait_for(state="visible", timeout=timeout)
    
    def wait_for_hidden(self, timeout: Optional[int] = None):
        """
        等待元素隐藏
        
        Args:
            timeout: 超时时间（毫秒）
        """
        self.wait_for(state="hidden", timeout=timeout)
    
    # ========== 元素查找 ==========
    def get_by_text(self, text: str, exact: bool = False) -> 'LocatorWrapper':
        """
        在当前元素内查找包含指定文本的子元素
        
        Args:
            text: 文本内容
            exact: 是否精确匹配
            
        Returns:
            LocatorWrapper: 子元素包装器
        """
        sub_locator = self._locator.get_by_text(text, exact=exact)
        return LocatorWrapper(sub_locator, f"{self._description} 中的文本 '{text}'")
    
    def get_by_role(self, role: str, **kwargs) -> 'LocatorWrapper':
        """
        通过 ARIA 角色查找子元素
        
        Args:
            role: ARIA 角色
            **kwargs: 其他选项，如 name, checked, disabled, expanded, hidden, level, pressed, selected
            
        Returns:
            LocatorWrapper: 子元素包装器
        """
        sub_locator = self._locator.get_by_role(role, **kwargs)
        return LocatorWrapper(sub_locator, f"{self._description} 中的角色 '{role}'")
    
    def get_by_label(self, text: str, exact: bool = False) -> 'LocatorWrapper':
        """
        通过标签文本查找子元素
        
        Args:
            text: 标签文本
            exact: 是否精确匹配
            
        Returns:
            LocatorWrapper: 子元素包装器
        """
        sub_locator = self._locator.get_by_label(text, exact=exact)
        return LocatorWrapper(sub_locator, f"{self._description} 中的标签 '{text}'")
    
    def get_by_placeholder(self, text: str, exact: bool = False) -> 'LocatorWrapper':
        """
        通过占位符文本查找子元素
        
        Args:
            text: 占位符文本
            exact: 是否精确匹配
            
        Returns:
            LocatorWrapper: 子元素包装器
        """
        sub_locator = self._locator.get_by_placeholder(text, exact=exact)
        return LocatorWrapper(sub_locator, f"{self._description} 中的占位符 '{text}'")
    
    def get_by_test_id(self, test_id: str) -> 'LocatorWrapper':
        """
        通过测试 ID 查找子元素
        
        Args:
            test_id: 测试 ID
            
        Returns:
            LocatorWrapper: 子元素包装器
        """
        sub_locator = self._locator.get_by_test_id(test_id)
        return LocatorWrapper(sub_locator, f"{self._description} 中的测试 ID '{test_id}'")
    
    def locator(self, selector: str) -> 'LocatorWrapper':
        """
        在当前元素内查找匹配选择器的子元素
        
        Args:
            selector: CSS 选择器
            
        Returns:
            LocatorWrapper: 子元素包装器
        """
        sub_locator = self._locator.locator(selector)
        return LocatorWrapper(sub_locator, f"{self._description} > {selector}")
    
    # ========== 元素计数和遍历 ==========
    def count(self) -> int:
        """
        获取匹配元素的数量
        
        Returns:
            int: 元素数量
        """
        return self._locator.count()
    
    def all(self) -> List['LocatorWrapper']:
        """
        获取所有匹配的元素包装器
        
        Returns:
            List[LocatorWrapper]: 元素包装器列表
        """
        locators = self._locator.all()
        return [LocatorWrapper(locator, f"{self._description}[{i}]") for i, locator in enumerate(locators)]
    
    def first(self) -> 'LocatorWrapper':
        """
        获取第一个匹配的元素
        
        Returns:
            LocatorWrapper: 第一个元素包装器
        """
        first_locator = self._locator.first
        return LocatorWrapper(first_locator, f"{self._description} (第一个)")
    
    def last(self) -> 'LocatorWrapper':
        """
        获取最后一个匹配的元素
        
        Returns:
            LocatorWrapper: 最后一个元素包装器
        """
        last_locator = self._locator.last
        return LocatorWrapper(last_locator, f"{self._description} (最后一个)")
    
    def nth(self, index: int) -> 'LocatorWrapper':
        """
        获取第 n 个匹配的元素
        
        Args:
            index: 索引
            
        Returns:
            LocatorWrapper: 第 n 个元素包装器
        """
        nth_locator = self._locator.nth(index)
        return LocatorWrapper(nth_locator, f"{self._description}[{index}]")
    
    # ========== 元素位置和大小 ==========
    def bounding_box(self, **kwargs) -> Optional[Dict[str, float]]:
        """
        获取元素边界框
        
        Args:
            **kwargs: 其他选项
            
        Returns:
            Optional[Dict]: 边界框信息，包含 x, y, width, height
        """
        return self._locator.bounding_box(**kwargs)
    
    def screenshot(self, **kwargs) -> bytes:
        """
        截取元素截图
        
        Args:
            **kwargs: 截图选项，如 path, type, quality, omit_background
            
        Returns:
            bytes: 截图二进制数据
        """
        with allure.step(f"截取元素截图: {self._description}"):
            return self._locator.screenshot(**kwargs)
    
    # ========== JavaScript 执行 ==========
    def evaluate(self, expression: str, arg: Any = None) -> Any:
        """
        在元素上执行 JavaScript 表达式
        
        Args:
            expression: JavaScript 表达式
            arg: 传递给表达式的参数
            
        Returns:
            Any: 表达式执行结果
        """
        return self._locator.evaluate(expression, arg)
    
    def evaluate_all(self, expression: str, arg: Any = None) -> Any:
        """
        在所有匹配元素上执行 JavaScript 表达式
        
        Args:
            expression: JavaScript 表达式
            arg: 传递给表达式的参数
            
        Returns:
            Any: 表达式执行结果列表
        """
        return self._locator.evaluate_all(expression, arg)
    
    # ========== 断言方法 ==========
    def assert_visible(self, timeout: Optional[int] = None):
        """
        断言元素可见
        
        Args:
            timeout: 超时时间（毫秒）
        """
        with allure.step(f"断言元素可见: {self._description}"):
            try:
                self.wait_for_visible(timeout)
            except Exception as e:
                raise AssertionError(f"元素不可见: {self._description}. 错误: {str(e)}")
    
    def assert_hidden(self, timeout: Optional[int] = None):
        """
        断言元素隐藏
        
        Args:
            timeout: 超时时间（毫秒）
        """
        with allure.step(f"断言元素隐藏: {self._description}"):
            try:
                self.wait_for_hidden(timeout)
            except Exception as e:
                raise AssertionError(f"元素未隐藏: {self._description}. 错误: {str(e)}")
    
    def assert_enabled(self):
        """
        断言元素可用
        """
        with allure.step(f"断言元素可用: {self._description}"):
            if not self.is_enabled():
                raise AssertionError(f"元素不可用: {self._description}")
    
    def assert_disabled(self):
        """
        断言元素禁用
        """
        with allure.step(f"断言元素禁用: {self._description}"):
            if not self.is_disabled():
                raise AssertionError(f"元素未禁用: {self._description}")
    
    def assert_checked(self):
        """
        断言元素被勾选
        """
        with allure.step(f"断言元素被勾选: {self._description}"):
            if not self.is_checked():
                raise AssertionError(f"元素未勾选: {self._description}")
    
    def assert_not_checked(self):
        """
        断言元素未勾选
        """
        with allure.step(f"断言元素未勾选: {self._description}"):
            if self.is_checked():
                raise AssertionError(f"元素已勾选: {self._description}")
    
    def assert_has_text(self, text: str, exact: bool = False, timeout: Optional[int] = None):
        """
        断言元素包含指定文本
        
        Args:
            text: 期望的文本
            exact: 是否精确匹配
            timeout: 超时时间（毫秒）
        """
        with allure.step(f"断言元素包含文本: {text}"):
            try:
                if exact:
                    self._locator.wait_for(state="visible", timeout=timeout)
                    actual_text = self.get_text()
                    if actual_text != text:
                        raise AssertionError(f"元素文本不匹配。期望: '{text}'，实际: '{actual_text}'")
                else:
                    self._locator.wait_for(state="visible", timeout=timeout)
                    self._locator.get_by_text(text, exact=exact).wait_for(state="visible", timeout=timeout)
            except Exception as e:
                raise AssertionError(f"元素不包含文本 '{text}': {self._description}. 错误: {str(e)}")
    
    def assert_has_value(self, value: str, timeout: Optional[int] = None):
        """
        断言元素具有指定值
        
        Args:
            value: 期望的值
            timeout: 超时时间（毫秒）
        """
        with allure.step(f"断言元素值为: {value}"):
            try:
                self.wait_for(state="visible", timeout=timeout)
                actual_value = self.get_value()
                if actual_value != value:
                    raise AssertionError(f"元素值不匹配。期望: '{value}'，实际: '{actual_value}'")
            except Exception as e:
                raise AssertionError(f"元素值不是 '{value}': {self._description}. 错误: {str(e)}")
    
    def assert_has_attribute(self, name: str, value: Optional[str] = None, timeout: Optional[int] = None):
        """
        断言元素具有指定属性
        
        Args:
            name: 属性名
            value: 期望的属性值（如果为 None 则只检查属性是否存在）
            timeout: 超时时间（毫秒）
        """
        with allure.step(f"断言元素具有属性: {name}={value}"):
            try:
                self.wait_for(state="visible", timeout=timeout)
                actual_value = self.get_attribute(name)
                
                if actual_value is None:
                    raise AssertionError(f"元素没有属性 '{name}': {self._description}")
                
                if value is not None and actual_value != value:
                    raise AssertionError(f"属性值不匹配。期望: '{value}'，实际: '{actual_value}'")
            except Exception as e:
                raise AssertionError(f"属性断言失败: {self._description}. 错误: {str(e)}")