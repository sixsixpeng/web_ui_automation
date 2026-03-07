# -*- coding: UTF-8 -*-
"""
pytest 配置文件
定义全局夹具和测试钩子
"""

import os
import pytest
import allure
from pathlib import Path
from typing import Generator, Optional

from playwright.sync_api import Page

from config.config_loader import config
from core.browser import browser_manager
from core.api_client import APIClient
from common.log_utils import LogUtils
from common.allure_utils import allure_utils


# 设置环境变量
os.environ["TEST_ENV"] = os.getenv("TEST_ENV", "dev")


@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """
    测试环境初始化（会话级别）
    """
    # 初始化日志系统
    LogUtils.setup_logging()
    logger = LogUtils.get_logger(__name__)
    
    logger.info("=" * 60)
    logger.info("开始测试执行")
    logger.info(f"测试环境: {config.get('env')}")
    logger.info(f"基础URL: {config.get_base_url()}")
    logger.info(f"API基础URL: {config.get_api_base_url()}")
    logger.info(f"浏览器类型: {config.get('browser_type')}")
    logger.info("=" * 60)
    
    # 确保必要的目录存在
    required_dirs = [
        config.get("log_dir"),
        config.get("screenshot_dir"),
        config.get("report_dir"),
        config.get("playwright_cache_dir"),
        config.get("data_dir")
    ]
    
    for dir_path in required_dirs:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
    
    yield
    
    # 测试会话结束后的清理工作
    logger.info("=" * 60)
    logger.info("测试执行结束")
    logger.info("=" * 60)


@pytest.fixture(scope="session")
def browser() -> Generator:
    """
    浏览器会话夹具（会话级别）
    """
    logger = LogUtils.get_logger("browser_fixture")
    
    try:
        logger.info("启动浏览器会话")
        browser_manager.start_browser()
        
        yield browser_manager
        
    finally:
        logger.info("关闭浏览器会话")
        browser_manager.close_browser()


@pytest.fixture(scope="function")
def page(browser) -> Generator[Page, None, None]:
    """
    页面夹具（函数级别）
    
    Args:
        browser: 浏览器会话夹具
    """
    logger = LogUtils.get_logger("page_fixture")
    test_page = None
    
    try:
        logger.info("创建新页面")
        test_page = browser_manager.new_page()
        
        # 设置视口大小
        viewport = config.get("viewport", {"width": 1920, "height": 1080})
        test_page.set_viewport_size(viewport)
        
        # 设置超时时间
        timeout = config.get("timeout", 30000)
        test_page.set_default_timeout(timeout)
        test_page.set_default_navigation_timeout(timeout)
        
        # 添加 Allure 步骤
        with allure.step("初始化浏览器页面"):
            allure.attach(
                f"视口大小: {viewport}\n超时时间: {timeout}ms",
                name="页面配置",
                attachment_type=allure.attachment_type.TEXT
            )
        
        yield test_page
        
    finally:
        if test_page:
            logger.info("关闭页面")
            test_page.close()


@pytest.fixture(scope="session")
def api_client() -> APIClient:
    """
    API 客户端夹具（会话级别）
    """
    logger = LogUtils.get_logger("api_client_fixture")
    logger.info("初始化 API 客户端")
    
    client = APIClient()
    
    # 设置认证信息（从配置读取）
    username = config.get("username")
    password = config.get("password")
    
    if username and password:
        logger.info(f"设置基本认证: {username}")
        client.set_basic_auth(username, password)
    
    return client


@pytest.fixture(scope="function")
def login_page(page):
    """
    登录页面夹具（函数级别）
    
    Args:
        page: 页面夹具
    """
    from page.login_page import LoginPage
    return LoginPage(page)


@pytest.fixture(scope="function")
def auth_api():
    """
    认证 API 夹具（函数级别）
    """
    from api.auth_api import AuthAPI
    return AuthAPI()


@pytest.fixture(scope="function")
def user_api():
    """
    用户 API 夹具（函数级别）
    """
    from api.user_api import UserAPI
    return UserAPI()


