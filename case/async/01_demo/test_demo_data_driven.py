# -*- coding: utf-8 -*-
"""Async Demo - Data driven (no browser needed)"""
import allure
import pytest

from utils import faker_util, get_logger

logger = get_logger("demo_async_data")


@pytest.mark.demo
@pytest.mark.asyncio
class TestDemoDataDrivenAsync:
    @allure.feature("Data")
    @allure.story("Faker")
    @allure.title("Async Demo: Faker data")
    async def test_faker_data(self):
        user = faker_util.user_profile()
        assert user["name"] and user["phone"]
        logger.info(f"Faker: {user['name']}")
