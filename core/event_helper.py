# -*- coding: UTF-8 -*-
"""
事件助手
处理页面事件，如请求、响应、控制台消息、页面错误等
"""

import allure
import json
import time
from typing import Optional, List, Dict, Any, Callable
from playwright.sync_api import Page, Request, Response, ConsoleMessage, WebSocket, Dialog
from common.log_utils import LogUtils

logger = LogUtils.get_logger(__name__)


class EventHelper:
    """事件助手"""
    
    def __init__(self, page: Page):
        """
        初始化事件助手
        
        Args:
            page: Playwright Page 对象
        """
        self._page = page
        self._requests: List[Request] = []
        self._responses: List[Response] = []
        self._console_messages: List[ConsoleMessage] = []
        self._page_errors: List[str] = []
        self._websocket_messages: List[Dict] = []
        self._event_listeners: Dict[str, List[Callable]] = {}
        
        # 设置默认事件监听
        self._setup_default_listeners()
    
    def _setup_default_listeners(self):
        """设置默认事件监听器"""
        # 请求监听
        self._page.on("request", self._handle_request)
        
        # 响应监听
        self._page.on("response", self._handle_response)
        
        # 控制台消息监听
        self._page.on("console", self._handle_console)
        
        # 页面错误监听
        self._page.on("pageerror", self._handle_page_error)
        
        # WebSocket 监听（如果可用）
        try:
            self._page.on("websocket", self._handle_websocket)
        except:
            pass  # 某些 Playwright 版本可能不支持
    
    # ========== 事件处理器 ==========
    def _handle_request(self, request: Request):
        """处理请求事件"""
        self._requests.append(request)
        
        # 记录请求信息
        request_info = {
            "url": request.url,
            "method": request.method,
            "headers": dict(request.headers),
            "resource_type": request.resource_type,
            "timestamp": time.time()
        }
        
        # 附加到 Allure 报告（简化版本，避免敏感信息）
        safe_headers = {k: v for k, v in request_info["headers"].items() 
                       if k.lower() not in ["authorization", "cookie"]}
        
        allure.attach(
            json.dumps({
                "url": request_info["url"],
                "method": request_info["method"],
                "resource_type": request_info["resource_type"],
                "headers": safe_headers
            }, indent=2, ensure_ascii=False),
            name="请求信息",
            attachment_type=allure.attachment_type.JSON
        )
        
        # 调用自定义监听器
        self._call_event_listeners("request", request)
    
    def _handle_response(self, response: Response):
        """处理响应事件"""
        self._responses.append(response)
        
        # 记录响应信息
        response_info = {
            "url": response.url,
            "status": response.status,
            "status_text": response.status_text,
            "headers": dict(response.headers),
            "timestamp": time.time()
        }
        
        # 附加到 Allure 报告
        allure.attach(
            json.dumps({
                "url": response_info["url"],
                "status": response_info["status"],
                "status_text": response_info["status_text"],
                "headers": response_info["headers"]
            }, indent=2, ensure_ascii=False),
            name="响应信息",
            attachment_type=allure.attachment_type.JSON
        )
        
        # 调用自定义监听器
        self._call_event_listeners("response", response)
    
    def _handle_console(self, message: ConsoleMessage):
        """处理控制台消息"""
        self._console_messages.append(message)
        
        # 记录控制台消息
        console_info = {
            "type": message.type,
            "text": message.text,
            "args": [str(arg) for arg in message.args],
            "timestamp": time.time()
        }
        
        # 将错误和警告附加到 Allure 报告
        if message.type in ["error", "warning"]:
            allure.attach(
                json.dumps(console_info, indent=2, ensure_ascii=False),
                name=f"控制台 {message.type}",
                attachment_type=allure.attachment_type.JSON
            )
        
        # 调用自定义监听器
        self._call_event_listeners("console", message)
    
    def _handle_page_error(self, error):
        """处理页面错误"""
        error_str = str(error)
        self._page_errors.append(error_str)
        
        # 记录页面错误
        allure.attach(
            error_str,
            name="页面错误",
            attachment_type=allure.attachment_type.TEXT
        )
        
        # 调用自定义监听器
        self._call_event_listeners("pageerror", error)
    
    def _handle_websocket(self, websocket: WebSocket):
        """处理 WebSocket 事件"""
        # 监听 WebSocket 消息
        websocket.on("framereceived", lambda data: self._handle_websocket_message(websocket, data, "received"))
        websocket.on("framesent", lambda data: self._handle_websocket_message(websocket, data, "sent"))
        
        # 调用自定义监听器
        self._call_event_listeners("websocket", websocket)
    
    def _handle_websocket_message(self, websocket: WebSocket, data: Any, direction: str):
        """处理 WebSocket 消息"""
        message_info = {
            "url": websocket.url,
            "direction": direction,
            "data": str(data),
            "timestamp": time.time()
        }
        self._websocket_messages.append(message_info)
        
        # 调用自定义监听器
        self._call_event_listeners("websocket_message", message_info)
    
    def _call_event_listeners(self, event_type: str, data: Any):
        """调用事件监听器"""
        if event_type in self._event_listeners:
            for listener in self._event_listeners[event_type]:
                try:
                    listener(data)
                except Exception as e:
                    print(f"事件监听器执行失败 ({event_type}): {e}")
    
    # ========== 事件监听器管理 ==========
    def add_event_listener(self, event_type: str, listener: Callable):
        """
        添加事件监听器
        
        Args:
            event_type: 事件类型
            listener: 监听器函数
        """
        if event_type not in self._event_listeners:
            self._event_listeners[event_type] = []
        
        self._event_listeners[event_type].append(listener)
        
        # 如果事件类型是 Playwright 支持的原生事件，也添加到页面
        if event_type in ["request", "response", "console", "pageerror", "websocket"]:
            # 我们已经设置了默认监听器，会调用自定义监听器
            pass
    
    def remove_event_listener(self, event_type: str, listener: Callable):
        """
        移除事件监听器
        
        Args:
            event_type: 事件类型
            listener: 监听器函数
        """
        if event_type in self._event_listeners and listener in self._event_listeners[event_type]:
            self._event_listeners[event_type].remove(listener)
    
    def clear_event_listeners(self, event_type: Optional[str] = None):
        """
        清除事件监听器
        
        Args:
            event_type: 事件类型，如果为 None 则清除所有
        """
        if event_type is None:
            self._event_listeners.clear()
        elif event_type in self._event_listeners:
            self._event_listeners[event_type].clear()
    
    # ========== 请求和响应管理 ==========
    def get_requests(self) -> List[Request]:
        """
        获取所有请求
        
        Returns:
            List[Request]: 请求列表
        """
        return self._requests.copy()
    
    def get_responses(self) -> List[Response]:
        """
        获取所有响应
        
        Returns:
            List[Response]: 响应列表
        """
        return self._responses.copy()
    
    def get_request_by_url(self, url_pattern: str) -> List[Request]:
        """
        根据 URL 模式获取请求
        
        Args:
            url_pattern: URL 模式（字符串包含匹配）
            
        Returns:
            List[Request]: 匹配的请求列表
        """
        return [req for req in self._requests if url_pattern in req.url]
    
    def get_response_by_url(self, url_pattern: str) -> List[Response]:
        """
        根据 URL 模式获取响应
        
        Args:
            url_pattern: URL 模式（字符串包含匹配）
            
        Returns:
            List[Response]: 匹配的响应列表
        """
        return [res for res in self._responses if url_pattern in res.url]
    
    def get_request_response_pair(self, url_pattern: str) -> List[Dict[str, Any]]:
        """
        获取请求-响应对
        
        Args:
            url_pattern: URL 模式
            
        Returns:
            List[Dict]: 请求-响应对列表
        """
        pairs = []
        for request in self.get_request_by_url(url_pattern):
            # 查找对应的响应
            for response in self._responses:
                if response.request == request:
                    pairs.append({
                        "request": request,
                        "response": response,
                        "timestamp": time.time()
                    })
                    break
        
        return pairs
    
    def clear_requests_responses(self):
        """清除所有请求和响应记录"""
        self._requests.clear()
        self._responses.clear()
    
    # ========== 控制台消息管理 ==========
    def get_console_messages(self) -> List[ConsoleMessage]:
        """
        获取所有控制台消息
        
        Returns:
            List[ConsoleMessage]: 控制台消息列表
        """
        return self._console_messages.copy()
    
    def get_console_messages_by_type(self, message_type: str) -> List[ConsoleMessage]:
        """
        根据类型获取控制台消息
        
        Args:
            message_type: 消息类型（"log", "error", "warning", "info", "debug"）
            
        Returns:
            List[ConsoleMessage]: 匹配的控制台消息列表
        """
        return [msg for msg in self._console_messages if msg.type == message_type]
    
    def get_console_messages_containing(self, text: str) -> List[ConsoleMessage]:
        """
        获取包含指定文本的控制台消息
        
        Args:
            text: 要搜索的文本
            
        Returns:
            List[ConsoleMessage]: 匹配的控制台消息列表
        """
        return [msg for msg in self._console_messages if text in msg.text]
    
    def clear_console_messages(self):
        """清除所有控制台消息记录"""
        self._console_messages.clear()
    
    # ========== 页面错误管理 ==========
    def get_page_errors(self) -> List[str]:
        """
        获取所有页面错误
        
        Returns:
            List[str]: 页面错误列表
        """
        return self._page_errors.copy()
    
    def clear_page_errors(self):
        """清除所有页面错误记录"""
        self._page_errors.clear()
    
    # ========== WebSocket 消息管理 ==========
    def get_websocket_messages(self) -> List[Dict]:
        """
        获取所有 WebSocket 消息
        
        Returns:
            List[Dict]: WebSocket 消息列表
        """
        return self._websocket_messages.copy()
    
    def clear_websocket_messages(self):
        """清除所有 WebSocket 消息记录"""
        self._websocket_messages.clear()
    
    # ========== 事件等待 ==========
    def wait_for_event(self, event_type: str, predicate: Optional[Callable[[Any], bool]] = None,
                      timeout: int = 30000) -> Any:
        """
        等待特定事件
        
        Args:
            event_type: 事件类型
            predicate: 事件谓词函数，如果为 None 则等待第一个事件
            timeout: 超时时间（毫秒）
            
        Returns:
            Any: 事件数据
            
        Raises:
            TimeoutError: 等待超时
        """
        start_time = time.time()
        event_queue = []
        
        # 定义临时事件处理器
        def temp_handler(data):
            if predicate is None or predicate(data):
                event_queue.append(data)
        
        # 添加临时监听器
        self.add_event_listener(event_type, temp_handler)
        
        try:
            while time.time() - start_time < timeout / 1000:
                if event_queue:
                    return event_queue[0]
                time.sleep(0.1)  # 100ms 轮询
            
            raise TimeoutError(f"等待事件 {event_type} 超时 ({timeout}ms)")
        finally:
            # 移除临时监听器
            self.remove_event_listener(event_type, temp_handler)
    
    def wait_for_request(self, url_pattern: str, timeout: int = 30000) -> Request:
        """
        等待匹配 URL 模式的请求
        
        Args:
            url_pattern: URL 模式
            timeout: 超时时间（毫秒）
            
        Returns:
            Request: 请求对象
        """
        return self.wait_for_event(
            "request",
            lambda req: url_pattern in req.url,
            timeout
        )
    
    def wait_for_response(self, url_pattern: str, timeout: int = 30000) -> Response:
        """
        等待匹配 URL 模式的响应
        
        Args:
            url_pattern: URL 模式
            timeout: 超时时间（毫秒）
            
        Returns:
            Response: 响应对象
        """
        return self.wait_for_event(
            "response",
            lambda res: url_pattern in res.url,
            timeout
        )
    
    def wait_for_console_message(self, message_type: Optional[str] = None,
                                text_contains: Optional[str] = None,
                                timeout: int = 30000) -> ConsoleMessage:
        """
        等待控制台消息
        
        Args:
            message_type: 消息类型
            text_contains: 消息包含的文本
            timeout: 超时时间（毫秒）
            
        Returns:
            ConsoleMessage: 控制台消息对象
        """
        def predicate(message):
            if message_type and message.type != message_type:
                return False
            if text_contains and text_contains not in message.text:
                return False
            return True
        
        return self.wait_for_event("console", predicate, timeout)
    
    # ========== 断言方法 ==========
    def assert_no_console_errors(self):
        """
        断言没有控制台错误
        
        Raises:
            AssertionError: 如果有控制台错误
        """
        errors = self.get_console_messages_by_type("error")
        if errors:
            error_messages = [f"{msg.text}" for msg in errors]
            raise AssertionError(f"发现控制台错误: {error_messages}")
    
    def assert_no_page_errors(self):
        """
        断言没有页面错误
        
        Raises:
            AssertionError: 如果有页面错误
        """
        if self._page_errors:
            raise AssertionError(f"发现页面错误: {self._page_errors}")
    
    def assert_console_message(self, message_type: str, text_contains: str,
                              timeout: int = 5000):
        """
        断言控制台消息
        
        Args:
            message_type: 消息类型
            text_contains: 消息包含的文本
            timeout: 超时时间（毫秒）
            
        Raises:
            AssertionError: 如果没有匹配的控制台消息
        """
        try:
            self.wait_for_console_message(message_type, text_contains, timeout)
        except TimeoutError:
            raise AssertionError(
                f"在 {timeout}ms 内没有找到控制台消息: type={message_type}, contains={text_contains}"
            )
    
    def assert_request_made(self, url_pattern: str, timeout: int = 5000):
        """
        断言请求已发送
        
        Args:
            url_pattern: URL 模式
            timeout: 超时时间（毫秒）
            
        Raises:
            AssertionError: 如果没有匹配的请求
        """
        try:
            self.wait_for_request(url_pattern, timeout)
        except TimeoutError:
            raise AssertionError(f"在 {timeout}ms 内没有找到请求: {url_pattern}")
    
    def assert_response_received(self, url_pattern: str, expected_status: Optional[int] = None,
                                timeout: int = 5000):
        """
        断言响应已接收
        
        Args:
            url_pattern: URL 模式
            expected_status: 期望的状态码
            timeout: 超时时间（毫秒）
            
        Raises:
            AssertionError: 如果没有匹配的响应
        """
        try:
            response = self.wait_for_response(url_pattern, timeout)
            
            if expected_status is not None and response.status != expected_status:
                raise AssertionError(
                    f"响应状态码不匹配。期望: {expected_status}，实际: {response.status}"
                )
        except TimeoutError:
            raise AssertionError(f"在 {timeout}ms 内没有找到响应: {url_pattern}")
    
    # ========== 性能监控 ==========
    def get_performance_metrics(self) -> Dict[str, Any]:
        """
        获取性能指标
        
        Returns:
            Dict[str, Any]: 性能指标字典
        """
        try:
            # 使用 Performance Timing API
            script = """
                const perf = window.performance || window.webkitPerformance || window.msPerformance || window.mozPerformance;
                if (perf && perf.timing) {
                    const timing = perf.timing;
                    return {
                        navigationStart: timing.navigationStart,
                        unloadEventStart: timing.unloadEventStart,
                        unloadEventEnd: timing.unloadEventEnd,
                        redirectStart: timing.redirectStart,
                        redirectEnd: timing.redirectEnd,
                        fetchStart: timing.fetchStart,
                        domainLookupStart: timing.domainLookupStart,
                        domainLookupEnd: timing.domainLookupEnd,
                        connectStart: timing.connectStart,
                        connectEnd: timing.connectEnd,
                        secureConnectionStart: timing.secureConnectionStart,
                        requestStart: timing.requestStart,
                        responseStart: timing.responseStart,
                        responseEnd: timing.responseEnd,
                        domLoading: timing.domLoading,
                        domInteractive: timing.domInteractive,
                        domContentLoadedEventStart: timing.domContentLoadedEventStart,
                        domContentLoadedEventEnd: timing.domContentLoadedEventEnd,
                        domComplete: timing.domComplete,
                        loadEventStart: timing.loadEventStart,
                        loadEventEnd: timing.loadEventEnd
                    };
                }
                return {};
            """
            
            timing_data = self._page.evaluate(script)
            
            # 计算关键指标
            metrics = {}
            if timing_data:
                nav_start = timing_data.get("navigationStart", 0)
                
                # 页面加载时间
                if timing_data.get("loadEventEnd"):
                    metrics["pageLoadTime"] = timing_data["loadEventEnd"] - nav_start
                
                # DOM 交互时间
                if timing_data.get("domInteractive"):
                    metrics["domInteractiveTime"] = timing_data["domInteractive"] - nav_start
                
                # DOM 完成时间
                if timing_data.get("domComplete"):
                    metrics["domCompleteTime"] = timing_data["domComplete"] - nav_start
                
                # 首次内容绘制 (模拟)
                if timing_data.get("responseStart"):
                    metrics["firstContentfulPaint"] = timing_data["responseStart"] - nav_start
                
                # 网络指标
                if timing_data.get("responseEnd") and timing_data.get("requestStart"):
                    metrics["serverResponseTime"] = timing_data["responseEnd"] - timing_data["requestStart"]
            
            return metrics
            
        except Exception as e:
            print(f"获取性能指标失败: {e}")
            return {}
    
    # ========== 清理 ==========
    def reset(self):
        """重置所有事件记录"""
        self.clear_requests_responses()
        self.clear_console_messages()
        self.clear_page_errors()
        self.clear_websocket_messages()
        self.clear_event_listeners()
        
        # 重新设置默认监听器
        self._setup_default_listeners()
        
        with allure.step("重置事件助手"):
            pass
    
    def remove_all_listeners(self):
        """移除所有事件监听器"""
        # 移除页面监听器
        self._page.remove_listener("request", self._handle_request)
        self._page.remove_listener("response", self._handle_response)
        self._page.remove_listener("console", self._handle_console)
        self._page.remove_listener("pageerror", self._handle_page_error)
        
        # 清除自定义监听器
        self.clear_event_listeners()
        
        with allure.step("移除所有事件监听器"):
            pass