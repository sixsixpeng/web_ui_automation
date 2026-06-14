# -*- coding: utf-8 -*-
"""
uuid_util - 全局唯一标识符生成工具
基于 Python uuid 模块，提供多种格式的 UUID 生成方法
适用场景：订单号、流水号、请求ID、文件名、token等
"""

import random
import time
import uuid
from datetime import datetime


class UuidUtil:
    """UUID 生成工具类"""

    # ========== 标准 UUID（4 种版本） ==========

    @staticmethod
    def uuid1() -> str:
        """基于时间戳+MAC地址（标准UUID v1），如 7c8e1a2e-3d4f-11ec-8d3a-000c291e1a2b"""
        return str(uuid.uuid1())

    @staticmethod
    def uuid3(name: str, namespace: uuid.UUID = uuid.NAMESPACE_DNS) -> str:
        """基于MD5命名空间（UUID v3），相同name生成相同UUID"""
        return str(uuid.uuid3(namespace, name))

    @staticmethod
    def uuid4() -> str:
        """完全随机（UUID v4），最常用，如 9a3b8c7d-5e6f-4a1b-8c9d-0e1f2a3b4c5d"""
        return str(uuid.uuid4())

    @staticmethod
    def uuid5(name: str, namespace: uuid.UUID = uuid.NAMESPACE_DNS) -> str:
        """基于SHA-1命名空间（UUID v5），相同name生成相同UUID"""
        return str(uuid.uuid5(namespace, name))

    # ========== 紧凑格式（去掉连字符） ==========

    @staticmethod
    def hex() -> str:
        """32位十六进制字符串（无连字符），如 9a3b8c7d5e6f4a1b8c9d0e1f2a3b4c5d"""
        return uuid.uuid4().hex

    @staticmethod
    def hex_upper() -> str:
        """32位大写十六进制字符串"""
        return uuid.uuid4().hex.upper()

    # ========== 纯数字格式 ==========

    @staticmethod
    def int_id(length: int = 16) -> str:
        """生成指定位数的纯数字ID（基于时间戳+随机数）"""
        ts = int(time.time() * 1000000)
        rand = random.randint(10 ** (length - 10), 10 ** (length - 5))
        return str(int(str(ts) + str(rand)))[:length]

    @staticmethod
    def short() -> str:
        """8位短ID（适合短链接、短标识）"""
        return uuid.uuid4().hex[:8]

    @staticmethod
    def short_16() -> str:
        """16位短ID"""
        return uuid.uuid4().hex[:16]

    # ========== 带时间戳的ID ==========

    @staticmethod
    def ts_uuid() -> str:
        """带时间戳的UUID: 20260614_132842_9a3b8c7d"""
        ts = datetime.now().strftime('%Y%m%d_%H%M%S')
        return f'{ts}_{uuid.uuid4().hex[:8]}'

    @staticmethod
    def ts_seq(prefix: str = '') -> str:
        """带前缀+时间戳+随机后缀: ORD_20260614_132842_3b8c7d"""
        ts = datetime.now().strftime('%Y%m%d_%H%M%S')
        suffix = uuid.uuid4().hex[:6]
        if prefix:
            return f'{prefix}_{ts}_{suffix}'
        return f'{ts}_{suffix}'

    @staticmethod
    def datetime_id(fmt: str = '%Y%m%d%H%M%S') -> str:
        """纯时间戳ID（按格式定制），默认 20260614132842"""
        return datetime.now().strftime(fmt)

    # ========== 业务场景专用 ==========

    @staticmethod
    def order_no() -> str:
        """模拟订单号: ORD202606141328423b8c7d"""
        ts = datetime.now().strftime('%Y%m%d%H%M%S')
        return f'ORD{ts}{uuid.uuid4().hex[:6].upper()}'

    @staticmethod
    def trace_id() -> str:
        """链路追踪ID: trc_9a3b8c7d5e6f4a1b"""
        return 'trc_' + uuid.uuid4().hex[:16]

    @staticmethod
    def session_id() -> str:
        """会话ID: sess_9a3b8c7d5e6f4a1b8c9d0e1f"""
        return 'sess_' + uuid.uuid4().hex

    @staticmethod
    def file_name(ext: str = '.png') -> str:
        """文件名: 20260614_132842_9a3b8c7d.png"""
        ts = datetime.now().strftime('%Y%m%d_%H%M%S')
        uid = uuid.uuid4().hex[:8]
        return f'{ts}_{uid}{ext}'

    @staticmethod
    def token() -> str:
        """模拟 Token 32位: tok_9a3b8c7d5e6f4a1b8c9d0e1f2a3b4c5d"""
        return 'tok_' + uuid.uuid4().hex

    # ========== 批量生成 ==========

    @staticmethod
    def batch(method: str = 'uuid4', count: int = 5) -> list:
        """批量生成UUID，method可选: uuid4/hex/short/int_id"""
        results = []
        for _ in range(count):
            if method == 'uuid4':
                results.append(UuidUtil.uuid4())
            elif method == 'hex':
                results.append(UuidUtil.hex())
            elif method == 'short':
                results.append(UuidUtil.short())
            elif method == 'int_id':
                results.append(UuidUtil.int_id())
            elif method == 'ts_uuid':
                results.append(UuidUtil.ts_uuid())
            elif method == 'order_no':
                results.append(UuidUtil.order_no())
            else:
                results.append(str(uuid.uuid4()))
        return results

    @staticmethod
    def unique_list(count: int = 10, method: str = 'hex') -> list:
        """生成不重复ID列表（去重保证）"""
        s = set()
        while len(s) < count:
            if method == 'hex':
                s.add(UuidUtil.hex())
            elif method == 'short':
                s.add(UuidUtil.short())
            else:
                s.add(UuidUtil.uuid4())
        return list(s)


uuid_util = UuidUtil()
