# -*- coding: UTF-8 -*-
"""
数据生成器
使用 Faker 生成随机、真实的测试数据
"""

import random
import string
from typing import Optional, Dict, Any, List
from faker import Faker


class DataGenerator:
    """数据生成器"""
    
    def __init__(self, locale: str = "zh_CN"):
        """
        初始化数据生成器
        
        Args:
            locale: 地区设置，支持 'zh_CN', 'en_US' 等
        """
        self.fake = Faker(locale)
        self.locale = locale
    
    def random_string(self, length: int = 10, prefix: str = "") -> str:
        """
        生成随机字符串
        
        Args:
            length: 字符串长度
            prefix: 前缀
            
        Returns:
            str: 随机字符串
        """
        chars = string.ascii_letters + string.digits
        random_str = ''.join(random.choice(chars) for _ in range(length))
        return prefix + random_str
    
    def random_number(self, min_value: int = 1, max_value: int = 100) -> int:
        """
        生成随机整数
        
        Args:
            min_value: 最小值
            max_value: 最大值
            
        Returns:
            int: 随机整数
        """
        return random.randint(min_value, max_value)
    
    def random_float(self, min_value: float = 0.0, max_value: float = 100.0, 
                     decimal_places: int = 2) -> float:
        """
        生成随机浮点数
        
        Args:
            min_value: 最小值
            max_value: 最大值
            decimal_places: 小数位数
            
        Returns:
            float: 随机浮点数
        """
        value = random.uniform(min_value, max_value)
        return round(value, decimal_places)
    
    def random_boolean(self) -> bool:
        """生成随机布尔值"""
        return random.choice([True, False])
    
    def random_choice(self, choices: List[Any]) -> Any:
        """
        从列表中随机选择
        
        Args:
            choices: 候选列表
            
        Returns:
            Any: 随机选择的元素
        """
        return random.choice(choices)
    
    # 个人信息生成
    def name(self) -> str:
        """生成姓名"""
        return self.fake.name()
    
    def first_name(self) -> str:
        """生成名"""
        return self.fake.first_name()
    
    def last_name(self) -> str:
        """生成姓"""
        return self.fake.last_name()
    
    def username(self, min_length: int = 6, max_length: int = 12) -> str:
        """
        生成用户名
        
        Args:
            min_length: 最小长度
            max_length: 最大长度
            
        Returns:
            str: 用户名
        """
        if self.locale.startswith("zh"):
            # 中文环境下使用拼音
            return self.fake.user_name()
        else:
            length = random.randint(min_length, max_length)
            return self.random_string(length)
    
    def email(self) -> str:
        """生成邮箱地址"""
        return self.fake.email()
    
    def phone_number(self) -> str:
        """生成手机号"""
        if self.locale.startswith("zh"):
            # 中国手机号
            return self.fake.phone_number()
        else:
            return self.fake.phone_number()
    
    def password(self, length: int = 12) -> str:
        """
        生成密码
        
        Args:
            length: 密码长度
            
        Returns:
            str: 密码
        """
        chars = string.ascii_letters + string.digits + "!@#$%^&*"
        return ''.join(random.choice(chars) for _ in range(length))
    
    # 地址信息生成
    def address(self) -> str:
        """生成地址"""
        return self.fake.address()
    
    def city(self) -> str:
        """生成城市"""
        return self.fake.city()
    
    def province(self) -> str:
        """生成省份"""
        if self.locale.startswith("zh"):
            return self.fake.province()
        else:
            return self.fake.state()
    
    def postcode(self) -> str:
        """生成邮编"""
        return self.fake.postcode()
    
    def country(self) -> str:
        """生成国家"""
        return self.fake.country()
    
    # 公司信息生成
    def company(self) -> str:
        """生成公司名"""
        return self.fake.company()
    
    def job(self) -> str:
        """生成职位"""
        return self.fake.job()
    
    # 网络信息生成
    def url(self) -> str:
        """生成 URL"""
        return self.fake.url()
    
    def ipv4(self) -> str:
        """生成 IPv4 地址"""
        return self.fake.ipv4()
    
    def user_agent(self) -> str:
        """生成 User-Agent"""
        return self.fake.user_agent()
    
    # 日期时间生成
    def date(self, start_date: str = "-30y", end_date: str = "today") -> str:
        """
        生成日期字符串
        
        Args:
            start_date: 开始日期，如 '-30y' 表示30年前
            end_date: 结束日期，如 'today' 表示今天
            
        Returns:
            str: 日期字符串 (YYYY-MM-DD)
        """
        date_obj = self.fake.date_between(start_date=start_date, end_date=end_date)
        return date_obj.strftime("%Y-%m-%d")
    
    def datetime(self, start_date: str = "-30y", end_date: str = "now") -> str:
        """
        生成日期时间字符串
        
        Args:
            start_date: 开始日期
            end_date: 结束日期
            
        Returns:
            str: 日期时间字符串 (YYYY-MM-DD HH:MM:SS)
        """
        datetime_obj = self.fake.date_time_between(start_date=start_date, end_date=end_date)
        return datetime_obj.strftime("%Y-%m-%d %H:%M:%S")
    
    def time(self) -> str:
        """生成时间字符串"""
        return self.fake.time()
    
    # 文本生成
    def sentence(self, nb_words: int = 6) -> str:
        """生成句子"""
        return self.fake.sentence(nb_words=nb_words)
    
    def paragraph(self, nb_sentences: int = 3) -> str:
        """生成段落"""
        return self.fake.paragraph(nb_sentences=nb_sentences)
    
    def text(self, max_nb_chars: int = 200) -> str:
        """生成文本"""
        return self.fake.text(max_nb_chars=max_nb_chars)
    
    # 特定业务数据生成
    def user_data(self, include_password: bool = True) -> Dict[str, Any]:
        """
        生成用户数据
        
        Args:
            include_password: 是否包含密码
            
        Returns:
            Dict: 用户数据
        """
        user_data = {
            "username": self.username(),
            "email": self.email(),
            "phone": self.phone_number(),
            "first_name": self.first_name(),
            "last_name": self.last_name(),
            "address": self.address(),
            "city": self.city(),
            "province": self.province(),
            "postcode": self.postcode(),
            "country": self.country()
        }
        
        if include_password:
            user_data["password"] = self.password()
        
        return user_data
    
    def product_data(self) -> Dict[str, Any]:
        """
        生成产品数据
        
        Returns:
            Dict: 产品数据
        """
        return {
            "name": f"产品_{self.random_string(8)}",
            "description": self.sentence(10),
            "price": self.random_float(10.0, 1000.0),
            "stock": self.random_number(1, 1000),
            "sku": f"SKU_{self.random_string(10).upper()}",
            "category": self.random_choice(["电子产品", "服装", "食品", "图书", "家居"])
        }
    
    def order_data(self, user_id: Optional[int] = None, product_ids: Optional[List[int]] = None) -> Dict[str, Any]:
        """
        生成订单数据
        
        Args:
            user_id: 用户ID，如果为None则生成随机ID
            product_ids: 产品ID列表，如果为None则生成随机列表
            
        Returns:
            Dict: 订单数据
        """
        if user_id is None:
            user_id = self.random_number(1000, 9999)
        
        if product_ids is None:
            product_ids = [self.random_number(100, 999) for _ in range(self.random_number(1, 5))]
        
        return {
            "user_id": user_id,
            "product_ids": product_ids,
            "quantity": self.random_number(1, 10),
            "total_amount": self.random_float(50.0, 5000.0),
            "shipping_address": self.address(),
            "billing_address": self.address(),
            "order_date": self.date(),
            "status": self.random_choice(["pending", "processing", "shipped", "delivered", "cancelled"])
        }


# 创建全局数据生成器实例（中文）
data_generator = DataGenerator("zh_CN")

# 创建英文数据生成器实例
data_generator_en = DataGenerator("en_US")