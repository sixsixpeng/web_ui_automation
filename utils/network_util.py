# -*- coding: utf-8 -*-
"""network_util - Network intercept (Sync + Async)"""
import json

import allure

from utils.log_util import get_logger
from utils.time_util import time_util

logger = get_logger("network_util")


class NetworkSyncUtil:
    def __init__(self):
        self._requests = []

    def start_intercept(self, page):
        """开始拦截网络请求"""
        self._requests.clear()

        def h(resp):
            """处理网络响应回调"""
            url = resp.url
            if any(e in url for e in [".js", ".css", ".png", ".jpg"]): return
            try:
                b = resp.body()
                try:
                    bj = json.loads(b)
                except:
                    bj = str(b[:500])
                self._requests.append({"url": url, "status": resp.status, "body": bj, "ts": time_util.datetime_str()})
            except:
                pass

        page.on("response", h)

    def get_requests(self):
        """获取缓存的请求列表"""
        return self._requests

    def clear(self):
        """清空请求缓存"""
        self._requests.clear()

    def attach_to_allure(self, name="network"):
        """挂载请求数据到 Allure 报告"""
        allure.attach(json.dumps(self._requests, indent=2, ensure_ascii=False), name=name, attachment_type=allure.attachment_type.JSON)


class NetworkAsyncUtil:
    def __init__(self):
        self._requests = []

    async def start_intercept(self, page):
        self._requests.clear()

        async def h(resp):
            url = resp.url
            if any(e in url for e in [".js", ".css", ".png", ".jpg"]): return
            try:
                b = await resp.body()
                try:
                    bj = json.loads(b)
                except:
                    bj = str(b[:500])
                self._requests.append({"url": url, "status": resp.status, "body": bj, "ts": time_util.datetime_str()})
            except:
                pass

        page.on("response", h)

    def get_requests(self):
        """获取缓存的请求列表"""
        return self._requests

    def clear(self):
        """清空请求缓存"""
        self._requests.clear()

    def attach_to_allure(self, name="network"):
        """挂载请求数据到 Allure 报告"""
        allure.attach(json.dumps(self._requests, indent=2, ensure_ascii=False), name=name, attachment_type=allure.attachment_type.JSON)
