# Web UI 自动化测试框架

## 框架简介

本框架为基于Python栈自研的Web UI自动化测试框架，遵循分层设计与POM（页面对象模型）核心思想，具备高可扩展、高复用、易上手的特点，适配各类Web项目的UI自动化测试需求。框架基于Playwright为自动化核心，pytest为测试框架，整合数据驱动、日志记录、测试报告等核心能力，可快速实现用例编写、批量执行、结果分析全流程自动化。

## 快速入门

### 框架概述

这是一个基于 Python 的现代化 Web UI/API 混合自动化测试框架，集成了以下核心技术：

- **pytest**: 测试框架，支持参数化、标记、夹具、插件
- **Playwright**: 浏览器自动化，支持 Chromium/Firefox/WebKit
- **requests**: HTTP 客户端，用于 API 测试
- **Faker**: 测试数据生成
- **Allure**: 美观的测试报告
- **pytest-xdist**: 并行测试执行

### 环境准备

#### 1. 安装 Python
- Python 3.8 或更高版本
- 建议使用虚拟环境

#### 2. 安装依赖
```bash
# 安装 Python 依赖
pip install -r requirements.txt

# 安装 Playwright 浏览器
playwright install
```

#### 3. 安装 Allure（可选，用于生成报告）
- 下载地址: https://docs.qameta.io/allure/#_installing
- 或使用 Allure Docker 镜像

### 配置文件

#### 环境配置
编辑 `config/config.yaml` 文件，配置测试环境：

```yaml
dev:
  base_url: "https://dev.example.com"
  api_base_url: "https://dev-api.example.com"
  username: "test_user"
  password: "test_pass"
```

#### 切换环境
```bash
# 通过环境变量切换环境
export TEST_ENV=staging  # Linux/Mac
set TEST_ENV=staging     # Windows

# 或通过命令行参数
python run_tests.py ui --env=staging
```

### 运行测试

#### 简化模式（推荐）
脚本已简化为通过取消注释代码行来选择要运行的测试类型，无需记忆复杂命令。

1. **打开运行脚本**：
   ```bash
   # 编辑 run_tests.py 文件
   code run_tests.py
   ```

2. **选择测试类型**：
   - 在 `main()` 函数中找到 `# ===== 选择要运行的测试类型 =====` 部分
   - 取消注释要运行的测试类型行，注释其他行
   - 示例：要运行演示测试，确保以下行取消注释：
     ```python
     success = run_demo_tests(
         mark=mark,
         browser=browser_type,
         headless=headless,
         parallel=parallel
     )
     ```

3. **配置测试参数**：
   - 修改配置参数（浏览器类型、无头模式、并行执行等）：
     ```python
     browser_type = "chromium"      # 浏览器类型
     headless = False               # 无头模式
     parallel = False               # 并行执行
     env = "dev"                    # 测试环境
     mark = None                    # 测试标记
     ```

4. **运行测试**：
   ```bash
   # 直接运行脚本，无需参数
   python run_tests.py
   ```

#### 命令行模式（备选）
如需使用命令行参数，可切换回原版main函数（在run_tests.py中注释/取消注释相应代码）。

```bash
# 安装依赖
python run_tests.py install

# 运行所有 UI 测试
python run_tests.py ui

# 运行所有 API 测试
python run_tests.py api

# 运行所有测试
python run_tests.py all

# 运行冒烟测试
python run_tests.py smoke

# 运行回归测试
python run_tests.py regression

# 运行演示测试（展示所有功能）
python run_tests.py demo

# 并行执行测试
python run_tests.py ui --parallel

# 指定浏览器
python run_tests.py ui --browser-type=firefox --headless

# 生成报告
python run_tests.py report

# 打开报告
python run_tests.py open
```

#### 使用 pytest 直接运行
```bash
# 运行 UI 测试
pytest -m ui -v --alluredir=report/allure_raw

# 运行 API 测试
pytest -m api -v --alluredir=report/allure_raw

# 运行特定测试文件
pytest test_case/test_login.py -v

# 运行特定测试类
pytest test_case/test_login.py::TestLogin -v

# 运行特定测试方法
pytest test_case/test_login.py::TestLogin::test_valid_login -v

# 并行执行
pytest -n auto -v

# 失败重试
pytest --reruns 2 --reruns-delay 1 -v
```

