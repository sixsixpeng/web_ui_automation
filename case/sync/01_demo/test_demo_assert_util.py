# -*- coding: utf-8 -*-
import allure
import pytest
import time

from utils import AssertUtil, get_logger

logger = get_logger("demo_sync_assert")


@pytest.mark.demo
class TestDemoAssertUtilSync:
    @allure.feature("Assert Tools")
    @allure.story("All assertions")
    @allure.title("Test all assertion methods")
    def test_basic_assertions(self):
        logger.info("=== Testing all assertions ===")
        AssertUtil.equals(1 + 1, 2);
        time.sleep(0.3)
        AssertUtil.not_equals(1, 2);
        time.sleep(0.3)
        AssertUtil.greater_than(5, 3);
        time.sleep(0.3)
        AssertUtil.less_than(3, 5);
        time.sleep(0.3)
        AssertUtil.is_true(True);
        time.sleep(0.3)
        AssertUtil.is_false(False);
        time.sleep(0.3)
        AssertUtil.is_none(None);
        time.sleep(0.3)
        AssertUtil.is_not_none("hello");
        time.sleep(0.3)
        AssertUtil.list_contains([1, 2, 3], 2);
        time.sleep(0.3)
        AssertUtil.starts_with("hello", "he");
        time.sleep(0.3)
        AssertUtil.ends_with("hello", "lo");
        time.sleep(0.3)
        AssertUtil.matches_regex("abc123", r"\d+");
        time.sleep(0.3)
        AssertUtil.not_empty([1, 2, 3]);
        time.sleep(0.3)
        AssertUtil.length_equals([1, 2, 3], 3);
        time.sleep(0.3)
        logger.info("=== All assertions passed ===")
