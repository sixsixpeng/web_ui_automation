# -*- coding: UTF-8 -*-
"""
Allure 报告工具
封装 Allure 相关功能，提供统一的报告附件添加接口
"""

import allure
import json
import time
from pathlib import Path
from typing import Any, Dict, Optional


class AllureUtils:
    """Allure 报告工具类"""
    
    @staticmethod
    def attach_screenshot(page, name: str = None):
        """
        附加页面截图到 Allure 报告
        
        Args:
            page: Playwright Page 对象
            name: 截图名称
        """
        if name is None:
            name = f"screenshot_{int(time.time())}"
        
        # 从配置获取截图目录
        from config.config_loader import config
        screenshot_dir = config.get("screenshot_dir", "screenshot")
        
        # 确保截图目录存在
        screenshot_path = Path(screenshot_dir) / f"{name}.png"
        screenshot_path.parent.mkdir(parents=True, exist_ok=True)
        
        page.screenshot(path=str(screenshot_path))
        
        allure.attach.file(
            str(screenshot_path),
            name=name,
            attachment_type=allure.attachment_type.PNG
        )
    
    @staticmethod
    def attach_page_source(page, name: str = "page_source"):
        """
        附加页面源代码到 Allure 报告
        
        Args:
            page: Playwright Page 对象
            name: 附件名称
        """
        page_source = page.content()
        allure.attach(
            page_source,
            name=name,
            attachment_type=allure.attachment_type.HTML
        )
    
    @staticmethod
    def attach_text(text: str, name: str = "text_attachment"):
        """
        附加文本到 Allure 报告
        
        Args:
            text: 文本内容
            name: 附件名称
        """
        allure.attach(
            text,
            name=name,
            attachment_type=allure.attachment_type.TEXT
        )
    
    @staticmethod
    def attach_json(data: Dict[str, Any], name: str = "json_attachment"):
        """
        附加 JSON 数据到 Allure 报告
        
        Args:
            data: JSON 数据
            name: 附件名称
        """
        json_str = json.dumps(data, indent=2, ensure_ascii=False)
        allure.attach(
            json_str,
            name=name,
            attachment_type=allure.attachment_type.JSON
        )
    
    @staticmethod
    def attach_file(file_path: str, name: str = None):
        """
        附加文件到 Allure 报告
        
        Args:
            file_path: 文件路径
            name: 附件名称，如果为 None 则使用文件名
        """
        if name is None:
            name = Path(file_path).name
        
        allure.attach.file(
            file_path,
            name=name,
            attachment_type=allure.attachment_type.from_file_path(file_path)
        )
    
    @staticmethod
    def step(step_name: str):
        """
        Allure 步骤装饰器
        
        Args:
            step_name: 步骤名称
        """
        return allure.step(step_name)
    
    @staticmethod
    def create_step(step_name: str, step_func):
        """
        创建 Allure 步骤
        
        Args:
            step_name: 步骤名称
            step_func: 步骤函数
        """
        with allure.step(step_name):
            return step_func()
    
    @staticmethod
    def add_description(description: str, description_type: str = "text"):
        """
        添加测试描述
        
        Args:
            description: 描述内容
            description_type: 描述类型，支持 'text', 'html', 'markdown'
        """
        if description_type == "html":
            allure.description_html(description)
        elif description_type == "markdown":
            allure.description_markdown(description)
        else:
            allure.description(description)
    
    @staticmethod
    def add_link(url: str, name: str = None, link_type: str = "link"):
        """
        添加链接
        
        Args:
            url: 链接地址
            name: 链接名称
            link_type: 链接类型，支持 'link', 'issue', 'test_case'
        """
        if link_type == "issue":
            allure.issue(url, name)
        elif link_type == "test_case":
            allure.testcase(url, name)
        else:
            allure.link(url, name)
    
    @staticmethod
    def add_severity(severity: str):
        """
        添加严重级别
        
        Args:
            severity: 严重级别，支持 'blocker', 'critical', 'normal', 'minor', 'trivial'
        """
        allure.severity(severity)
    
    @staticmethod
    def add_epic(epic: str):
        """
        添加史诗
        
        Args:
            epic: 史诗名称
        """
        allure.epic(epic)
    
    @staticmethod
    def add_feature(feature: str):
        """
        添加特性
        
        Args:
            feature: 特性名称
        """
        allure.feature(feature)
    
    @staticmethod
    def add_story(story: str):
        """
        添加用户故事
        
        Args:
            story: 用户故事名称
        """
        allure.story(story)
    
    @staticmethod
    def add_tag(tag: str):
        """
        添加标签
        
        Args:
            tag: 标签名称
        """
        allure.tag(tag)
    
    @staticmethod
    def attach_network_logs(page, name: str = "network_logs"):
        """
        附加网络请求日志到 Allure 报告
        
        Args:
            page: Playwright Page 对象
            name: 附件名称
        """
        # 获取页面网络请求（需要先启用网络跟踪）
        requests = []
        for request in page.context._requests:
            requests.append({
                "url": request.url,
                "method": request.method,
                "status": request.response().status if request.response() else None,
                "timing": request.timing
            })
        
        AllureUtils.attach_json(requests, name)
    
    @staticmethod
    def attach_console_logs(page, name: str = "console_logs"):
        """
        附加控制台日志到 Allure 报告
        
        Args:
            page: Playwright Page 对象
            name: 附件名称
        """
        # 监听控制台消息（需要在页面初始化时设置）
        console_messages = []
        
        def on_console_message(msg):
            console_messages.append({
                "type": msg.type,
                "text": msg.text,
                "timestamp": time.time()
            })
        
        page.on("console", on_console_message)
        
        # 返回一个函数，用于在测试结束时获取并附加日志
        def attach_logs():
            if console_messages:
                AllureUtils.attach_json(console_messages, name)
        
        return attach_logs
    
    @staticmethod
    def attach_performance_metrics(page, name: str = "performance_metrics"):
        """
        附加性能指标到 Allure 报告
        
        Args:
            page: Playwright Page 对象
            name: 附件名称
        """
        # 获取性能指标（需要先导航到页面）
        metrics = {
            "timestamp": time.time(),
            "url": page.url,
            "title": page.title(),
            "viewport_size": page.viewport_size,
            "evaluate_metrics": page.evaluate("JSON.stringify(window.performance.timing)")
        }
        
        AllureUtils.attach_json(metrics, name)


# 创建全局 Allure 工具实例
allure_utils = AllureUtils()