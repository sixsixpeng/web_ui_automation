# -*- coding: UTF-8 -*-
"""
核心封装模块 (core)

提供自动化测试框架的核心封装功能，包括：
- 浏览器管理：封装 Playwright 浏览器的启动、配置和管理，支持 Chromium、Firefox、WebKit、Chrome、Edge
- 页面基类：提供通用的页面操作方法（点击、输入、等待、截图等）
- API 客户端：封装 HTTP 请求，提供统一的 RESTful API 调用接口
- 异常处理：定义完整的自定义异常体系，包括浏览器、元素、API、超时等异常类型
- Playwright 高级封装：对 Browser、BrowserContext、Page、Locator 等高频使用对象进行深度封装
  * 浏览器包装器 (BrowserWrapper)
  * 对话框处理 (DialogHandler)
  * 下载管理 (DownloadHelper)
  * 键盘鼠标交互 (KeyboardMouseHelper)
  * 事件监听 (EventHelper)
  * 等待辅助 (WaitHelper)
  * 断言辅助 (AssertionHelper)
  * 元素定位器包装 (LocatorWrapper)
  * 页面包装器 (PageWrapper)
  * 视频录制 (VideoRecorder)
  * 调试工具 (DebugHelper)

主要组件：
- browser.py: 浏览器管理器，支持多浏览器类型和自定义浏览器路径
- base_page.py: 页面基类，所有页面对象都应继承此类，提供通用页面操作方法
- api_client.py: API 客户端，提供 GET、POST、PUT、DELETE 等 HTTP 方法封装
- exception_handle.py: 异常处理，定义以下自定义异常类：
  * BrowserException: 浏览器相关异常
  * APICallException: API 调用异常
  * ElementNotFoundException: 元素未找到异常
  * TimeoutException: 操作超时异常
  * ConfigException: 配置相关异常
  * FrameworkException: 框架基础异常

新增高级封装：
- page_wrapper.py: 页面包装器，扩展 BasePage，提供对话框处理、下载管理、键盘鼠标事件等高级功能
- locator_wrapper.py: 元素定位器包装器，封装 Locator 对象，提供丰富的元素操作方法
- wait_helper.py: 等待辅助类，封装各种等待条件，提供灵活的等待机制
- assertion_helper.py: 断言辅助类，提供丰富的断言方法，基于 Playwright 的 expect
- dialog_handler.py: 对话框处理器，专门处理浏览器对话框（alert, confirm, prompt）
- download_helper.py: 下载助手，处理文件下载，管理下载的文件
- keyboard_mouse_helper.py: 键盘鼠标助手，封装键盘和鼠标的交互操作
- event_helper.py: 事件助手，处理页面事件，如请求、响应、控制台消息、页面错误等
- video_recorder.py: 视频录制器，封装 Playwright 视频录制功能
- debug_helper.py: 调试助手，提供调试功能，如暂停、慢动作、追踪、性能分析等
- browser_wrapper.py: 浏览器包装器，封装 Browser 对象，提供浏览器级别操作和持久化上下文支持

使用方式：
1. 通过 browser_manager 全局实例管理浏览器生命周期
2. 页面对象继承 BasePage 或 PageWrapper 类，复用通用页面操作
3. API 测试使用 APIClient 类发送 HTTP 请求
4. 使用自定义异常提高错误处理能力和调试效率
5. 使用高级封装简化复杂操作，提升测试代码可读性和维护性

导入示例：
```python
# 基础功能
from core import browser_manager, BasePage, APIClient
from core import BrowserException, APICallException, ElementNotFoundException

# 高级封装
from core import BrowserWrapper, PageWrapper, LocatorWrapper, WaitHelper, AssertionHelper
from core import DialogHandler, DownloadHelper, KeyboardMouseHelper, EventHelper
from core import VideoRecorder, DebugHelper
```
"""

from .browser import BrowserManager, browser_manager
from .base_page import BasePage
from .api_client import APIClient
from .exception_handle import (
    BrowserException, 
    APICallException, 
    ElementNotFoundException, 
    TimeoutException, 
    ConfigException, 
    FrameworkException
)

# 新增高级封装
from .page_wrapper import PageWrapper
from .locator_wrapper import LocatorWrapper
from .wait_helper import WaitHelper
from .assertion_helper import AssertionHelper
from .dialog_handler import DialogHandler
from .download_helper import DownloadHelper
from .keyboard_mouse_helper import KeyboardMouseHelper
from .event_helper import EventHelper
from .video_recorder import VideoRecorder
from .debug_helper import DebugHelper
from .browser_wrapper import BrowserWrapper

# 定义公开接口
__all__ = [
    # 浏览器管理
    "BrowserManager",
    "browser_manager",  # 全局浏览器管理器实例
    
    # 页面基类
    "BasePage",
    
    # API 客户端
    "APIClient",
    
    # 异常类
    "BrowserException",
    "APICallException",
    "ElementNotFoundException",
    "TimeoutException",
    "ConfigException",
    "FrameworkException",
    
    # 新增高级封装
    "PageWrapper",
    "LocatorWrapper",
    "WaitHelper",
    "AssertionHelper",
    "DialogHandler",
    "DownloadHelper",
    "KeyboardMouseHelper",
    "EventHelper",
    "VideoRecorder",
    "DebugHelper",
    "BrowserWrapper",
]