# -*- coding: UTF-8 -*-
"""
示例测试用例
演示成功、失败、跳过的测试用例，使用本地 Chrome 浏览器
"""

import pytest
import allure
from playwright.sync_api import sync_playwright
from common.log_utils import LogUtils


@allure.epic("示例")
@allure.feature("演示测试用例")
@pytest.mark.ui
class TestExample:
    """示例测试类"""
    
    @pytest.fixture(scope="class")
    def browser(self):
        """使用本地 Chrome 浏览器的夹具"""
        playwright = sync_playwright().start()
        # 使用本地 Chrome（通过 channel 参数）
        browser = playwright.chromium.launch(
            channel="chrome",  # 使用系统安装的 Chrome
            headless=False,    # 显示浏览器，便于观察
            slow_mo=500        # 慢动作，便于观察操作
        )
        yield browser
        browser.close()
        playwright.stop()
    
    @pytest.fixture
    def page(self, browser):
        """页面夹具"""
        page = browser.new_page()
        page.set_viewport_size({"width": 1920, "height": 1080})
        page.set_default_timeout(30000)
        yield page
        page.close()
    
    @allure.story("成功测试")
    @allure.tag("example", "success")
    def test_success_example(self, page):
        """
        成功测试示例：访问百度并验证标题
        """
        logger = LogUtils.get_logger(__name__)
        
        with allure.step("访问百度首页"):
            page.goto("https://www.baidu.com")
            logger.info("已访问百度首页")
        
        with allure.step("验证页面标题包含'百度'"):
            title = page.title()
            logger.info(f"页面标题: {title}")
            assert "百度" in title, f"标题不包含'百度'，实际标题: {title}"
        
        with allure.step("验证搜索框存在"):
            search_input = page.locator("#kw")
            assert search_input.is_visible(), "搜索框不可见"
            logger.info("搜索框存在且可见")
        
        with allure.step("在搜索框中输入关键词"):
            search_input.fill("自动化测试")
            logger.info("已输入搜索关键词")
        
        with allure.step("点击搜索按钮"):
            search_button = page.locator("#su")
            search_button.click()
            logger.info("已点击搜索按钮")
        
        with allure.step("等待搜索结果加载"):
            page.wait_for_selector(".result", state="visible", timeout=5000)
            logger.info("搜索结果已加载")
        
        logger.info("成功测试用例执行完成")
    
    @allure.story("失败测试")
    @allure.tag("example", "failure")
    def test_failure_example(self, page):
        """
        失败测试示例：故意断言失败
        """
        logger = LogUtils.get_logger(__name__)
        
        with allure.step("访问百度首页"):
            page.goto("https://www.baidu.com")
            logger.info("已访问百度首页")
        
        with allure.step("故意进行错误断言"):
            title = page.title()
            logger.info(f"页面标题: {title}")
            # 故意断言失败：百度标题不会包含"谷歌"
            assert "谷歌" in title, f"标题不包含'谷歌'，实际标题: {title}"
        
        # 这行代码不会执行，因为上面断言会失败
        logger.info("这行日志不会输出")
    
    @allure.story("跳过测试")
    @allure.tag("example", "skip")
    @pytest.mark.skip(reason="示例：跳过测试，不执行")
    def test_skip_example(self, page):
        """
        跳过测试示例：被标记为跳过的测试
        """
        logger = LogUtils.get_logger(__name__)
        logger.info("这个测试被跳过，不会执行")
        
        with allure.step("访问百度"):
            page.goto("https://www.baidu.com")
        
        # 这里不会执行
        assert False, "这个断言不会执行"
    
    @allure.story("条件跳过测试")
    @allure.tag("example", "conditional_skip")
    @pytest.mark.skipif(True, reason="条件为真，跳过测试")
    def test_conditional_skip_example(self):
        """
        条件跳过测试示例：根据条件跳过
        """
        logger = LogUtils.get_logger(__name__)
        logger.info("这个测试根据条件跳过")
        # 不会执行
    
    @allure.story("预期失败测试")
    @allure.tag("example", "xfail")
    @pytest.mark.xfail(reason="预期会失败，但测试继续执行")
    def test_expected_failure_example(self, page):
        """
        预期失败测试示例：预期会失败，但测试继续执行
        """
        logger = LogUtils.get_logger(__name__)
        
        with allure.step("访问百度首页"):
            page.goto("https://www.baidu.com")
            logger.info("已访问百度首页")
        
        with allure.step("进行预期会失败的断言"):
            # 这个断言预期会失败，但测试标记为 xfail，所以不算失败
            assert page.title() == "错误的标题", "标题不符合预期"
        
        logger.info("预期失败测试执行完成")
    
    @allure.story("参数化测试")
    @allure.tag("example", "parametrize")
    @pytest.mark.parametrize("search_keyword, expected_in_title", [
        ("自动化测试", "百度一下"),
        ("Playwright", "百度一下"),
        ("Python", "百度一下"),
    ])
    def test_parametrize_example(self, page, search_keyword, expected_in_title):
        """
        参数化测试示例：使用不同参数运行多次
        """
        logger = LogUtils.get_logger(__name__)
        
        with allure.step(f"搜索关键词: {search_keyword}"):
            page.goto("https://www.baidu.com")
            page.locator("#kw").fill(search_keyword)
            page.locator("#su").click()
            page.wait_for_selector(".result", state="visible", timeout=5000)
            
            title = page.title()
            logger.info(f"搜索 '{search_keyword}' 后标题: {title}")
            
            # 验证标题包含预期内容
            assert expected_in_title in title, f"标题不包含'{expected_in_title}'，实际标题: {title}"
        
        logger.info(f"参数化测试完成: {search_keyword}")


