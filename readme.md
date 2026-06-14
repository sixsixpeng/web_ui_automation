# Web UI Automation Framework

基于 **pytest + Playwright** 的现代化 Web UI 自动化测试框架，同步/异步双 API 完整实现，自定义 Fixture 体系，标准 POM 分层架构。

## 技术栈

| 组件             | 版本    |
|----------------|-------|
| Python         | 3.10+ |
| pytest         | 8.4   |
| Playwright     | 1.52  |
| pytest-asyncio | 0.25  |
| Allure         | 2.13  |
| Pillow         | 10+   |

## 快速开始

```bash
pip install -r requirements.txt
playwright install chromium
python run_tests.py                    # 运行同步 Demo
allure serve reports\allure\raw_202*   # 查看报告
```

## 项目结构

```
web_ui_automation/
├── run_tests.py              # 统一运行入口（参数化）
├── run_async_gather.py       # async gather + semaphore 并发演示
├── run_async_xdist.py        # xdist 多进程并发（同步用例）
├── run_sync_xdist.py         # xdist 4 进程并发
├── conftest.py               # 全局 Fixture + 钩子（完全自定义）
├── pytest.ini                # pytest 配置
├── requirements.txt          # 依赖清单
│
├── config/
│   └── config.yaml           # 全局配置（环境/浏览器/超时/日志/报告/截图等）
│
├── case/                     # 测试用例
│   ├── sync/                 #   同步测试
│   │   ├── 01_demo/          #     演示用例
│   │   └── 10_business/      #     业务用例
│   └── async/                #   异步测试
│       ├── 01_demo/          #     演示用例
│       ├── 02_concurrent/    #     并发用例（gather + semaphore）
│       └── 10_business/      #     业务用例
│
├── pages/                    # POM 页面对象层
│   ├── base/                 #   基础父类
│   │   ├── base_sync_page.py #     同步（导航/点击/输入/等待/窗口管理/弹窗/截图+步骤截图）
│   │   └── base_async_page.py#     异步（同上，async/await 版本+步骤截图）
│   ├── business/             #   业务页面
│   │   ├── login_page.py
│   │   └── product_page.py
│   ├── common/
│   │   └── global_popup.py
│   └── page_manager.py       #   页面管理器（自动加载 + 缓存 + 类型注解）
│
├── utils/                    # 工具类（24+ 模块）
│   ├── path_util.py          #   路径管理（pathlib 封装）
│   ├── config_util.py        #   配置读取（yaml + env 回退，点号分隔键）
│   ├── log_util.py           #   日志（配置驱动，控制台+文件，脱敏过滤）
│   ├── time_util.py          #   时间日期（时间戳/格式化文件名等）
│   ├── uuid_util.py          #   唯一 ID 生成器（uuid1/uuid4/uuid7）
│   ├── hash_util.py          #   哈希编码（MD5/SHA/Base64/HMAC/加盐）
│   ├── validate_util.py      #   数据格式校验（手机/邮箱/身份证等）
│   ├── assert_util.py        #   增强断言（@allure.step 标记，调用位置打印）
│   ├── async_runner.py       #   并发执行器（ConcurrentGroup 自动发现）
│   ├── screenshot_util.py    #   截图（Sync+Async, URL 水印, allure 附件）
│   ├── network_util.py       #   网络拦截 + Mock
│   ├── popup_util.py         #   弹窗处理（自动关闭，前后截图）
│   ├── storage_util.py       #   浏览器存储
│   ├── performance_util.py   #   页面性能采集（LCP/CLS/FCP）
│   ├── captcha_util.py       #   验证码处理
│   ├── api_util.py           #   HTTP 请求客户端（allure.step 标记）
│   ├── data_util.py          #   多格式数据读取
│   ├── faker_util.py         #   随机数据生成
│   ├── crypto_util.py        #   AES 加解密
│   ├── db_util.py            #   数据库操作
│   ├── mail_util.py          #   邮件推送
│   ├── file_util.py          #   文件操作（临时文件/清理）
│   ├── cache_util.py         #   内存缓存
│   ├── allure_attach_util.py #   Allure 附件挂载（文本/JSON/图片/HTML）
│   └── yaml_json_util.py     #   YAML/JSON 解析
│
├── plugins/
│   └── allure_plugin.py      # Allure 报告增强
│
├── reports/allure/           # 报告产物
│   ├── raw_YYYYMMDD_HHMMSS/  #   原始数据（每次运行独立命名）
│   └── static/               #   静态 HTML 报告（每次覆盖）
│
├── screenshots/              # 截图（按日期分目录）
│
├── logs/                     # 运行日志
│   └── automation.log        #   自动轮转日志文件
│
└── browser_data/             # 浏览器持久化缓存（已 gitignore）
```

