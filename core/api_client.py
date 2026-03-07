# -*- coding: UTF-8 -*-
"""
API 客户端模块
封装 requests 库，提供统一的 API 调用接口
"""

import json
import time
import allure
from typing import Optional, Dict, Any, Union
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from config.config_loader import config
from core.exception_handle import APICallException


class APIClient:
    """API 客户端"""
    
    def __init__(self, base_url: str = None, timeout: int = 30):
        """
        初始化 API 客户端
        
        Args:
            base_url: API 基础 URL，如果为 None 则从配置读取
            timeout: 默认超时时间（秒）
        """
        self.base_url = base_url or config.get_api_base_url()
        self.timeout = timeout
        self.session = requests.Session()
        
        # 设置重试策略
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET", "POST", "PUT", "DELETE", "PATCH"]
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        
        # 设置默认请求头
        self.session.headers.update({
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": "WebUI-Automation-Framework/1.0"
        })
        
        # 认证信息
        self.auth_token = None
        self.auth_type = None
    
    def set_auth_token(self, token: str, auth_type: str = "Bearer"):
        """
        设置认证 token
        
        Args:
            token: 认证 token
            auth_type: 认证类型，如 "Bearer", "Basic" 等
        """
        self.auth_token = token
        self.auth_type = auth_type
        self.session.headers.update({
            "Authorization": f"{auth_type} {token}"
        })
    
    def set_basic_auth(self, username: str, password: str):
        """
        设置 Basic 认证
        
        Args:
            username: 用户名
            password: 密码
        """
        self.session.auth = (username, password)
    
    def set_headers(self, headers: Dict[str, str]):
        """
        设置请求头
        
        Args:
            headers: 请求头字典
        """
        self.session.headers.update(headers)
    
    def _build_url(self, endpoint: str) -> str:
        """
        构建完整的 URL
        
        Args:
            endpoint: 端点路径
            
        Returns:
            str: 完整 URL
        """
        if endpoint.startswith(("http://", "https://")):
            return endpoint
        
        base = self.base_url.rstrip("/")
        endpoint = endpoint.lstrip("/")
        return f"{base}/{endpoint}"
    
    def _log_request(self, method: str, url: str, **kwargs):
        """记录请求信息到 Allure"""
        with allure.step(f"API 请求: {method} {url}"):
            # 记录请求头（排除敏感信息）
            headers = kwargs.get("headers", {})
            safe_headers = {k: v for k, v in headers.items() 
                          if k.lower() not in ["authorization", "cookie"]}
            
            allure.attach(
                json.dumps(safe_headers, indent=2, ensure_ascii=False),
                name="请求头",
                attachment_type=allure.attachment_type.JSON
            )
            
            # 记录请求体
            if "json" in kwargs:
                allure.attach(
                    json.dumps(kwargs["json"], indent=2, ensure_ascii=False),
                    name="请求体",
                    attachment_type=allure.attachment_type.JSON
                )
            elif "data" in kwargs:
                allure.attach(
                    str(kwargs["data"]),
                    name="请求体",
                    attachment_type=allure.attachment_type.TEXT
                )
    
    def _log_response(self, response: requests.Response):
        """记录响应信息到 Allure"""
        # 记录响应头
        allure.attach(
            json.dumps(dict(response.headers), indent=2, ensure_ascii=False),
            name="响应头",
            attachment_type=allure.attachment_type.JSON
        )
        
        # 记录响应体
        content_type = response.headers.get("Content-Type", "")
        try:
            if "application/json" in content_type:
                response_json = response.json()
                allure.attach(
                    json.dumps(response_json, indent=2, ensure_ascii=False),
                    name="响应体",
                    attachment_type=allure.attachment_type.JSON
                )
            else:
                allure.attach(
                    response.text[:10000],  # 限制长度
                    name="响应体",
                    attachment_type=allure.attachment_type.TEXT
                )
        except:
            allure.attach(
                response.text[:10000],
                name="响应体",
                attachment_type=allure.attachment_type.TEXT
            )
        
        # 记录状态码和耗时
        allure.attach(
            f"状态码: {response.status_code}\n"
            f"耗时: {response.elapsed.total_seconds():.3f}秒",
            name="响应信息",
            attachment_type=allure.attachment_type.TEXT
        )
    
    def _make_request(self, method: str, endpoint: str, **kwargs) -> requests.Response:
        """
        发送 HTTP 请求
        
        Args:
            method: HTTP 方法
            endpoint: 端点路径
            **kwargs: 传递给 requests 的参数
            
        Returns:
            requests.Response: 响应对象
        """
        url = self._build_url(endpoint)
        
        # 记录请求
        self._log_request(method, url, **kwargs)
        
        # 发送请求
        start_time = time.time()
        try:
            response = self.session.request(
                method=method,
                url=url,
                timeout=self.timeout,
                **kwargs
            )
            response.elapsed = time.time() - start_time  # 记录实际耗时
        except requests.exceptions.RequestException as e:
            raise APICallException(url, 0, f"请求异常: {str(e)}")
        
        # 记录响应
        self._log_response(response)
        
        # 检查状态码
        if not 200 <= response.status_code < 300:
            raise APICallException(
                url, 
                response.status_code,
                response.text[:1000]
            )
        
        return response
    
    def get(self, endpoint: str, params: Optional[Dict] = None, **kwargs) -> requests.Response:
        """
        GET 请求
        
        Args:
            endpoint: 端点路径
            params: 查询参数
            **kwargs: 其他参数
            
        Returns:
            requests.Response: 响应对象
        """
        return self._make_request("GET", endpoint, params=params, **kwargs)
    
    def post(self, endpoint: str, data: Optional[Union[Dict, str]] = None, 
             json: Optional[Dict] = None, **kwargs) -> requests.Response:
        """
        POST 请求
        
        Args:
            endpoint: 端点路径
            data: 表单数据
            json: JSON 数据
            **kwargs: 其他参数
            
        Returns:
            requests.Response: 响应对象
        """
        return self._make_request("POST", endpoint, data=data, json=json, **kwargs)
    
    def put(self, endpoint: str, data: Optional[Union[Dict, str]] = None,
            json: Optional[Dict] = None, **kwargs) -> requests.Response:
        """
        PUT 请求
        
        Args:
            endpoint: 端点路径
            data: 表单数据
            json: JSON 数据
            **kwargs: 其他参数
            
        Returns:
            requests.Response: 响应对象
        """
        return self._make_request("PUT", endpoint, data=data, json=json, **kwargs)
    
    def patch(self, endpoint: str, data: Optional[Union[Dict, str]] = None,
              json: Optional[Dict] = None, **kwargs) -> requests.Response:
        """
        PATCH 请求
        
        Args:
            endpoint: 端点路径
            data: 表单数据
            json: JSON 数据
            **kwargs: 其他参数
            
        Returns:
            requests.Response: 响应对象
        """
        return self._make_request("PATCH", endpoint, data=data, json=json, **kwargs)
    
    def delete(self, endpoint: str, **kwargs) -> requests.Response:
        """
        DELETE 请求
        
        Args:
            endpoint: 端点路径
            **kwargs: 其他参数
            
        Returns:
            requests.Response: 响应对象
        """
        return self._make_request("DELETE", endpoint, **kwargs)
    
    def get_json(self, endpoint: str, params: Optional[Dict] = None, **kwargs) -> Dict:
        """
        GET 请求，返回 JSON
        
        Args:
            endpoint: 端点路径
            params: 查询参数
            **kwargs: 其他参数
            
        Returns:
            Dict: JSON 响应数据
        """
        response = self.get(endpoint, params=params, **kwargs)
        return response.json()
    
    def post_json(self, endpoint: str, json: Optional[Dict] = None, **kwargs) -> Dict:
        """
        POST 请求，返回 JSON
        
        Args:
            endpoint: 端点路径
            json: JSON 数据
            **kwargs: 其他参数
            
        Returns:
            Dict: JSON 响应数据
        """
        response = self.post(endpoint, json=json, **kwargs)
        return response.json()
    
    def download_file(self, endpoint: str, save_path: str, **kwargs):
        """
        下载文件
        
        Args:
            endpoint: 端点路径
            save_path: 保存路径
            **kwargs: 其他参数
        """
        response = self.get(endpoint, **kwargs)
        
        with open(save_path, 'wb') as f:
            f.write(response.content)
        
        allure.attach.file(
            save_path,
            name="下载的文件",
            attachment_type=allure.attachment_type.from_file_path(save_path)
        )
    
    def upload_file(self, endpoint: str, file_path: str, field_name: str = "file", **kwargs) -> requests.Response:
        """
        上传文件
        
        Args:
            endpoint: 端点路径
            file_path: 文件路径
            field_name: 表单字段名
            **kwargs: 其他参数
            
        Returns:
            requests.Response: 响应对象
        """
        with open(file_path, 'rb') as f:
            files = {field_name: f}
            return self.post(endpoint, files=files, **kwargs)
    
    def health_check(self) -> bool:
        """
        健康检查
        
        Returns:
            bool: 是否健康
        """
        try:
            response = self.get("/health", timeout=5)
            return response.status_code == 200
        except:
            return False


# 创建全局 API 客户端实例
api_client = APIClient()