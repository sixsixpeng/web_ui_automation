# -*- coding: UTF-8 -*-
"""
键盘鼠标助手
封装键盘和鼠标的交互操作
"""

import allure
import time
from typing import Optional, List, Tuple
from playwright.sync_api import Page, Locator, Keyboard, Mouse


class KeyboardMouseHelper:
    """键盘鼠标助手"""
    
    def __init__(self, page: Page):
        """
        初始化键盘鼠标助手
        
        Args:
            page: Playwright Page 对象
        """
        self._page = page
        self._keyboard = page.keyboard
        self._mouse = page.mouse
    
    # ========== 键盘操作 ==========
    def press(self, key: str):
        """
        按下并释放单个键
        
        Args:
            key: 按键名称，如 "Enter", "Escape", "Tab", "ArrowDown" 等
        """
        with allure.step(f"按下键盘键: {key}"):
            self._keyboard.press(key)
    
    def down(self, key: str):
        """
        按下键（不释放）
        
        Args:
            key: 按键名称
        """
        with allure.step(f"按下键（不释放）: {key}"):
            self._keyboard.down(key)
    
    def up(self, key: str):
        """
        释放键
        
        Args:
            key: 按键名称
        """
        with allure.step(f"释放键: {key}"):
            self._keyboard.up(key)
    
    def type(self, text: str, delay: int = 0):
        """
        输入文本（模拟键盘输入）
        
        Args:
            text: 要输入的文本
            delay: 延迟时间（毫秒）
        """
        with allure.step(f"输入文本: {text}"):
            self._keyboard.type(text, delay=delay)
    
    def insert_text(self, text: str):
        """
        插入文本（不触发输入事件）
        
        Args:
            text: 要插入的文本
        """
        with allure.step(f"插入文本: {text}"):
            self._keyboard.insert_text(text)
    
    # ========== 组合键操作 ==========
    def press_combination(self, keys: List[str], delay_between: int = 0):
        """
        按下组合键
        
        Args:
            keys: 按键列表，如 ["Control", "A"] 表示 Ctrl+A
            delay_between: 按键之间的延迟（毫秒）
        """
        with allure.step(f"按下组合键: {'+'.join(keys)}"):
            # 按下修饰键
            for key in keys[:-1]:
                self._keyboard.down(key)
                if delay_between > 0:
                    time.sleep(delay_between / 1000)
            
            # 按下主键
            self._keyboard.press(keys[-1])
            
            # 释放修饰键
            for key in reversed(keys[:-1]):
                self._keyboard.up(key)
                if delay_between > 0:
                    time.sleep(delay_between / 1000)
    
    def ctrl_a(self):
        """全选 (Ctrl+A)"""
        self.press_combination(["Control", "A"])
    
    def ctrl_c(self):
        """复制 (Ctrl+C)"""
        self.press_combination(["Control", "C"])
    
    def ctrl_v(self):
        """粘贴 (Ctrl+V)"""
        self.press_combination(["Control", "V"])
    
    def ctrl_x(self):
        """剪切 (Ctrl+X)"""
        self.press_combination(["Control", "X"])
    
    def ctrl_z(self):
        """撤销 (Ctrl+Z)"""
        self.press_combination(["Control", "Z"])
    
    def ctrl_y(self):
        """重做 (Ctrl+Y)"""
        self.press_combination(["Control", "Y"])
    
    def ctrl_f(self):
        """查找 (Ctrl+F)"""
        self.press_combination(["Control", "F"])
    
    def ctrl_s(self):
        """保存 (Ctrl+S)"""
        self.press_combination(["Control", "S"])
    
    def alt_tab(self):
        """切换窗口 (Alt+Tab)"""
        self.press_combination(["Alt", "Tab"])
    
    def alt_f4(self):
        """关闭窗口 (Alt+F4)"""
        self.press_combination(["Alt", "F4"])
    
    # ========== 鼠标移动 ==========
    def move_to(self, x: int, y: int):
        """
        移动鼠标到指定坐标
        
        Args:
            x: X 坐标
            y: Y 坐标
        """
        with allure.step(f"移动鼠标到坐标 ({x}, {y})"):
            self._mouse.move(x, y)
    
    def move_to_element(self, selector: str, offset_x: int = 0, offset_y: int = 0):
        """
        移动鼠标到元素中心
        
        Args:
            selector: 元素选择器
            offset_x: X 轴偏移量
            offset_y: Y 轴偏移量
        """
        with allure.step(f"移动鼠标到元素: {selector}"):
            element = self._page.locator(selector)
            box = element.bounding_box()
            if box:
                center_x = box["x"] + box["width"] / 2 + offset_x
                center_y = box["y"] + box["height"] / 2 + offset_y
                self._mouse.move(center_x, center_y)
            else:
                raise ValueError(f"无法获取元素边界框: {selector}")
    
    # ========== 鼠标点击 ==========
    def click(self, x: Optional[int] = None, y: Optional[int] = None,
             button: str = "left", click_count: int = 1, delay: int = 0):
        """
        鼠标点击
        
        Args:
            x: X 坐标，如果为 None 则在当前位置点击
            y: Y 坐标，如果为 None 则在当前位置点击
            button: 鼠标按钮，"left", "right", "middle"
            click_count: 点击次数
            delay: 按下和释放之间的延迟（毫秒）
        """
        if x is not None and y is not None:
            self.move_to(x, y)
        
        with allure.step(f"鼠标点击 ({button}, {click_count}次)"):
            self._mouse.click(button=button, click_count=click_count, delay=delay)
    
    def click_element(self, selector: str, button: str = "left", 
                     click_count: int = 1, delay: int = 0):
        """
        点击元素
        
        Args:
            selector: 元素选择器
            button: 鼠标按钮
            click_count: 点击次数
            delay: 按下和释放之间的延迟
        """
        with allure.step(f"点击元素: {selector}"):
            self.move_to_element(selector)
            self._mouse.click(button=button, click_count=click_count, delay=delay)
    
    def double_click(self, x: Optional[int] = None, y: Optional[int] = None):
        """
        双击
        
        Args:
            x: X 坐标
            y: Y 坐标
        """
        self.click(x, y, click_count=2)
    
    def double_click_element(self, selector: str):
        """
        双击元素
        
        Args:
            selector: 元素选择器
        """
        self.click_element(selector, click_count=2)
    
    def right_click(self, x: Optional[int] = None, y: Optional[int] = None):
        """
        右键点击
        
        Args:
            x: X 坐标
            y: Y 坐标
        """
        self.click(x, y, button="right")
    
    def right_click_element(self, selector: str):
        """
        右键点击元素
        
        Args:
            selector: 元素选择器
        """
        self.click_element(selector, button="right")
    
    def middle_click(self, x: Optional[int] = None, y: Optional[int] = None):
        """
        中键点击
        
        Args:
            x: X 坐标
            y: Y 坐标
        """
        self.click(x, y, button="middle")
    
    # ========== 鼠标拖拽 ==========
    def drag(self, start_x: int, start_y: int, end_x: int, end_y: int,
            delay: int = 0):
        """
        拖拽操作
        
        Args:
            start_x: 起始 X 坐标
            start_y: 起始 Y 坐标
            end_x: 结束 X 坐标
            end_y: 结束 Y 坐标
            delay: 按下和移动之间的延迟（毫秒）
        """
        with allure.step(f"拖拽: ({start_x}, {start_y}) -> ({end_x}, {end_y})"):
            self.move_to(start_x, start_y)
            self._mouse.down()
            
            if delay > 0:
                time.sleep(delay / 1000)
            
            self.move_to(end_x, end_y)
            self._mouse.up()
    
    def drag_element(self, source_selector: str, target_selector: str,
                    delay: int = 0):
        """
        拖拽元素到目标位置
        
        Args:
            source_selector: 源元素选择器
            target_selector: 目标元素选择器
            delay: 延迟时间
        """
        with allure.step(f"拖拽元素: {source_selector} -> {target_selector}"):
            # 获取源元素位置
            source_element = self._page.locator(source_selector)
            source_box = source_element.bounding_box()
            if not source_box:
                raise ValueError(f"无法获取源元素边界框: {source_selector}")
            
            # 获取目标元素位置
            target_element = self._page.locator(target_selector)
            target_box = target_element.bounding_box()
            if not target_box:
                raise ValueError(f"无法获取目标元素边界框: {target_selector}")
            
            # 计算中心点
            source_x = source_box["x"] + source_box["width"] / 2
            source_y = source_box["y"] + source_box["height"] / 2
            target_x = target_box["x"] + target_box["width"] / 2
            target_y = target_box["y"] + target_box["height"] / 2
            
            # 执行拖拽
            self.drag(source_x, source_y, target_x, target_y, delay)
    
    # ========== 鼠标滚轮 ==========
    def wheel(self, delta_x: float, delta_y: float):
        """
        滚动鼠标滚轮
        
        Args:
            delta_x: 水平滚动量
            delta_y: 垂直滚动量
        """
        with allure.step(f"滚动鼠标滚轮: delta_x={delta_x}, delta_y={delta_y}"):
            self._mouse.wheel(delta_x, delta_y)
    
    def scroll_up(self, pixels: int = 100):
        """
        向上滚动
        
        Args:
            pixels: 滚动像素数
        """
        self.wheel(0, -pixels)
    
    def scroll_down(self, pixels: int = 100):
        """
        向下滚动
        
        Args:
            pixels: 滚动像素数
        """
        self.wheel(0, pixels)
    
    def scroll_left(self, pixels: int = 100):
        """
        向左滚动
        
        Args:
            pixels: 滚动像素数
        """
        self.wheel(-pixels, 0)
    
    def scroll_right(self, pixels: int = 100):
        """
        向右滚动
        
        Args:
            pixels: 滚动像素数
        """
        self.wheel(pixels, 0)
    
    def scroll_to_element(self, selector: str):
        """
        滚动到元素
        
        Args:
            selector: 元素选择器
        """
        with allure.step(f"滚动到元素: {selector}"):
            element = self._page.locator(selector)
            element.scroll_into_view_if_needed()
    
    # ========== 鼠标悬停 ==========
    def hover(self, x: Optional[int] = None, y: Optional[int] = None,
             steps: int = 1):
        """
        鼠标悬停
        
        Args:
            x: X 坐标
            y: Y 坐标
            steps: 移动步数
        """
        if x is not None and y is not None:
            self.move_to(x, y)
        
        with allure.step(f"鼠标悬停在 ({x}, {y})"):
            # 悬停就是移动到位置，不需要额外操作
            pass
    
    def hover_element(self, selector: str, steps: int = 1):
        """
        鼠标悬停在元素上
        
        Args:
            selector: 元素选择器
            steps: 移动步数
        """
        with allure.step(f"鼠标悬停在元素上: {selector}"):
            element = self._page.locator(selector)
            element.hover()
    
    # ========== 上下文菜单 ==========
    def open_context_menu(self, x: Optional[int] = None, y: Optional[int] = None):
        """
        打开上下文菜单（右键菜单）
        
        Args:
            x: X 坐标
            y: Y 坐标
        """
        self.right_click(x, y)
    
    def open_element_context_menu(self, selector: str):
        """
        打开元素的上下文菜单
        
        Args:
            selector: 元素选择器
        """
        self.right_click_element(selector)
    
    # ========== 高级操作 ==========
    def drag_and_drop(self, source_selector: str, target_selector: str):
        """
        拖放元素（使用 Playwright 的 drag_to 方法）
        
        Args:
            source_selector: 源元素选择器
            target_selector: 目标元素选择器
        """
        with allure.step(f"拖放元素: {source_selector} -> {target_selector}"):
            source_element = self._page.locator(source_selector)
            target_element = self._page.locator(target_selector)
            source_element.drag_to(target_element)
    
    def click_and_hold(self, x: Optional[int] = None, y: Optional[int] = None):
        """
        点击并按住
        
        Args:
            x: X 坐标
            y: Y 坐标
        """
        if x is not None and y is not None:
            self.move_to(x, y)
        
        with allure.step("点击并按住鼠标"):
            self._mouse.down()
    
    def release(self):
        """释放鼠标按钮"""
        with allure.step("释放鼠标按钮"):
            self._mouse.up()
    
    def move_by_offset(self, offset_x: int, offset_y: int):
        """
        相对移动鼠标
        
        Args:
            offset_x: X 轴偏移量
            offset_y: Y 轴偏移量
        """
        current_position = self._mouse.position
        new_x = current_position["x"] + offset_x
        new_y = current_position["y"] + offset_y
        
        with allure.step(f"相对移动鼠标: ({offset_x}, {offset_y})"):
            self._mouse.move(new_x, new_y)
    
    # ========== 状态获取 ==========
    def get_mouse_position(self) -> Tuple[int, int]:
        """
        获取当前鼠标位置
        
        Returns:
            Tuple[int, int]: (x, y) 坐标
        """
        position = self._mouse.position
        return position["x"], position["y"]
    
    def is_mouse_down(self) -> bool:
        """
        检查鼠标按钮是否按下
        
        Returns:
            bool: 是否按下
        """
        # Playwright 不直接提供此信息，我们可以跟踪状态
        # 这里返回一个默认值，实际使用中可能需要自己维护状态
        return False
    
    # ========== 模拟人类操作 ==========
    def human_type(self, text: str, min_delay: int = 50, max_delay: int = 150):
        """
        模拟人类输入（随机延迟）
        
        Args:
            text: 要输入的文本
            min_delay: 最小延迟（毫秒）
            max_delay: 最大延迟（毫秒）
        """
        import random
        
        with allure.step(f"模拟人类输入: {text}"):
            for char in text:
                self._keyboard.type(char)
                delay = random.randint(min_delay, max_delay)
                time.sleep(delay / 1000)
    
    def human_click(self, selector: str, move_variance: int = 5):
        """
        模拟人类点击（带随机移动）
        
        Args:
            selector: 元素选择器
            move_variance: 移动方差
        """
        import random
        
        with allure.step(f"模拟人类点击: {selector}"):
            element = self._page.locator(selector)
            box = element.bounding_box()
            if box:
                # 添加随机偏移
                offset_x = random.randint(-move_variance, move_variance)
                offset_y = random.randint(-move_variance, move_variance)
                
                center_x = box["x"] + box["width"] / 2 + offset_x
                center_y = box["y"] + box["height"] / 2 + offset_y
                
                # 缓慢移动
                self._mouse.move(center_x, center_y, steps=random.randint(3, 10))
                
                # 随机点击延迟
                time.sleep(random.uniform(0.1, 0.3))
                
                # 点击
                self._mouse.click()
            else:
                element.click()