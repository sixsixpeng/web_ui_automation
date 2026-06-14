# -*- coding: utf-8 -*-
"""Async + xdist: sync cases only (async skipped)"""
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
    "--alluredir", allure_raw_dir,            # Allure 报告数据目录
    "--clean-alluredir",                      # 清理旧数据
    "-n", "3",                                # 并发进程数
    "--ignore", path_util.join_str("case", "async"),  # 跳过异步用例（与xdist冲突）
    "-vvs",                                   # 详细输出
    path_util.join_str("case"),               # 测试目录
]

print("=" * 55)
print(" Concurrency: sync + xdist 3 workers")
print(" Note: async + xdist conflict, async/ skipped")
print("=" * 55)
exit_code = pytest.main(pytest_args)

# === Allure 静态报告生成 ===
if exit_code != 2:
    import subprocess
    report_dir = path_util.join_str("reports", "allure", "static")
    subprocess.run(
        ["allure", "generate", str(allure_raw_dir), "-o", str(report_dir), "--clean"],
        capture_output=True, text=True, shell=True,
    )
    print("")
    print("=" * 50)
    print("  [Allure] 静态报告已生成")
    print(f"    目录: {report_dir}")
    print(f"    打开: file:///{report_dir.replace(chr(92), chr(47))}/index.html")
    print(f"    查看: allure serve {allure_raw_dir}")
    print("=" * 50)

print(f"\n[run_async_xdist] 完成, 退出码: {exit_code}")
sys.exit(exit_code)
