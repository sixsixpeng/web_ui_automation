#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
run_tests.py - 统一运行入口
支持参数切换同步/异步模式、筛选Scope、控制 Allure 报告生成
"""

import argparse
import os
import sys
from datetime import datetime

from utils.path_util import path_util

# 确保项目根目录在 sys.path 中
PROJECT_ROOT = str(path_util.root)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)


def parse_args() -> argparse.Namespace:
    """解析命令行参数"""
    parser = argparse.ArgumentParser(
        description="Web UI Automation Framework - 统一运行入口",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "--async-mode", type=str, default=None,
        choices=["True", "False"],
        help="全局切换Mode：True 异步协程、False 同步 API",
    )
    parser.add_argument(
        "--env", type=str, default=None,
        choices=["dev", "test", "pre", "prod"],
        help="Override environment (dev/test/pre/prod)",
    )
    parser.add_argument(
        "--headless", type=str, default=None,
        choices=["True", "False"],
        help="动态切换无头/可视化浏览器模式",
    )
    parser.add_argument(
        "-n", "--worker", type=int, default=None,
        help="设置同步模式并发进程数量",
    )
    parser.add_argument(
        "-m", type=str, default=None,
        help='指定 mark 标签筛选执行，如 "smoke and not critical"',
    )
    parser.add_argument(
        "--file", type=str, default=None,
        help="仅运行指定单个测试文件",
    )
    parser.add_argument(
        "--module", type=str, default=None,
        help="运行指定文件夹下全部测试用例",
    )
    parser.add_argument(
        "--case", type=str, default=None,
        help="精准执行单条测试用例（完整路径::类名::方法名）",
    )
    parser.add_argument(
        "--no-report", action="store_true", default=False,
        help="Skip Allure report generation",
    )
    parser.add_argument(
        "--demo", action="store_true",
        help="仅执行 case 目录下template用例",
    )
    parser.add_argument(
        "--send-mail", type=str, default=None,
        choices=["True", "False"],
        help="动态控制本次执行结束是否推送汇总邮件",
    )
    parser.add_argument(
        "-k", type=str, default=None,
        help="关键字表达式筛选用例",
    )

    return parser.parse_args()


def main():
    """主执行逻辑"""
    args = parse_args()

    # 1. 配置来源: config.yaml (primary). .env 已废弃。
    #    命令行参数 --env 可覆盖当前环境。

    # 2. 动态Override env变量
    if args.env:
        os.environ["ENV"] = args.env
        from utils.config_util import _load as _reload_cfg
        _reload_cfg.cache_clear() if hasattr(_reload_cfg, "cache_clear") else None
        print(f"[run_tests] Override env: {args.env}")

    if args.headless:
        os.environ["HEADLESS"] = args.headless
        print(f"[run_tests] Headless: {args.headless}")

    if args.send_mail:
        os.environ["SEND_MAIL"] = args.send_mail

    # 3. 判断同步/异步模式
    is_async = False
    if args.async_mode is not None:
        is_async = args.async_mode == "True"
    else:
        is_async = False  # default sync

    mode_str = "async" if is_async else "sync"
    print(f"[run_tests] Mode: {mode_str}")

    # 4. 选择 pytest 配置
    ini_file = path_util.join_str("config", f"pytest_{mode_str}.ini")
    if not os.path.exists(ini_file):
        ini_file = path_util.join_str("config", "pytest_sync.ini")

    # 5. 构建 pytest 命令
    pytest_args = ["--rootdir", PROJECT_ROOT, "-s"]

    # 加载对应 ini 作为配置（不再用 -c，避免阻止 conftest 发现）
    # 改用 --override-ini 传递关键参数
    if is_async:
        pytest_args.extend(["--override-ini", "asyncio_mode=auto"])
    else:
        pytest_args.extend(["--override-ini", "asyncio_mode=strict"])

    # Always generate Allure report data with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    os.environ["RUN_TIMESTAMP"] = f"raw_{timestamp}"
    allure_raw_dir = path_util.join_str("reports", "allure", f"raw_{timestamp}")
    path_util.ensure_dir(allure_raw_dir)
    pytest_args.extend(["--alluredir", allure_raw_dir, "--clean-alluredir"])

    # 筛选Scope
    if args.demo:
        demo_dir = path_util.join_str("case")
        # 根据模式筛选对应目录
        mode_dir = "sync" if not is_async else "async"
        pytest_args.append(path_util.join_str("case", mode_dir))
        print(f"[run_tests] Scope: Demo template ({mode_dir})")
    elif args.file:
        pytest_args.append(args.file)
        print(f"[run_tests] File: {args.file}")
    elif args.module:
        pytest_args.append(args.module)
        print(f"[run_tests] Module: {args.module}")
    elif args.case:
        pytest_args.extend(["-k", args.case.split("::")[-1]])
        print(f"[run_tests] Case: {args.case}")
    elif args.m or args.k:
        pass  # 使用标签或关键字筛选，不限制目录
    else:
        # 默认仅运行 Demo 模板
        demo_dir = path_util.join_str("case")
        mode_dir = "sync" if not is_async else "async"
        pytest_args.append(path_util.join_str("case", mode_dir))
        print(f"[run_tests] Default scope: Demo template ({mode_dir})")

    # Mark tag filter
    if args.m:
        pytest_args.extend(["-m", args.m])  # 按标签筛选用例

    # Keyword filter
    if args.k:
        pytest_args.extend(["-k", args.k])  # 按关键字筛选用例

    # Playwright plugin (required for both sync and async)

    # xdist concurrency
    if args.worker:
        pytest_args.extend(["-n", str(args.worker)])  # 并发进程数

    # Async plugin
    if is_async:
        pytest_args.extend(["-p", "pytest_asyncio"])  # 异步协程支持

    # 异步模式自动加载 pytest-asyncio
    if is_async:
        pytest_args.extend(["-p", "pytest_asyncio"])

    print(f"[run_tests] pytest 参数: {' '.join(pytest_args)}")

    # 6. 执行 pytest
    exit_code = pytest.main(pytest_args)

    # 7. 报告后处理
    if exit_code != 2:
        report_dir = path_util.join_str("reports", "allure", "static")
        import subprocess
        subprocess.run(
            ["allure", "generate", str(allure_raw_dir), "-o", str(report_dir), "--clean"],
            capture_output=True, text=True, shell=True
        )
        print(f"\n{'=' * 50}")
        print(f"  [Allure] Allure static report generated")
        print(f"    Dir: {report_dir}")
        print(f"    Web: file:///{report_dir.replace(chr(92), chr(47))}/index.html")
        print(f"    Cmd: allure serve {allure_raw_dir}")
        print(f"{'=' * 50}")

    print(f"\n[run_tests] Done, exit code: {exit_code}")
    sys.exit(exit_code)


if __name__ == "__main__":
    # 延迟导入
    import pytest

    main()
