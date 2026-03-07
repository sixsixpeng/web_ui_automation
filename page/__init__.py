# -*- coding: UTF-8 -*-
"""
页面对象模块 (page)

提供自动化测试框架的页面对象封装，遵循 POM（页面对象模型）设计模式：
- 元素定位器：集中管理页面元素的定位表达式，支持 CSS、XPath、文本等多种定位方式
- 页面操作：封装页面的业务操作方法，如登录、搜索、提交表单等
- 页面验证：提供页面状态的验证方法，如元素可见性、文本内容、URL 验证等
- 页面导航：封装页面间的跳转和导航逻辑

主要组件：
- login_page.py: 登录页面对象，封装登录页面的元素和操作
- 其他页面：按业务需求添加的页面对象（如 dashboard_page.py, user_profile_page.py 等）

页面对象设计原则：
1. 每个页面对应一个 Python 类，类名以 Page 结尾（如 LoginPage）
2. 页面元素定位器作为类属性，使用明确的命名（如 USERNAME_INPUT）
3. 页面操作方法作为类方法，方法名应描述业务操作（如 login(username, password)）
4. 所有页面对象继承 core.BasePage 类，复用通用页面操作方法
5. 页面对象不包含断言逻辑，只提供操作和状态查询方法
6. 页面对象应独立于测试用例，可被多个测试用例复用

使用方式：
```python
from page import LoginPage

# 通过夹具获取页面实例（推荐方式）
def test_login(login_page):
    # login_page 是通过 conftest.py 中定义的夹具提供的 LoginPage 实例
    login_page.login("test_user", "password123")
    assert login_page.is_logged_in()

# 手动创建页面实例
from core import browser_manager
browser_manager.start_browser()
page = browser_manager.new_page()
login_page = LoginPage(page)
login_page.navigate_to_login()
login_page.login("admin", "admin123")
```

页面对象示例（login_page.py 结构）：
```python
from core.base_page import BasePage

class LoginPage(BasePage):
    # 元素定位器
    USERNAME_INPUT = "#username"
    PASSWORD_INPUT = "#password"
    LOGIN_BUTTON = "#login-btn"
    ERROR_MESSAGE = ".error-message"
    
    def login(self, username, password):
        self.fill(self.USERNAME_INPUT, username)
        self.fill(self.PASSWORD_INPUT, password)
        self.click(self.LOGIN_BUTTON)
        self.wait_for_navigation()
    
    def is_error_displayed(self):
        return self.is_visible(self.ERROR_MESSAGE)
    
    def get_error_text(self):
        return self.get_text(self.ERROR_MESSAGE)
```

扩展指南：
1. 在 page/ 目录创建新页面文件，如 dashboard_page.py
2. 定义页面类并继承 BasePage
3. 添加元素定位器和业务方法
4. 在此文件中导入新页面类并添加到 __all__ 列表
"""

from .login_page import LoginPage

# 定义公开接口
__all__ = [
    "LoginPage",
]

# 未来扩展：在此处导入新页面类并添加到 __all__ 中