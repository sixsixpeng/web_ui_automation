# -*- coding: UTF-8 -*-
"""
公共工具模块 (common)

提供自动化测试框架的通用工具和辅助功能，包括：
- 数据生成器：使用 Faker 生成随机测试数据，支持用户、产品、订单等多种数据类型
- 文件操作：支持 Excel、YAML、JSON、CSV 等格式的读写，提供统一的数据加载接口
- 日志工具：彩色控制台输出、按天分割日志、模块化级别控制、ANSI 转义码彩色方案
- Allure 工具：截图附件、页面源码附件、日志附件等报告增强功能

主要组件：
- data_generator: 测试数据生成器，提供丰富的随机数据生成方法
- file_utils: 文件操作工具，支持多种文件格式的读写和解析
- log_utils: 高级日志工具，包含彩色格式化器、按天分割处理器、模块化级别控制器
- allure_utils: Allure 报告工具，简化测试报告中的附件添加操作

使用方式：
```python
from common import data_generator, file_utils, LogUtils, allure_utils

# 生成测试数据
user_data = data_generator.user_data()
product_data = data_generator.product_data()

# 文件操作
config_data = file_utils.load_yaml("config/config.yaml")
test_cases = file_utils.load_excel("test_data/test_cases.xlsx")

# 日志记录
logger = LogUtils.get_logger(__name__)
logger.info("测试开始执行")

# Allure 报告增强
allure_utils.attach_screenshot(page, "登录页面截图")
allure_utils.attach_page_source(page, "页面源码")
```

全局工具实例：
- `data_generator`: DataGenerator 的单例实例
- `file_utils`: FileUtils 的单例实例
- `allure_utils`: AllureUtils 的单例实例
- `LogUtils`: 日志工具类，提供静态方法获取日志记录器
"""

from .data_generator import DataGenerator
from .file_utils import FileUtils
from .log_utils import LogUtils, AdvancedLogUtils, ColoredFormatter
from .allure_utils import AllureUtils

# 定义公开接口
__all__ = [
    # 数据生成
    "DataGenerator",
    "data_generator",  # DataGenerator 实例
    
    # 文件操作
    "FileUtils",
    "file_utils",  # FileUtils 实例
    
    # 日志工具
    "LogUtils",
    "AdvancedLogUtils",
    "ColoredFormatter",
    
    # Allure 工具
    "AllureUtils",
    "allure_utils",  # AllureUtils 实例
]

# 创建全局工具实例（单例模式）
data_generator = DataGenerator()
file_utils = FileUtils()
allure_utils = AllureUtils()

# 日志工具已在其模块中初始化，无需重复创建