## 核心特性

### 1. 同步/异步双 API

所有页面对象和工具均提供同步/异步两套实现，统一配置、一键切换。

```python
# 同步模式 — 使用 page_sync fixture
def test_login(self, page_sync):
    p = BaseSyncPage(page_sync)
    p.fill("#username", "admin")
    p.click("#loginBtn")

# 异步模式 — 使用 browser_async fixture
async def test_login(self, browser_async):
    c = await browser_async.new_context()
    p = BaseAsyncPage(await c.new_page())
    await p.open("https://example.com")
    await p.fill("#username", "admin")
    await p.click("#loginBtn")
    await c.close()
```

### 2. 自定义 Fixture（无 pytest-playwright）

```python
# 完整 fixture 链
playwright_sync -> browser_sync -> context_sync -> page_sync
playwright_async -> browser_async -> context_async -> page_async

# 参数化浏览器 — 通过 indirect=True
@pytest.mark.parametrize("browser_sync", [
    {"browser_type": "chromium", "headless": True, "viewport": {"width": 1280, "height": 720}},
    {"browser_type": "firefox", "headless": True},
], indirect=True)
def test_cross_browser(self, browser_sync):
    ...

# 持久化上下文 — session 自动保存到 browser_data/
def test_with_session(self, persistent_context):
    page = persistent_context.pages[0]  # 注意: 取 pages[0], 不是 new_page()
    page.goto("https://example.com")
    # 登录后 session 自动保存
    
def test_reuse_session(self, persistent_context):
    page = persistent_context.pages[0]
    page.goto("https://example.com")  # 上次登录 session 还在
```

### 3. 异步并发

**asyncio.gather** — 多 Context 并行：

```python
async def test_gather(self, browser_async):
    async def open_page(i):
        c = await browser_async.new_context()
        p = BaseAsyncPage(await c.new_page())
        await p.open(URL)
        t = await p.get_title()
        await c.close()
        return t
    r1, r2, r3 = await asyncio.gather(open_page(1), open_page(2), open_page(3))
```

**Semaphore** — 控制并发上限：

```python
sem = asyncio.Semaphore(2)
async def task(i):
    async with sem:          # 最多 2 个同时执行
        c = await browser_async.new_context()
        p = BaseAsyncPage(await c.new_page())
        ...
rs = await asyncio.gather(*[task(i) for i in range(6)])
```

**ConcurrentGroup** — 自动发现 + 并发执行：

```python
from utils.async_runner import ConcurrentGroup

class Steps(ConcurrentGroup):
    max_concurrency = 3
    async def step_login(self): ...
    async def step_search(self): ...

results = await Steps().run()
results = await Steps(include=["step_login"]).run()  # 选择子集
```

### 4. PageManager — 页面对象自动加载

```python
def test_login(self, pages_sync):
    login: LoginPageSync = pages_sync.login      # 自动加载 + 缓存 + IDE 类型提示
    product: ProductPageSync = pages_sync.product
```

### 5. BasePage 方法一览

| 分类         | 方法                                                                                                      | 步骤截图 |
|------------|---------------------------------------------------------------------------------------------------------|--------|
| **导航**     | `open`, `refresh`, `go_back`, `go_forward`                                                              | ✅     |
| **元素操作**   | `click`, `fill`, `type_text`, `select_option`, `check`, `uncheck`, `hover`, `double_click`, `right_click`, `press_key` | ✅     |
| **元素状态**   | `is_visible`, `is_enabled`, `is_checked`                                                                | —     |
| **获取信息**   | `get_text`, `get_attribute`, `get_input_value`, `get_title`, `get_url`, `get_count`                     | —     |
| **等待**     | `wait_for_visible`, `wait_for_hidden`, `wait_for_load_state`, `wait_for_timeout`                        | —     |
| **鼠标**     | `click_position`, `double_click_position`, `hover_position`                                            | ✅     |
| **滚动**     | `scroll_to_top`, `scroll_to_bottom`, `scroll_to_element`                                                | ✅     |
| **窗口/标签页** | `new_tab`, `tab_count`, `current_tab`, `wait_for_new_tab`                                              | ✅     |
| **弹窗**     | `handle_alert`, `close_ad_popups`                                                                       | ✅     |
| **截图**     | `attach_window_screenshot`, `attach_full_screenshot`, `attach_element_screenshot`                       | —     |
| **网络/框架**  | `wait_for_response`, `reload_and_wait`, `switch_to_frame`, `switch_to_main_frame`, `copy_to_clipboard`  | ✅     |

