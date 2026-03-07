# -*- coding: UTF-8 -*-
"""
浏览器包装器
封装 Playwright Browser 对象，提供更丰富的浏览器级别操作
包括持久化上下文、浏览器信息、扩展管理等
"""

import os
import allure
import json
from pathlib import Path
from typing import Optional, Dict, Any, List
from playwright.sync_api import Browser, BrowserType, BrowserContext

from config.config_loader import config
from core.exception_handle import BrowserException


class BrowserWrapper:
    """浏览器包装器"""
    
    def __init__(self, browser: Browser):
        """
        初始化浏览器包装器
        
        Args:
            browser: Playwright Browser 对象
        """
        self._browser = browser
        self._browser_type = self._detect_browser_type()
        self._contexts: List[BrowserContext] = []
    
    def _detect_browser_type(self) -> str:
        """
        检测浏览器类型
        
        Returns:
            str: 浏览器类型（"chromium", "firefox", "webkit"）
        """
        browser = self._browser
        if hasattr(browser, '_impl_obj'):
            impl_obj = browser._impl_obj
            if hasattr(impl_obj, '_browser_type'):
                browser_type = impl_obj._browser_type
                if hasattr(browser_type, '_name'):
                    return browser_type._name
        
        # 通过启发式方法检测
        if hasattr(browser, 'chromium'):
            return "chromium"
        elif hasattr(browser, 'firefox'):
            return "firefox"
        elif hasattr(browser, 'webkit'):
            return "webkit"
        else:
            return "unknown"
    
    @property
    def browser(self) -> Browser:
        """获取原始 Browser 对象"""
        return self._browser
    
    @property
    def browser_type(self) -> str:
        """获取浏览器类型"""
        return self._browser_type
    
    @property
    def version(self) -> str:
        """获取浏览器版本"""
        try:
            # 尝试获取版本信息
            return self._browser.version
        except:
            return "unknown"
    
    # ========== 上下文管理 ==========
    def new_context(self, **kwargs) -> BrowserContext:
        """
        创建新的浏览器上下文
        
        Args:
            **kwargs: 上下文选项，如：
                viewport: 视口大小
                storage_state: 存储状态
                ignore_https_errors: 是否忽略 HTTPS 错误
                java_script_enabled: 是否启用 JavaScript
                bypass_csp: 是否绕过 CSP
                user_agent: 用户代理
                locale: 语言环境
                timezone_id: 时区
            
        Returns:
            BrowserContext: 浏览器上下文对象
        """
        # 设置默认值
        default_kwargs = {
            "viewport": config.get("viewport", {"width": 1920, "height": 1080}),
            "ignore_https_errors": True,
            "java_script_enabled": True,
            "bypass_csp": True,
            "locale": "zh-CN",
            "timezone_id": "Asia/Shanghai"
        }
        
        # 合并参数
        context_kwargs = {**default_kwargs, **kwargs}
        
        # 创建上下文
        context = self._browser.new_context(**context_kwargs)
        self._contexts.append(context)
        
        # 设置默认超时
        context.set_default_timeout(config.get("timeout", 30000))
        
        with allure.step("创建新的浏览器上下文"):
            allure.attach(
                json.dumps(context_kwargs, indent=2, ensure_ascii=False),
                name="上下文配置",
                attachment_type=allure.attachment_type.JSON
            )
        
        return context
    
    def new_persistent_context(self, user_data_dir: str, **kwargs) -> BrowserContext:
        """
        创建持久化浏览器上下文
        
        Args:
            user_data_dir: 用户数据目录路径
            **kwargs: 上下文选项
            
        Returns:
            BrowserContext: 持久化浏览器上下文对象
        """
        # 确保用户数据目录存在
        os.makedirs(user_data_dir, exist_ok=True)
        
        # 设置持久化上下文参数
        persistent_kwargs = {
            "user_data_dir": user_data_dir,
            **kwargs
        }
        
        # 创建持久化上下文
        context = self._browser.new_context(**persistent_kwargs)
        self._contexts.append(context)
        
        # 设置默认超时
        context.set_default_timeout(config.get("timeout", 30000))
        
        with allure.step(f"创建持久化浏览器上下文: {user_data_dir}"):
            allure.attach(
                json.dumps(persistent_kwargs, indent=2, ensure_ascii=False),
                name="持久化上下文配置",
                attachment_type=allure.attachment_type.JSON
            )
        
        return context
    
    def get_contexts(self) -> List[BrowserContext]:
        """
        获取所有浏览器上下文
        
        Returns:
            List[BrowserContext]: 浏览器上下文列表
        """
        return self._contexts.copy()
    
    def get_context_count(self) -> int:
        """
        获取浏览器上下文数量
        
        Returns:
            int: 上下文数量
        """
        return len(self._contexts)
    
    def close_context(self, context: BrowserContext):
        """
        关闭浏览器上下文
        
        Args:
            context: 要关闭的浏览器上下文
        """
        if context in self._contexts:
            context.close()
            self._contexts.remove(context)
            
            with allure.step("关闭浏览器上下文"):
                pass
    
    def close_all_contexts(self):
        """关闭所有浏览器上下文"""
        with allure.step("关闭所有浏览器上下文"):
            for context in self._contexts[:]:
                self.close_context(context)
    
    # ========== 页面管理 ==========
    def new_page(self, **kwargs) -> BrowserContext:
        """
        创建新页面（自动创建上下文）
        
        Args:
            **kwargs: 上下文选项
            
        Returns:
            BrowserContext: 包含新页面的浏览器上下文
        """
        context = self.new_context(**kwargs)
        return context
    
    def get_pages(self) -> List:
        """
        获取所有页面
        
        Returns:
            List: 所有上下文中的所有页面
        """
        pages = []
        for context in self._contexts:
            pages.extend(context.pages)
        return pages
    
    def get_page_count(self) -> int:
        """
        获取页面数量
        
        Returns:
            int: 页面数量
        """
        count = 0
        for context in self._contexts:
            count += len(context.pages)
        return count
    
    # ========== 浏览器信息 ==========
    def get_browser_info(self) -> Dict[str, Any]:
        """
        获取浏览器信息
        
        Returns:
            Dict[str, Any]: 浏览器信息字典
        """
        info = {
            "browser_type": self._browser_type,
            "version": self.version,
            "is_connected": self._browser.is_connected(),
            "context_count": self.get_context_count(),
            "page_count": self.get_page_count()
        }
        
        return info
    
    def log_browser_info(self):
        """记录浏览器信息"""
        info = self.get_browser_info()
        
        with allure.step("浏览器信息"):
            allure.attach(
                json.dumps(info, indent=2, ensure_ascii=False),
                name="浏览器信息",
                attachment_type=allure.attachment_type.JSON
            )
    
    # ========== 扩展管理 ==========
    def add_init_script(self, script: str):
        """
        添加初始化脚本（在所有页面中执行）
        
        Args:
            script: JavaScript 脚本
        """
        self._browser.add_init_script(script)
        
        with allure.step("添加浏览器初始化脚本"):
            allure.attach(
                script,
                name="初始化脚本",
                attachment_type=allure.attachment_type.TEXT
            )
    
    def add_cookie(self, cookie: Dict[str, Any]):
        """
        添加 Cookie（已弃用，建议在上下文中添加）
        
        Args:
            cookie: Cookie 字典
        """
        print("警告：add_cookie 方法已弃用，请在浏览器上下文中添加 Cookie")
    
    def clear_cookies(self):
        """清除所有 Cookie（已弃用）"""
        print("警告：clear_cookies 方法已弃用，请使用浏览器上下文方法")
    
    # ========== 浏览器操作 ==========
    def start_tracing(self, **kwargs):
        """
        开始追踪
        
        Args:
            **kwargs: 追踪选项
        """
        # 追踪是在上下文级别进行的
        print("追踪应在浏览器上下文级别进行")
    
    def stop_tracing(self, **kwargs):
        """
        停止追踪
        
        Args:
            **kwargs: 追踪选项
        """
        # 追踪是在上下文级别进行的
        print("追踪应在浏览器上下文级别进行")
    
    # ========== 连接状态 ==========
    def is_connected(self) -> bool:
        """
        检查浏览器是否连接
        
        Returns:
            bool: 是否连接
        """
        return self._browser.is_connected()
    
    def disconnect(self):
        """断开浏览器连接"""
        # Playwright 的 Browser 对象没有直接的 disconnect 方法
        # 可以通过关闭浏览器来断开连接
        print("使用 close() 方法关闭浏览器")
    
    # ========== 清理 ==========
    def close(self):
        """关闭浏览器"""
        self.close_all_contexts()
        self._browser.close()
        
        with allure.step("关闭浏览器"):
            pass
    
    def __enter__(self):
        """上下文管理器入口"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器出口"""
        self.close()