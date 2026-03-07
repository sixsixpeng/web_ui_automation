# -*- coding: UTF-8 -*-
"""
登录功能 UI 自动化测试用例
"""

import pytest
import allure
from common.file_utils import file_utils
from common.log_utils import LogUtils


@allure.epic("用户认证")
@allure.feature("登录功能")
@pytest.mark.ui
class TestLogin:
    """登录测试类"""
    
    @pytest.fixture(autouse=True)
    def setup(self, login_page):
        """
        测试初始化
        
        Args:
            login_page: 登录页面夹具
        """
        self.login_page = login_page
        self.logger = LogUtils.get_logger(__name__)
        
        # 加载测试数据
        self.test_data = file_utils.load_test_data(
            file_utils.config.get("data_dir"),
            "login"
        )
    
    @allure.story("成功登录")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.tag("ui", "smoke", "regression")
    def test_valid_login(self):
        """
        测试有效用户名和密码登录
        """
        test_case = self.test_data.get("test_cases", {}).get("valid_login", {})
        username = test_case.get("username", "test_user")
        password = test_case.get("password", "test_password")
        
        with allure.step("执行登录操作"):
            self.login_page.login(username, password)
        
        with allure.step("验证登录成功"):
            # 等待登录成功（页面跳转或显示成功消息）
            try:
                self.login_page.wait_for_login_success()
                
                # 验证 URL 包含 dashboard 或首页
                current_url = self.login_page.page.url
                assert "dashboard" in current_url or "home" in current_url, \
                    f"登录后未跳转到正确页面，当前URL: {current_url}"
                
                self.logger.info("登录成功，页面跳转正确")
                
            except Exception as e:
                # 如果页面未跳转，检查是否有成功消息
                success_message = self.login_page.get_success_message()
                assert success_message is not None, "登录失败，既未跳转也未显示成功消息"
                self.logger.info(f"登录成功，显示消息: {success_message}")
    
    @allure.story("失败登录")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.tag("ui", "regression")
    @pytest.mark.parametrize("test_case_key", [
        "invalid_username",
        "invalid_password",
        "empty_username",
        "empty_password"
    ])
    def test_invalid_login(self, test_case_key):
        """
        测试无效登录场景
        
        Args:
            test_case_key: 测试用例键名
        """
        test_cases = self.test_data.get("test_cases", {})
        test_case = test_cases.get(test_case_key, {})
        
        username = test_case.get("username", "")
        password = test_case.get("password", "")
        expected_error = test_case.get("error_message", "用户名或密码错误")
        
        with allure.step(f"执行登录操作（{test_case_key}）"):
            self.login_page.login(username, password)
        
        with allure.step("验证登录失败"):
            # 等待错误消息出现
            self.login_page.wait_for_login_error()
            
            # 获取错误消息
            error_message = self.login_page.get_error_message()
            
            # 验证错误消息
            assert error_message is not None, "未显示错误消息"
            assert expected_error in error_message, \
                f"错误消息不匹配，预期包含: {expected_error}，实际: {error_message}"
            
            self.logger.info(f"登录失败验证成功，错误消息: {error_message}")
    
    @allure.story("登录页面元素")
    @allure.severity(allure.severity_level.MINOR)
    @allure.tag("ui")
    def test_login_page_elements(self):
        """
        测试登录页面元素是否正常显示
        """
        with allure.step("导航到登录页面"):
            self.login_page.navigate_to_login()
        
        with allure.step("验证页面元素"):
            # 验证用户名输入框可见
            assert self.login_page.is_username_field_visible(), "用户名输入框不可见"
            
            # 验证密码输入框可见
            assert self.login_page.is_password_field_visible(), "密码输入框不可见"
            
            # 验证登录按钮可用
            assert self.login_page.is_login_button_enabled(), "登录按钮不可用"
            
            # 验证页面标题
            page_title = self.login_page.get_title()
            assert page_title, "页面标题为空"
            self.logger.info(f"页面标题: {page_title}")
            
            # 验证当前URL包含login
            current_url = self.login_page.get_current_url()
            assert "login" in current_url, f"当前URL不包含login: {current_url}"
    
    @allure.story("记住我功能")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.tag("ui", "regression")
    def test_remember_me(self):
        """
        测试记住我功能
        """
        test_case = self.test_data.get("test_cases", {}).get("valid_login", {})
        username = test_case.get("username", "test_user")
        password = test_case.get("password", "test_password")
        
        with allure.step("执行带记住我的登录"):
            self.login_page.login(username, password, remember_me=True)
        
        with allure.step("验证登录成功"):
            self.login_page.wait_for_login_success()
            
            # 这里可以添加验证记住我功能的逻辑
            # 例如：关闭浏览器重新打开，检查是否自动登录
            self.logger.info("记住我功能测试完成（需要后续验证）")
    
    @allure.story("密码显示/隐藏")
    @allure.severity(allure.severity_level.MINOR)
    @allure.tag("ui")
    def test_password_visibility(self):
        """
        测试密码显示/隐藏功能
        """
        with allure.step("导航到登录页面"):
            self.login_page.navigate_to_login()
        
        with allure.step("输入密码"):
            self.login_page.enter_password("test_password")
            
            # 验证密码输入框类型为password（默认隐藏）
            password_type = self.login_page.get_attribute(
                self.login_page.PASSWORD_INPUT, 
                "type"
            )
            assert password_type == "password", f"密码输入框类型不正确: {password_type}"
        
        # 注意：这里需要页面上有显示/隐藏密码的按钮才能继续测试
        # 如果有的话，可以添加点击按钮验证类型变化的测试
    
    @allure.story("登录失败重试")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.tag("ui", "security")
    @pytest.mark.flaky(reruns=3)
    def test_login_retry(self):
        """
        测试登录失败后的重试功能
        """
        with allure.step("连续尝试错误密码"):
            for i in range(3):
                self.logger.info(f"第 {i+1} 次尝试错误登录")
                
                self.login_page.navigate_to_login()
                self.login_page.enter_username("test_user")
                self.login_page.enter_password(f"wrong_password_{i}")
                self.login_page.click_login()
                
                # 验证错误消息
                error_message = self.login_page.get_error_message()
                assert error_message is not None, f"第 {i+1} 次尝试未显示错误消息"
        
        with allure.step("验证账户是否被锁定（如果支持）"):
            # 这里可以验证账户是否被锁定，或者显示账户锁定消息
            self.logger.info("登录重试测试完成")
    
    @allure.story("登录后跳转")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.tag("ui")
    def test_login_redirect(self):
        """
        测试登录后的页面跳转
        """
        test_case = self.test_data.get("test_cases", {}).get("valid_login", {})
        username = test_case.get("username", "test_user")
        password = test_case.get("password", "test_password")
        
        with allure.step("从其他页面跳转到登录页面"):
            # 先访问其他页面
            self.login_page.navigate("/products")
            # 然后访问登录页面
            self.login_page.navigate_to_login()
        
        with allure.step("执行登录"):
            self.login_page.login(username, password)
        
        with allure.step("验证跳转回原页面或默认页面"):
            current_url = self.login_page.get_current_url()
            
            # 根据业务逻辑验证跳转
            # 可能跳转到首页，也可能跳转回原页面
            assert "dashboard" in current_url or "products" in current_url, \
                f"登录后跳转页面不正确: {current_url}"
            
            self.logger.info(f"登录后正确跳转到: {current_url}")