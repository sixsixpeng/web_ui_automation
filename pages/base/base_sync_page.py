# -*- coding: utf-8 -*-

"""base_sync_page - 同步 BasePage 父类"""
import time
from typing import List, Union

import allure

from utils.log_util import get_logger

logger = get_logger("base_sync_page")


def _screenshot_wrapper_sync(method):
    """装饰器：方法执行前后自动截图（同步版）"""

    def wrapper(self, *args, **kwargs):
        method_name = method.__name__
        try:
            from utils.config_util import get as cfg
            if str(cfg("screenshot.auto_attach_allure", "false")).lower() == "true":
                self.attach_window_screenshot(name=f"before_{method_name}")
        except:
            pass
        result = method(self, *args, **kwargs)
        try:
            from utils.config_util import get as cfg
            if str(cfg("screenshot.auto_attach_allure", "false")).lower() == "true":
                self.attach_window_screenshot(name=f"after_{method_name}")
        except:
            pass
        return result

    return wrapper


def _log_call():
    import traceback, threading
    try:
        thr = threading.current_thread()
        thread_id = thr.ident or 0
        st = traceback.extract_stack(limit=4)
        if len(st) >= 2:
            f2 = st[-3]
            logger.debug(f"[Th:{thread_id}][{f2.name}] {f2.filename}:{f2.lineno}")
    except:
        pass


