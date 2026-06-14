# -*- coding: utf-8 -*-
"""
faker_util - Faker 随机测试数据工具
功能：合规/边界随机数据生成、批量生成、固定种子复现
"""

import random

from faker import Faker

from utils.log_util import get_logger

logger = get_logger("faker_util")


class FakerUtil:
    """标准化随机测试数据生成器（单例）"""

    _instance = None

    def __new__(cls):
        """Singleton pattern for FakerUtil"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        """Init Faker util with optional seed"""
        if self._initialized:
            return
        self._initialized = True
        # Read seed from config (optional)
        from utils.config_util import get as cfg_get
        seed = cfg_get("faker_seed", "")
        self._seed = int(seed) if seed else None
        from faker import Faker
        self._fake = Faker("zh_CN")
        if self._seed:
            Faker.seed(self._seed)
            random.seed(self._seed)
            logger.info(f"Faker 已设置随机种子: {self._seed}")

    # ========== 合规正常数据 ==========

    def valid_phone(self) -> str:
        """生成合规手机号"""
        return self._fake.phone_number()

    def valid_name(self) -> str:
        """生成中文姓名"""
        return self._fake.name()

    def valid_email(self) -> str:
        """生成邮箱"""
        return self._fake.email()

    def valid_id_card(self) -> str:
        """生成身份证号"""
        return self._fake.ssn()

    def valid_address(self) -> str:
        """生成地址"""
        return self._fake.address()

    def valid_company(self) -> str:
        """生成企业名称"""
        return self._fake.company()

    def valid_order_no(self) -> str:
        """生成订单编号"""
        return f"ORD{self._fake.random_number(digits=10, fix_len=True)}"

    def valid_url(self) -> str:
        """生成URL"""
        return self._fake.url()

    def valid_amount(self, min_val: float = 0.01, max_val: float = 999999.99) -> float:
        """生成金额"""
        return round(random.uniform(min_val, max_val), 2)

    def valid_text(self, max_nb_chars: int = 200) -> str:
        """生成合规文本"""
        return self._fake.text(max_nb_chars=max_nb_chars)

    # ========== 边界非法异常数据 ==========

    def invalid_long_text(self, length: int = 1000) -> str:
        """生成超长文本"""
        return "A" * length

    def invalid_special_chars(self) -> str:
        """生成全特殊符号字符串"""
        return "!@#$%^&*()_+-=[]{}|;:,.<>?/~`"

    def invalid_empty_string(self) -> str:
        """生成空字符串"""
        return ""

    def invalid_negative_amount(self) -> float:
        """生成负数金额"""
        return -random.uniform(1, 9999)

    def invalid_oversized_number(self) -> int:
        """生成超范围数字"""
        return 999999999999

    def invalid_phone_format(self) -> str:
        """生成违规手机号"""
        return f"1{random.randint(0, 9)}{random.randint(0, 9)}xxxx5678"

    def invalid_html_injection(self) -> str:
        """生成 HTML 注入脚本"""
        return "<script>alert('xss')</script>"

    def invalid_emoji_text(self) -> str:
        """生成包含 emoji 的文本"""
        return "测试数据🚀🔥💯✅❌"

    def invalid_sql_injection(self) -> str:
        """生成 SQL 注入字符串"""
        return "' OR 1=1 --"

    # ========== 批量生成与工具方法 ==========

    def batch_generate(self, field: str, count: int = 5, **kwargs) -> list:
        """批量生成指定字段的随机数据（去重可选）"""
        results = []
        for _ in range(count):
            method = getattr(self, f"valid_{field}", None)
            if method:
                results.append(method(**kwargs))
            else:
                results.append(self._fake.word())
        return results

    def user_profile(self) -> dict:
        """生成完整的用户档案"""
        return {
            "name": self.valid_name(),
            "phone": self.valid_phone(),
            "email": self.valid_email(),
            "address": self.valid_address(),
            "id_card": self.valid_id_card(),
            "company": self.valid_company(),
        }

    def order_data(self) -> dict:
        """生成订单测试数据"""
        return {
            "order_no": self.valid_order_no(),
            "amount": self.valid_amount(),
            "buyer": self.valid_name(),
            "phone": self.valid_phone(),
            "address": self.valid_address(),
        }

    def set_seed(self, seed: int):
        """动态设置随机种子"""
        self._seed = seed
        Faker.seed(seed)
        random.seed(seed)
        logger.info(f"Faker 种子已更新: {seed}")


# 全局单例
faker_util = FakerUtil()
