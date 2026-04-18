# -*- coding: UTF-8 -*-
"""
页面包装器
扩展 BasePage，提供更丰富的 Playwright Page 对象封装
包括对话框处理、下载管理、键盘鼠标事件、截图视频等高级功能
"""

import time
import allure
import os
from pathlib import Path
from typing import Optional, List, Dict, Any, Union, Callable
from playwright.sync_api import Page, Locator, Dialog, Download, FileChooser, Request, Response, ConsoleMessage, WebSocket
from playwright._impl._api_structures import ViewportSize

from config.config_loader import config
from core.exception_handle import ElementNotFoundException, TimeoutException, BrowserException
from core.base_page import BasePage
from common.log_utils import LogUtils

logger = LogUtils.get_logger(__name__)


class PageWrapper(BasePage):
    """页面包装器，扩展 BasePage 功能"""
    
    def __init__(self, page: Optional[Page] = None):
        """
        初始化页面包装器
        
        Args:
            page: Playwright Page 对象，如果为 None 则创建新页面
        """
        super().__init__(page)
        self._downloads = []  # 下载文件列表
        self._dialogs = []    # 对话框列表
        self._event_listeners = {}  # 事件监听器
        
        # 设置默认事件监听
        self._setup_default_listeners()
    
    def _setup_default_listeners(self):
        """设置默认事件监听器"""
        # 监听对话框
        self._page.on("dialog", self._handle_dialog)
        
        # 监听下载
        self._page.on("download", self._handle_download)
        
        # 监听控制台消息（用于调试）
        self._page.on("console", self._handle_console)
        
        # 监听页面错误
        self._page.on("pageerror", self._handle_page_error)
    
    def _handle_dialog(self, dialog: Dialog):
        """处理对话框"""
        self._dialogs.append(dialog)
        logger.info(f"对话框出现: {dialog.type} - {dialog.message}")
    
    def _handle_download(self, download: Download):
        """处理下载"""
        self._downloads.append(download)
        print(f"下载开始: {download.url}")
    
    def _handle_console(self, message: ConsoleMessage):
        """处理控制台消息"""
        msg_type = message.type
        text = message.text
        print(f"控制台 [{msg_type}]: {text}")
        
        # 将错误和警告附加到 Allure 报告
        if msg_type in ["error", "warning"]:
            allure.attach(
                f"控制台 {msg_type}: {text}",
                name=f"console_{msg_type}",
                attachment_type=allure.attachment_type.TEXT
            )
    
    def _handle_page_error(self, error):
        """处理页面错误"""
        print(f"页面错误: {error}")
        allure.attach(
            f"页面错误: {error}",
            name="page_error",
            attachment_type=allure.attachment_type.TEXT
        )
    
    # ========== 对话框处理 ==========
    def accept_dialog(self, text: Optional[str] = None):
        """
        接受对话框（确认/确定）
        
        Args:
            text: 如果对话框是提示框，可输入文本
        """
        if not self._dialogs:
            raise BrowserException("没有待处理的对话框")
        
        dialog = self._dialogs.pop(0)
        if text is not None:
            dialog.accept(text)
        else:
            dialog.accept()
        
        with allure.step(f"接受对话框: {dialog.type} - {dialog.message}"):
            pass
    
    def dismiss_dialog(self):
        """取消/关闭对话框"""
        if not self._dialogs:
            raise BrowserException("没有待处理的对话框")
        
        dialog = self._dialogs.pop(0)
        dialog.dismiss()
        
        with allure.step(f"取消对话框: {dialog.type} - {dialog.message}"):
            pass
    
    def get_dialog_message(self) -> Optional[str]:
        """获取最近对话框的消息"""
        if self._dialogs:
            return self._dialogs[0].message
        return None
    
    def wait_for_dialog(self, timeout: Optional[int] = None) -> Dialog:
        """
        等待对话框出现
        
        Args:
            timeout: 超时时间（毫秒）
            
        Returns:
            Dialog: 对话框对象
        """
        timeout = timeout or config.get("timeout", 30000)
        start_time = time.time()
        
        while time.time() - start_time < timeout / 1000:
            if self._dialogs:
                return self._dialogs[0]
            time.sleep(0.1)
        
        raise TimeoutException("等待对话框", timeout)
    
    # ========== 下载处理 ==========
    def wait_for_download(self, timeout: Optional[int] = None) -> Download:
        """
        等待下载完成
        
        Args:
            timeout: 超时时间（毫秒）
            
        Returns:
            Download: 下载对象
        """
        timeout = timeout or config.get("timeout", 30000)
        start_time = time.time()
        
        while time.time() - start_time < timeout / 1000:
            if self._downloads:
                download = self._downloads.pop(0)
                # 等待下载完成
                download.path()  # 这会阻塞直到下载完成
                return download
            time.sleep(0.1)
        
        raise TimeoutException("等待下载", timeout)
    
    def save_download(self, save_dir: Optional[str] = None, filename: Optional[str] = None) -> str:
        """
        保存下载的文件
        
        Args:
            save_dir: 保存目录，如果为 None 则使用配置的下载目录
            filename: 文件名，如果为 None 则使用下载建议的文件名
            
        Returns:
            str: 保存的文件路径
        """
        download = self.wait_for_download()
        
        if save_dir is None:
            save_dir = config.get("download_dir", "./downloads")
        
        os.makedirs(save_dir, exist_ok=True)
        
        if filename is None:
            # 获取下载建议的文件名
            suggested_filename = download.suggested_filename
            filename = suggested_filename or f"download_{int(time.time())}"
        
        save_path = os.path.join(save_dir, filename)
        download.save_as(save_path)
        
        with allure.step(f"保存下载文件: {save_path}"):
            allure.attach.file(
                save_path,
                name="下载文件",
                attachment_type=allure.attachment_type.from_file_path(save_path)
            )
        
        return save_path
    
    # ========== 键盘操作 ==========
    def press_key(self, key: str):
        """
        按下键盘键
        
        Args:
            key: 按键名称，如 "Enter", "Escape", "Tab", "ArrowDown" 等
        """
        with allure.step(f"按下键盘键: {key}"):
            self._page.keyboard.press(key)
    
    def type_text(self, text: str, delay: int = 0):
        """
        输入文本（模拟键盘输入）
        
        Args:
            text: 要输入的文本
            delay: 延迟时间（毫秒）
        """
        with allure.step(f"输入文本: {text}"):
            self._page.keyboard.type(text, delay=delay)
    
    def press_combination(self, keys: List[str]):
        """
        按下组合键
        
        Args:
            keys: 按键列表，如 ["Control", "A"] 表示 Ctrl+A
        """
        with allure.step(f"按下组合键: {'+'.join(keys)}"):
            for key in keys[:-1]:
                self._page.keyboard.down(key)
            self._page.keyboard.press(keys[-1])
            for key in reversed(keys[:-1]):
                self._page.keyboard.up(key)
    
    # ========== 鼠标操作 ==========
    def click_at(self, x: int, y: int, button: str = "left", click_count: int = 1):
        """
        在指定坐标点击
        
        Args:
            x: X 坐标
            y: Y 坐标
            button: 鼠标按钮，"left", "right", "middle"
            click_count: 点击次数
        """
        with allure.step(f"在坐标 ({x}, {y}) 点击"):
            self._page.mouse.click(x, y, button=button, click_count=click_count)
    
    def double_click(self, selector: str, timeout: Optional[int] = None):
        """
        双击元素
        
        Args:
            selector: 元素选择器
            timeout: 超时时间（毫秒）
        """
        with allure.step(f"双击元素: {selector}"):
            element = self.get_element(selector, timeout)
            element.dblclick()
    
    def right_click(self, selector: str, timeout: Optional[int] = None):
        """
        右键点击元素
        
        Args:
            selector: 元素选择器
            timeout: 超时时间（毫秒）
        """
        with allure.step(f"右键点击元素: {selector}"):
            element = self.get_element(selector, timeout)
            element.click(button="right")
    
    def hover(self, selector: str, timeout: Optional[int] = None):
        """
        鼠标悬停在元素上
        
        Args:
            selector: 元素选择器
            timeout: 超时时间（毫秒）
        """
        with allure.step(f"鼠标悬停在元素上: {selector}"):
            element = self.get_element(selector, timeout)
            element.hover()
    
    def drag_and_drop(self, source_selector: str, target_selector: str, timeout: Optional[int] = None):
        """
        拖放元素
        
        Args:
            source_selector: 源元素选择器
            target_selector: 目标元素选择器
            timeout: 超时时间（毫秒）
        """
        with allure.step(f"拖放元素: {source_selector} -> {target_selector}"):
            source = self.get_element(source_selector, timeout)
            target = self.get_element(target_selector, timeout)
            source.drag_to(target)
    
    # ========== 截图和视频 ==========
    def screenshot_full_page(self, name: str = None) -> str:
        """
        截取整个页面（包括滚动区域）
        
        Args:
            name: 截图名称，如果为 None 则使用时间戳
            
        Returns:
            str: 截图文件路径
        """
        if name is None:
            name = f"fullpage_{int(time.time())}"
        
        screenshot_path = Path(self._screenshot_dir) / f"{name}.png"
        self._page.screenshot(path=str(screenshot_path), full_page=True)
        
        # 附加到 Allure 报告
        allure.attach.file(
            str(screenshot_path),
            name=f"fullpage_{name}",
            attachment_type=allure.attachment_type.PNG
        )
        
        return str(screenshot_path)
    
    def screenshot_element(self, selector: str, name: str = None, timeout: Optional[int] = None) -> str:
        """
        截取指定元素
        
        Args:
            selector: 元素选择器
            name: 截图名称，如果为 None 则使用时间戳
            timeout: 超时时间（毫秒）
            
        Returns:
            str: 截图文件路径
        """
        if name is None:
            name = f"element_{int(time.time())}"
        
        element = self.get_element(selector, timeout)
        screenshot_path = Path(self._screenshot_dir) / f"{name}.png"
        element.screenshot(path=str(screenshot_path))
        
        # 附加到 Allure 报告
        allure.attach.file(
            str(screenshot_path),
            name=f"element_{name}",
            attachment_type=allure.attachment_type.PNG
        )
        
        return str(screenshot_path)
    
    # ========== 页面操作 ==========
    def emulate_device(self, device_name: str):
        """
        模拟移动设备
        
        Args:
            device_name: 设备名称，如 "iPhone 12", "Pixel 5" 等
        """
        from playwright.sync_api import Devices
        device = Devices[device_name]
        self._page.emulate(**device)
        
        with allure.step(f"模拟设备: {device_name}"):
            pass
    
    def set_viewport_size(self, width: int, height: int):
        """
        设置视口大小
        
        Args:
            width: 宽度
            height: 高度
        """
        self._page.set_viewport_size({"width": width, "height": height})
        
        with allure.step(f"设置视口大小: {width}x{height}"):
            pass
    
    def get_viewport_size(self) -> ViewportSize:
        """
        获取当前视口大小
        
        Returns:
            ViewportSize: 视口大小
        """
        return self._page.viewport_size
    
    # ========== 执行脚本 ==========
    def evaluate_script(self, script: str, *args) -> Any:
        """
        在页面上下文中执行 JavaScript 并返回结果
        
        Args:
            script: JavaScript 代码
            *args: 传递给脚本的参数
            
        Returns:
            Any: 脚本执行结果
        """
        return self._page.evaluate(script, args)
    
    def evaluate_on_element(self, selector: str, script: str, *args, timeout: Optional[int] = None) -> Any:
        """
        在指定元素上执行 JavaScript
        
        Args:
            selector: 元素选择器
            script: JavaScript 代码
            *args: 传递给脚本的参数
            timeout: 超时时间（毫秒）
            
        Returns:
            Any: 脚本执行结果
        """
        element = self.get_element(selector, timeout)
        return element.evaluate(script, args)
    
    # ========== 事件监听 ==========
    def add_event_listener(self, event_type: str, handler: Callable):
        """
        添加事件监听器
        
        Args:
            event_type: 事件类型，如 "request", "response", "load", "domcontentloaded"
            handler: 事件处理函数
        """
        if event_type not in self._event_listeners:
            self._event_listeners[event_type] = []
        
        self._event_listeners[event_type].append(handler)
        self._page.on(event_type, handler)
    
    def remove_event_listener(self, event_type: str, handler: Callable):
        """
        移除事件监听器
        
        Args:
            event_type: 事件类型
            handler: 事件处理函数
        """
        if event_type in self._event_listeners and handler in self._event_listeners[event_type]:
            self._event_listeners[event_type].remove(handler)
            self._page.remove_listener(event_type, handler)
    
    # ========== 等待条件 ==========
    def wait_for_url(self, url: str, timeout: Optional[int] = None):
        """
        等待 URL 变为指定值
        
        Args:
            url: 期望的 URL（可以是部分匹配）
            timeout: 超时时间（毫秒）
        """
        timeout = timeout or config.get("timeout", 30000)
        self._page.wait_for_url(url, timeout=timeout)
        
        with allure.step(f"等待 URL 变为: {url}"):
            pass
    
    def wait_for_function(self, script: str, *args, timeout: Optional[int] = None):
        """
        等待 JavaScript 函数返回真值
        
        Args:
            script: JavaScript 函数，返回布尔值
            *args: 传递给函数的参数
            timeout: 超时时间（毫秒）
        """
        timeout = timeout or config.get("timeout", 30000)
        self._page.wait_for_function(script, args, timeout=timeout)
        
        with allure.step(f"等待函数条件: {script}"):
            pass
    
    # ========== 文件上传 ==========
    def upload_file(self, selector: str, file_path: str, timeout: Optional[int] = None):
        """
        上传文件
        
        Args:
            selector: 文件输入框选择器
            file_path: 文件路径
            timeout: 超时时间（毫秒）
        """
        with allure.step(f"上传文件: {file_path}"):
            element = self.get_element(selector, timeout)
            element.set_input_files(file_path)
    
    def upload_multiple_files(self, selector: str, file_paths: List[str], timeout: Optional[int] = None):
        """
        上传多个文件
        
        Args:
            selector: 文件输入框选择器
            file_paths: 文件路径列表
            timeout: 超时时间（毫秒）
        """
        with allure.step(f"上传多个文件: {len(file_paths)} 个文件"):
            element = self.get_element(selector, timeout)
            element.set_input_files(file_paths)
    
    # ========== 其他实用方法 ==========
    def get_cookies(self) -> List[Dict]:
        """
        获取页面 cookies
        
        Returns:
            List[Dict]: cookies 列表
        """
        return self._page.context.cookies()
    
    def set_cookies(self, cookies: List[Dict]):
        """
        设置 cookies
        
        Args:
            cookies: cookies 列表
        """
        self._page.context.add_cookies(cookies)
        
        with allure.step(f"设置 cookies: {len(cookies)} 个"):
            pass
    
    def clear_cookies(self):
        """清除所有 cookies"""
        self._page.context.clear_cookies()
        
        with allure.step("清除所有 cookies"):
            pass
    
    def get_local_storage(self, key: str = None) -> Any:
        """
        获取 localStorage 值
        
        Args:
            key: 键名，如果为 None 则返回所有
            
        Returns:
            Any: 存储的值
        """
        if key is None:
            # 返回所有 localStorage
            script = "return Object.keys(localStorage).reduce((obj, key) => { obj[key] = localStorage.getItem(key); return obj; }, {});"
            return self.evaluate_script(script)
        else:
            script = f"return localStorage.getItem('{key}');"
            return self.evaluate_script(script)
    
    def set_local_storage(self, key: str, value: str):
        """
        设置 localStorage 值
        
        Args:
            key: 键名
            value: 值
        """
        script = f"localStorage.setItem('{key}', '{value}');"
        self.evaluate_script(script)
        
        with allure.step(f"设置 localStorage: {key}={value}"):
            pass
    
    def clear_local_storage(self):
        """清除 localStorage"""
        script = "localStorage.clear();"
        self.evaluate_script(script)
        
        with allure.step("清除 localStorage"):
            pass
    
    # ========== sessionStorage 操作 ==========
    def get_session_storage(self, key: str = None) -> Any:
        """
        获取 sessionStorage 值
        
        Args:
            key: 键名，如果为 None 则返回所有
            
        Returns:
            Any: 存储的值
        """
        if key is None:
            # 返回所有 sessionStorage
            script = "return Object.keys(sessionStorage).reduce((obj, key) => { obj[key] = sessionStorage.getItem(key); return obj; }, {});"
            return self.evaluate_script(script)
        else:
            script = f"return sessionStorage.getItem('{key}');"
            return self.evaluate_script(script)
    
    def set_session_storage(self, key: str, value: str):
        """
        设置 sessionStorage 值
        
        Args:
            key: 键名
            value: 值
        """
        script = f"sessionStorage.setItem('{key}', '{value}');"
        self.evaluate_script(script)
        
        with allure.step(f"设置 sessionStorage: {key}={value}"):
            pass
    
    def clear_session_storage(self):
        """清除 sessionStorage"""
        script = "sessionStorage.clear();"
        self.evaluate_script(script)
        
        with allure.step("清除 sessionStorage"):
            pass
    
    # ========== 缓存管理工具 ==========
    def save_cache_to_local_storage(self, cache_key: str, data: Dict[str, Any]):
        """
        保存数据到 localStorage 缓存
        
        Args:
            cache_key: 缓存键名
            data: 要缓存的数据
        """
        import json as json_module
        json_str = json_module.dumps(data, ensure_ascii=False)
        self.set_local_storage(cache_key, json_str)
        
        with allure.step(f"保存缓存到 localStorage: {cache_key}"):
            allure.attach(
                json_module.dumps(data, indent=2, ensure_ascii=False),
                name=f"缓存数据_{cache_key}",
                attachment_type=allure.attachment_type.JSON
            )
    
    def load_cache_from_local_storage(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """
        从 localStorage 缓存加载数据
        
        Args:
            cache_key: 缓存键名
            
        Returns:
            Optional[Dict[str, Any]]: 缓存数据，如果不存在则返回 None
        """
        import json as json_module
        json_str = self.get_local_storage(cache_key)
        if json_str:
            try:
                data = json_module.loads(json_str)
                with allure.step(f"从 localStorage 加载缓存: {cache_key}"):
                    allure.attach(
                        json_module.dumps(data, indent=2, ensure_ascii=False),
                        name=f"缓存数据_{cache_key}",
                        attachment_type=allure.attachment_type.JSON
                    )
                return data
            except:
                return None
        return None
    
    def clear_cache_from_local_storage(self, cache_key: str = None):
        """
        清除 localStorage 缓存
        
        Args:
            cache_key: 缓存键名，如果为 None 则清除所有缓存
        """
        if cache_key:
            self.set_local_storage(cache_key, "")
            with allure.step(f"清除 localStorage 缓存: {cache_key}"):
                pass
        else:
            self.clear_local_storage()
    
    def save_cache_to_session_storage(self, cache_key: str, data: Dict[str, Any]):
        """
        保存数据到 sessionStorage 缓存
        
        Args:
            cache_key: 缓存键名
            data: 要缓存的数据
        """
        import json as json_module
        json_str = json_module.dumps(data, ensure_ascii=False)
        self.set_session_storage(cache_key, json_str)
        
        with allure.step(f"保存缓存到 sessionStorage: {cache_key}"):
            allure.attach(
                json_module.dumps(data, indent=2, ensure_ascii=False),
                name=f"缓存数据_{cache_key}",
                attachment_type=allure.attachment_type.JSON
            )
    
    def load_cache_from_session_storage(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """
        从 sessionStorage 缓存加载数据
        
        Args:
            cache_key: 缓存键名
            
        Returns:
            Optional[Dict[str, Any]]: 缓存数据，如果不存在则返回 None
        """
        import json as json_module
        json_str = self.get_session_storage(cache_key)
        if json_str:
            try:
                data = json_module.loads(json_str)
                with allure.step(f"从 sessionStorage 加载缓存: {cache_key}"):
                    allure.attach(
                        json_module.dumps(data, indent=2, ensure_ascii=False),
                        name=f"缓存数据_{cache_key}",
                        attachment_type=allure.attachment_type.JSON
                    )
                return data
            except:
                return None
        return None
    
    def clear_cache_from_session_storage(self, cache_key: str = None):
        """
        清除 sessionStorage 缓存
        
        Args:
            cache_key: 缓存键名，如果为 None 则清除所有缓存
        """
        if cache_key:
            self.set_session_storage(cache_key, "")
            with allure.step(f"清除 sessionStorage 缓存: {cache_key}"):
                pass
        else:
            self.clear_session_storage()
    
    # ========== IndexedDB 工具方法（基础） ==========
    def execute_indexeddb_transaction(self, database_name: str, store_name: str, operation: str, key: str = None, value: Any = None) -> Any:
        """
        执行 IndexedDB 事务操作
        
        Args:
            database_name: 数据库名称
            store_name: 对象存储名称
            operation: 操作类型，'get', 'put', 'delete', 'clear'
            key: 键名（对于 get、put、delete 操作）
            value: 值（对于 put 操作）
            
        Returns:
            Any: 操作结果
            
        Note:
            这是一个基础方法，复杂的 IndexedDB 操作建议直接使用 evaluate_script
        """
        scripts = {
            'get': f"""
                return new Promise((resolve, reject) => {{
                    const request = indexedDB.open('{database_name}');
                    request.onsuccess = (event) => {{
                        const db = event.target.result;
                        const transaction = db.transaction(['{store_name}'], 'readonly');
                        const store = transaction.objectStore('{store_name}');
                        const getRequest = store.get('{key}');
                        getRequest.onsuccess = () => resolve(getRequest.result);
                        getRequest.onerror = () => reject(getRequest.error);
                    }};
                    request.onerror = () => reject(request.error);
                }});
            """,
            'put': f"""
                return new Promise((resolve, reject) => {{
                    const request = indexedDB.open('{database_name}');
                    request.onsuccess = (event) => {{
                        const db = event.target.result;
                        const transaction = db.transaction(['{store_name}'], 'readwrite');
                        const store = transaction.objectStore('{store_name}');
                        const putRequest = store.put({value}, '{key}');
                        putRequest.onsuccess = () => resolve(putRequest.result);
                        putRequest.onerror = () => reject(putRequest.error);
                    }};
                    request.onerror = () => reject(request.error);
                }});
            """,
            'delete': f"""
                return new Promise((resolve, reject) => {{
                    const request = indexedDB.open('{database_name}');
                    request.onsuccess = (event) => {{
                        const db = event.target.result;
                        const transaction = db.transaction(['{store_name}'], 'readwrite');
                        const store = transaction.objectStore('{store_name}');
                        const deleteRequest = store.delete('{key}');
                        deleteRequest.onsuccess = () => resolve(deleteRequest.result);
                        deleteRequest.onerror = () => reject(deleteRequest.error);
                    }};
                    request.onerror = () => reject(request.error);
                }});
            """,
            'clear': f"""
                return new Promise((resolve, reject) => {{
                    const request = indexedDB.open('{database_name}');
                    request.onsuccess = (event) => {{
                        const db = event.target.result;
                        const transaction = db.transaction(['{store_name}'], 'readwrite');
                        const store = transaction.objectStore('{store_name}');
                        const clearRequest = store.clear();
                        clearRequest.onsuccess = () => resolve(clearRequest.result);
                        clearRequest.onerror = () => reject(clearRequest.error);
                    }};
                    request.onerror = () => reject(request.error);
                }});
            """
        }
        
        if operation not in scripts:
            raise ValueError(f"不支持的 IndexedDB 操作: {operation}")
        
        script = scripts[operation]
        return self.evaluate_script(script)