> 步骤截图：每个有前后差异的执行方法自动在操作完成后截图，受 `config.yaml` → `screenshot.auto_attach_allure` 控制。

### 6. 全局配置

```yaml
# config/config.yaml — 完整配置项
run:
  mode: sync                    # sync / async
  env: test                     # dev / test / pre / prod
  browser: chromium
  headless: false
  workers: 4

step_delay_ms: 100              # 步骤间延时（调试可视化），>0 减缓执行速度

timeout:
  default: 30000
  page_load: 60000
  element: 10000
  assertion: 5000

browser:
  viewport: {width: 1920, height: 1080}
  args:
    - --disable-blink-features=AutomationControlled
    - --disable-dev-shm-usage

async:
  default_concurrency: 5
  max_concurrency: 10

allure:
  raw_data_path: reports/allure/raw
  static_report_path: reports/allure/static
  auto_generate_static: true

logging:
  level: DEBUG                  # 日志级别，同时控制控制台和文件
  file:
    enabled: true               # 是否写入日志文件
    max_size_mb: 500
    backup_count: 7
  format: "%(asctime)s | %(levelname)-8s | %(name)s | %(process)d | %(filename)s:%(lineno)d | %(message)s"
  enable_desensitization: true  # 脱敏密码/token

screenshot:
  save_dir: screenshots
  auto_attach_allure: true      # 自动步骤截图开关
  image_format: png
  cleanup_days: 7

retry:
  max_retry_times: 3
  retry_interval_ms: 500
```

### 7. 步骤自动截图

每次关键操作（`click`、`fill`、`check`、`open`、`scroll`、`new_tab` 等）完成后，自动截取页面状态并附到 Allure 报告：

```python
# base_async_page.py 内部自动执行
async def click(self, selector, ...):
    _log_call()
    await self.page.locator(selector).click()
    logger.debug(f"异步已点击: {selector}")
    await self._auto_step_screenshot(name=f"click_{selector}")  # ← 自动截图
```

截图保存在 `screenshots/YYYYMMDD/` 目录下，文件名格式 `YYYYMMDD_HHMMSS_before/after_方法名.png`。

### 8. 失败自动截图

```python
# conftest.py pytest_runtest_makereport 钩子
def _capture(item):
    page = item.funcargs.get("page_sync") or item.funcargs.get("page_async")
    ScreenshotSyncUtil.take_window_screenshot(page, name="failure_window")
    ScreenshotSyncUtil.take_full_page_screenshot(page, name="failure_fullpage")
    allure.attach(str(page.url), name="failure_url")
```

### 9. 日志系统

- **控制台**：实时输出，统一格式 `时间 | 级别 | 模块 | 进程ID | 文件:行号 | 消息`
- **文件**：自动轮转（500MB/个，保留 7 个备份），路径 `logs/automation.log`
- **脱敏**：自动过滤密码、token、手机号中间四位等敏感信息
- **配置驱动**：日志级别和格式完全由 `config.yaml` 控制，修改无需改代码

### 10. 运行入口

| 命令                                                                                   | 说明                          |
|--------------------------------------------------------------------------------------|-----------------------------|
| `python run_tests.py`                                                                | 默认运行同步 Demo                 |
| `python run_tests.py --async-mode True`                                              | 运行异步 Demo                   |
| `python run_tests.py -m smoke`                                                       | 按标签筛选                       |
| `python run_tests.py --env dev --headless True`                                      | 指定环境 + 无头模式                |
| `python run_tests.py --file case/sync/10_business/test_login.py`                     | 运行指定文件                      |
| `python run_sync_xdist.py`                                                           | 4 进程并发（同步用例，自动生成 Allure 报告）|
| `python run_async_xdist.py`                                                          | 3 进程并发（跳过异步用例，自动生成报告）    |
| `python run_async_gather.py`                                                         | async gather + semaphore 演示 |
| `python -m pytest case/async/ --override-ini asyncio_mode=auto -p pytest_asyncio -v` | 运行全部异步测试                    |
| `allure serve reports\allure\raw_202*`                                               | 查看 Allure 报告                |

所有入口脚本（`run_*.py`）执行后自动生成带时间戳的 Allure 原始数据目录和静态报告。

## 依赖安装

```bash
conda create -n web_ui python=3.10 -y
conda activate web_ui
pip install -r requirements.txt
playwright install chromium
```

## 截图命名规范

```
screenshots/20260614/
    20260614_201719_click_#searchBtn.png
    20260614_201730_fill_#username.png
    20260614_201741_before_open_url.png
    20260614_201742_after_open_url.png
```

格式：`YYYYMMDD_HHMMSS_[before/after]_方法名[_参数].png`，按日期分目录存储。
