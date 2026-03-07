# -*- coding: UTF-8 -*-
"""
用户管理相关 API 接口封装
"""

from typing import Dict, List, Optional
from core.api_client import api_client
from config.config_loader import config


class UserAPI:
    """用户管理 API"""
    
    def __init__(self):
        self.base_url = config.get_api_base_url()
        self.endpoints = config.endpoints.get("user", {})
    
    def create_user(self, user_data: Dict) -> Dict:
        """
        创建用户
        
        Args:
            user_data: 用户数据
            
        Returns:
            Dict: 创建的用户数据
        """
        endpoint = self.endpoints.get("create_user", "/api/v1/users")
        return api_client.post_json(endpoint, json=user_data)
    
    def get_user(self, user_id: str) -> Dict:
        """
        获取用户信息
        
        Args:
            user_id: 用户ID
            
        Returns:
            Dict: 用户信息
        """
        endpoint = self.endpoints.get("get_user", "/api/v1/users/{user_id}")
        endpoint = endpoint.format(user_id=user_id)
        return api_client.get_json(endpoint)
    
    def update_user(self, user_id: str, user_data: Dict) -> Dict:
        """
        更新用户信息
        
        Args:
            user_id: 用户ID
            user_data: 更新的用户数据
            
        Returns:
            Dict: 更新后的用户数据
        """
        endpoint = self.endpoints.get("update_user", "/api/v1/users/{user_id}")
        endpoint = endpoint.format(user_id=user_id)
        return api_client.put_json(endpoint, json=user_data)
    
    def delete_user(self, user_id: str) -> Dict:
        """
        删除用户
        
        Args:
            user_id: 用户ID
            
        Returns:
            Dict: 删除响应数据
        """
        endpoint = self.endpoints.get("delete_user", "/api/v1/users/{user_id}")
        endpoint = endpoint.format(user_id=user_id)
        return api_client.delete(endpoint).json()
    
    def list_users(self, page: int = 1, per_page: int = 20, 
                   filters: Optional[Dict] = None) -> Dict:
        """
        获取用户列表
        
        Args:
            page: 页码
            per_page: 每页数量
            filters: 过滤条件
            
        Returns:
            Dict: 用户列表数据
        """
        endpoint = self.endpoints.get("list_users", "/api/v1/users")
        
        params = {
            "page": page,
            "per_page": per_page
        }
        
        if filters:
            params.update(filters)
        
        return api_client.get_json(endpoint, params=params)
    
    def search_users(self, query: str, page: int = 1, per_page: int = 20) -> Dict:
        """
        搜索用户
        
        Args:
            query: 搜索关键词
            page: 页码
            per_page: 每页数量
            
        Returns:
            Dict: 搜索结果
        """
        endpoint = "/api/v1/users/search"
        
        params = {
            "q": query,
            "page": page,
            "per_page": per_page
        }
        
        return api_client.get_json(endpoint, params=params)
    
    def update_user_status(self, user_id: str, status: str) -> Dict:
        """
        更新用户状态
        
        Args:
            user_id: 用户ID
            status: 状态（active/inactive/suspended）
            
        Returns:
            Dict: 更新响应数据
        """
        endpoint = f"/api/v1/users/{user_id}/status"
        
        payload = {
            "status": status
        }
        
        return api_client.patch_json(endpoint, json=payload)
    
    def assign_role(self, user_id: str, role_id: str) -> Dict:
        """
        分配角色给用户
        
        Args:
            user_id: 用户ID
            role_id: 角色ID
            
        Returns:
            Dict: 分配响应数据
        """
        endpoint = f"/api/v1/users/{user_id}/roles"
        
        payload = {
            "role_id": role_id
        }
        
        return api_client.post_json(endpoint, json=payload)
    
    def upload_avatar(self, user_id: str, image_path: str) -> Dict:
        """
        上传用户头像
        
        Args:
            user_id: 用户ID
            image_path: 图片文件路径
            
        Returns:
            Dict: 上传响应数据
        """
        endpoint = f"/api/v1/users/{user_id}/avatar"
        return api_client.upload_file(endpoint, image_path, field_name="avatar")
    
    def export_users(self, save_path: str, format: str = "csv"):
        """
        导出用户列表
        
        Args:
            save_path: 保存路径
            format: 导出格式（csv/excel）
        """
        endpoint = f"/api/v1/users/export?format={format}"
        api_client.download_file(endpoint, save_path)


# 创建全局用户 API 实例
user_api = UserAPI()