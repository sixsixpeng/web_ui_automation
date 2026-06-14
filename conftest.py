# -*- coding: utf-8 -*-
"""Global conftest - fully custom fixtures (no pytest-playwright)"""
import allure
import pytest
from _pytest.nodes import Item

from utils import get_logger, mail_sender
from utils.config_util import get as cfg, get_env_config

logger = get_logger("conftest")


def pytest_configure(config):
    for m in ["smoke", "regression", "critical", "login", "product", "demo", "compatibility", "async"]:
        config.addinivalue_line("markers", m)


def _build_opts(request):
    opts = {
        "headless": cfg("headless", "false").lower() == "true",
        "slow_mo": int(cfg("step_delay_ms", 0)),
        "args": cfg("browser.args", [
            "--disable-features=Translate", "--disable-gpu", "--no-first-run",
            "--no-default-browser-check", "--disable-popup-blocking",
        ]),
    }
    if hasattr(request, "param") and request.param:
        if isinstance(request.param, dict):
            opts.update(request.param)
        elif isinstance(request.param, str):
            opts["browser_type"] = request.param
    return opts


# ====== Sync Fixtures ======
@pytest.fixture(scope="function")
def playwright_sync():
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        yield p


@pytest.fixture(scope="function")
def browser_sync(request, playwright_sync):
    opts = _build_opts(request)
    bt = opts.pop("browser_type", cfg("browser_type", "chromium"))
    b = getattr(playwright_sync, bt).launch(**opts)
    yield b
    b.close()


@pytest.fixture(scope="function")
def context_sync(browser_sync):
    vp = cfg("browser.viewport", {"width": 1920, "height": 1080})
    ctx = browser_sync.new_context(viewport=vp, locale="zh-CN")
    yield ctx
    ctx.close()


@pytest.fixture(scope="function")
def page_sync(context_sync):
    pg = context_sync.new_page()
    pg.set_default_timeout(int(cfg("timeout.default", 30000)))
    yield pg
    pg.close()


# ====== Async Fixtures ======
@pytest.fixture(scope="function")
async def playwright_async():
    from playwright.async_api import async_playwright
    async with async_playwright() as p:
        yield p


@pytest.fixture(scope="function")
async def browser_async(request, playwright_async):
    opts = _build_opts(request)
    bt = opts.pop("browser_type", cfg("browser_type", "chromium"))
    b = await getattr(playwright_async, bt).launch(**opts)
    yield b
    await b.close()


@pytest.fixture(scope="function")
async def context_async(browser_async):
    vp = cfg("browser.viewport", {"width": 1920, "height": 1080})
    ctx = await browser_async.new_context(viewport=vp, locale="zh-CN")
    yield ctx
    await ctx.close()


@pytest.fixture(scope="function")
async def page_async(context_async):
    pg = await context_async.new_page()
    pg.set_default_timeout(int(cfg("timeout.default", 30000)))
    yield pg
    await pg.close()


# ====== Persistent Context Fixture ======
@pytest.fixture(scope="function")
def persistent_context(request):
    from playwright.sync_api import sync_playwright
    from utils.path_util import path_util
    cache_root = path_util.root / "browser_data"
    cache_root.mkdir(parents=True, exist_ok=True)
    if hasattr(request, "param") and request.param:
        user_dir = str(request.param)
    else:
        user_dir = str(cache_root / "default")
    with sync_playwright() as p:
        ctx = p.chromium.launch_persistent_context(user_dir, headless=False, viewport={"width": 1920, "height": 1080})
        yield ctx
        ctx.close()


@pytest.fixture(scope="function")
def page_persistent(persistent_context):
    pg = persistent_context.pages[0] if persistent_context.pages else persistent_context.new_page()
    pg.set_default_timeout(int(cfg("timeout.default", 30000)))
    yield pg


# ====== Environment Config ======
@pytest.fixture(scope="session")
def env_config():
    return get_env_config()


# ====== Auto Tagging ======
@pytest.fixture(autouse=True)
def _auto_tag(request):
    allure.dynamic.tag(cfg("run.env", "test"))
    node = request.node.nodeid.lower()
    if "login" in node:
        allure.dynamic.feature("Login")
    elif "product" in node:
        allure.dynamic.feature("Product")
    yield


# ====== Failure Screenshot Hook ======
@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item: Item, call):
    outcome = yield
    report = outcome.get_result()
    if report.when == "call":
        mail_sender.add_result(node_id=report.nodeid, status="passed" if report.passed else ("skipped" if report.skipped else "failed"), duration=getattr(report, "duration", 0), error=str(report.longrepr) if report.failed else "")
        if report.failed:
            _capture(item)


def _capture(item):
    page = (getattr(item, "funcargs", {}).get("page_sync") or getattr(item, "funcargs", {}).get("page") or getattr(item, "funcargs", {}).get("page_async"))
    if page is None: return
    try:
        from utils.screenshot_util import ScreenshotSyncUtil
        ScreenshotSyncUtil.take_window_screenshot(page, name="failure_window", attach_allure=True)
        ScreenshotSyncUtil.take_full_page_screenshot(page, name="failure_fullpage", attach_allure=True)
        allure.attach(str(page.url), name="failure_url", attachment_type=allure.attachment_type.TEXT)
    except Exception as e:
        logger.warning(f"Failure screenshot: {e}")


def pytest_sessionfinish(session, exitstatus):
    logger.info(f"Test session finished, exit code: {exitstatus}")
    try:
        mail_sender.send_report()
    except:
        pass
    try:
        from utils.file_util import file_util
        file_util.cleanup_temp_files()
    except:
        pass