#### 生成 Allure 报告
```bash
# 生成报告
allure generate report/allure_raw -o report/allure_html --clean

# 打开报告
allure open report/allure_html
```

### 编写测试用例

#### UI 测试用例示例
```python
import allure
import pytest
from page.login_page import LoginPage

@allure.epic("用户认证")
@allure.feature("登录功能")
class TestLogin:
    
    @pytest.fixture(autouse=True)
    def setup(self, login_page):
        self.login_page = login_page
    
    @allure.story("成功登录")
    @allure.tag("ui", "smoke")
    def test_valid_login(self):
        # 执行登录
        self.login_page.login("test_user", "test_password")
        
        # 验证登录成功
        self.login_page.wait_for_login_success()
        assert "dashboard" in self.login_page.page.url
```

#### API 测试用例示例
```python
import allure
import pytest
from common.data_generator import data_generator

@allure.epic("用户管理")
@allure.feature("用户API")
class TestUserAPI:
    
    @pytest.fixture(autouse=True)
    def setup(self, user_api):
        self.user_api = user_api
    
    @allure.story("创建用户")
    @allure.tag("api", "smoke")
    def test_create_user(self):
        # 生成随机用户数据
        user_data = data_generator.user_data()
        
        # 创建用户
        response = self.user_api.create_user(user_data)
        
        # 验证响应
        assert "id" in response
        assert response["username"] == user_data["username"]
```

#### 数据驱动测试示例
```python
import pytest
from common.file_utils import file_utils

# 从 YAML 文件加载测试数据
test_data = file_utils.load_test_data("test_data", "login")

@pytest.mark.parametrize("username,password,expected", [
    ("user1", "pass1", "success"),
    ("user2", "wrong", "failure"),
    ("", "pass3", "failure"),
])
def test_login_with_data(username, password, expected):
    # 测试逻辑
    pass
```

## 核心技术栈

| 模块类型     | 主流技术/工具                | 核心优势                                         | 需实现功能                             |
| ------------ | ---------------------------- | ------------------------------------------------ | -------------------------------------- |
| 核心自动化库 | Playwright                   | 无需驱动、支持多标签、跨浏览器                   | 浏览器操作、元素定位、页面交互核心能力 |
| 测试框架     | pytest                       | 插件丰富、语法简洁，支持失败重跑、参数化         | 用例管理、批量执行、断言、用例分层     |
| 配置文件管理 | PyYaml                       | 读写方便，支持多环境配置快速切换                 | 全局配置存储、读取，多环境适配         |
| 数据驱动     | pandas/openpyxl/yaml         | 轻量易维护，适配测试人员数据管理习惯             | 测试数据读写、多组数据驱动用例执行     |
| 日志记录     | Python logging + ANSI 转义码 | 支持彩色输出、自定义格式、模块化级别控制、按天分割 | 框架运行日志、用例执行日志记录与归档   |
| 测试报告     | Allure Report                | 美观直观，支持多维度统计、可集成CI/CD            | 测试结果可视化、失败原因展示、报告导出 |
| 驱动管理     | Playwright 内置              | 自动下载更新驱动，解决版本兼容问题               | 浏览器驱动自动管理、适配多浏览器       |
| 断言库       | pytest 内置断言              | 支持多断言，失败不中断用例执行                   | 用例检查点断言、复杂场景断言适配       |

## 框架目录架构及功能说明

框架采用分层设计，目录结构清晰、职责明确，各目录及文件核心功能如下（按底层到上层排序）：

### 根目录结构

