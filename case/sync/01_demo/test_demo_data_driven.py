# -*- coding: utf-8 -*-
import allure
import pytest
import time

from utils import data_util, faker_util, AssertUtil, get_logger

logger = get_logger("demo_sync_data")


@pytest.mark.demo
class TestDemoDataDrivenSync:
    @allure.feature("Data Driven")
    @allure.story("Faker data")
    @allure.title("Generate fake data")
    def test_faker_data(self):
        logger.info("=== Generating fake data ===")
        user = faker_util.user_profile();
        time.sleep(0.3)
        AssertUtil.is_not_none(user["name"]);
        time.sleep(0.2)
        AssertUtil.is_not_none(user["phone"]);
        time.sleep(0.2)
        AssertUtil.matches_regex(user["phone"], r"^1\d{10}$");
        time.sleep(0.2)
        order = faker_util.order_data();
        time.sleep(0.3)
        AssertUtil.is_not_none(order["order_no"]);
        time.sleep(0.2)
        items = faker_util.batch_generate("phone", 3);
        time.sleep(0.3)
        AssertUtil.length_equals(items, 3);
        time.sleep(0.2)
        logger.info("Faker data verified")

    @allure.feature("Data Driven")
    @allure.story("CSV data")
    @allure.title("Read CSV data")
    def test_csv_data(self):
        logger.info("=== Reading CSV ===")
        csv_data = data_util.read_csv("case_data.csv");
        time.sleep(0.3)
        AssertUtil.not_empty(csv_data);
        time.sleep(0.2)
        AssertUtil.is_true("username" in csv_data[0]);
        time.sleep(0.2)
        logger.info(f"CSV read: {len(csv_data)} rows")
