# -*- coding: utf-8 -*-
"""
assert_util - 全局增强断言工具
功能：替代原生 assert，统一失败处理链路（自动截图、日志、报错信息）
"""

from typing import Any, Union

import allure

from utils.log_util import get_logger

logger = get_logger("assert_util")


class AssertUtil:
    """增强断言工具类"""

    # 软断言模式：收集所有失败，不立即终止
    _soft_assert_mode = False
    _soft_errors = []

    # ========== 模式控制 ==========

    @classmethod
    def enable_soft_assert(cls):
        """开启软断言模式"""
        cls._soft_assert_mode = True
        cls._soft_errors = []
        logger.info("软断言模式已开启")

    @classmethod
    def disable_soft_assert(cls):
        """关闭软断言模式"""
        cls._soft_assert_mode = False
        cls._soft_errors = []

    @classmethod
    def assert_all(cls):
        """收集所有软断言失败，统一抛出"""
        if cls._soft_errors:
            errors = "\n".join(cls._soft_errors)
            cls._soft_errors = []
            cls._soft_assert_mode = False
            raise AssertionError(f"软断言存在失败:\n{errors}")

    # ========== 核心断言 ==========

    @classmethod
    def _handle_assertion(cls, condition: bool, message: str):
        """统一处理断言结果，成功/失败均包含调用位置信息"""
        # Get caller location (skip assert_util frames)
        import inspect
        frame = inspect.currentframe()
        caller_frame = None
        f = frame.f_back
        while f:
            mod = f.f_globals.get("__name__", "")
            if "assert_util" not in mod and "unittest" not in mod:
                caller_frame = f
                break
            f = f.f_back
        del frame

        if caller_frame:
            filename = caller_frame.f_code.co_filename
            lineno = caller_frame.f_lineno
            func = caller_frame.f_code.co_name
            location = f"{filename}:{lineno} ({func})"
        else:
            location = "unknown"

        if condition:
            logger.info(f"[ASSERT OK] {message} | at {location}")
            return True

        full_msg = f"ASSERT FAILED: {message}"
        log_msg = f"[ASSERT FAIL] {message} | at {location}"

        logger.error(log_msg)
        allure.attach(f"{full_msg}\nLocation: {location}", name="assert_failure", attachment_type=allure.attachment_type.TEXT)

        if cls._soft_assert_mode:
            cls._soft_errors.append(log_msg)
            return False
        else:
            raise AssertionError(f"{full_msg}\n  at {location}")

    # ========== 页面状态断言 ==========

    @classmethod
    def url_contains(cls, page, expected: str, msg: str = ""):
        """断言当前 URL 包含预期文本"""
        actual = page.url if hasattr(page, 'url') else str(page)
        condition = expected in actual
        cls._handle_assertion(condition, msg or f"URL 应包含 '{expected}'，实际: '{actual}'")

    @classmethod
    def url_equals(cls, page, expected: str, msg: str = ""):
        """断言当前 URL 完全等于预期"""
        actual = page.url if hasattr(page, 'url') else str(page)
        condition = actual == expected
        cls._handle_assertion(condition, msg or f"URL 应等于 '{expected}'，实际: '{actual}'")

    @classmethod
    def title_contains(cls, page, expected: str, msg: str = ""):
        """断言页面标题包含预期文本"""
        actual = page.title() if hasattr(page, 'title') else ""
        condition = expected in actual
        cls._handle_assertion(condition, msg or f"标题应包含 '{expected}'，实际: '{actual}'")

    @classmethod
    def title_equals(cls, page, expected: str, msg: str = ""):
        """断言页面标题完全等于预期"""
        actual = page.title() if hasattr(page, 'title') else ""
        condition = actual == expected
        cls._handle_assertion(condition, msg or f"标题应等于 '{expected}'，实际: '{actual}'")

    # ========== 元素状态断言 ==========

    @classmethod
    def element_visible(cls, page, selector: str, msg: str = ""):
        """断言元素可见"""
        try:
            element = page.locator(selector) if hasattr(page, 'locator') else None
            is_visible = element.is_visible() if element else False
            if not is_visible:
                cls._handle_assertion(False, msg or f"元素应可见: {selector}")
        except Exception as e:
            cls._handle_assertion(False, msg or f"元素可见性检查失败: {selector}, {e}")

    @classmethod
    def element_not_visible(cls, page, selector: str, msg: str = ""):
        """断言元素不可见"""
        try:
            element = page.locator(selector) if hasattr(page, 'locator') else None
            is_hidden = not element.is_visible() if element else True
            if not is_hidden:
                cls._handle_assertion(False, msg or f"元素应不可见: {selector}")
        except Exception as e:
            cls._handle_assertion(False, msg or f"元素不可见性检查失败: {selector}, {e}")

    @classmethod
    def element_enabled(cls, page, selector: str, msg: str = ""):
        """断言元素可交互"""
        try:
            element = page.locator(selector) if hasattr(page, 'locator') else None
            is_enabled = element.is_enabled() if element else False
            if not is_enabled:
                cls._handle_assertion(False, msg or f"元素应可点击: {selector}")
        except Exception as e:
            cls._handle_assertion(False, msg or f"元素可交互性检查失败: {selector}, {e}")

    @classmethod
    def element_disabled(cls, page, selector: str, msg: str = ""):
        """断言元素不可交互"""
        try:
            element = page.locator(selector) if hasattr(page, 'locator') else None
            is_disabled = not element.is_enabled() if element else True
            if not is_disabled:
                cls._handle_assertion(False, msg or f"元素应不可点击: {selector}")
        except Exception as e:
            cls._handle_assertion(False, msg or f"元素不可交互性检查失败: {selector}, {e}")

    # ========== 文本断言 ==========

    @classmethod
    def text_contains(cls, element_or_text, expected: str, msg: str = ""):
        """断言文本包含预期"""
        actual = element_or_text.text_content() if hasattr(element_or_text, 'text_content') else str(element_or_text)
        condition = expected in actual
        cls._handle_assertion(condition, msg or f"文本应包含 '{expected}'，实际: '{actual[:200]}'")

    @classmethod
    def text_equals(cls, element_or_text, expected: str, msg: str = ""):
        """断言文本完全等于预期"""
        actual = element_or_text.text_content() if hasattr(element_or_text, 'text_content') else str(element_or_text)
        condition = actual.strip() == expected.strip()
        cls._handle_assertion(condition, msg or f"文本应等于 '{expected}'，实际: '{actual}'")

    # ========== 数值断言 ==========

    @classmethod
    def equals(cls, actual: Any, expected: Any, msg: str = ""):
        """断言相等"""
        cls._handle_assertion(actual == expected, msg or f"值应等于 {expected}，实际: {actual}")

    @classmethod
    def not_equals(cls, actual: Any, expected: Any, msg: str = ""):
        """断言不相等"""
        cls._handle_assertion(actual != expected, msg or f"值应不等于 {expected}，实际: {actual}")

    @classmethod
    def greater_than(cls, actual: Union[int, float], expected: Union[int, float], msg: str = ""):
        """断言大于"""
        cls._handle_assertion(actual > expected, msg or f"值应大于 {expected}，实际: {actual}")

    @classmethod
    def less_than(cls, actual: Union[int, float], expected: Union[int, float], msg: str = ""):
        """断言小于"""
        cls._handle_assertion(actual < expected, msg or f"值应小于 {expected}，实际: {actual}")

    @classmethod
    def greater_or_equals(cls, actual: Union[int, float], expected: Union[int, float], msg: str = ""):
        """断言大于等于"""
        cls._handle_assertion(actual >= expected, msg or f"值应大于等于 {expected}，实际: {actual}")

    # ========== 列表断言 ==========

    @classmethod
    def list_contains(cls, items: list, expected: Any, msg: str = ""):
        """断言列表包含元素"""
        cls._handle_assertion(expected in items, msg or f"列表应包含 '{expected}'")

    @classmethod
    def list_not_contains(cls, items: list, expected: Any, msg: str = ""):
        """断言列表不包含元素"""
        cls._handle_assertion(expected not in items, msg or f"列表不应包含 '{expected}'")

    # ========== 布尔断言 ==========

    @classmethod
    def is_true(cls, condition: bool, msg: str = ""):
        """断言为 True"""
        cls._handle_assertion(condition, msg or "条件应为 True")

    @classmethod
    def is_false(cls, condition: bool, msg: str = ""):
        """断言为 False"""
        cls._handle_assertion(not condition, msg or "条件应为 False")

    @classmethod
    def is_none(cls, value: Any, msg: str = ""):
        """断言为 None"""
        cls._handle_assertion(value is None, msg or "值应为 None")

    @classmethod
    def is_not_none(cls, value: Any, msg: str = ""):
        """断言不为 None"""
        cls._handle_assertion(value is not None, msg or "值不应为 None")

    # ========== 新增：类型断言 ==========

    @classmethod
    def is_instance(cls, obj, expected_type, msg: str = ""):
        """断言对象是指定类型的实例"""
        cls._handle_assertion(isinstance(obj, expected_type),
                              msg or f"Object should be instance of {expected_type}, got {type(obj)}")

    # ========== 新增：字符串匹配 ==========

    @classmethod
    def matches_regex(cls, text: str, pattern: str, msg: str = ""):
        """断言文本匹配正则表达式"""
        import re
        cls._handle_assertion(bool(re.search(pattern, str(text))),
                              msg or f"Text '{text}' should match pattern '{pattern}'")

    @classmethod
    def starts_with(cls, text: str, prefix: str, msg: str = ""):
        """断言文本以指定前缀开头"""
        cls._handle_assertion(str(text).startswith(prefix),
                              msg or f"Text '{text}' should start with '{prefix}'")

    @classmethod
    def ends_with(cls, text: str, suffix: str, msg: str = ""):
        """断言文本以指定后缀结尾"""
        cls._handle_assertion(str(text).endswith(suffix),
                              msg or f"Text '{text}' should end with '{suffix}'")

    @classmethod
    def not_empty(cls, value, msg: str = ""):
        """断言值不为空（非 None/非空字符串/非空列表/非空字典）"""
        cls._handle_assertion(value is not None and value != "" and value != [] and value != {},
                              msg or "Value should not be empty")

    @classmethod
    def length_equals(cls, items, length: int, msg: str = ""):
        """断言集合长度等于预期值"""
        actual = len(items)
        cls._handle_assertion(actual == length,
                              msg or f"Length should be {length}, got {actual}")

    @classmethod
    def length_greater(cls, items, length: int, msg: str = ""):
        """断言集合长度大于预期值"""
        actual = len(items)
        cls._handle_assertion(actual > length,
                              msg or f"Length should be > {length}, got {actual}")

    # ========== 新增：浮点数近似断言 ==========

    @classmethod
    def almost_equal(cls, actual: float, expected: float, precision: int = 2, msg: str = ""):
        """断言浮点数近似相等（指定精度）"""
        cls._handle_assertion(round(actual, precision) == round(expected, precision),
                              msg or f"{actual} should be approximately {expected} (precision={precision})")

    # ========== 新增：字典/JSON 断言 ==========

    @classmethod
    def dict_contains_subset(cls, full_dict: dict, subset: dict, msg: str = ""):
        """断言字典包含子集的所有键值对"""
        for k, v in subset.items():
            if k not in full_dict or full_dict[k] != v:
                cls._handle_assertion(False,
                                      msg or f"Dict missing or mismatched key '{k}': expected {v}, got {full_dict.get(k, 'MISSING')}")
                return
        cls._handle_assertion(True, msg or "Dict contains subset")

    @classmethod
    def dict_equals(cls, actual: dict, expected: dict, msg: str = ""):
        """断言两个字典完全相等（含详细 diff 输出）"""
        if actual != expected:
            diff = []
            all_keys = set(actual.keys()) | set(expected.keys())
            for k in all_keys:
                if k not in actual:
                    diff.append(f"  missing key: {k}")
                elif k not in expected:
                    diff.append(f"  extra key: {k}")
                elif actual[k] != expected[k]:
                    diff.append(f"  key '{k}': expected {expected[k]!r}, got {actual[k]!r}")
            cls._handle_assertion(False,
                                  msg or f"Dicts differ:\n" + "\n".join(diff))
        else:
            cls._handle_assertion(True, msg or "Dicts equal")

    # ========== 新增：页面元素断言（直接操作页面） ==========

    @classmethod
    def element_has_class(cls, page, selector: str, class_name: str, msg: str = ""):
        """断言元素包含指定的 CSS 类名"""
        classes = page.locator(selector).get_attribute("class") or ""
        cls._handle_assertion(class_name in classes.split(),
                              msg or f"Element '{selector}' should have class '{class_name}', got classes='{classes}'")

    @classmethod
    def element_count_equals(cls, page, selector: str, count: int, msg: str = ""):
        """断言匹配选择器的元素数量等于预期"""
        actual = page.locator(selector).count()
        cls._handle_assertion(actual == count,
                              msg or f"Element '{selector}' count should be {count}, got {actual}")

    @classmethod
    def element_text_equals(cls, page, selector: str, expected: str, msg: str = ""):
        """断言元素的文本内容等于预期"""
        actual = (page.locator(selector).text_content() or "").strip()
        cls._handle_assertion(actual == expected,
                              msg or f"Element '{selector}' text should be '{expected}', got '{actual}'")

    @classmethod
    def element_attribute_equals(cls, page, selector: str, attr: str, expected: str, msg: str = ""):
        """断言元素的指定属性值等于预期"""
        actual = page.locator(selector).get_attribute(attr) or ""
        cls._handle_assertion(actual == expected,
                              msg or f"Element '{selector}' attribute '{attr}' should be '{expected}', got '{actual}'")

    # ========== 新增：文件断言 ==========

    @classmethod
    def file_exists(cls, file_path: str, msg: str = ""):
        """断言文件存在"""
        import os
        cls._handle_assertion(os.path.exists(file_path),
                              msg or f"File should exist: {file_path}")

    # ========== 新增：等待条件断言 ==========

    @classmethod
    def waits_for(cls, condition_fn, timeout: int = 5, msg: str = ""):
        """等待条件函数返回 True，超时则断言失败"""
        import time
        start = time.time()
        last_error = None
        while time.time() - start < timeout:
            try:
                if condition_fn():
                    cls._handle_assertion(True, msg or "Condition met")
                    return
            except Exception as e:
                last_error = e
            time.sleep(0.1)
        cls._handle_assertion(False, msg or f"Condition not met within {timeout}s. Last error: {last_error}")


# 全局实例
assert_util = AssertUtil()
