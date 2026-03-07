# -*- coding: UTF-8 -*-
"""
浏览器管理模块
封装 Playwright 浏览器的启动、配置和管理
"""

import os
from pathlib import Path
from typing import Optional

from playwright.sync_api import sync_playwright, Browser, BrowserContext, Page

from config.config_loader import config
from core.exception_handle import BrowserException


class BrowserManager:
    """浏览器管理器"""
    
    _instance = None
    _browser: Optional[Browser] = None
    _context: Optional[BrowserContext] = None
    _playwright = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not hasattr(self, '_initialized'):
            self._initialized = True
            self._playwright = None
            self._browser = None
            self._context = None
            self._pages = []
            
    def start_browser(self):
        """启动浏览器"""
        try:
            self._playwright = sync_playwright().start()
            
            browser_type = config.get("browser_type", "chromium")
            headless = config.get("headless", False)
            
            # 确保缓存目录存在
            cache_dir = config.get("playwright_cache_dir")
            os.makedirs(cache_dir, exist_ok=True)
            
            # 根据浏览器类型启动
            browser_executable_path = config.get("browser_executable_path")
            launch_args = {
                "headless": headless,
                "slow_mo": config.get("slow_mo", 100),
            }
            
            # 如果有自定义可执行路径，添加该参数
            if browser_executable_path:
                launch_args["executable_path"] = browser_executable_path
            
            if browser_type == "chromium":
                launch_args["args"] = ["--start-maximized"]
                self._browser = self._playwright.chromium.launch(**launch_args)
            elif browser_type == "firefox":
                self._browser = self._playwright.firefox.launch(**launch_args)
            elif browser_type == "webkit":
                self._browser = self._playwright.webkit.launch(**launch_args)
            elif browser_type == "chrome":
                # 使用 Chrome 渠道
                launch_args["channel"] = "chrome"
                launch_args["args"] = ["--start-maximized"]
                self._browser = self._playwright.chromium.launch(**launch_args)
            elif browser_type == "edge":
                # 使用 Microsoft Edge 渠道
                launch_args["channel"] = "msedge"
                launch_args["args"] = ["--start-maximized"]
                self._browser = self._playwright.chromium.launch(**launch_args)
            else:
                raise BrowserException(f"不支持的浏览器类型: {browser_type}")
            
            # 创建浏览器上下文
            self._context = self._browser.new_context(
                viewport=config.get("viewport", {"width": 1920, "height": 1080}),
                storage_state=None,  # 可以加载已有的存储状态
                ignore_https_errors=True,
                java_script_enabled=True,
                bypass_csp=True,
                user_agent=None,
                locale="zh-CN",
                timezone_id="Asia/Shanghai"
            )
            
            # 设置默认超时
            self._context.set_default_timeout(config.get("timeout", 30000))
            
            print(f"浏览器已启动: {browser_type} {'(无头模式)' if headless else ''}")
            
        except Exception as e:
            raise BrowserException(f"启动浏览器失败: {str(e)}")
    
    def start_persistent_browser(self, user_data_dir: Optional[str] = None, **kwargs):
        """
        启动持久化浏览器（使用用户数据目录）
        
        Args:
            user_data_dir: 用户数据目录路径，如果为 None 则使用配置中的目录
            **kwargs: 额外的启动参数
        """
        try:
            self._playwright = sync_playwright().start()
            
            browser_type = config.get("browser_type", "chromium")
            headless = config.get("headless", False)
            
            # 确定用户数据目录
            if user_data_dir is None:
                user_data_dir = config.get("user_data_dir", "./user_data")
            
            # 确保用户数据目录存在
            os.makedirs(user_data_dir, exist_ok=True)
            
            # 根据浏览器类型启动持久化上下文
            browser_executable_path = config.get("browser_executable_path")
            launch_args = {
                "headless": headless,
                "slow_mo": config.get("slow_mo", 100),
                **kwargs
            }
            
            # 如果有自定义可执行路径，添加该参数
            if browser_executable_path:
                launch_args["executable_path"] = browser_executable_path
            
            if browser_type == "chromium":
                launch_args["args"] = ["--start-maximized"]
                self._context = self._playwright.chromium.launch_persistent_context(
                    user_data_dir=user_data_dir,
                    **launch_args
                )
                self._browser = self._context.browser
            elif browser_type == "firefox":
                self._context = self._playwright.firefox.launch_persistent_context(
                    user_data_dir=user_data_dir,
                    **launch_args
                )
                self._browser = self._context.browser
            elif browser_type == "webkit":
                self._context = self._playwright.webkit.launch_persistent_context(
                    user_data_dir=user_data_dir,
                    **launch_args
                )
                self._browser = self._context.browser
            elif browser_type == "chrome":
                # 使用 Chrome 渠道
                launch_args["channel"] = "chrome"
                launch_args["args"] = ["--start-maximized"]
                self._context = self._playwright.chromium.launch_persistent_context(
                    user_data_dir=user_data_dir,
                    **launch_args
                )
                self._browser = self._context.browser
            elif browser_type == "edge":
                # 使用 Microsoft Edge 渠道
                launch_args["channel"] = "msedge"
                launch_args["args"] = ["--start-maximized"]
                self._context = self._playwright.chromium.launch_persistent_context(
                    user_data_dir=user_data_dir,
                    **launch_args
                )
                self._browser = self._context.browser
            else:
                raise BrowserException(f"不支持的浏览器类型: {browser_type}")
            
            # 设置默认超时
            self._context.set_default_timeout(config.get("timeout", 30000))
            
            print(f"持久化浏览器已启动: {browser_type} (用户数据目录: {user_data_dir}) {'(无头模式)' if headless else ''}")
            
        except Exception as e:
            raise BrowserException(f"启动持久化浏览器失败: {str(e)}")
    
    def new_page(self) -> Page:
        """创建新页面"""
        if not self._context:
            self.start_browser()
        
        page = self._context.new_page()
        self._pages.append(page)
        
        # 设置页面超时
        page.set_default_timeout(config.get("timeout", 30000))
        page.set_default_navigation_timeout(config.get("timeout", 30000))
        
        return page
    
    def get_current_page(self) -> Optional[Page]:
        """获取当前页面（最后创建的页面）"""
        if self._pages:
            return self._pages[-1]
        return None
    
    def close_page(self, page: Page):
        """关闭指定页面"""
        if page in self._pages:
            page.close()
            self._pages.remove(page)
    
    def close_all_pages(self):
        """关闭所有页面"""
        for page in self._pages[:]:
            self.close_page(page)
    
    def close_browser(self):
        """关闭浏览器"""
        self.close_all_pages()
        
        if self._context:
            self._context.close()
            self._context = None
        
        if self._browser:
            self._browser.close()
            self._browser = None
        
        if self._playwright:
            self._playwright.stop()
            self._playwright = None
        
        print("浏览器已关闭")
    
    def save_storage_state(self, file_path: str):
        """保存浏览器存储状态（cookies, localStorage等）"""
        if self._context:
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            self._context.storage_state(path=file_path)
    
    def load_storage_state(self, file_path: str):
        """加载浏览器存储状态"""
        if os.path.exists(file_path) and self._context:
            # 需要重新创建上下文以加载状态
            self.close_all_pages()
            self._context.close()
            
            self._context = self._browser.new_context(
                viewport=config.get("viewport", {"width": 1920, "height": 1080}),
                storage_state=file_path,
                ignore_https_errors=True
            )
            self._context.set_default_timeout(config.get("timeout", 30000))
    
    def get_browser(self) -> Optional[Browser]:
        """
        获取 Browser 对象
        
        Returns:
            Optional[Browser]: Browser 对象
        """
        return self._browser
    
    def get_context(self) -> Optional[BrowserContext]:
        """
        获取 BrowserContext 对象
        
        Returns:
            Optional[BrowserContext]: BrowserContext 对象
        """
        return self._context


# 全局浏览器管理器实例
browser_manager = BrowserManager()