```
web_ui_automation/
├── config/                 # 配置文件
│   ├── config.yaml        # 主配置文件
│   ├── api_endpoints.yaml # API 端点配置
│   └── config_loader.py   # 配置加载器
├── core/                  # 核心封装
│   ├── browser.py        # 浏览器管理
│   ├── base_page.py      # 页面基类
│   ├── api_client.py     # API 客户端
│   └── exception_handle.py # 异常处理
├── page/                  # 页面对象
│   ├── login_page.py     # 登录页面
│   └── ...               # 其他页面
├── api/                   # API 接口封装
│   ├── auth_api.py       # 认证 API
│   ├── user_api.py       # 用户 API
│   └── ...               # 其他 API
├── common/                # 公共工具
│   ├── data_generator.py # 数据生成器
│   ├── file_utils.py     # 文件操作
│   ├── log_utils.py      # 日志工具
│   └── allure_utils.py   # Allure 工具
├── test_case/            # 测试用例
│   ├── test_login.py     # 登录测试
│   ├── test_user_api.py  # 用户 API 测试
│   └── conftest.py       # pytest 夹具
├── test_data/            # 测试数据
│   ├── login_data.yaml   # 登录测试数据
│   └── user_data.yaml    # 用户测试数据
├── report/               # 测试报告（自动生成）
├── log/                  # 运行日志（自动生成）
├── screenshot/           # 失败截图（自动生成）
├── playwright_cache/     # Playwright 缓存（自动生成）
├── requirements.txt      # 项目依赖
├── pytest.ini           # pytest 配置
├── conftest.py          # 全局夹具
├── run_tests.py         # 测试运行脚本
└── README.md            # 项目说明
```

### 各目录详细说明

1.  **config/ - 基础配置层目录**
    - 作用：存储框架全局配置，实现配置与代码解耦，支持多环境快速切换
    - 核心文件：config.yaml、api_endpoints.yaml、config_loader.py
    - 功能：存储浏览器类型、测试环境地址、超时时间、账号密码等配置；日志格式、存储路径等配置定义；配置文件读取方法封装

2.  **core/ - 核心封装层目录**
    - 作用：封装框架底层核心能力，为上层提供通用调用接口，减少代码冗余
    - 核心文件：browser.py（驱动管理）、base_page.py（元素操作）、exception_handle.py（异常处理）
    - 功能：浏览器驱动初始化、关闭、切换等操作封装；通用元素操作（点击、输入、等待等）封装；全局异常捕获、统一处理逻辑封装；元素等待机制实现

3.  **page/ - 页面封装层（POM）目录**
    - 作用：遵循POM思想，封装各业务页面的元素与操作，实现页面与用例分离
    - 核心文件：按业务页面划分（如login_page.py、home_page.py）
    - 功能：页面元素定位表达式统一管理；页面专属业务操作（如登录、页面跳转）封装为方法；继承base_page.py，复用通用元素操作

4.  **api/ - API 接口封装目录**
    - 作用：封装业务系统的API接口，提供统一的调用接口
    - 核心文件：按业务模块划分（如auth_api.py、user_api.py）
    - 功能：API请求封装、响应处理、异常处理；与api_endpoints.yaml配置结合，实现端点管理

5.  **common/ - 公共工具目录**
    - 作用：封装跨页面、跨模块的通用工具方法，提升用例编写效率
    - 核心文件：data_generator.py（数据生成）、file_utils.py（文件操作）、log_utils.py（日志工具）、allure_utils.py（Allure工具）
    - 功能：测试数据生成、文件读写、日志记录、报告附件等通用功能

6.  **test_case/ - 测试用例目录**
    - 作用：管理所有Web UI自动化测试用例，实现用例分层、批量执行
    - 核心文件：conftest.py（pytest夹具）、按模块划分的用例文件（如test_login.py、test_user_api.py）
    - 功能：基于pytest编写业务用例，调用page层与common层方法；全局前置/后置操作（打开浏览器、登录、关闭浏览器）用夹具实现；用例分层（冒烟、回归）标记；用例断言实现

7.  **test_data/ - 测试数据目录**
    - 作用：存储测试用例所需数据，实现数据与用例分离，支持多组数据驱动
    - 核心文件：按模块划分的测试数据文件（如login_data.yaml、user_data.yaml）
    - 功能：存储用例所需的输入数据、预期结果；支持从yaml/Excel/csv读取测试数据；数据格式规整，适配用例参数化调用

