#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""
自动化测试运行脚本（简化版）
提供两种运行方式：
1. 简化模式：通过取消注释代码行选择要运行的测试类型（默认）
2. 命令行模式：保留原有命令行接口，可通过注释/取消注释切换

使用说明：
- 默认使用简化模式，直接运行脚本即可（python run_tests.py）
- 如需使用命令行模式，请注释掉简化模式的main函数，取消注释命令行模式的main函数
- 简化模式下，通过修改配置参数和取消注释代码行来选择测试类型
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path
from common.log_utils import LogUtils

# 获取日志记录器
logger = LogUtils.get_logger(__name__)


def run_command(cmd, description):
    """
    运行命令并打印输出
    
    Args:
        cmd: 命令列表
        description: 命令描述
    """
    logger.info(f"\n{'=' * 60}")
    logger.info(f"{description}")
    logger.info(f"{'=' * 60}")
    logger.info(f"执行命令: {' '.join(cmd)}")

    try:
        # 使用字节模式捕获输出，然后尝试解码，忽略解码错误
        result = subprocess.run(cmd, check=True, capture_output=True)
        
        # 尝试解码输出，忽略错误
        try:
            stdout = result.stdout.decode('utf-8', errors='ignore')
        except:
            stdout = result.stdout.decode('gbk', errors='ignore')
        
        try:
            stderr = result.stderr.decode('utf-8', errors='ignore')
        except:
            stderr = result.stderr.decode('gbk', errors='ignore')
        
        logger.info(stdout)
        if stderr:
            logger.warning(f"错误输出: {stderr}")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"命令执行失败，退出码: {e.returncode}")
        
        # 解码输出
        try:
            stdout = e.stdout.decode('utf-8', errors='ignore') if e.stdout else ""
        except:
            stdout = e.stdout.decode('gbk', errors='ignore') if e.stdout else ""
        
        try:
            stderr = e.stderr.decode('utf-8', errors='ignore') if e.stderr else ""
        except:
            stderr = e.stderr.decode('gbk', errors='ignore') if e.stderr else ""
        
        logger.info(f"标准输出: {stdout}")
        logger.warning(f"错误输出: {stderr}")
        return False


def install_dependencies():
    """安装项目依赖"""
    logger.info("正在安装依赖...")

    # 检查 requirements.txt 是否存在
    if not Path("requirements.txt").exists():
        logger.error("错误: requirements.txt 文件不存在")
        return False

    cmd = [sys.executable, "-m", "pip", "install", "-r", "requirements.txt"]
    return run_command(cmd, "安装项目依赖")


def run_ui_tests(mark=None, browser=None, headless=False, parallel=False):
    """
    运行 UI 测试
    
    Args:
        mark: pytest 标记选择器
        browser: 浏览器类型
        headless: 是否无头模式
        parallel: 是否并行执行
    """
    cmd = [sys.executable, "-m", "pytest", "-v", "-s", "--tb=short"]

    # 添加标记选择器
    if mark:
        cmd.extend(["-m", mark])
    else:
        cmd.append("-m ui")

    # 添加浏览器选项
    if browser:
        cmd.extend(["--browser-type", browser])

    if headless:
        cmd.append("--headless")

    # 并行执行
    if parallel:
        cmd.extend(["-n", "auto"])

    # 添加报告目录
    cmd.extend(["--alluredir", "report/allure_raw"])

    return run_command(cmd, "运行 UI 自动化测试")


def run_api_tests(mark=None, parallel=False):
    """
    运行 API 测试
    
    Args:
        mark: pytest 标记选择器
        parallel: 是否并行执行
    """
    cmd = [sys.executable, "-m", "pytest", "-v", "-s", "--tb=short"]

    # 添加标记选择器
    if mark:
        cmd.extend(["-m", mark])
    else:
        cmd.append("-m api")

    # 并行执行
    if parallel:
        cmd.extend(["-n", "auto"])

    # 添加报告目录
    cmd.extend(["--alluredir", "report/allure_raw"])

    return run_command(cmd, "运行 API 自动化测试")


def run_demo_tests(mark=None, browser=None, headless=False, parallel=False):
    """
    运行演示测试
    """
    cmd = [sys.executable, "-m", "pytest", "-v", "-s", "--tb=short"]

    # 添加标记选择器
    if mark:
        cmd.extend(["-m", mark])
    else:
        cmd.append("-m demo")

    # 添加浏览器选项
    if browser:
        cmd.extend(["--browser-type", browser])

    if headless:
        cmd.append("--headless")

    # 并行执行
    if parallel:
        cmd.extend(["-n", "auto"])

    # 添加报告目录
    cmd.extend(["--alluredir", "report/allure_raw"])

    # 可选：指定测试文件（如果只想运行演示测试文件）
    # cmd.append("test_case/test_demo_all_features.py")

    return run_command(cmd, "运行演示测试")