class BaseSyncPage:
    """同步页面父类，所有 sync_pages 继承此类"""

    def __init__(self, page, base_url: str = "", step_delay_ms: int = 0):
        self.page = page
        self.base_url = base_url
        from utils.config_util import get as cfg
        self.timeout = int(cfg("timeout.default", 30000))
        self.element_timeout = int(cfg("timeout.element", 10000))
        self.step_delay_ms = step_delay_ms

    def _step_delay(self):
        """步骤间同步延时"""
        if self.step_delay_ms:
            time.sleep(self.step_delay_ms / 1000.0)

    def _step_screenshot(self, name: str = ""):
        """自动步骤截图（受 config.yaml screenshot.auto_attach_allure 控制）"""
        try:
            from utils.config_util import get as cfg
            if str(cfg("screenshot.auto_attach_allure", "false")).lower() == "true":
                self.attach_window_screenshot(name=name)
        except:
            pass

    # ====== 导航 ======
    @_screenshot_wrapper_sync
    def open(self, url: str = ""):
        _log_call()
        """打开页面"""
        target = url if url else self.base_url
        with allure.step(f"打开页面: {target}"):
            self.page.goto(target, timeout=self.timeout)
        self._step_screenshot(name=f"open_{target[:30]}")

    @_screenshot_wrapper_sync
    def refresh(self):
        _log_call()
        """刷新页面"""
        with allure.step("刷新页面"):
            self.page.reload(timeout=self.timeout)
        self._step_screenshot(name="after_refresh")

    @_screenshot_wrapper_sync
    def go_back(self):
        _log_call()
        """后退"""
        with allure.step("后退"):
            self.page.go_back()
        self._step_screenshot(name="after_go_back")

    @_screenshot_wrapper_sync
    def go_forward(self):
        _log_call()
        """前进"""
        with allure.step("前进"):
            self.page.go_forward()
        self._step_screenshot(name="after_go_forward")

    # ====== 定位 ======
    @_screenshot_wrapper_sync
    def locator(self, selector: str):
        _log_call()
        """获取元素定位器"""
        return self.page.locator(selector)

    # ====== 元素交互 ======
    @_screenshot_wrapper_sync
    def click(self, selector: str, timeout: int = None, **kwargs):
        _log_call()
        """点击元素"""
        with allure.step(f"点击: {selector}"):
            t = timeout or self.timeout
            self.page.locator(selector).click(timeout=t, **kwargs)
            logger.debug(f"已点击: {selector}")
            self._step_screenshot(name=f"click_{selector}")
            self._step_delay()

    @_screenshot_wrapper_sync
    def fill(self, selector: str, text: str, timeout: int = None):
        _log_call()
        """输入文本"""
        with allure.step(f"输入: {selector}"):
            self.page.locator(selector).fill(text, timeout=timeout)
            logger.debug(f"已输入: {selector}")
            self._step_screenshot(name=f"fill_{selector}")
            self._step_delay()

    @_screenshot_wrapper_sync
    def type_text(self, selector: str, text: str, delay: int = 50):
        _log_call()
        """逐字输入文本"""
        self.page.locator(selector).press_sequentially(text, delay=delay)
        self._step_screenshot(name=f"type_{selector}")

    @_screenshot_wrapper_sync
    def select_option(self, selector: str, value: Union[str, List[str]]):
        _log_call()
        """选择下拉选项"""
        self.page.locator(selector).select_option(value)
        self._step_screenshot(name=f"select_{selector}")

    @_screenshot_wrapper_sync
    def check(self, selector: str):
        _log_call()
        """勾选复选框"""
        self.page.locator(selector).check()
        self._step_screenshot(name=f"check_{selector}")
        self._step_delay()

    @_screenshot_wrapper_sync
    def uncheck(self, selector: str):
        _log_call()
        """取消勾选"""
        self.page.locator(selector).uncheck()
        self._step_screenshot(name=f"uncheck_{selector}")

    @_screenshot_wrapper_sync
    def hover(self, selector: str):
        _log_call()
        """悬停"""
        self.page.locator(selector).hover()
        self._step_screenshot(name=f"hover_{selector}")

    @_screenshot_wrapper_sync
    def double_click(self, selector: str):
        _log_call()
        """双击"""
        self.page.locator(selector).dblclick()
        self._step_screenshot(name=f"dblclick_{selector}")

    @_screenshot_wrapper_sync
    def right_click(self, selector: str):
        _log_call()
        """右键点击"""
        self.page.locator(selector).click(button="right")
        self._step_screenshot(name=f"rightclick_{selector}")

    @_screenshot_wrapper_sync
    def press_key(self, key: str):
        _log_call()
        """按键"""
        self.page.keyboard.press(key)
        self._step_screenshot(name=f"press_{key}")

    # ====== 状态判断 ======
    @_screenshot_wrapper_sync
    def is_visible(self, selector: str, timeout: int = None) -> bool:
        _log_call()
        """判断元素可见"""
        return self.page.locator(selector).is_visible(timeout=timeout or self.element_timeout)

    @_screenshot_wrapper_sync
    def is_enabled(self, selector: str) -> bool:
        _log_call()
        """判断元素可用"""
        return self.page.locator(selector).is_enabled()

    @_screenshot_wrapper_sync
    def is_checked(self, selector: str) -> bool:
        _log_call()
        """判断复选框是否选中"""
        return self.page.locator(selector).is_checked()

    # ====== 获取属性 ======
    @_screenshot_wrapper_sync
    def get_text(self, selector: str, timeout: int = None) -> str:
        _log_call()
        """获取元素文本"""
        return self.page.locator(selector).text_content(timeout=timeout or self.element_timeout)

    @_screenshot_wrapper_sync
    def get_inner_text(self, selector: str) -> str:
        _log_call()
        """获取元素内部文本"""
        return self.page.locator(selector).inner_text()

    @_screenshot_wrapper_sync
    def get_attribute(self, selector: str, attr: str) -> str:
        _log_call()
        """获取元素属性"""
        return self.page.locator(selector).get_attribute(attr)

    @_screenshot_wrapper_sync
    def get_input_value(self, selector: str) -> str:
        _log_call()
        """获取输入框值"""
        return self.page.locator(selector).input_value()

    @_screenshot_wrapper_sync
    def get_count(self, selector: str) -> int:
        _log_call()
        """获取匹配元素数量"""
        return self.page.locator(selector).count()

    # ====== 等待 ======
    @_screenshot_wrapper_sync
    def wait_for_visible(self, selector: str, timeout: int = None):
        _log_call()
        """等待元素可见"""
        self.page.locator(selector).wait_for(state="visible", timeout=timeout or self.timeout)

    @_screenshot_wrapper_sync
    def wait_for_hidden(self, selector: str, timeout: int = None):
        _log_call()
        """等待元素隐藏"""
        self.page.locator(selector).wait_for(state="hidden", timeout=timeout or self.timeout)

    @_screenshot_wrapper_sync
    def wait_for_load_state(self, state: str = "networkidle"):
        _log_call()
        """等待页面加载完成"""
        self.page.wait_for_load_state(state, timeout=self.timeout)

    @_screenshot_wrapper_sync
    def force_wait(self, seconds: float):
        """强制等待指定秒数（仅在调试时使用）"""
        time.sleep(seconds)

    # ====== 页面信息 ======
    @_screenshot_wrapper_sync
    def get_title(self) -> str:
        _log_call()
        """获取页面标题"""
        return self.page.title()

    @_screenshot_wrapper_sync
    def get_url(self) -> str:
        _log_call()
        """获取当前URL"""
        return self.page.url

    # ====== 截图 ======
    def attach_window_screenshot(self, name: str = None):
        _log_call()
        """截取窗口截图并附到报告"""
        from utils.screenshot_util import ScreenshotSyncUtil
        ScreenshotSyncUtil.take_window_screenshot(self.page, name=name)

    def attach_full_screenshot(self, name: str = None):
        _log_call()
        """截取全页截图并附到报告"""
        from utils.screenshot_util import ScreenshotSyncUtil
        ScreenshotSyncUtil.take_full_page_screenshot(self.page, name=name)

    def attach_element_screenshot(self, selector: str, name: str = None):
        _log_call()
        """截取元素截图并附到报告"""
        from utils.screenshot_util import ScreenshotSyncUtil
        ScreenshotSyncUtil.take_element_screenshot(self.page, selector, name=name)

    # ====== 弹窗 ======
    @_screenshot_wrapper_sync
    def handle_alert(self, accept: bool = True):
        """
        处理 alert/confirm/prompt 弹窗
        注意：Playwright 默认自动关闭弹窗
        """
        # Playwright auto-dismisses, no explicit handling needed
        pass

    # ====== 滚动 ======
    @_screenshot_wrapper_sync
    def scroll_to_top(self):
        _log_call()
        """滚动到页面顶部"""
        self.page.evaluate("window.scrollTo(0,0)")
        self._step_screenshot(name="scroll_top")

    @_screenshot_wrapper_sync
    def scroll_to_bottom(self):
        _log_call()
        """滚动到页面底部"""
        self.page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        self._step_screenshot(name="scroll_bottom")

    @_screenshot_wrapper_sync
    def scroll_to_element(self, selector: str):
        _log_call()
        """滚动到元素位置"""
        self.page.locator(selector).scroll_into_view_if_needed()
        self._step_screenshot(name=f"scroll_{selector}")

    # ====== 框架 ======
    @_screenshot_wrapper_sync
    def switch_to_frame(self, selector: str):
        _log_call()
        """切换到 iframe"""
        frame = self.page.frame_locator(selector)
        self.page = frame
        self._step_screenshot(name="switch_frame")

    @_screenshot_wrapper_sync
    def switch_to_main_frame(self):
        _log_call()
        """切换回主框架"""
        pass  # self.page already is the main page

    # ====== 网络 ======
    @_screenshot_wrapper_sync
    def wait_for_response(self, url_pattern: str, timeout: int = None):
        _log_call()
        """等待指定网络响应"""
        timeout = timeout or self.timeout
        return self.page.wait_for_response(url_pattern, timeout=timeout)

    # ====== 窗口/标签页管理 ======
    @_screenshot_wrapper_sync
    def new_tab(self, url: str = ""):
        _log_call()
        """打开新标签页"""
        ctx = self.page.context
        pg = ctx.new_page()
        if url:
            pg.goto(url, timeout=self.timeout)
        self._step_screenshot(name="new_tab")
        return pg

    @_screenshot_wrapper_sync
    def tab_count(self) -> int:
        _log_call()
        """获取当前标签页数量"""
        return len(self.page.context.pages)

    @_screenshot_wrapper_sync
    def current_tab(self):
        _log_call()
        """获取当前标签页索引"""
        pages = self.page.context.pages
        for i, p in enumerate(pages):
            if p == self.page:
                return i
        return 0

    @_screenshot_wrapper_sync
    def close_ad_popups(self, timeout: int = None) -> bool:
        _log_call()
        """关闭弹窗/广告弹窗，返回是否成功关闭"""
        timeout = timeout or self.element_timeout
        start = time.time()
        while time.time() - start < timeout / 1000:
            try:
                dialogs = self.page.context.pages
                if len(dialogs) > 1:
                    for d in dialogs:
                        if d != self.page:
                            d.close()
                    self._step_screenshot(name="popup_closed")
                    return True
            except:
                pass
            time.sleep(0.2)
        return False

    @_screenshot_wrapper_sync
    def wait_for_new_tab(self, timeout: int = None):
        _log_call()
        """等待新标签页并返回"""
        timeout = timeout or self.element_timeout
        start = time.time()
        pages_before = len(self.page.context.pages)
        while time.time() - start < timeout / 1000:
            pages = self.page.context.pages
            if len(pages) > pages_before:
                new_page = pages[-1]
                new_page.wait_for_load_state()
                self._step_screenshot(name="new_tab_waited")
                return new_page
            time.sleep(0.1)
        raise TimeoutError(f"No new tab within {timeout}ms")

    @_screenshot_wrapper_sync
    def force_wait(self, seconds: float):
        """强制等待指定秒数（仅在调试时使用）"""
        time.sleep(seconds)
