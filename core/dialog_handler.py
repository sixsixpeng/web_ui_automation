# -*- coding: UTF-8 -*-
"""
对话框处理器
专门处理浏览器对话框（alert, confirm, prompt）
"""

import allure
import time
from typing import Optional, List, Callable
from playwright.sync_api import Page, Dialog

from core.exception_handle import BrowserException, TimeoutException


class DialogHandler:
    """对话框处理器"""
    
    def __init__(self, page: Page):
        """
        初始化对话框处理器
        
        Args:
            page: Playwright Page 对象
        """
        self._page = page
        self._dialogs: List[Dialog] = []
        self._auto_accept = False
        self._auto_dismiss = False
        self._auto_text: Optional[str] = None
        
        # 监听对话框事件
        self._page.on("dialog", self._handle_dialog)
    
    def _handle_dialog(self, dialog: Dialog):
        """
        处理对话框事件
        
        Args:
            dialog: 对话框对象
        """
        self._dialogs.append(dialog)
        
        # 记录对话框信息
        dialog_info = f"对话框出现: {dialog.type} - {dialog.message}"
        print(dialog_info)
        
        with allure.step(dialog_info):
            # 附加对话框信息到报告
            allure.attach(
                f"类型: {dialog.type}\n消息: {dialog.message}",
                name="对话框信息",
                attachment_type=allure.attachment_type.TEXT
            )
        
        # 自动处理逻辑
        if self._auto_accept:
            if self._auto_text is not None and dialog.type == "prompt":
                dialog.accept(self._auto_text)
            else:
                dialog.accept()
        elif self._auto_dismiss:
            dialog.dismiss()
    
    # ========== 自动处理配置 ==========
    def auto_accept(self, prompt_text: Optional[str] = None):
        """
        设置自动接受所有对话框
        
        Args:
            prompt_text: 对于 prompt 对话框，自动输入的文本
        """
        self._auto_accept = True
        self._auto_dismiss = False
        self._auto_text = prompt_text
        
        with allure.step("设置自动接受对话框"):
            pass
    
    def auto_dismiss(self):
        """设置自动取消所有对话框"""
        self._auto_accept = False
        self._auto_dismiss = True
        self._auto_text = None
        
        with allure.step("设置自动取消对话框"):
            pass
    
    def disable_auto_handle(self):
        """禁用自动处理"""
        self._auto_accept = False
        self._auto_dismiss = False
        self._auto_text = None
        
        with allure.step("禁用自动对话框处理"):
            pass
    
    # ========== 对话框检查 ==========
    def has_dialog(self) -> bool:
        """
        检查是否有待处理的对话框
        
        Returns:
            bool: 是否有对话框
        """
        return len(self._dialogs) > 0
    
    def get_dialog_count(self) -> int:
        """
        获取待处理对话框数量
        
        Returns:
            int: 对话框数量
        """
        return len(self._dialogs)
    
    def get_dialog(self, index: int = 0) -> Optional[Dialog]:
        """
        获取指定索引的对话框
        
        Args:
            index: 对话框索引
            
        Returns:
            Optional[Dialog]: 对话框对象，如果不存在则返回 None
        """
        if 0 <= index < len(self._dialogs):
            return self._dialogs[index]
        return None
    
    def get_latest_dialog(self) -> Optional[Dialog]:
        """
        获取最新的对话框
        
        Returns:
            Optional[Dialog]: 最新的对话框对象
        """
        if self._dialogs:
            return self._dialogs[-1]
        return None
    
    def get_dialog_message(self, index: int = 0) -> Optional[str]:
        """
        获取对话框消息
        
        Args:
            index: 对话框索引
            
        Returns:
            Optional[str]: 对话框消息
        """
        dialog = self.get_dialog(index)
        if dialog:
            return dialog.message
        return None
    
    def get_dialog_type(self, index: int = 0) -> Optional[str]:
        """
        获取对话框类型
        
        Args:
            index: 对话框索引
            
        Returns:
            Optional[str]: 对话框类型（"alert", "confirm", "prompt"）
        """
        dialog = self.get_dialog(index)
        if dialog:
            return dialog.type
        return None
    
    # ========== 等待对话框 ==========
    def wait_for_dialog(self, timeout: int = 30000) -> Dialog:
        """
        等待对话框出现
        
        Args:
            timeout: 超时时间（毫秒）
            
        Returns:
            Dialog: 对话框对象
            
        Raises:
            TimeoutException: 等待超时
        """
        start_time = time.time()
        
        while time.time() - start_time < timeout / 1000:
            if self._dialogs:
                return self._dialogs[0]
            time.sleep(0.1)  # 100ms 轮询
        
        raise TimeoutException("等待对话框", timeout)
    
    def wait_for_alert(self, timeout: int = 30000) -> Dialog:
        """
        等待 alert 对话框
        
        Args:
            timeout: 超时时间（毫秒）
            
        Returns:
            Dialog: alert 对话框对象
        """
        dialog = self.wait_for_dialog(timeout)
        if dialog.type != "alert":
            raise BrowserException(f"期望 alert 对话框，但实际是 {dialog.type}")
        return dialog
    
    def wait_for_confirm(self, timeout: int = 30000) -> Dialog:
        """
        等待 confirm 对话框
        
        Args:
            timeout: 超时时间（毫秒）
            
        Returns:
            Dialog: confirm 对话框对象
        """
        dialog = self.wait_for_dialog(timeout)
        if dialog.type != "confirm":
            raise BrowserException(f"期望 confirm 对话框，但实际是 {dialog.type}")
        return dialog
    
    def wait_for_prompt(self, timeout: int = 30000) -> Dialog:
        """
        等待 prompt 对话框
        
        Args:
            timeout: 超时时间（毫秒）
            
        Returns:
            Dialog: prompt 对话框对象
        """
        dialog = self.wait_for_dialog(timeout)
        if dialog.type != "prompt":
            raise BrowserException(f"期望 prompt 对话框，但实际是 {dialog.type}")
        return dialog
    
    # ========== 对话框操作 ==========
    def accept(self, index: int = 0, prompt_text: Optional[str] = None):
        """
        接受对话框
        
        Args:
            index: 对话框索引
            prompt_text: 对于 prompt 对话框，输入的文本
        """
        if not self._dialogs:
            raise BrowserException("没有待处理的对话框")
        
        if index >= len(self._dialogs):
            raise BrowserException(f"对话框索引 {index} 超出范围，共有 {len(self._dialogs)} 个对话框")
        
        dialog = self._dialogs.pop(index)
        
        with allure.step(f"接受对话框: {dialog.type} - {dialog.message}"):
            if prompt_text is not None and dialog.type == "prompt":
                dialog.accept(prompt_text)
            else:
                dialog.accept()
    
    def accept_all(self, prompt_text: Optional[str] = None):
        """接受所有对话框"""
        with allure.step("接受所有对话框"):
            while self._dialogs:
                self.accept(0, prompt_text)
    
    def dismiss(self, index: int = 0):
        """
        取消对话框
        
        Args:
            index: 对话框索引
        """
        if not self._dialogs:
            raise BrowserException("没有待处理的对话框")
        
        if index >= len(self._dialogs):
            raise BrowserException(f"对话框索引 {index} 超出范围，共有 {len(self._dialogs)} 个对话框")
        
        dialog = self._dialogs.pop(index)
        
        with allure.step(f"取消对话框: {dialog.type} - {dialog.message}"):
            dialog.dismiss()
    
    def dismiss_all(self):
        """取消所有对话框"""
        with allure.step("取消所有对话框"):
            while self._dialogs:
                self.dismiss(0)
    
    def accept_alert(self, timeout: int = 30000):
        """
        等待并接受 alert 对话框
        
        Args:
            timeout: 超时时间（毫秒）
        """
        dialog = self.wait_for_alert(timeout)
        dialog.accept()
    
    def accept_confirm(self, timeout: int = 30000):
        """
        等待并接受 confirm 对话框
        
        Args:
            timeout: 超时时间（毫秒）
        """
        dialog = self.wait_for_confirm(timeout)
        dialog.accept()
    
    def accept_prompt(self, text: str, timeout: int = 30000):
        """
        等待并接受 prompt 对话框
        
        Args:
            text: 输入的文本
            timeout: 超时时间（毫秒）
        """
        dialog = self.wait_for_prompt(timeout)
        dialog.accept(text)
    
    def dismiss_confirm(self, timeout: int = 30000):
        """
        等待并取消 confirm 对话框
        
        Args:
            timeout: 超时时间（毫秒）
        """
        dialog = self.wait_for_confirm(timeout)
        dialog.dismiss()
    
    # ========== 断言方法 ==========
    def assert_has_dialog(self, message: Optional[str] = None, 
                         dialog_type: Optional[str] = None,
                         timeout: int = 30000):
        """
        断言有对话框出现
        
        Args:
            message: 期望的对话框消息（部分匹配）
            dialog_type: 期望的对话框类型
            timeout: 超时时间（毫秒）
            
        Raises:
            AssertionError: 断言失败
        """
        try:
            dialog = self.wait_for_dialog(timeout)
            
            if dialog_type and dialog.type != dialog_type:
                raise AssertionError(
                    f"对话框类型不匹配。期望: {dialog_type}，实际: {dialog.type}"
                )
            
            if message and message not in dialog.message:
                raise AssertionError(
                    f"对话框消息不包含期望文本。期望包含: '{message}'，实际: '{dialog.message}'"
                )
            
            with allure.step(f"断言对话框出现: {dialog.type} - {dialog.message}"):
                pass
                
        except TimeoutException:
            raise AssertionError(f"在 {timeout}ms 内没有对话框出现")
    
    def assert_no_dialog(self, timeout: int = 5000):
        """
        断言没有对话框出现
        
        Args:
            timeout: 等待时间（毫秒），在这个时间内确认没有对话框
            
        Raises:
            AssertionError: 在等待时间内有对话框出现
        """
        try:
            self.wait_for_dialog(timeout)
            # 如果执行到这里，说明有对话框出现
            raise AssertionError(f"在 {timeout}ms 内有对话框出现")
        except TimeoutException:
            # 这是期望的情况，没有对话框
            with allure.step("断言没有对话框出现"):
                pass
    
    # ========== 自定义处理 ==========
    def set_custom_handler(self, handler: Callable[[Dialog], None]):
        """
        设置自定义对话框处理函数
        
        Args:
            handler: 处理函数，接收 Dialog 对象作为参数
        """
        # 移除现有监听器
        self._page.remove_listener("dialog", self._handle_dialog)
        
        # 设置新的处理函数
        def custom_handler(dialog: Dialog):
            self._dialogs.append(dialog)
            handler(dialog)
        
        self._page.on("dialog", custom_handler)
        
        with allure.step("设置自定义对话框处理函数"):
            pass
    
    # ========== 清理 ==========
    def clear_dialogs(self):
        """清除所有对话框记录"""
        self._dialogs.clear()
        
        with allure.step("清除对话框记录"):
            pass
    
    def remove_listeners(self):
        """移除对话框监听器"""
        self._page.remove_listener("dialog", self._handle_dialog)
        
        with allure.step("移除对话框监听器"):
            pass