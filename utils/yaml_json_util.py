# -*- coding: utf-8 -*-
"""
yaml_json_util - YAML/JSON 解析转换工具
功能：多配置文件加载、深层字段提取、JSON 差异比对
"""

import json
import os
from typing import Any, Dict

import yaml

# get_logger imported lazily inside methods
_logger = None


def _get_logger():
    global _logger
    if _logger is None:
        import logging
        _l = logging.getLogger("yaml_json_util")
        _logger = lambda name: _l
    return _logger("yaml_json_util")


class YamlJsonUtil:
    """YAML/JSON 解析转换工具类"""

    @staticmethod
    def load_yaml(file_path: str) -> dict:
        """加载 YAML 文件"""
        try:
            if not os.path.exists(file_path):
                _get_logger().error(f"YAML 文件不存在: {file_path}")
                raise FileNotFoundError(f"YAML 文件不存在: {file_path}")
            with open(file_path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)
            if data is None:
                return {}
            _get_logger().debug(f"YAML 文件加载成功: {file_path}")
            return data
        except yaml.YAMLError as e:
            _get_logger().error(f"YAML 解析失败: {e}")
            raise
        except Exception as e:
            _get_logger().error(f"加载 YAML 失败: {e}")
            raise

    @staticmethod
    def dump_yaml(data: dict, file_path: str):
        """写入 YAML 文件"""
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                yaml.dump(data, f, allow_unicode=True, default_flow_style=False)
            _get_logger().debug(f"YAML 文件写入成功: {file_path}")
        except Exception as e:
            _get_logger().error(f"写入 YAML 失败: {e}")
            raise

    @staticmethod
    def load_json(file_path: str) -> dict:
        """加载 JSON 文件"""
        try:
            if not os.path.exists(file_path):
                _get_logger().error(f"JSON 文件不存在: {file_path}")
                raise FileNotFoundError(f"JSON 文件不存在: {file_path}")
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            _get_logger().debug(f"JSON 文件加载成功: {file_path}")
            return data
        except json.JSONDecodeError as e:
            _get_logger().error(f"JSON 解析失败: {e}")
            raise
        except Exception as e:
            _get_logger().error(f"加载 JSON 失败: {e}")
            raise

    @staticmethod
    def dump_json(data: dict, file_path: str, pretty: bool = True):
        """写入 JSON 文件"""
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                if pretty:
                    json.dump(data, f, ensure_ascii=False, indent=2)
                else:
                    json.dump(data, f, ensure_ascii=False)
            _get_logger().debug(f"JSON 文件写入成功: {file_path}")
        except Exception as e:
            _get_logger().error(f"写入 JSON 失败: {e}")
            raise

    @staticmethod
    def yaml_to_json_str(yaml_data: dict) -> str:
        """YAML 数据转 JSON 字符串"""
        return json.dumps(yaml_data, ensure_ascii=False, indent=2)

    @staticmethod
    def json_str_to_yaml(json_str: str) -> dict:
        """JSON 字符串转 YAML 字典"""
        return json.loads(json_str)

    @staticmethod
    def get_nested_value(data: dict, key_path: str, default: Any = None) -> Any:
        """从嵌套字典中提取深层字段值（key_path 用点分隔）"""
        keys = key_path.split(".")
        current = data
        try:
            for key in keys:
                if isinstance(current, dict):
                    current = current[key]
                elif isinstance(current, list):
                    current = current[int(key)]
                else:
                    return default
            return current
        except (KeyError, IndexError, TypeError, ValueError):
            return default

    @staticmethod
    def json_diff(json1: dict, json2: dict) -> Dict[str, dict]:
        """比较两个 JSON 的差异，返回差异字典"""
        diff = {"added": {}, "removed": {}, "changed": {}}

        all_keys = set(json1.keys()) | set(json2.keys())
        for key in all_keys:
            if key not in json1:
                diff["added"][key] = json2[key]
            elif key not in json2:
                diff["removed"][key] = json1[key]
            elif json1[key] != json2[key]:
                diff["changed"][key] = {"old": json1[key], "new": json2[key]}

        return diff

    @staticmethod
    def merge_configs(base: dict, override: dict) -> dict:
        """合并两个配置字典（深层合并）"""
        result = base.copy()
        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = YamlJsonUtil.merge_configs(result[key], value)
            else:
                result[key] = value
        return result


yaml_json_util = YamlJsonUtil()