8.  **report/ - 测试报告目录**
    - 作用：存储自动化测试执行后的测试报告，便于结果查看与分析
    - 功能：自动生成Allure测试报告；报告按执行时间命名，便于归档；支持报告手动导出、在线查看

9.  **log/ - 日志目录**
    - 作用：存储框架运行日志与用例执行日志，便于问题定位与排查
    - 功能：日志按天自动分割，自动归档；支持彩色控制台输出；可自定义日志格式；模块化日志级别控制；日志包含时间、级别、模块、具体信息等关键内容

10. **screenshot/ - 失败截图目录**
    - 作用：存储用例执行失败时的页面截图，辅助问题定位
    - 功能：用例执行失败时自动截取当前页面；截图按用例名称、执行时间命名；截图路径与测试报告关联，便于快速查看

11. **playwright_cache/ - Playwright缓存目录**
    - 作用：存储Playwright浏览器缓存、Cookie、页面会话状态等，用于复用缓存提升测试速度、保持会话持久化
    - 功能：配合core/browser.py中的浏览器驱动封装，指定缓存目录路径；支持多浏览器缓存隔离（可选）；无需手动操作，由框架自动生成管理

## 框架设计原则

1.  分层设计：页面与用例分离、业务与操作分离，降低维护成本，避免改一处动全身
2.  高可扩展：支持新增浏览器、定位方式、报告模板等，无需大幅修改原有代码
3.  高复用性：公共操作、通用方法统一封装，用例、页面均可直接调用，减少冗余
4.  易上手：测试人员只需关注业务用例编写，无需关注底层代码实现，降低使用门槛

## 常用功能

### 1. 浏览器操作
```python
# 页面导航
page.navigate("/login")

# 元素操作
page.click("#submit-button")
page.fill("#username", "test_user")
text = page.get_text(".welcome-message")

# 等待
page.wait_for_selector(".loading", state="hidden")
page.wait_for_page_load()

# 截图
page.screenshot("login_page")
```

### 2. API 操作
```python
# 发送请求
response = api_client.get("/api/v1/users")
response = api_client.post("/api/v1/users", json=user_data)

# 处理响应
users = response.json()
status_code = response.status_code
```

### 3. 测试数据生成
```python
from common.data_generator import data_generator

# 生成随机数据
user = data_generator.user_data()
product = data_generator.product_data()
email = data_generator.email()
phone = data_generator.phone_number()
```

### 4. 日志记录
```python
from common.log_utils import LogUtils

logger = LogUtils.get_logger(__name__)
logger.info("测试开始")
logger.error("测试失败", exc_info=True)
```

### 5. Allure 报告增强
```python
import allure

# 添加步骤
@allure.step("执行登录操作")
def login(username, password):
    pass

# 添加附件
allure.attach.file("screenshot.png", name="页面截图")
allure.attach.text("测试日志", name="执行日志")

# 添加描述
allure.description("这是一个重要的测试用例")
```

## 故障排除

### 常见问题

1. **导入错误**: 确保 Python 路径正确，所有依赖已安装
2. **浏览器启动失败**: 运行 `playwright install` 安装浏览器
3. **Allure 报告无法生成**: 检查 Allure 是否已正确安装
4. **API 测试失败**: 检查 `config.yaml` 中的 API 基础 URL
5. **元素找不到**: 增加等待时间或检查元素选择器

### 调试技巧

- 启用详细日志: `pytest -v -s`
- 禁用无头模式: `--headless=false`
- 增加超时时间: 在 `config.yaml` 中调整 `timeout`
- 查看浏览器: 禁用 `headless` 模式观察执行过程

## 扩展框架

### 添加新页面对象
1. 在 `page/` 目录创建新文件，如 `dashboard_page.py`
2. 继承 `BasePage` 类
3. 定义元素定位器和页面操作方法

### 添加新 API 接口
1. 在 `api/` 目录创建新文件，如 `order_api.py`
2. 继承或使用 `APIClient`
3. 在 `api_endpoints.yaml` 中定义端点

