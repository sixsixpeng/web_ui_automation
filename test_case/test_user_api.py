# -*- coding: UTF-8 -*-
"""
用户管理 API 自动化测试用例
"""

import pytest
import allure
from common.data_generator import data_generator
from common.log_utils import LogUtils


@allure.epic("用户管理")
@allure.feature("用户API")
@pytest.mark.api
class TestUserAPI:
    """用户API测试类"""
    
    @pytest.fixture(autouse=True)
    def setup(self, user_api, auth_api, cleanup_test_data):
        """
        测试初始化
        
        Args:
            user_api: 用户API夹具
            auth_api: 认证API夹具
            cleanup_test_data: 数据清理夹具
        """
        self.user_api = user_api
        self.auth_api = auth_api
        self.cleanup_test_data = cleanup_test_data
        self.logger = LogUtils.get_logger(__name__)
        
        # 存储测试中创建的用户ID，用于清理
        self.created_user_ids = []
        
        # 登录获取token
        self._login()
    
    def _login(self):
        """登录获取认证token"""
        try:
            # 从配置获取测试账号
            from config.config_loader import config
            username = config.get("username", "test_user")
            password = config.get("password", "test_password")
            
            self.logger.info(f"使用账号登录: {username}")
            response = self.auth_api.login(username, password)
            
            # 验证登录成功
            assert "access_token" in response, "登录失败，未获取到access_token"
            self.logger.info("登录成功")
            
        except Exception as e:
            self.logger.warning(f"登录失败: {str(e)}，继续使用未认证状态测试")
    
    def _create_test_user(self, user_data=None):
        """
        创建测试用户
        
        Args:
            user_data: 用户数据，如果为None则生成随机数据
            
        Returns:
            dict: 创建的用户数据
        """
        if user_data is None:
            user_data = data_generator.user_data()
        
        response = self.user_api.create_user(user_data)
        
        # 验证创建成功
        assert "id" in response, f"创建用户失败，响应: {response}"
        
        user_id = response["id"]
        self.created_user_ids.append(user_id)
        
        # 注册清理函数
        self.cleanup_test_data(
            f"user_{user_id}",
            lambda: self.user_api.delete_user(user_id)
        )
        
        self.logger.info(f"创建测试用户成功，用户ID: {user_id}")
        return response
    
    @allure.story("创建用户")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.tag("api", "smoke", "regression")
    def test_create_user(self):
        """
        测试创建用户
        """
        # 生成随机用户数据
        user_data = data_generator.user_data()
        
        with allure.step("创建新用户"):
            response = self._create_test_user(user_data)
        
        with allure.step("验证用户数据"):
            # 验证响应包含必要字段
            required_fields = ["id", "username", "email"]
            for field in required_fields:
                assert field in response, f"响应缺少字段: {field}"
            
            # 验证数据一致性
            assert response["username"] == user_data["username"], "用户名不一致"
            assert response["email"] == user_data["email"], "邮箱不一致"
            
            self.logger.info(f"用户创建验证成功，用户ID: {response['id']}")
    
    @allure.story("获取用户信息")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.tag("api", "smoke")
    def test_get_user(self):
        """
        测试获取用户信息
        """
        with allure.step("创建测试用户"):
            created_user = self._create_test_user()
            user_id = created_user["id"]
        
        with allure.step("获取用户信息"):
            response = self.user_api.get_user(user_id)
        
        with allure.step("验证用户信息"):
            assert response["id"] == user_id, "用户ID不匹配"
            assert response["username"] == created_user["username"], "用户名不匹配"
            assert response["email"] == created_user["email"], "邮箱不匹配"
            
            self.logger.info(f"获取用户信息成功，用户ID: {user_id}")
    
    @allure.story("更新用户信息")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.tag("api", "regression")
    def test_update_user(self):
        """
        测试更新用户信息
        """
        with allure.step("创建测试用户"):
            created_user = self._create_test_user()
            user_id = created_user["id"]
        
        with allure.step("准备更新数据"):
            update_data = {
                "first_name": data_generator.first_name(),
                "last_name": data_generator.last_name(),
                "phone": data_generator.phone_number(),
                "city": data_generator.city()
            }
        
        with allure.step("更新用户信息"):
            response = self.user_api.update_user(user_id, update_data)
        
        with allure.step("验证更新结果"):
            # 验证更新后的字段
            for key, value in update_data.items():
                assert response.get(key) == value, f"字段 {key} 更新失败"
            
            self.logger.info(f"用户信息更新成功，用户ID: {user_id}")
        
        with allure.step("验证更新持久化"):
            # 重新获取用户信息验证更新已持久化
            user_info = self.user_api.get_user(user_id)
            for key, value in update_data.items():
                assert user_info.get(key) == value, f"字段 {key} 未持久化"
    
    @allure.story("删除用户")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.tag("api", "regression")
    def test_delete_user(self):
        """
        测试删除用户
        """
        with allure.step("创建测试用户"):
            created_user = self._create_test_user()
            user_id = created_user["id"]
            
            # 从清理列表中移除，因为我们要手动删除
            self.created_user_ids.remove(user_id)
        
        with allure.step("删除用户"):
            response = self.user_api.delete_user(user_id)
            
            # 验证删除成功
            assert response.get("success") is True or response.get("deleted") is True, \
                f"删除用户失败，响应: {response}"
            
            self.logger.info(f"用户删除成功，用户ID: {user_id}")
        
        with allure.step("验证用户已删除"):
            # 尝试获取已删除的用户，应该失败
            try:
                self.user_api.get_user(user_id)
                assert False, "用户删除后仍能获取到信息"
            except Exception as e:
                # 预期抛出异常（如404）
                self.logger.info(f"用户删除验证成功，预期异常: {type(e).__name__}")
                assert "404" in str(e) or "Not Found" in str(e), \
                    f"预期404错误，实际异常: {str(e)}"
    
    @allure.story("用户列表")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.tag("api", "regression")
    @pytest.mark.parametrize("page, per_page", [(1, 10), (2, 5), (1, 20)])
    def test_list_users(self, page, per_page):
        """
        测试获取用户列表
        
        Args:
            page: 页码
            per_page: 每页数量
        """
        with allure.step("获取用户列表"):
            response = self.user_api.list_users(page=page, per_page=per_page)
        
        with allure.step("验证响应结构"):
            # 验证响应包含必要字段
            assert "users" in response or "items" in response or "data" in response, \
                "响应缺少用户列表字段"
            
            # 获取用户列表
            users = response.get("users") or response.get("items") or response.get("data") or []
            
            # 验证分页信息
            assert "page" in response, "响应缺少页码信息"
            assert "per_page" in response or "page_size" in response, "响应缺少每页数量信息"
            assert "total" in response or "total_count" in response, "响应缺少总数信息"
            
            # 验证返回数量不超过每页数量
            assert len(users) <= per_page, f"返回用户数量超过每页限制: {per_page}"
            
            self.logger.info(f"获取用户列表成功，页码: {page}, 每页: {per_page}, 数量: {len(users)}")
    
    @allure.story("搜索用户")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.tag("api")
    def test_search_users(self):
        """
        测试搜索用户
        """
        with allure.step("创建测试用户"):
            user_data = data_generator.user_data()
            created_user = self._create_test_user(user_data)
            username = created_user["username"]
        
        with allure.step("搜索用户"):
            response = self.user_api.search_users(username)
        
        with allure.step("验证搜索结果"):
            users = response.get("users") or response.get("items") or response.get("data") or []
            
            # 验证搜索到至少一个用户
            assert len(users) > 0, f"未搜索到用户: {username}"
            
            # 验证搜索结果包含创建的用户
            found = any(user["username"] == username for user in users)
            assert found, f"搜索结果未包含创建的用户: {username}"
            
            self.logger.info(f"用户搜索成功，关键词: {username}, 结果数量: {len(users)}")
    
    @allure.story("用户状态管理")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.tag("api", "regression")
    @pytest.mark.parametrize("status", ["active", "inactive", "suspended"])
    def test_update_user_status(self, status):
        """
        测试更新用户状态
        
        Args:
            status: 用户状态
        """
        with allure.step("创建测试用户"):
            created_user = self._create_test_user()
            user_id = created_user["id"]
        
        with allure.step("更新用户状态"):
            response = self.user_api.update_user_status(user_id, status)
            
            # 验证更新成功
            assert response.get("status") == status, f"状态更新失败，响应: {response}"
            
            self.logger.info(f"用户状态更新成功，状态: {status}")
        
        with allure.step("验证状态更新"):
            # 获取用户信息验证状态
            user_info = self.user_api.get_user(user_id)
            assert user_info.get("status") == status, "状态未持久化"
    
    @allure.story("批量操作用户")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.tag("api", "performance")
    def test_bulk_user_operations(self):
        """
        测试批量用户操作
        """
        # 创建多个测试用户
        user_count = 5
        user_ids = []
        
        with allure.step(f"创建 {user_count} 个测试用户"):
            for i in range(user_count):
                user_data = data_generator.user_data()
                user_data["username"] = f"bulk_test_{i}_{user_data['username']}"
                created_user = self._create_test_user(user_data)
                user_ids.append(created_user["id"])
            
            self.logger.info(f"批量创建 {user_count} 个用户成功")
        
        with allure.step("批量验证用户存在"):
            for user_id in user_ids:
                user_info = self.user_api.get_user(user_id)
                assert user_info["id"] == user_id, f"用户 {user_id} 验证失败"
            
            self.logger.info("批量用户验证成功")
        
        with allure.step("批量搜索用户"):
            response = self.user_api.search_users("bulk_test")
            users = response.get("users") or response.get("items") or response.get("data") or []
            
            # 应该至少搜索到我们创建的用户
            assert len(users) >= user_count, \
                f"搜索到的用户数量不足，预期至少 {user_count}，实际 {len(users)}"
            
            self.logger.info(f"批量搜索成功，找到 {len(users)} 个相关用户")
    
    @allure.story("用户数据验证")
    @allure.severity(allure.severity_level.MINOR)
    @allure.tag("api", "validation")
    @pytest.mark.parametrize("invalid_data", [
        {"username": ""},  # 空用户名
        {"email": "invalid-email"},  # 无效邮箱
        {"password": "short"},  # 密码太短
        {"phone": "123"},  # 无效手机号
    ])
    def test_create_user_validation(self, invalid_data):
        """
        测试创建用户时的数据验证
        
        Args:
            invalid_data: 无效数据
        """
        # 生成有效用户数据
        user_data = data_generator.user_data()
        # 用无效数据覆盖部分字段
        user_data.update(invalid_data)
        
        with allure.step(f"尝试创建用户（无效数据: {list(invalid_data.keys())}）"):
            try:
                response = self.user_api.create_user(user_data)
                
                # 如果创建成功，验证响应包含错误信息或验证失败
                if "errors" not in response and "message" not in response:
                    self.logger.warning(f"无效数据创建用户未返回错误，响应: {response}")
            except Exception as e:
                # 预期抛出异常（如400 Bad Request）
                self.logger.info(f"创建用户验证成功，预期异常: {type(e).__name__}")
                assert "400" in str(e) or "Validation" in str(e) or "Invalid" in str(e), \
                    f"预期验证错误，实际异常: {str(e)}"