def run_all_tests(parallel=False):
    """
    运行所有测试
    
    Args:
        parallel: 是否并行执行
    """
    cmd = [sys.executable, "-m", "pytest", "-v", "-s", "--tb=short"]

    # 并行执行
    if parallel:
        cmd.extend(["-n", "auto"])

    # 添加报告目录
    cmd.extend(["--alluredir", "report/allure_raw"])

    return run_command(cmd, "运行所有测试")


def generate_report():
    """生成 Allure 报告"""
    # 检查 allure 命令是否可用
    try:
        subprocess.run(["allure", "--version"], check=True, capture_output=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        logger.warning("Allure 未安装，跳过报告生成")
        logger.warning("请安装 Allure: https://docs.qameta.io/allure/#_installing")
        return False

    # 确保报告目录存在
    Path("report/allure_html").mkdir(parents=True, exist_ok=True)

    cmd = ["allure", "generate", "report/allure_raw", "-o", "report/allure_html", "--clean"]
    if run_command(cmd, "生成 Allure 报告"):
        logger.info(f"\n报告已生成: file://{os.path.abspath('report/allure_html/index.html')}")
        return True
    return False


def open_report():
    """打开 Allure 报告"""
    # 检查报告是否存在
    report_index = Path("report/allure_html/index.html")
    if not report_index.exists():
        logger.warning("报告不存在，请先运行测试并生成报告")
        return False

    # 尝试在浏览器中打开报告
    import webbrowser
    url = f"file://{os.path.abspath('report/allure_html/index.html')}"
    print(f"在浏览器中打开报告: {url}")
    webbrowser.open(url)
    return True


def main():
    """简化的主函数 - 通过取消注释选择要运行的测试类型"""
    logger.info("=" * 60)
    logger.info("Web UI 自动化测试框架 - 简化运行脚本")
    logger.info("=" * 60)
    logger.info("\n说明：")
    logger.info("1. 通过取消注释下面的代码行来选择要运行的测试类型")
    logger.info("2. 注释掉其他不需要运行的测试类型")
    logger.info("3. 可以直接修改配置参数（浏览器类型、无头模式等）")
    logger.info("\n当前配置：")
    
    # ===== 配置参数 =====
    # 修改以下参数来调整测试行为
    browser_type = "chromium"      # 可选: "chromium", "firefox", "webkit", "chrome", "edge"
    headless = False               # 是否使用无头模式
    parallel = False               # 是否并行执行
    env = "dev"                    # 测试环境: dev, staging, prod
    mark = None                    # pytest 标记选择器，例如: "smoke", "regression"
    
    logger.info(f"  浏览器类型: {browser_type}")
    logger.info(f"  无头模式: {headless}")
    logger.info(f"  并行执行: {parallel}")
    logger.info(f"  测试环境: {env}")
    logger.info(f"  测试标记: {mark or '默认'}")
    
    # 设置环境变量
    os.environ["TEST_ENV"] = env
    
    # ===== 选择要运行的测试类型 =====
    # 取消注释其中一行，注释其他行（保留一个要运行的测试）
    
    success = True
    
    # UI 测试
    # success = run_ui_tests(
    #     mark=mark,
    #     browser=browser_type,
    #     headless=headless,
    #     parallel=parallel
    # )
    
    # API 测试
    # success = run_api_tests(mark=mark, parallel=parallel)
    
    # 演示测试（展示所有功能）
    success = run_demo_tests(
        mark=mark,
        browser=browser_type,
        headless=headless,
        parallel=parallel
    )
    
    # 所有测试
    # success = run_all_tests(parallel=parallel)
    
    # 冒烟测试
    # success = run_ui_tests(mark="smoke", browser=browser_type, headless=headless, parallel=False)
    # success = success and run_api_tests(mark="smoke", parallel=False)
    
    # 回归测试
    # success = run_all_tests(parallel=parallel)
    
    # 安装依赖（首次运行）
    # success = install_dependencies()
    
    # 仅生成报告
    # success = generate_report()
    
    # 仅打开报告
    # success = open_report()
    
    # ===== 生成报告 =====
    # 如果运行了测试，自动生成报告（如需关闭，请注释下面两行）
    if success and not any([
        # 如果是安装依赖、仅生成报告或仅打开报告，跳过报告生成
        # 这里根据上面的选择自动判断
        # 可以通过检查 success 调用的函数来判断，简单起见，我们假设运行了测试就需要生成报告
        # 如果不想生成报告，注释下面的 generate_report() 调用
    ]):
        generate_report()
    
    # 返回退出码
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
