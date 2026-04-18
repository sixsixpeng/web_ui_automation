# -*- coding: UTF-8 -*-
"""
调试助手
提供调试功能，如暂停、慢动作、追踪、性能分析等
"""

import time
import json
import allure
import inspect
import traceback
from typing import Optional, Callable, Any, Dict, List
from playwright.sync_api import Page, BrowserContext, Locator
from contextlib import contextmanager
from common.log_utils import LogUtils

logger = LogUtils.get_logger(__name__)


class DebugHelper:
    """调试助手"""
    
    def __init__(self, page: Page):
        """
        初始化调试助手
        
        Args:
            page: Playwright Page 对象
        """
        self._page = page
        self._context = page.context
        self._browser = page.context.browser
        self._slow_mo = 0  # 慢动作延迟（毫秒）
        self._pause_on_failure = False
        self._trace_enabled = False
        self._trace_path = "./trace"
        self._performance_recording = False
        self._performance_data = []
        
    # ========== 慢动作控制 ==========
    def set_slow_mo(self, milliseconds: int):
        """
        设置慢动作延迟
        
        Args:
            milliseconds: 延迟时间（毫秒）
        """
        self._slow_mo = milliseconds
        
        # 更新浏览器上下文的 slow_mo
        # 注意：Playwright 的 slow_mo 是在启动浏览器时设置的
        # 这里我们通过在每个操作后添加延迟来模拟
        
        with allure.step(f"设置慢动作延迟: {milliseconds}ms"):
            pass
    
    def enable_slow_mo(self, milliseconds: int = 100):
        """
        启用慢动作
        
        Args:
            milliseconds: 延迟时间（毫秒）
        """
        self.set_slow_mo(milliseconds)
    
    def disable_slow_mo(self):
        """禁用慢动作"""
        self.set_slow_mo(0)
    
    def _apply_slow_mo(self):
        """应用慢动作延迟"""
        if self._slow_mo > 0:
            time.sleep(self._slow_mo / 1000)
    
    # ========== 暂停控制 ==========
    def pause(self, message: str = "调试暂停"):
        """
        暂停执行
        
        Args:
            message: 暂停消息
        """
        logger.info(f"\n{'='*60}")
        logger.info(f"调试暂停: {message}")
        logger.info(f"当前 URL: {self._page.url}")
        logger.info(f"按 Enter 键继续...")
        logger.info(f"{'='*60}")
        
        # 附加信息到 Allure 报告
        with allure.step(f"调试暂停: {message}"):
            allure.attach(
                f"URL: {self._page.url}\n"
                f"标题: {self._page.title()}\n"
                f"时间: {time.strftime('%Y-%m-%d %H:%M:%S')}",
                name="调试暂停信息",
                attachment_type=allure.attachment_type.TEXT
            )
        
        # 在实际自动化中，我们无法真正暂停，所以这里只是记录
        # 在交互式调试中，可以手动暂停
        input()  # 这会在控制台暂停，但在自动化测试中不合适
        
    def pause_on_failure(self, enable: bool = True):
        """
        启用/禁用失败时暂停
        
        Args:
            enable: 是否启用
        """
        self._pause_on_failure = enable
        
        with allure.step(f"{'启用' if enable else '禁用'}失败时暂停"):
            pass
    
    # ========== 追踪功能 ==========
    def start_tracing(self, trace_path: Optional[str] = None, **kwargs):
        """
        开始追踪
        
        Args:
            trace_path: 追踪文件保存路径
            **kwargs: 追踪选项，如：
                screenshots: 是否截图
                snapshots: 是否保存快照
                sources: 是否保存源代码
        """
        if self._trace_enabled:
            logger.warning("追踪已在进行中")
            return
        
        self._trace_enabled = True
        self._trace_path = trace_path or "./trace"
        
        # 确保目录存在
        import os
        os.makedirs(os.path.dirname(self._trace_path), exist_ok=True)
        
        # 开始追踪
        trace_options = {
            "screenshots": True,
            "snapshots": True,
            "sources": True,
            **kwargs
        }
        
        try:
            self._context.tracing.start(**trace_options)
            print(f"开始追踪: {self._trace_path}")
        except Exception as e:
            print(f"开始追踪失败: {e}")
            self._trace_enabled = False
        
        with allure.step("开始追踪"):
            pass
    
    def stop_tracing(self, save: bool = True) -> Optional[str]:
        """
        停止追踪
        
        Args:
            save: 是否保存追踪文件
            
        Returns:
            Optional[str]: 追踪文件路径，如果不保存则返回 None
        """
        if not self._trace_enabled:
            print("没有正在进行的追踪")
            return None
        
        self._trace_enabled = False
        
        if save:
            trace_file = f"{self._trace_path}/trace_{int(time.time())}.zip"
            
            try:
                self._context.tracing.stop(path=trace_file)
                print(f"追踪已保存: {trace_file}")
                
                # 附加追踪文件到报告
                with allure.step("停止追踪并保存"):
                    try:
                        allure.attach.file(
                            trace_file,
                            name="追踪文件",
                            attachment_type=allure.attachment_type.ZIP
                        )
                    except Exception as e:
                        print(f"无法附加追踪文件到报告: {e}")
                
                return trace_file
            except Exception as e:
                print(f"停止追踪失败: {e}")
                return None
        else:
            self._context.tracing.stop()
            print("追踪已停止（未保存）")
            return None
    
    @contextmanager
    def tracing(self, trace_path: Optional[str] = None, **kwargs):
        """
        追踪上下文管理器
        
        Args:
            trace_path: 追踪文件保存路径
            **kwargs: 追踪选项
            
        Yields:
            DebugHelper: 调试助手实例
        """
        self.start_tracing(trace_path, **kwargs)
        try:
            yield self
        finally:
            self.stop_tracing()
    
    # ========== 性能分析 ==========
    def start_performance_recording(self):
        """开始性能记录"""
        self._performance_recording = True
        self._performance_data = []
        
        with allure.step("开始性能记录"):
            pass
    
    def stop_performance_recording(self) -> List[Dict]:
        """
        停止性能记录
        
        Returns:
            List[Dict]: 性能数据列表
        """
        self._performance_recording = False
        data = self._performance_data.copy()
        self._performance_data.clear()
        
        with allure.step("停止性能记录"):
            # 附加性能数据到报告
            if data:
                allure.attach(
                    json.dumps(data, indent=2, ensure_ascii=False),
                    name="性能数据",
                    attachment_type=allure.attachment_type.JSON
                )
        
        return data
    
    def record_performance(self, operation: str, start_time: float, end_time: float,
                          details: Optional[Dict] = None):
        """
        记录性能数据
        
        Args:
            operation: 操作名称
            start_time: 开始时间
            end_time: 结束时间
            details: 详细信息
        """
        if not self._performance_recording:
            return
        
        duration = end_time - start_time
        record = {
            "operation": operation,
            "start_time": start_time,
            "end_time": end_time,
            "duration": duration,
            "timestamp": time.time(),
            "details": details or {}
        }
        
        self._performance_data.append(record)
    
    @contextmanager
    def measure_performance(self, operation: str):
        """
        性能测量上下文管理器
        
        Args:
            operation: 操作名称
            
        Yields:
            None
        """
        start_time = time.time()
        try:
            yield
        finally:
            end_time = time.time()
            self.record_performance(operation, start_time, end_time)
    
    # ========== 元素调试 ==========
    def highlight_element(self, selector: str, duration: float = 2.0,
                         color: str = "red", border_width: int = 3):
        """
        高亮显示元素
        
        Args:
            selector: 元素选择器
            duration: 高亮持续时间（秒）
            color: 边框颜色
            border_width: 边框宽度
        """
        script = f"""
            (function() {{
                const element = document.querySelector('{selector}');
                if (element) {{
                    // 保存原始样式
                    const originalOutline = element.style.outline;
                    const originalOutlineOffset = element.style.outlineOffset;
                    const originalTransition = element.style.transition;
                    
                    // 设置高亮样式
                    element.style.outline = '{border_width}px solid {color}';
                    element.style.outlineOffset = '{border_width}px';
                    element.style.transition = 'outline 0.3s ease';
                    
                    // 恢复原始样式
                    setTimeout(() => {{
                        element.style.outline = originalOutline;
                        element.style.outlineOffset = originalOutlineOffset;
                        element.style.transition = originalTransition;
                    }}, {duration * 1000});
                    
                    return true;
                }}
                return false;
            }})();
        """
        
        result = self._page.evaluate(script)
        
        with allure.step(f"高亮元素: {selector}"):
            if result:
                print(f"元素已高亮: {selector}")
            else:
                print(f"元素未找到: {selector}")
    
    def get_element_info(self, selector: str) -> Dict[str, Any]:
        """
        获取元素详细信息
        
        Args:
            selector: 元素选择器
            
        Returns:
            Dict[str, Any]: 元素信息
        """
        script = f"""
            (function() {{
                const element = document.querySelector('{selector}');
                if (!element) return {{ error: '元素未找到' }};
                
                const rect = element.getBoundingClientRect();
                const computedStyle = window.getComputedStyle(element);
                
                return {{
                    tagName: element.tagName,
                    id: element.id,
                    className: element.className,
                    textContent: element.textContent?.substring(0, 200),
                    innerText: element.innerText?.substring(0, 200),
                    innerHTML: element.innerHTML?.substring(0, 500),
                    
                    // 位置和尺寸
                    boundingRect: {{
                        x: rect.x,
                        y: rect.y,
                        width: rect.width,
                        height: rect.height,
                        top: rect.top,
                        right: rect.right,
                        bottom: rect.bottom,
                        left: rect.left
                    }},
                    
                    // 样式
                    computedStyle: {{
                        display: computedStyle.display,
                        visibility: computedStyle.visibility,
                        opacity: computedStyle.opacity,
                        position: computedStyle.position,
                        zIndex: computedStyle.zIndex,
                        backgroundColor: computedStyle.backgroundColor,
                        color: computedStyle.color,
                        fontSize: computedStyle.fontSize,
                        fontWeight: computedStyle.fontWeight,
                        fontFamily: computedStyle.fontFamily
                    }},
                    
                    // 属性
                    attributes: Array.from(element.attributes).reduce((obj, attr) => {{
                        obj[attr.name] = attr.value;
                        return obj;
                    }}, {{}}),
                    
                    // 状态
                    disabled: element.disabled,
                    checked: element.checked,
                    selected: element.selected,
                    readOnly: element.readOnly,
                    required: element.required
                }};
            }})();
        """
        
        try:
            element_info = self._page.evaluate(script)
            
            # 附加到 Allure 报告
            with allure.step(f"获取元素信息: {selector}"):
                allure.attach(
                    json.dumps(element_info, indent=2, ensure_ascii=False),
                    name="元素信息",
                    attachment_type=allure.attachment_type.JSON
                )
            
            return element_info
        except Exception as e:
            error_info = {"error": str(e)}
            print(f"获取元素信息失败: {e}")
            return error_info
    
    # ========== JavaScript 调试 ==========
    def evaluate_and_log(self, script: str, name: str = "JavaScript 表达式") -> Any:
        """
        执行 JavaScript 并记录结果
        
        Args:
            script: JavaScript 代码
            name: 记录名称
            
        Returns:
            Any: 执行结果
        """
        start_time = time.time()
        
        try:
            result = self._page.evaluate(script)
            end_time = time.time()
            
            # 记录结果
            log_data = {
                "script": script[:500],  # 限制长度
                "result": str(result)[:1000],
                "duration": end_time - start_time,
                "timestamp": time.time()
            }
            
            with allure.step(f"执行 JavaScript: {name}"):
                allure.attach(
                    json.dumps(log_data, indent=2, ensure_ascii=False),
                    name="JavaScript 执行结果",
                    attachment_type=allure.attachment_type.JSON
                )
            
            return result
        except Exception as e:
            error_data = {
                "script": script[:500],
                "error": str(e),
                "timestamp": time.time()
            }
            
            with allure.step(f"执行 JavaScript 失败: {name}"):
                allure.attach(
                    json.dumps(error_data, indent=2, ensure_ascii=False),
                    name="JavaScript 执行错误",
                    attachment_type=allure.attachment_type.JSON
                )
            
            raise
    
    # ========== 网络调试 ==========
    def intercept_requests(self, url_pattern: str, handler: Callable):
        """
        拦截请求
        
        Args:
            url_pattern: URL 模式
            handler: 处理函数，接收 Request 对象
        """
        def interception_route(route, request):
            if url_pattern in request.url:
                handler(request)
            route.continue_()
        
        self._page.route(url_pattern, interception_route)
        
        with allure.step(f"拦截请求: {url_pattern}"):
            pass
    
    def mock_response(self, url_pattern: str, response_data: Dict):
        """
        模拟响应
        
        Args:
            url_pattern: URL 模式
            response_data: 响应数据
        """
        def mock_route(route, request):
            route.fulfill(
                status=response_data.get("status", 200),
                headers=response_data.get("headers", {}),
                body=response_data.get("body", "")
            )
        
        self._page.route(url_pattern, mock_route)
        
        with allure.step(f"模拟响应: {url_pattern}"):
            pass
    
    # ========== 控制台覆盖 ==========
    def override_console(self, level: str = "log"):
        """
        覆盖控制台方法
        
        Args:
            level: 控制台级别，如 "log", "error", "warn"
        """
        script = f"""
            (function() {{
                const originalConsole = console.{level};
                console.{level} = function(...args) {{
                    // 调用原始方法
                    originalConsole.apply(console, args);
                    
                    // 发送到页面（供 Playwright 捕获）
                    window._debugConsole = window._debugConsole || [];
                    window._debugConsole.push({{
                        level: '{level}',
                        args: args.map(arg => typeof arg === 'object' ? JSON.stringify(arg) : String(arg)),
                        timestamp: Date.now()
                    }});
                }};
            }})();
        """
        
        self._page.evaluate(script)
        
        with allure.step(f"覆盖控制台.{level} 方法"):
            pass
    
    # ========== 错误捕获 ==========
    def capture_errors(self):
        """捕获页面错误"""
        # 通过 pageerror 事件监听器捕获
        # 已经在 EventHelper 中实现
        
        with allure.step("启用错误捕获"):
            pass
    
    # ========== 调试工具 ==========
    def take_debug_screenshot(self, name: Optional[str] = None):
        """
        拍摄调试截图
        
        Args:
            name: 截图名称
        """
        if name is None:
            name = f"debug_{int(time.time())}"
        
        # 使用 PageWrapper 的截图功能
        # 这里我们直接使用 page.screenshot
        screenshot_path = f"./screenshot/{name}.png"
        self._page.screenshot(path=screenshot_path)
        
        with allure.step(f"拍摄调试截图: {name}"):
            allure.attach.file(
                screenshot_path,
                name="调试截图",
                attachment_type=allure.attachment_type.PNG
            )
    
    def log_page_state(self):
        """记录页面状态"""
        page_state = {
            "url": self._page.url,
            "title": self._page.title(),
            "viewport_size": self._page.viewport_size,
            "cookies": self._page.context.cookies(),
            "local_storage": self._page.evaluate("JSON.stringify(window.localStorage)"),
            "session_storage": self._page.evaluate("JSON.stringify(window.sessionStorage)"),
            "timestamp": time.time()
        }
        
        with allure.step("记录页面状态"):
            allure.attach(
                json.dumps(page_state, indent=2, ensure_ascii=False),
                name="页面状态",
                attachment_type=allure.attachment_type.JSON
            )
    
    # ========== 断言辅助 ==========
    def assert_with_screenshot(self, assertion_func: Callable, 
                              screenshot_name: Optional[str] = None):
        """
        带截图的断言
        
        Args:
            assertion_func: 断言函数
            screenshot_name: 截图名称
            
        Returns:
            bool: 断言结果
        """
        try:
            assertion_func()
            return True
        except AssertionError as e:
            # 断言失败时截图
            self.take_debug_screenshot(screenshot_name or "assertion_failed")
            raise e
        except Exception as e:
            # 其他异常时也截图
            self.take_debug_screenshot(screenshot_name or "exception")
            raise e
    
    # ========== 清理 ==========
    def reset(self):
        """重置调试状态"""
        self.disable_slow_mo()
        self.pause_on_failure(False)
        
        if self._trace_enabled:
            self.stop_tracing(save=False)
        
        if self._performance_recording:
            self.stop_performance_recording()
        
        with allure.step("重置调试状态"):
            pass