### 添加新测试用例
1. 在 `test_case/` 目录创建新文件
2. 使用现有的夹具和工具类
3. 添加适当的 Allure 注解和 pytest 标记

## 下一步

1. **运行示例测试**: `python run_tests.py smoke`
2. **查看报告**: `python run_tests.py open`
3. **编写自己的测试**: 参考示例测试用例
4. **配置 CI/CD**: 集成到 Jenkins/GitLab CI

## 获取帮助

- 查看详细文档: `README.md`
- 查看示例代码: `test_case/` 目录
- 查看配置说明: `config/config.yaml`
- 查看工具类文档: `common/` 目录中的文档字符串

## 模块详细说明

### config 模块
**概述**：配置管理模块，负责框架全局配置的加载、解析和多环境切换。

**主要组件**：
- **config_loader.py**: 配置加载器，读取YAML配置文件，根据环境变量提供配置项
- **config.yaml**: 主配置文件，包含日志、浏览器、环境等全局配置
- **api_endpoints.yaml**: API端点配置文件，定义各个API接口的路径

**导出接口**：
```python
from config import config, ConfigLoader

# 获取配置项
browser_type = config.get('browser.type')
base_url = config.get('base_url')

# 获取API端点
login_endpoint = config.get_endpoint('auth.login')
```

**常用方法**：
- `config.get(key, default=None)`: 获取配置项
- `config.get_endpoint(name)`: 获取API端点
- `config.get_current_env()`: 获取当前环境名称
- `config.set_env(env_name)`: 动态切换环境

### core 模块
**概述**：核心封装模块，提供浏览器管理、页面基类、API客户端和异常处理等基础能力，并新增高级封装类，提供更丰富的自动化操作功能。

**主要组件**：
- **browser.py**: 浏览器管理器，封装Playwright浏览器的启动、配置和管理，支持Chromium、Firefox、WebKit、Chrome、Edge
- **base_page.py**: 页面基类，提供通用的页面操作方法（点击、输入、等待等）
- **api_client.py**: API客户端，封装HTTP请求，提供统一的API调用接口
- **exception_handle.py**: 异常处理，定义框架自定义异常和异常处理逻辑
- **browser_wrapper.py**: 浏览器包装器，封装Browser对象，提供浏览器级别操作和持久化上下文支持
- **page_wrapper.py**: 页面包装器，扩展BasePage，提供对话框处理、下载管理、键盘鼠标事件等高级功能
- **locator_wrapper.py**: 元素定位器包装器，封装Locator对象，提供丰富的元素操作方法
- **wait_helper.py**: 等待辅助类，封装各种等待条件，提供灵活的等待机制
- **assertion_helper.py**: 断言辅助类，提供丰富的断言方法，基于Playwright的expect
- **dialog_handler.py**: 对话框处理器，专门处理浏览器对话框（alert, confirm, prompt）
- **download_helper.py**: 下载助手，处理文件下载，管理下载的文件
- **keyboard_mouse_helper.py**: 键盘鼠标助手，封装键盘和鼠标的交互操作
- **event_helper.py**: 事件助手，处理页面事件，如请求、响应、控制台消息、页面错误等
- **video_recorder.py**: 视频录制器，封装Playwright视频录制功能
- **debug_helper.py**: 调试助手，提供调试功能，如暂停、慢动作、追踪、性能分析等

**导出接口**：
```python
from core import (
    # 基础功能
    browser_manager,  # 浏览器管理器实例
    BrowserManager,   # 浏览器管理器类
    BasePage,         # 页面基类
    APIClient,        # API客户端类
    BrowserException, APICallException, ElementNotFoundException,
    TimeoutException, ConfigException, FrameworkException,
    
    # 高级封装
    BrowserWrapper,   # 浏览器包装器
    PageWrapper,      # 页面包装器
    LocatorWrapper,   # 元素定位器包装器
    WaitHelper,       # 等待辅助类
    AssertionHelper,  # 断言辅助类
    DialogHandler,    # 对话框处理器
    DownloadHelper,   # 下载助手
    KeyboardMouseHelper,  # 键盘鼠标助手
    EventHelper,      # 事件助手
    VideoRecorder,    # 视频录制器
    DebugHelper       # 调试助手
)

# 使用浏览器管理器
browser_manager.start_browser()
page = browser_manager.new_page()

# 使用页面包装器
page_wrapper = PageWrapper(page)
page_wrapper.handle_dialog(accept=True)  # 自动处理对话框

# 使用等待辅助
wait_helper = WaitHelper(page)
wait_helper.wait_for_element_visible("#submit")

# 使用断言辅助
assertion_helper = AssertionHelper(page)
assertion_helper.assert_text_contains(".message", "成功")

# 使用异常处理
try:
    element = page.locator("#submit")
except ElementNotFoundException as e:
    print(f"元素未找到: {e}")
```

