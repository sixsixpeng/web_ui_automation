# -*- coding: utf-8 -*-
"""validate_util - 通用数据格式校验器"""
import re


class ValidateUtil:
    """数据格式校验工具"""

    _PHONE = re.compile(r"^1[3-9]\d{9}$")
    _EMAIL = re.compile(r"^[\w.-]+@[\w.-]+\.\w{2,}$")
    _URL = re.compile(r"^https?://[^\s/$.?#].[^\s]*$", re.I)
    _IPV4 = re.compile(r"^(?:\d{1,3}\.){3}\d{1,3}$")
    _ID_CARD = re.compile(r"^\d{17}[\dXx]$")
    _MONEY = re.compile(r"^(0|[1-9]\d*)(\.\d{1,2})?$")

    @staticmethod
    def is_phone(val: str) -> bool:
        """校验手机号（中国大陆）"""
        return bool(ValidateUtil._PHONE.match(str(val)))

    @staticmethod
    def is_email(val: str) -> bool:
        """校验是否为有效邮箱地址"""
        """Check if string is a valid email"""
        return bool(ValidateUtil._EMAIL.match(str(val)))

    @staticmethod
    def is_url(val: str) -> bool:
        """校验是否为有效 URL"""
        """Check if string is a valid HTTP URL"""
        return bool(ValidateUtil._URL.match(str(val)))

    @staticmethod
    def is_ipv4(val: str) -> bool:
        """校验是否为有效 IPv4 地址"""
        """Check if string is a valid IPv4 address"""
        if not ValidateUtil._IPV4.match(str(val)):
            return False
        parts = val.split(".")
        return all(0 <= int(p) <= 255 for p in parts)

    @staticmethod
    def is_id_card(val: str) -> bool:
        """校验身份证号（18位，含校验码验证）"""
        v = str(val).upper()
        if not ValidateUtil._ID_CARD.match(v):
            return False
        # 校验码验证
        w = [7, 9, 10, 5, 8, 4, 2, 1, 6, 3, 7, 9, 10, 5, 8, 4, 2]
        s = sum(int(v[i]) * w[i] for i in range(17))
        c = "10X98765432"
        return v[17] == c[s % 11]

    @staticmethod
    def is_money(val) -> bool:
        """校验金额格式（正数，最多两位小数）"""
        return bool(ValidateUtil._MONEY.match(str(val)))

    @staticmethod
    def is_empty(val) -> bool:
        """判断值是否为 None 或空字符串"""
        """Check if value is None or empty string"""
        return val is None or (isinstance(val, str) and val.strip() == "")

    @staticmethod
    def length_between(val: str, min_len: int = 0, max_len: int = 100) -> bool:
        """判断字符串长度是否在指定范围内"""
        """Check if string length is within range"""
        return min_len <= len(str(val)) <= max_len

    @staticmethod
    def value_between(val, min_v, max_v) -> bool:
        """判断数值是否在指定范围内"""
        """Check if numeric value is within range"""
        try:
            return min_v <= float(val) <= max_v
        except (ValueError, TypeError):
            return False

    @staticmethod
    def is_chinese(val: str) -> bool:
        """是否纯中文"""
        return bool(re.fullmatch(r"[\u4e00-\u9fff]+", str(val)))

    @staticmethod
    def has_chinese(val: str) -> bool:
        """是否包含中文"""
        return bool(re.search(r"[\u4e00-\u9fff]", str(val)))

    @staticmethod
    def is_alphanumeric(val: str) -> bool:
        """是否纯字母数字"""
        return bool(re.fullmatch(r"[a-zA-Z0-9]+", str(val)))


validate_util = ValidateUtil()
