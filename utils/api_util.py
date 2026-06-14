# -*- coding: utf-8 -*-
"""
api_util - HTTP 请求客户端
"""

import json
import time
from urllib.parse import urljoin, urlparse

import allure
import requests
from requests.adapters import HTTPAdapter

from utils.log_util import get_logger

logger = get_logger("api_util")


class ApiClient:
    def __init__(self, base_url="", timeout=30, max_retries=3):
        """Init API client with base_url, timeout, retries"""
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.max_retries = max_retries
        self._session = requests.Session()
        adapter = HTTPAdapter(pool_connections=10, pool_maxsize=20, max_retries=max_retries)
        self._session.mount("https://", adapter)
        self._session.mount("http://", adapter)
        self._token = None
        self._token_refresh_hook = None
        self._session.headers.update({"Content-Type": "application/json"})

    def set_header(self, key, value):
        """设置默认请求头"""
        """Set a default request header"""
        self._session.headers[key] = value

    def set_token(self, token, prefix="Bearer "):
        """设置 Authorization 令牌"""
        """Set Authorization header with bearer token"""
        self._session.headers["Authorization"] = prefix + token
        self._token = token

    def set_token_refresh_hook(self, hook):
        """设置 Token 自动刷新回调"""
        """Set callback for auto token refresh on 401"""
        self._token_refresh_hook = hook

    def _request(self, method, url, **kw):
        """Core request method with retry, allure log, token refresh"""
        full_url = urljoin(self.base_url + "/", url.lstrip("/")) if self.base_url else url
        kw.setdefault("timeout", self.timeout)
        for attempt in range(1, self.max_retries + 1):
            try:
                start = time.time()
                resp = self._session.request(method, full_url, **kw)
                elp = round(time.time() - start, 3)
                self._attach(method, full_url, kw, resp, elp)
                if resp.status_code == 401 and self._token_refresh_hook and attempt < self.max_retries:
                    new_tok = self._token_refresh_hook()
                    if new_tok:
                        self.set_token(new_tok)
                        logger.info("Token refreshed, retrying")
                        continue
                logger.debug(f"{method} {full_url} -> {resp.status_code} ({elp}s)")
                return resp
            except requests.RequestException as e:
                logger.warning(f"Retry [{attempt}/{self.max_retries}]: {e}")
                if attempt == self.max_retries:
                    raise
                time.sleep(1 * attempt)
        raise RuntimeError(f"Request failed: {method} {full_url}")

    def _attach(self, method, url, kw, resp, elp):
        """Attach request/response details to Allure report"""
        try:
            req_body = kw.get("json") or kw.get("data") or ""
            req_headers = dict(kw.get("headers", {}))
            if "Authorization" in req_headers:
                req_headers["Authorization"] = "******"
            resp_body = resp.text[:2000] if resp.text else ""
            txt = f"REQUEST: {method} {url}\nHeaders: {json.dumps(req_headers)}\nBody: {json.dumps(req_body) if isinstance(req_body, dict) else req_body}\n\nRESPONSE ({elp}s): {resp.status_code}\n{resp_body[:1000]}"
            allure.attach(txt, name="API " + method + " " + urlparse(url).path,
                          attachment_type=allure.attachment_type.TEXT)
        except Exception:
            pass

    def get(self, url, params=None, **kw):
        """发送 GET 请求"""
        """Send GET request"""
        return self._request("GET", url, params=params, **kw)

    def post(self, url, json=None, data=None, **kw):
        """发送 POST 请求"""
        """Send POST request"""
        return self._request("POST", url, json=json, data=data, **kw)

    def put(self, url, json=None, **kw):
        """发送 PUT 请求"""
        """Send PUT request"""
        return self._request("PUT", url, json=json, **kw)

    def delete(self, url, **kw):
        """发送 DELETE 请求"""
        """Send DELETE request"""
        return self._request("DELETE", url, **kw)

    def patch(self, url, json=None, **kw):
        """发送 PATCH 请求"""
        """Send PATCH request"""
        return self._request("PATCH", url, json=json, **kw)

    @staticmethod
    def to_json(resp):
        """解析响应为 JSON 字典"""
        """Parse response as JSON dict"""
        return resp.json()

    @staticmethod
    def ok(resp):
        """判断响应状态码是否为 2xx"""
        """Check if status code is 2xx"""
        return 200 <= resp.status_code < 300

    @staticmethod
    def data(resp, key="data", default=None):
        """从 JSON 响应中提取指定字段"""
        """Extract field from JSON response, e.g. {code,msg,data}"""
        try:
            return resp.json().get(key, default)
        except:
            return default

    def close(self):
        """关闭 HTTP 会话"""
        """Close the HTTP session"""
        self._session.close()


api_client = ApiClient()