**常用类和方法**：
- `browser_manager.start_browser(**kwargs)`: 启动浏览器
- `browser_manager.close_browser()`: 关闭浏览器
- `BasePage(page)`: 页面基类构造函数
- `BasePage.click(locator)`, `BasePage.fill(locator, text)`, `BasePage.wait_for_element(locator)`
- `APIClient(base_url)`: API客户端构造函数
- `APIClient.get(endpoint)`, `APIClient.post(endpoint, data)`, `APIClient.put(endpoint, data)`, `APIClient.delete(endpoint)`
- `BrowserWrapper(browser)`: 浏览器包装器构造函数
- `BrowserWrapper.create_persistent_context()`: 创建持久化上下文
- `PageWrapper(page)`: 页面包装器构造函数
- `PageWrapper.handle_dialog(accept=True, text=None)`: 处理对话框
- `PageWrapper.download_file(selector)`: 下载文件
- `LocatorWrapper(locator)`: 元素定位器包装器构造函数
- `LocatorWrapper.hover_and_click()`: 悬停并点击
- `WaitHelper(page)`: 等待辅助类构造函数
- `WaitHelper.wait_for_element_visible(selector, timeout=None)`: 等待元素可见
- `AssertionHelper(page)`: 断言辅助类构造函数
- `AssertionHelper.assert_text_contains(selector, text)`: 断言文本包含
- `DialogHandler(page)`: 对话框处理器构造函数
- `DialogHandler.accept_alert(text=None)`: 接受警告框
- `DownloadHelper(page)`: 下载助手构造函数
- `DownloadHelper.wait_for_download()`: 等待下载完成
- `KeyboardMouseHelper(page)`: 键盘鼠标助手构造函数
- `KeyboardMouseHelper.press_keys(*keys)`: 按下按键组合
- `EventHelper(page)`: 事件助手构造函数
- `EventHelper.on_request(callback)`: 监听请求事件
- `VideoRecorder(page, output_dir)`: 视频录制器构造函数
- `VideoRecorder.start_recording()`: 开始录制
- `DebugHelper(page)`: 调试助手构造函数
- `DebugHelper.pause()`: 暂停执行

### page 模块
**概述**：页面对象模块，遵循POM（页面对象模型）设计模式，封装各业务页面的元素和操作。

**主要组件**：
- **login_page.py**: 登录页面对象，封装登录页面的元素和操作
- **其他页面**: 按业务需求添加的页面对象（如dashboard_page.py, user_profile_page.py等）

**导出接口**：
```python
from page import LoginPage

# 在测试用例中使用页面对象
login_page = LoginPage(page)
login_page.login("username", "password")
```

**页面对象设计原则**：
1. 每个页面对应一个Python类
2. 页面元素定位器作为类属性
3. 页面操作方法作为类方法
4. 所有页面对象继承`core.BasePage`类
5. 页面对象不包含断言逻辑，只提供操作和状态查询方法

### api 模块
**概述**：API接口封装模块，封装业务系统的API接口，提供统一的调用接口。

**主要组件**：
- **auth_api.py**: 认证API接口封装（登录、注销、令牌管理）
- **user_api.py**: 用户API接口封装（用户管理、权限管理）
- **其他API**: 按业务需求添加的API接口封装

**导出接口**：
```python
from api import AuthAPI, UserAPI

# 在测试用例中使用API封装
auth_api = AuthAPI()
token = auth_api.login("username", "password")

user_api = UserAPI(token)
user = user_api.get_user(123)
```

