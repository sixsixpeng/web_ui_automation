# -*- coding: UTF-8 -*-
"""
配置模块 (config)

提供自动化测试框架的配置管理功能，包括：
- 配置文件读取：支持 YAML 格式配置文件，自动解析嵌套结构
- 多环境配置：支持 dev、staging、prod 等多环境切换，支持环境变量覆盖
- API 端点管理：集中管理所有 API 接口端点，支持路径参数替换
- 路径解析：自动处理相对路径，转换为绝对路径，支持跨平台路径兼容

主要组件：
- config_loader.py: 配置加载器，读取配置文件并提供统一访问接口
- config.yaml: 主配置文件，包含日志、浏览器、环境、超时等全局配置
- api_endpoints.yaml: API 端点配置文件，定义各个 API 接口的路径和默认参数

使用方式：
```python
from config import config

# 获取配置项
browser_type = config.get('browser.type')
base_url = config.get('base_url')
timeout = config.get('timeout', 30000)  # 带默认值

# 获取API端点
login_endpoint = config.get_endpoint('auth.login')
user_endpoint = config.get_endpoint('user.profile', user_id=123)

# 切换环境（运行时动态切换）
config.set_env('staging')
staging_url = config.get('base_url')

# 获取当前环境信息
current_env = config.get_current_env()
env_config = config.get_all_config()
```

配置优先级（从高到低）：
1. 环境变量覆盖（如 TEST_BROWSER_TYPE）
2. 运行时动态设置（config.set()）
3. 当前环境配置（dev/staging/prod）
4. 默认配置（config.yaml 中的 defaults 部分）

支持的环境变量：
- TEST_ENV: 测试环境（dev/staging/prod）
- TEST_BROWSER_TYPE: 浏览器类型
- TEST_BASE_URL: 基础URL
- TEST_HEADLESS: 是否无头模式
"""

from .config_loader import ConfigLoader

# 定义公开接口
__all__ = [
    "ConfigLoader",
    "config",  # 全局配置实例
]

# 创建全局配置实例（单例模式）
config = ConfigLoader()