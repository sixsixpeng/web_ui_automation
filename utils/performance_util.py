# -*- coding: utf-8 -*-
"""performance_util - Page performance (Sync + Async)"""
import json

import allure

from utils.log_util import get_logger

logger = get_logger("performance_util")


class PerformanceSyncUtil:
    @staticmethod
    def collect_metrics(page):
        """采集页面性能指标"""
        try:
            js = "()=>{const p=performance.getEntriesByType('navigation')[0];const pt=performance.getEntriesByType('paint');return{load:p?p.loadEventEnd:0,fcp:pt.find(x=>x.name==='first-contentful-paint')?.startTime||0,lcp:performance.getEntriesByType('largest-contentful-paint').pop()?.startTime||0}}"
            return page.evaluate(js)
        except:
            return {}

    @staticmethod
    def attach_to_allure(metrics, name="performance"):
        """挂载请求数据到 Allure 报告"""
        allure.attach(json.dumps(metrics, indent=2), name=name, attachment_type=allure.attachment_type.JSON)


class PerformanceAsyncUtil:
    @staticmethod
    async def collect_metrics(page):
        try:
            js = "()=>{const p=performance.getEntriesByType('navigation')[0];const pt=performance.getEntriesByType('paint');return{load:p?p.loadEventEnd:0,fcp:pt.find(x=>x.name==='first-contentful-paint')?.startTime||0,lcp:performance.getEntriesByType('largest-contentful-paint').pop()?.startTime||0}}"
            return await page.evaluate(js)
        except:
            return {}

    @staticmethod
    def attach_to_allure(metrics, name="performance"):
        """挂载请求数据到 Allure 报告"""
        allure.attach(json.dumps(metrics, indent=2), name=name, attachment_type=allure.attachment_type.JSON)