**API设计原则**：
1. 每个业务模块对应一个API类
2. API方法对应具体的业务接口
3. 统一使用`core.APIClient`发送请求
4. 统一处理响应和异常
5. 与`config/api_endpoints.yaml`配置结合，实现端点管理

### common 模块
**概述**：公共工具模块，提供跨模块的通用工具方法，提升用例编写效率。

**主要组件**：
- **data_generator.py**: 测试数据生成器，使用Faker生成随机测试数据
- **file_utils.py**: 文件操作工具，支持Excel、YAML、JSON等格式的读写
- **log_utils.py**: 日志工具，提供彩色输出、按天分割、模块化级别控制
- **allure_utils.py**: Allure报告工具，提供截图附件、页面源码附件等功能

**导出接口**：
```python
from common import (
    data_generator,  # 数据生成器实例
    file_utils,      # 文件操作工具实例
    LogUtils,        # 日志工具类
    allure_utils     # Allure工具实例
)

# 生成测试数据
user_data = data_generator.user_data()
email = data_generator.email()

# 文件操作
test_data = file_utils.load_yaml("test_data/login.yaml")

# 日志记录
logger = LogUtils.get_logger(__name__)
logger.info("测试开始")

# Allure报告增强
allure_utils.attach_screenshot(page, "登录页面截图")
```

**常用工具**：
- `data_generator.user_data()`: 生成随机用户数据
- `data_generator.product_data()`: 生成随机产品数据
- `file_utils.load_yaml(file_path)`: 加载YAML文件
- `file_utils.load_excel(file_path, sheet_name)`: 加载Excel文件
- `LogUtils.get_logger(name)`: 获取日志记录器
- `LogUtils.setup_logging()`: 设置日志配置
- `allure_utils.attach_screenshot(page, name)`: 附加截图到报告
- `allure_utils.attach_page_source(page, name)`: 附加页面源码到报告

### test_case 模块
**概述**：测试用例模块，管理所有Web UI和API自动化测试用例，实现用例分层、批量执行。

**主要组件**：
- **conftest.py**: pytest全局夹具，定义浏览器、页面、API客户端等夹具
- **test_login.py**: 登录功能测试用例
- **test_user_api.py**: 用户API测试用例
- **test_example.py**: 示例测试用例（成功、失败、跳过示例）
- **其他测试**: 按业务需求添加的测试用例

**测试用例设计原则**：
1. 使用pytest测试框架编写测试用例
2. 使用Allure注解增强测试报告（@allure.epic, @allure.feature, @allure.story）
3. 使用pytest标记进行分类（@pytest.mark.ui, @pytest.mark.api, @pytest.mark.smoke）
4. 使用夹具管理测试资源（browser, page, api_client）
5. 使用页面对象和API封装进行测试，避免直接操作底层API
6. 断言使用pytest内置断言，支持多断言

**运行测试**：
```bash
# 运行UI测试
pytest -m ui -v --alluredir=report/allure_raw

# 运行API测试
pytest -m api -v --alluredir=report/allure_raw

# 运行冒烟测试
pytest -m smoke -v

# 运行特定测试文件
pytest test_case/test_login.py -v
```

## 更新日志

- 2026-03-07: 简化运行脚本，支持通过注释代码行选择测试类型，降低使用复杂度
- 2026-03-07: 修复core模块导入错误，移除对不存在的ElementHandle的依赖
- 2026-03-07: 更新README.md文档，补充core模块高级封装类的详细说明
- 2026-03-07: 添加综合演示测试案例，展示框架所有高级功能，支持通过 `python run_tests.py demo` 运行
- 2026-03-06: 重构日志系统，使用ANSI转义码替代colorama，实现按天自动分割日志
- 2026-03-06: 增强Playwright浏览器配置，支持本地Chrome/Edge浏览器
- 2026-03-06: 完善模块文档和__init__.py文件，提供更好的导入体验
- 2026-03-06: 合并QUICKSTART.md到README.md，提供完整的框架文档