@pytest.fixture(scope="function", autouse=True)
def log_test_info(request):
    """
    记录测试信息（自动使用）
    """
    logger = LogUtils.get_logger("test_info")
    
    # 获取测试信息
    test_name = request.node.name
    test_module = request.node.module.__name__ if request.node.module else "未知模块"
    
    # 记录测试开始
    LogUtils.log_test_start(test_name, test_module)
    
    # 添加 Allure 标签
    allure.dynamic.title(test_name)
    allure.dynamic.description(f"测试模块: {test_module}")
    
    # 获取测试标记
    markers = [marker.name for marker in request.node.own_markers]
    if markers:
        allure.dynamic.tag(*markers)
        logger.info(f"测试标记: {', '.join(markers)}")
    
    yield
    
    # 记录测试结束
    LogUtils.log_test_end(test_name, test_module)


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """
    处理测试报告，添加失败截图
    """
    outcome = yield
    report = outcome.get_result()
    
    # 只在测试失败时执行
    if report.when == "call" and report.failed:
        logger = LogUtils.get_logger("failure_handler")
        logger.error(f"测试失败: {item.name}")
        
        # 尝试获取页面对象并截图
        try:
            # 查找页面夹具
            page_fixture = None
            for fixture_name in item.fixturenames:
                if "page" in fixture_name:
                    try:
                        page_fixture = item.funcargs.get(fixture_name)
                        if page_fixture:
                            break
                    except:
                        continue
            
            if page_fixture:
                # 截取失败截图
                screenshot_name = f"failure_{item.name}_{report.when}"
                allure_utils.attach_screenshot(page_fixture, screenshot_name)
                
                # 附加页面源代码
                allure_utils.attach_page_source(page_fixture, f"page_source_{item.name}")
                
                logger.info(f"已添加失败截图: {screenshot_name}")
        except Exception as e:
            logger.warning(f"添加失败截图时出错: {str(e)}")
        
        # 附加测试日志到 Allure
        LogUtils.attach_log_to_allure()


@pytest.fixture(scope="function")
def cleanup_test_data():
    """
    测试数据清理夹具
    """
    test_data = []
    
    def add_cleanup(data_id: str, cleanup_func):
        """
        添加清理函数
        
        Args:
            data_id: 数据ID
            cleanup_func: 清理函数
        """
        test_data.append((data_id, cleanup_func))
    
    yield add_cleanup
    
    # 测试结束后执行清理
    logger = LogUtils.get_logger("cleanup")
    for data_id, cleanup_func in test_data:
        try:
            logger.info(f"清理测试数据: {data_id}")
            cleanup_func()
        except Exception as e:
            logger.warning(f"清理数据 {data_id} 时出错: {str(e)}")


@pytest.fixture(scope="function")
def random_user_data():
    """
    生成随机用户数据夹具
    """
    from common.data_generator import data_generator
    return data_generator.user_data()


@pytest.fixture(scope="function")
def random_product_data():
    """
    生成随机产品数据夹具
    """
    from common.data_generator import data_generator
    return data_generator.product_data()


# 命令行选项
def pytest_addoption(parser):
    """添加命令行选项"""
    parser.addoption(
        "--env",
        action="store",
        default="dev",
        help="测试环境: dev, staging, prod"
    )
    parser.addoption(
        "--browser-type",
        action="store",
        default="chromium",
        help="浏览器类型: chromium, firefox, webkit"
    )
    parser.addoption(
        "--headless",
        action="store_true",
        default=False,
        help="是否使用无头模式"
    )


@pytest.fixture(scope="session", autouse=True)
def configure_environment(request):
    """
    根据命令行选项配置环境
    """
    # 设置环境变量
    env = request.config.getoption("--env")
    os.environ["TEST_ENV"] = env
    
    # 可以在这里更新配置，但注意 config 已经加载
    # 更好的做法是在测试开始前重新加载配置
    logger = LogUtils.get_logger("environment")
    logger.info(f"命令行指定环境: {env}")
    
    browser_type = request.config.getoption("--browser-type")
    if browser_type:
        # 更新配置（注意：这不会影响已经加载的配置）
        logger.info(f"命令行指定浏览器: {browser_type}")
    
    headless = request.config.getoption("--headless")
    if headless:
        logger.info("使用无头模式")