@allure.epic("示例")
@allure.feature("演示配置使用")
@pytest.mark.ui
class TestConfigExample:
    """配置使用示例"""
    
    @allure.story("使用自定义浏览器路径")
    @allure.tag("example", "custom_browser")
    def test_custom_chrome_path(self):
        """
        演示如何使用自定义 Chrome 浏览器路径
        """
        logger = LogUtils.get_logger(__name__)
        
        # 方法1：通过 channel 参数使用系统安装的 Chrome（推荐）
        logger.info("方法1: 使用 channel='chrome' 参数")
        with sync_playwright() as p:
            browser = p.chromium.launch(channel="chrome", headless=False)
            page = browser.new_page()
            page.goto("https://www.baidu.com")
            logger.info(f"使用 channel='chrome' 访问百度，标题: {page.title()}")
            page.close()
            browser.close()
        
        # 方法2：通过 executable_path 参数指定具体路径
        # 用户指定的路径是目录，需要找到 chrome.exe
        chrome_dir = r"C:\Program Files\Google\Chrome\Application"
        chrome_exe = f"{chrome_dir}\\chrome.exe"
        
        import os
        if os.path.exists(chrome_exe):
            logger.info(f"方法2: 使用 executable_path='{chrome_exe}'")
            with sync_playwright() as p:
                browser = p.chromium.launch(
                    executable_path=chrome_exe,
                    headless=False
                )
                page = browser.new_page()
                page.goto("https://www.baidu.com")
                logger.info(f"使用自定义路径访问百度，标题: {page.title()}")
                page.close()
                browser.close()
        else:
            logger.warning(f"Chrome 可执行文件不存在: {chrome_exe}")
            # 如果目录存在但找不到 chrome.exe，尝试查找
            if os.path.exists(chrome_dir):
                # 列出目录下的 .exe 文件
                exe_files = [f for f in os.listdir(chrome_dir) if f.lower().endswith('.exe')]
                if exe_files:
                    # 尝试找到 chrome.exe 或类似的可执行文件
                    for exe in exe_files:
                        if 'chrome' in exe.lower():
                            chrome_exe = os.path.join(chrome_dir, exe)
                            logger.info(f"尝试使用: {chrome_exe}")
                            with sync_playwright() as p:
                                browser = p.chromium.launch(
                                    executable_path=chrome_exe,
                                    headless=False
                                )
                                page = browser.new_page()
                                page.goto("https://www.baidu.com")
                                logger.info(f"使用找到的可执行文件访问百度，标题: {page.title()}")
                                page.close()
                                browser.close()
                            break
                    else:
                        logger.warning(f"在 {chrome_dir} 中未找到 Chrome 可执行文件")
                        # 跳过测试，因为这是示例，不影响整体
                        pytest.skip(f"Chrome 可执行文件不存在: {chrome_exe}")
                else:
                    logger.warning(f"在 {chrome_dir} 中未找到任何 .exe 文件")
                    pytest.skip(f"Chrome 目录中无 .exe 文件: {chrome_dir}")
            else:
                logger.warning(f"Chrome 目录不存在: {chrome_dir}")
                pytest.skip(f"Chrome 目录不存在: {chrome_dir}")
        
        logger.info("自定义浏览器路径示例完成")


if __name__ == "__main__":
    """直接运行示例（用于快速测试）"""
    import sys
    sys.exit(pytest.main(["-v", __file__]))