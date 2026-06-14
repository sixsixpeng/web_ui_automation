# -*- coding: utf-8 -*-
"""
cache_util - 内存本地缓存工具
功能：全局内存键值缓存，支持过期时间和同步/异步隔离
"""

import time
from typing import Any

from utils.log_util import get_logger

logger = get_logger("cache_util")


class CacheItem:
    """缓存条目"""

    def __init__(self, value: Any, ttl: int = None):
        """Init cache storage dict"""
        self.value = value
        self.created_at = time.time()
        self.ttl = ttl  # 过期时间（秒）

    @property
    def is_expired(self) -> bool:
        """判断缓存条目是否已过期"""
        """Check if cache item has expired"""
        if self.ttl is None:
            return False
        return time.time() - self.created_at > self.ttl


class CacheUtil:
    """内存缓存工具（单例）"""

    _instance = None

    def __new__(cls):
        """Singleton pattern"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._cache = {}
        return cls._instance

    def __init__(self):
        """Init cache storage dict"""
        pass

    def _make_key(self, key: str, mode: str = "sync") -> str:
        """生成隔离的缓存键"""
        return f"{mode}:{key}"

    def set(self, key: str, value: Any, ttl: int = None, mode: str = "sync"):
        """设置缓存"""
        cache_key = self._make_key(key, mode)
        self._cache[cache_key] = CacheItem(value, ttl)
        logger.debug(f"缓存设置: {cache_key}")

    def get(self, key: str, default: Any = None, mode: str = "sync") -> Any:
        """获取缓存"""
        cache_key = self._make_key(key, mode)
        item = self._cache.get(cache_key)
        if item is None:
            return default
        if item.is_expired:
            del self._cache[cache_key]
            logger.debug(f"缓存已过期: {cache_key}")
            return default
        return item.value

    def delete(self, key: str, mode: str = "sync"):
        """删除指定缓存"""
        cache_key = self._make_key(key, mode)
        self._cache.pop(cache_key, None)

    def clear(self, mode: str = None):
        """清空缓存（指定 mode 或全部）"""
        if mode:
            keys_to_delete = [k for k in self._cache if k.startswith(f"{mode}:")]
            for k in keys_to_delete:
                del self._cache[k]
            logger.info(f"缓存清空（{mode}模式）: 共 {len(keys_to_delete)} 条")
        else:
            self._cache.clear()
            logger.info("全局缓存已全部清空")

    @property
    def size(self) -> int:
        """当前缓存条目数"""
        self._clean_expired()
        return len(self._cache)

    def _clean_expired(self):
        """清理过期缓存"""
        now = time.time()
        expired = [k for k, v in self._cache.items() if v.is_expired]
        for k in expired:
            del self._cache[k]

    def exists(self, key: str, mode: str = "sync") -> bool:
        """检查缓存是否存在且未过期"""
        return self.get(key, mode=mode) is not None

    def get_or_set(self, key: str, factory, ttl: int = None, mode: str = "sync") -> Any:
        """获取缓存，不存在则通过 factory 创建"""
        value = self.get(key, mode=mode)
        if value is None:
            value = factory() if callable(factory) else factory
            self.set(key, value, ttl, mode)
        return value


# 全局单例
cache_util = CacheUtil()
