# -*- coding: UTF-8 -*-
"""
API 接口模块 (api)

提供自动化测试框架的 API 接口封装，包括：
- API 请求封装：统一处理 HTTP 请求、响应、异常，支持认证、重试、超时控制
- 端点管理：与 config/api_endpoints.yaml 配置结合，支持路径参数、查询参数
- 业务逻辑封装：封装业务系统的 API 接口，提供面向业务的调用方法
- 响应处理：自动解析 JSON/XML 响应，提供类型提示和验证

主要组件：
- auth_api.py: 认证 API 接口封装（登录、注销、令牌管理、权限验证）
- user_api.py: 用户 API 接口封装（用户 CRUD、权限管理、个人信息）
- 其他 API：按业务需求添加的 API 接口封装（如 order_api.py, product_api.py）

API 设计原则：
1. 每个业务模块对应一个 API 类，类名以 API 结尾（如 AuthAPI）
2. API 方法对应具体的业务接口，方法名应描述业务操作（如 login, create_user）
3. 统一使用 core.APIClient 发送请求，确保一致的请求处理和错误处理
4. 统一处理响应和异常，将 HTTP 错误转换为有意义的业务异常
5. 与 config/api_endpoints.yaml 配置结合，实现端点集中管理
6. 支持认证令牌自动管理，减少测试代码中的认证逻辑

使用方式：
```python
from api import AuthAPI, UserAPI

# 通过夹具获取 API 实例（推荐方式）
def test_user_creation(user_api):
    # user_api 是通过 conftest.py 中定义的夹具提供的 UserAPI 实例
    user_data = {
        "username": "test_user",
        "email": "test@example.com",
        "password": "password123"
    }
    response = user_api.create_user(user_data)
    assert response["id"] is not None
    assert response["username"] == user_data["username"]

# 手动创建 API 实例
from config import config
from core import APIClient

# 创建 APIClient 实例
api_client = APIClient(base_url=config.get("api_base_url"))
auth_api = AuthAPI(api_client=api_client)

# 使用 API
token = auth_api.login("admin", "admin123")
print(f"认证令牌: {token}")
```

API 端点配置示例（api_endpoints.yaml）：
```yaml
auth:
  login: "/api/v1/auth/login"
  logout: "/api/v1/auth/logout"
  refresh: "/api/v1/auth/refresh"

user:
  create: "/api/v1/users"
  get: "/api/v1/users/{user_id}"
  update: "/api/v1/users/{user_id}"
  delete: "/api/v1/users/{user_id}"
  list: "/api/v1/users"
```

API 类示例（auth_api.py 结构）：
```python
from core.api_client import APIClient
from core.exception_handle import APICallException

class AuthAPI:
    def __init__(self, api_client=None):
        self.api_client = api_client or APIClient()
    
    def login(self, username, password):
        endpoint = self.api_client.config.get_endpoint("auth.login")
        data = {"username": username, "password": password}
        response = self.api_client.post(endpoint, json=data)
        return response.get("token")
    
    def logout(self, token):
        endpoint = self.api_client.config.get_endpoint("auth.logout")
        headers = {"Authorization": f"Bearer {token}"}
        self.api_client.post(endpoint, headers=headers)
```

扩展指南：
1. 在 api/ 目录创建新 API 文件，如 order_api.py
2. 定义 API 类并初始化 APIClient
3. 在 api_endpoints.yaml 中配置端点
4. 实现业务方法，处理请求和响应
5. 在此文件中导入新 API 类并添加到 __all__ 列表
"""

from .auth_api import AuthAPI
from .user_api import UserAPI

# 定义公开接口
__all__ = [
    "AuthAPI",
    "UserAPI",
]

# 未来扩展：在此处导入新 API 类并添加到 __all__ 中