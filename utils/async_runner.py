# -*- coding: utf-8 -*-
"""async_runner - Auto-discover and concurrently execute test methods with Semaphore control"""
import asyncio
import inspect

from utils import get_logger

logger = get_logger("async_runner")

# Global semaphore for controlling max concurrency
_semaphore = None


def _load_concurrency():
    """Load max concurrency from config.yaml, fallback to 5"""
    try:
        from utils.config_util import get as cfg
        return int(cfg("async.max_concurrency", 5))
    except Exception:
        return 5


def set_max_concurrency(n: int = None):
    """
    Set global max concurrent tasks.

    并发数控制方式（优先级从高到低）:
      1. set_max_concurrency(3)  — 代码中直接指定
      2. config.yaml 中 async.max_concurrency — 全局配置
      3. 默认 5
    """
    global _semaphore
    if n is None:
        n = _load_concurrency()
    _semaphore = asyncio.Semaphore(n)
    logger.info(f"Max concurrency set to {n}")


def get_semaphore():
    """Get or create default semaphore"""
    global _semaphore
    if _semaphore is None:
        _semaphore = asyncio.Semaphore(5)
    return _semaphore


class ConcurrentGroup:
    """
    自动发现并并发执行 step_* 方法，无需手写 asyncio.gather。

    并发数控制（优先级从高到低）:
      1. 子类定义 max_concurrency = N
      2. set_max_concurrency(N) 全局设置
      3. config.yaml → async.max_concurrency
      4. 默认 5

    指定测试用例:
      - 文件级别: pytest case/async/02_concurrent/test_concurrent_group.py
      - 用例级别: pytest -k "test_login" case/async/
      - 标签级别: pytest -m smoke case/async/
      - 并发组内选择性执行: ConcurrentGroup(include=["step_valid", "step_wrong"])

    Usage:
        class LoginBatch(ConcurrentGroup):
            max_concurrency = 3

            async def step_valid(self):
                ...

        @pytest.mark.asyncio
        async def test_login_all():
            results = await LoginBatch().run()
            for name, ok, err in results:
                assert ok
    """

    max_concurrency = None  # 默认使用全局设置

    def __init__(self, include=None):
        """
        include: optional list of step names to run (e.g. ["step_valid", "step_wrong"])
                 默认 None = 运行所有 step_* 方法
        """
        self._include = include or []

    async def run(self, **kwargs):
        """
        Discover all step_* methods and run them concurrently.
        Returns list of (name, success, error) tuples.
        """
        sem = asyncio.Semaphore(self.max_concurrency or _load_concurrency())

        # Discover methods (filtered by include if specified)
        methods = []
        for name, method in inspect.getmembers(self, predicate=inspect.iscoroutinefunction):
            if name.startswith("step_") and (not self._include or name in self._include):
                methods.append((name, method))

        if not methods:
            logger.warning(f"No step_* methods found in {self.__class__.__name__}")
            return []

        logger.info(f"Running {len(methods)} steps concurrently (max {self.max_concurrency})")

        async def run_one(name, method):
            async with sem:
                try:
                    await method(**kwargs)
                    logger.info(f"  ✅ {name}")
                    return (name, True, None)
                except Exception as e:
                    logger.error(f"  ❌ {name}: {e}")
                    return (name, False, str(e))

        tasks = [run_one(name, method) for name, method in methods]
        results = await asyncio.gather(*tasks)
        return results


def concurrent_group(max_concurrency: int = 5):
    """
    Decorator: run all step_* methods in a class concurrently.

    Usage:
        @concurrent_group(max_concurrency=3)
        class Steps:
            async def step_a(self):
                ...
            async def step_b(self):
                ...

        results = await Steps().run()
    """

    def decorator(cls):
        """重试装饰器工厂函数"""
        cls.max_concurrency = max_concurrency
        if not hasattr(cls, "run"):
            cls.run = ConcurrentGroup.run
        return cls

    return decorator
