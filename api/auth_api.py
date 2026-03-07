# -*- coding: UTF-8 -*-
"""
认证相关 API 接口封装
"""

from typing import Dict, Optional
from core.api_client import api_client
from config.config_loader import config


class AuthAPI:
    """认证 API"""
    
    def __init__(self):
        self.base_url = config.get_api_base_url()
        self.endpoints = config.endpoints.get("auth", {})
    
    def login(self, username: str, password: str, remember_me: bool = False) -> Dict:
        """
        用户登录
        
        Args:
            username: 用户名
            password: 密码
            remember_me: 是否记住登录状态
            
        Returns:
            Dict: 登录响应数据
        """
        endpoint = self.endpoints.get("login", "/api/v1/auth/login")
        
        payload = {
            "username": username,
            "password": password,
            "remember_me": remember_me
        }
        
        response = api_client.post_json(endpoint, json=payload)
        
        # 如果响应中包含 token，设置到 API 客户端
        if "access_token" in response:
            api_client.set_auth_token(response["access_token"])
        
        return response
    
    def logout(self) -> Dict:
        """
        用户登出
        
        Returns:
            Dict: 登出响应数据
        """
        endpoint = self.endpoints.get("logout", "/api/v1/auth/logout")
        return api_client.post_json(endpoint)
    
    def refresh_token(self, refresh_token: str) -> Dict:
        """
        刷新访问令牌
        
        Args:
            refresh_token: 刷新令牌
            
        Returns:
            Dict: 刷新令牌响应数据
        """
        endpoint = self.endpoints.get("refresh_token", "/api/v1/auth/refresh")
        
        payload = {
            "refresh_token": refresh_token
        }
        
        return api_client.post_json(endpoint, json=payload)
    
    def get_current_user(self) -> Dict:
        """
        获取当前用户信息
        
        Returns:
            Dict: 用户信息
        """
        # 假设有一个获取当前用户的端点
        endpoint = "/api/v1/auth/me"
        return api_client.get_json(endpoint)
    
    def change_password(self, old_password: str, new_password: str) -> Dict:
        """
        修改密码
        
        Args:
            old_password: 旧密码
            new_password: 新密码
            
        Returns:
            Dict: 修改密码响应数据
        """
        endpoint = "/api/v1/auth/change-password"
        
        payload = {
            "old_password": old_password,
            "new_password": new_password
        }
        
        return api_client.put_json(endpoint, json=payload)


# 创建全局认证 API 实例
auth_api = AuthAPI()