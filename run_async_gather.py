# -*- coding: utf-8 -*-
"""Async concurrency demo: asyncio.gather + Semaphore"""
import os
import sys
from datetime import datetime

from utils.path_util import path_util

root = str(path_util.root)
os.chdir(root)
sys.path.insert(0, root)

import pytest

# === Allure 报告配置 ===
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
allure_raw_dir = path_util.join_str("reports", "allure", f"raw_{timestamp}")
path_util.ensure_dir(allure_raw_dir)

pytest_args = [
    "--rootdir", root,                        # 项目根目录
    "--override-ini", "asyncio_mode=auto",    # 异步模式
    "-p", "pytest_asyncio",                   # 异步协程支持
    "--alluredir", allure_raw_dir,            # Allure 报告数据目录
    "--clean-alluredir",                      # 清理旧数据
    "-vvs",                                   # 详细输出
    path_util.join_str("case", "async", "02_concurrent", "concurrent_patterns.py"),  # 并发演示用例
]

print("=" * 50)
print(" Concurrency: asyncio.gather + Semaphore")
print("=" * 50)
exit_code = pytest.main(pytest_args)

# === Allure 静态报告生成 ===
if exit_code != 2:
    import subprocess
    report_dir = path_util.join_str("reports", "allure", "static")
    subprocess.run(
        ["allure", "generate", str(allure_raw_dir), "-o", str(report_dir), "--clean"],
        capture_output=True, text=True, shell=True,
    )
    print(f"\n{'=' * 50}")
    print(f"  [Allure] 静态报告已生成")
    print(f"    目录: {report_dir}")
    print(f"    打开: file:///{report_dir.replace(chr(92), chr(47))}/index.html")
    print(f"    查看: allure serve {allure_raw_dir}")
    print(f"{'=' * 50}")

print(f"\n[run_async_gather] 完成, 退出码: {exit_code}")
sys.exit(exit_code)
