# -*- coding: utf-8 -*-
"""
allure_attach_util - Allure 附件统一挂载工具
功能：封装 allure.attach 方法，提供统一附件挂载接口
"""

import json
import os
from typing import Any, Optional

import allure

from utils.log_util import get_logger

logger = get_logger("allure_attach_util")


class AllureAttachUtil:
    """Allure 附件挂载工具类"""

    @staticmethod
    def attach_text(content: str, attach_name: str = "text", attach_type: str = "text"):
        """挂载纯文本附件（日志、指标、报错堆栈）"""
        allure.attach(
            content,
            name=attach_name,
            attachment_type=allure.attachment_type.TEXT,
        )
        logger.debug(f"Allure 文本附件已挂载: {attach_name}")

    @staticmethod
    def attach_json(json_data: Any, attach_name: str = "json_data"):
        """挂载 JSON 附件（接口报文、测试数据、缓存快照）"""
        if isinstance(json_data, (dict, list)):
            json_str = json.dumps(json_data, ensure_ascii=False, indent=2)
        elif isinstance(json_data, str):
            try:
                json.loads(json_data)
                json_str = json_data
            except json.JSONDecodeError:
                json_str = json_data
        else:
            json_str = str(json_data)

        allure.attach(
            json_str,
            name=attach_name,
            attachment_type=allure.attachment_type.JSON,
        )
        logger.debug(f"Allure JSON 附件已挂载: {attach_name}")

    @staticmethod
    def attach_image_binary(binary_data: bytes, attach_name: str = "screenshot"):
        """挂载图片二进制附件（截图工具调用）"""
        allure.attach(
            binary_data,
            name=attach_name,
            attachment_type=allure.attachment_type.PNG,
        )
        logger.debug(f"Allure 图片附件已挂载: {attach_name}")

    @staticmethod
    def attach_file(file_path: str, attach_name: Optional[str] = None):
        """挂载本地文件附件"""
        if not os.path.exists(file_path):
            logger.warning(f"附件文件不存在: {file_path}")
            return

        if attach_name is None:
            attach_name = os.path.basename(file_path)

        with open(file_path, "rb") as f:
            file_data = f.read()

        # 根据扩展名判断附件类型
        ext = os.path.splitext(file_path)[1].lower()
        if ext in (".png", ".jpg", ".jpeg", ".gif", ".bmp"):
            allure.attach(file_data, name=attach_name, attachment_type=allure.attachment_type.PNG)
        elif ext in (".json",):
            allure.attach(file_data, name=attach_name, attachment_type=allure.attachment_type.JSON)
        elif ext in (".txt", ".log"):
            allure.attach(file_data, name=attach_name, attachment_type=allure.attachment_type.TEXT)
        elif ext in (".html",):
            allure.attach(file_data, name=attach_name, attachment_type=allure.attachment_type.HTML)
        elif ext in (".csv",):
            allure.attach(file_data, name=attach_name, attachment_type=allure.attachment_type.CSV)
        else:
            allure.attach(file_data, name=attach_name, attachment_type=allure.attachment_type.TEXT)

        logger.debug(f"文件附件已挂载: {attach_name}")

    @staticmethod
    def attach_html(html_content: str, attach_name: str = "html_content"):
        """挂载 HTML 附件"""
        allure.attach(
            html_content,
            name=attach_name,
            attachment_type=allure.attachment_type.HTML,
        )
        logger.debug(f"HTML 附件已挂载: {attach_name}")


# 全局实例
allure_attach = AllureAttachUtil()
