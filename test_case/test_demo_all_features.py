# -*- coding: UTF-8 -*-
"""
综合演示测试用例
展示框架所有高级功能，包括截图、视频录制和报告生成
"""

import os
import time
import pytest
import allure
from pathlib import Path
from typing import Dict, Any, List

from common.log_utils import LogUtils
from common.allure_utils import allure_utils
from common.data_generator import data_generator

# 导入所有核心模块功能
from core import (
    browser_manager, BrowserManager, BasePage, APIClient,
    BrowserException, APICallException, ElementNotFoundException,
    TimeoutException, ConfigException, FrameworkException,
    BrowserWrapper, PageWrapper, LocatorWrapper, WaitHelper, 
    AssertionHelper, DialogHandler, DownloadHelper, KeyboardMouseHelper,
    EventHelper, VideoRecorder, DebugHelper
)


@allure.epic("综合演示")
@allure.feature("框架所有功能展示")
@pytest.mark.ui
@pytest.mark.demo
@pytest.mark.smoke
class TestDemoAllFeatures:
    """综合演示测试类，展示框架所有高级功能"""
    
    @classmethod
    def setup_class(cls):
        """类级别初始化"""
        # 这些是类属性，但测试方法需要实例属性
        # 我们将在setup_method中初始化实例属性
        cls._logger = LogUtils.get_logger(__name__)
        cls._video_recorder = None
        cls._video_output_dir = "report/videos"
        
        cls._logger.info("开始综合演示测试")
        # 创建视频输出目录
        Path(cls._video_output_dir).mkdir(parents=True, exist_ok=True)
    
    @classmethod
    def teardown_class(cls):
        """类级别清理"""
        cls._logger.info("综合演示测试结束")
    
    def setup_method(self):
        """方法级别初始化"""
        # 将类属性复制到实例属性
        self.logger = self._logger
        self.video_recorder = self._video_recorder
        self.video_output_dir = self._video_output_dir
    
    @allure.story("基础功能演示")
    @allure.tag("demo", "basic", "browser")
    def test_browser_wrapper_demo(self, page):
        """
        演示浏览器包装器功能
        """
        self.logger.info("开始演示浏览器包装器功能")
        
        # 1. 使用浏览器包装器
        with allure.step("创建浏览器包装器"):
            browser_wrapper = BrowserWrapper(browser_manager.get_browser())
            allure.attach(
                f"浏览器包装器创建成功\n浏览器类型: {browser_wrapper.browser_type}",
                name="浏览器包装器信息",
                attachment_type=allure.attachment_type.TEXT
            )
        
        # 2. 创建持久化上下文
        with allure.step("创建持久化上下文"):
            context = browser_wrapper.create_persistent_context(
                storage_state_path="playwright_cache/storage_state.json"
            )
            self.logger.info("持久化上下文创建成功")
        
        # 3. 浏览器信息获取
        with allure.step("获取浏览器信息"):
            browser_info = browser_wrapper.get_browser_info()
            allure.attach(
                f"浏览器信息:\n{browser_info}",
                name="浏览器信息",
                attachment_type=allure.attachment_type.TEXT
            )
        
        self.logger.info("浏览器包装器功能演示完成")
        return True
    
    @allure.story("页面包装器演示")
    @allure.tag("demo", "page", "wrapper")
    def test_page_wrapper_demo(self, page):
        """
        演示页面包装器功能
        """
        self.logger.info("开始演示页面包装器功能")
        
        # 1. 创建页面包装器
        with allure.step("创建页面包装器"):
            page_wrapper = PageWrapper(page)
            allure_utils.attach_screenshot(page, "页面包装器创建")
        
        # 2. 导航到测试页面
        with allure.step("导航到测试页面"):
            page_wrapper.navigate("https://the-internet.herokuapp.com/")
            page_wrapper.wait_for_page_load()
            allure_utils.attach_screenshot(page, "测试页面加载")
        
        # 3. 处理对话框（示例）
        with allure.step("演示对话框处理能力"):
            dialog_handler = DialogHandler(page)
            # 注意：这里只是展示API，实际需要触发对话框
            self.logger.info("对话框处理器已创建，可用于处理alert/confirm/prompt")
        
        # 4. 视口操作
        with allure.step("视口操作演示"):
            original_size = page_wrapper.get_viewport_size()
            page_wrapper.set_viewport_size(800, 600)
            time.sleep(1)
            page_wrapper.set_viewport_size(original_size["width"], original_size["height"])
            allure_utils.attach_screenshot(page, "视口调整后")
        
        # 5. 页面信息获取
        with allure.step("获取页面信息"):
            page_info = {
                "URL": page_wrapper.page.url,
                "标题": page_wrapper.page.title(),
                "视口大小": page_wrapper.get_viewport_size()
            }
            allure.attach(
                str(page_info),
                name="页面信息",
                attachment_type=allure.attachment_type.TEXT
            )
        
        self.logger.info("页面包装器功能演示完成")
        return True
    
    @allure.story("元素定位器包装器演示")
    @allure.tag("demo", "locator", "element")
    def test_locator_wrapper_demo(self, page):
        """
        演示元素定位器包装器功能
        """
        self.logger.info("开始演示元素定位器包装器功能")
        
        # 1. 导航到测试页面
        with allure.step("导航到元素测试页面"):
            page.goto("https://the-internet.herokuapp.com/add_remove_elements/")
            page.wait_for_load_state("networkidle")
            allure_utils.attach_screenshot(page, "元素页面加载")
        
        # 2. 创建定位器包装器
        with allure.step("创建定位器包装器"):
            add_button = page.locator("button:has-text('Add Element')")
            locator_wrapper = LocatorWrapper(add_button, "添加元素按钮")
            self.logger.info(f"定位器包装器创建成功: {locator_wrapper.description}")
        
        # 3. 元素操作
        with allure.step("执行元素操作"):
            # 点击添加按钮
            locator_wrapper.click()
            time.sleep(0.5)
            
            # 再次点击
            locator_wrapper.click()
            time.sleep(0.5)
            
            # 验证添加的元素
            delete_buttons = page.locator(".added-manually")
            assert delete_buttons.count() == 2, f"应添加2个元素，实际添加了{delete_buttons.count()}个"
            
            allure_utils.attach_screenshot(page, "元素添加后")
        
        # 4. 元素状态检查
        with allure.step("检查元素状态"):
            delete_wrappers = []
            for i in range(delete_buttons.count()):
                delete_locator = page.locator(f".added-manually:nth-child({i+1})")
                wrapper = LocatorWrapper(delete_locator, f"删除按钮{i+1}")
                delete_wrappers.append(wrapper)
            
            for wrapper in delete_wrappers:
                assert wrapper.is_visible(), f"{wrapper.description} 应可见"
                assert wrapper.is_enabled(), f"{wrapper.description} 应启用"
        
        self.logger.info("元素定位器包装器功能演示完成")
        return True
    
    @allure.story("等待辅助演示")
    @allure.tag("demo", "wait", "helper")
    def test_wait_helper_demo(self, page):
        """
        演示等待辅助功能
        """
        self.logger.info("开始演示等待辅助功能")
        
        # 1. 创建等待辅助
        with allure.step("创建等待辅助"):
            wait_helper = WaitHelper(page)
            self.logger.info("等待辅助创建成功")
        
        # 2. 导航到动态加载页面
        with allure.step("导航到动态加载页面"):
            page.goto("https://the-internet.herokuapp.com/dynamic_loading")
            allure_utils.attach_screenshot(page, "动态加载页面")
        
        # 3. 测试各种等待条件
        with allure.step("测试各种等待条件"):
            # 点击示例1
            example1_link = page.locator("a[href='/dynamic_loading/1']")
            example1_link.click()
            
            # 等待元素可见
            wait_helper.wait_for_element_visible("#start button")
            
            # 点击开始按钮
            start_button = page.locator("#start button")
            start_button.click()
            
            # 等待元素隐藏（加载完成）
            wait_helper.wait_for_element_hidden("#loading")
            
            # 等待文本出现
            wait_helper.wait_for_text_present("#finish h4", "Hello World!")
            
            allure_utils.attach_screenshot(page, "动态加载完成")
        
        self.logger.info("等待辅助功能演示完成")
        return True
    
    @allure.story("断言辅助演示")
    @allure.tag("demo", "assertion", "helper")
    def test_assertion_helper_demo(self, page):
        """
        演示断言辅助功能
        """
        self.logger.info("开始演示断言辅助功能")
        
        # 1. 创建断言辅助
        with allure.step("创建断言辅助"):
            assertion_helper = AssertionHelper(page)
            self.logger.info("断言辅助创建成功")
        
        # 2. 导航到测试页面
        with allure.step("导航到测试页面"):
            page.goto("https://the-internet.herokuapp.com/")
            allure_utils.attach_screenshot(page, "断言测试页面")
        
        # 3. 执行各种断言
        with allure.step("执行各种断言测试"):
            # 断言页面标题
            assertion_helper.assert_title_contains("The Internet")
            
            # 断言元素存在
            assertion_helper.assert_element_present("h1")
            
            # 断言元素可见
            assertion_helper.assert_element_visible("h1")
            
            # 断言文本内容
            assertion_helper.assert_text_contains("h1", "Welcome to the-internet")
            
            # 断言URL
            assertion_helper.assert_url_contains("the-internet")
            
            # 断言元素数量
            assertion_helper.assert_element_count("li", 44)  # 页面有44个链接
            
            self.logger.info("所有断言测试通过")
        
        self.logger.info("断言辅助功能演示完成")
        return True
    
    @allure.story("键盘鼠标助手演示")
    @allure.tag("demo", "keyboard", "mouse")
    def test_keyboard_mouse_helper_demo(self, page):
        """
        演示键盘鼠标助手功能
        """
        self.logger.info("开始演示键盘鼠标助手功能")
        
        # 1. 创建键盘鼠标助手
        with allure.step("创建键盘鼠标助手"):
            km_helper = KeyboardMouseHelper(page)
            self.logger.info("键盘鼠标助手创建成功")
        
        # 2. 导航到测试页面
        with allure.step("导航到测试页面"):
            page.goto("https://the-internet.herokuapp.com/key_presses")
            allure_utils.attach_screenshot(page, "键盘测试页面")
        
        # 3. 键盘操作演示
        with allure.step("键盘操作演示"):
            # 聚焦输入框
            input_field = page.locator("#target")
            input_field.click()
            
            # 模拟按键
            km_helper.press("Tab")
            km_helper.press("Enter")
            km_helper.press("Escape")
            
            # 组合键
            km_helper.press_combination(["Control", "A"])
            km_helper.press_combination(["Control", "C"])
            km_helper.press_combination(["Control", "V"])
            
            allure_utils.attach_screenshot(page, "键盘操作后")
        
        # 4. 鼠标操作演示
        with allure.step("鼠标操作演示"):
            # 导航到另一个页面
            page.goto("https://the-internet.herokuapp.com/hovers")
            
            # 鼠标悬停
            avatar = page.locator(".figure:first-child img")
            km_helper.hover(avatar)
            time.sleep(1)
            
            allure_utils.attach_screenshot(page, "鼠标悬停效果")
        
        self.logger.info("键盘鼠标助手功能演示完成")
        return True
    
    @allure.story("事件助手演示")
    @allure.tag("demo", "event", "helper")
    def test_event_helper_demo(self, page):
        """
        演示事件助手功能
        """
        self.logger.info("开始演示事件助手功能")
        
        # 1. 创建事件助手
        with allure.step("创建事件助手"):
            event_helper = EventHelper(page)
            self.logger.info("事件助手创建成功")
        
        # 2. 设置事件监听器
        with allure.step("设置事件监听器"):
            events_captured = []
            
            def on_request_callback(request):
                events_captured.append({
                    "type": "request",
                    "url": request.url,
                    "method": request.method,
                    "time": time.time()
                })
            
            def on_response_callback(response):
                events_captured.append({
                    "type": "response",
                    "url": response.url,
                    "status": response.status,
                    "time": time.time()
                })
            
            # 注册事件监听器
            event_helper.add_event_listener("request", on_request_callback)
            event_helper.add_event_listener("response", on_response_callback)
        
        # 3. 触发事件
        with allure.step("触发事件并捕获"):
            page.goto("https://the-internet.herokuapp.com/")
            time.sleep(1)  # 等待事件捕获
            
            # 记录捕获的事件
            if events_captured:
                allure.attach(
                    f"捕获到 {len(events_captured)} 个事件:\n" + 
                    "\n".join([str(e) for e in events_captured[:5]]),  # 只显示前5个
                    name="捕获的事件",
                    attachment_type=allure.attachment_type.TEXT
                )
                self.logger.info(f"捕获到 {len(events_captured)} 个网络事件")
        
        self.logger.info("事件助手功能演示完成")
        return True
    
    @allure.story("视频录制演示")
    @allure.tag("demo", "video", "recording")
    def test_video_recorder_demo(self, page, request):
        """
        演示视频录制功能
        """
        self.logger.info("开始演示视频录制功能")
        
        # 1. 创建视频录制器
        with allure.step("创建视频录制器"):
            test_name = request.node.name
            
            # VideoRecorder需要BrowserContext而不是Page
            video_recorder = VideoRecorder(page.context)
            video_recorder.set_video_dir(self.video_output_dir)
            self.logger.info(f"视频录制器创建成功，输出路径: {self.video_output_dir}")
        
        # 2. 开始录制
        with allure.step("开始视频录制"):
            video_path = video_recorder.start_page_recording(page, test_name)
            self.logger.info(f"视频录制已开始，保存路径: {video_path}")
        
        # 3. 执行一些操作
        with allure.step("录制操作过程"):
            page.goto("https://the-internet.herokuapp.com/")
            time.sleep(1)
            
            # 点击几个链接
            page.locator("a[href='/abtest']").click()
            time.sleep(0.5)
            
            page.go_back()
            time.sleep(0.5)
            
            page.locator("a[href='/add_remove_elements/']").click()
            time.sleep(0.5)
            
            allure_utils.attach_screenshot(page, "录制过程中的截图")
        
        # 4. 停止录制
        with allure.step("停止视频录制"):
            video_path = video_recorder.stop_page_recording(page)
            self.logger.info(f"视频录制已停止，文件保存到: {video_path}")
            
            # 将视频附加到Allure报告
            if video_path and Path(video_path).exists():
                allure.attach.file(
                    video_path,
                    name="演示视频",
                    attachment_type=allure.attachment_type.WEBM
                )
                self.logger.info("视频已附加到Allure报告")
        
        self.logger.info("视频录制功能演示完成")
        return True
    
    @allure.story("调试助手演示")
    @allure.tag("demo", "debug", "helper")
    def test_debug_helper_demo(self, page):
        """
        演示调试助手功能
        """
        self.logger.info("开始演示调试助手功能")
        
        # 1. 创建调试助手
        with allure.step("创建调试助手"):
            debug_helper = DebugHelper(page)
            self.logger.info("调试助手创建成功")
        
        # 2. 演示调试功能
        with allure.step("演示调试功能"):
            page.goto("https://the-internet.herokuapp.com/")
            
            # 启用慢动作（仅用于演示）
            debug_helper.set_slow_mo(1000)  # 1秒延迟
            
            # 点击一个链接
            page.locator("a[href='/abtest']").click()
            time.sleep(1)
            
            # 禁用慢动作
            debug_helper.set_slow_mo(0)
            
            allure_utils.attach_screenshot(page, "调试功能演示")
        
        # 3. 性能分析演示
        with allure.step("性能分析演示"):
            # 开始追踪
            debug_helper.start_tracing()
            
            # 执行一些操作
            page.go_back()
            page.locator("a[href='/add_remove_elements/']").click()
            
            # 停止追踪并保存
            trace_path = debug_helper.stop_tracing("demo_trace")
            
            if trace_path and Path(trace_path).exists():
                allure.attach.file(
                    trace_path,
                    name="性能追踪文件",
                    attachment_type=allure.attachment_type.JSON
                )
                self.logger.info("性能追踪文件已保存")
        
        self.logger.info("调试助手功能演示完成")
        return True
    
    @allure.story("综合场景演示")
    @allure.tag("demo", "integration", "scenario")
    def test_integration_scenario_demo(self, page):
        """
        综合场景演示：模拟真实测试场景
        """
        self.logger.info("开始综合场景演示")
        
        # 创建所有辅助工具
        page_wrapper = PageWrapper(page)
        wait_helper = WaitHelper(page)
        assertion_helper = AssertionHelper(page)
        km_helper = KeyboardMouseHelper(page)
        
        # 场景：模拟用户注册流程
        with allure.step("场景1: 导航到测试应用"):
            page.goto("https://the-internet.herokuapp.com/login")
            wait_helper.wait_for_page_load()
            allure_utils.attach_screenshot(page, "登录页面")
        
        with allure.step("场景2: 使用定位器包装器操作表单"):
            # 创建定位器包装器
            username_input = LocatorWrapper(
                page.locator("#username"),
                "用户名输入框"
            )
            password_input = LocatorWrapper(
                page.locator("#password"),
                "密码输入框"
            )
            login_button = LocatorWrapper(
                page.locator("button[type='submit']"),
                "登录按钮"
            )
            
            # 填充表单
            username_input.fill("tomsmith")
            password_input.fill("SuperSecretPassword!")
            
            # 使用键盘助手按Tab键
            km_helper.press("Tab")
            km_helper.press("Enter")
            
            allure_utils.attach_screenshot(page, "表单填写后")
        
        with allure.step("场景3: 等待和断言"):
            # 等待登录成功
            wait_helper.wait_for_element_visible("#flash")
            
            # 断言登录成功
            assertion_helper.assert_text_contains("#flash", "You logged into a secure area!")
            
            allure_utils.attach_screenshot(page, "登录成功")
        
        with allure.step("场景4: 登出操作"):
            # 点击登出
            logout_button = LocatorWrapper(
                page.locator("a[href='/logout']"),
                "登出按钮"
            )
            logout_button.click()
            
            # 等待登出成功
            wait_helper.wait_for_element_visible("#flash")
            assertion_helper.assert_text_contains("#flash", "You logged out of the secure area!")
            
            allure_utils.attach_screenshot(page, "登出成功")
        
        self.logger.info("综合场景演示完成")
        return True
    
    @allure.story("数据驱动演示")
    @allure.tag("demo", "data-driven", "generator")
    @pytest.mark.parametrize("user_data", [
        data_generator.user_data(),
        data_generator.user_data(),
        data_generator.user_data()
    ])
    def test_data_driven_demo(self, page, user_data):
        """
        演示数据驱动测试
        """
        self.logger.info(f"开始数据驱动演示，用户数据: {user_data}")
        
        # 将用户数据附加到报告
        allure.attach(
            str(user_data),
            name="生成的用户数据",
            attachment_type=allure.attachment_type.TEXT
        )
        
        # 导航到测试页面
        page.goto("https://the-internet.herokuapp.com/")
        
        # 验证页面标题
        assertion_helper = AssertionHelper(page)
        assertion_helper.assert_title_contains("The Internet")
        
        # 使用生成的数据（这里只是演示，实际会用于表单填写等）
        self.logger.info(f"使用用户数据: {user_data['username']}, {user_data['email']}")
        
        allure_utils.attach_screenshot(page, f"数据驱动测试_{user_data['username']}")
        
        self.logger.info("数据驱动演示完成")
        return True
    
    @allure.story("报告增强演示")
    @allure.tag("demo", "report", "allure")
    def test_report_enhancement_demo(self, page):
        """
        演示报告增强功能
        """
        self.logger.info("开始报告增强演示")
        
        # 1. 添加多种类型的附件
        with allure.step("添加文本附件"):
            allure.attach(
                "这是测试执行的文本日志\n包含重要信息",
                name="文本日志",
                attachment_type=allure.attachment_type.TEXT
            )
        
        with allure.step("添加JSON附件"):
            test_data = {
                "test_name": "报告增强演示",
                "timestamp": time.time(),
                "status": "running",
                "metadata": {
                    "browser": "chromium",
                    "viewport": "1920x1080",
                    "environment": "demo"
                }
            }
            allure.attach(
                str(test_data),
                name="测试元数据",
                attachment_type=allure.attachment_type.JSON
            )
        
        with allure.step("添加截图附件"):
            page.goto("https://the-internet.herokuapp.com/")
            allure_utils.attach_screenshot(page, "报告增强截图")
        
        with allure.step("添加页面源码"):
            allure_utils.attach_page_source(page, "页面源码")
        
        # 2. 添加详细的步骤描述
        with allure.step("详细的操作步骤"):
            with allure.step("步骤1: 导航到特定页面"):
                page.locator("a[href='/abtest']").click()
                time.sleep(0.5)
            
            with allure.step("步骤2: 验证页面内容"):
                assertion_helper = AssertionHelper(page)
                assertion_helper.assert_element_present("h3")
            
            with allure.step("步骤3: 返回首页"):
                page.go_back()
                time.sleep(0.5)
        
        # 3. 添加测试描述和链接
        allure.dynamic.description("""
        这个测试演示了如何增强Allure报告，包括：
        1. 添加多种类型的附件（文本、JSON、截图、源码）
        2. 使用详细的步骤描述
        3. 添加测试元数据
        4. 生成丰富的测试报告
        """)
        
        self.logger.info("报告增强演示完成")
        return True


if __name__ == "__main__":
    """直接运行此测试（用于调试）"""
    import sys
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    # 运行测试
    pytest.main([
        "-v",
        "-s",
        "--alluredir=report/allure_raw",
        __file__
    ])