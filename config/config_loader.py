# -*- coding: UTF-8 -*-
"""
配置加载模块
负责读取 YAML 配置文件，根据环境变量提供配置项
"""

import os
import yaml
from pathlib import Path


class ConfigLoader:
    """配置加载器"""
    
    def __init__(self):
        self.config_dir = Path(__file__).parent
        self.config = self._load_config()
        self.endpoints = self._load_endpoints()
        
    def _load_config(self):
        """加载主配置文件"""
        config_file = self.config_dir / "config.yaml"
        with open(config_file, 'r', encoding='utf-8') as f:
            config_data = yaml.safe_load(f)
        
        # 获取当前环境，默认为 dev
        env = os.getenv("TEST_ENV", "dev").lower()
        
        # 合并基础配置和环境特定配置
        base_config = config_data.get("base", {})
        env_config = config_data.get(env, {})
        
        # 合并配置，环境配置覆盖基础配置
        merged_config = {**base_config, **env_config}
        merged_config["env"] = env
        
        # 处理路径，确保是绝对路径
        project_root = Path(__file__).parent.parent
        for key in ["log_dir", "screenshot_dir", "report_dir", "playwright_cache_dir", "data_dir"]:
            if key in merged_config:
                path_str = merged_config[key]
                if path_str.startswith("../"):
                    merged_config[key] = str(project_root / path_str[3:])
                else:
                    merged_config[key] = str(project_root / path_str)
        
        return merged_config
    
    def _load_endpoints(self):
        """加载 API 端点配置"""
        endpoints_file = self.config_dir / "api_endpoints.yaml"
        with open(endpoints_file, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    
    def get(self, key, default=None):
        """获取配置项"""
        return self.config.get(key, default)
    
    def get_endpoint(self, module, endpoint):
        """获取 API 端点路径"""
        module_dict = self.endpoints.get(module, {})
        return module_dict.get(endpoint)
    
    def get_base_url(self):
        """获取基础 URL"""
        return self.config.get("base_url")
    
    def get_api_base_url(self):
        """获取 API 基础 URL"""
        return self.config.get("api_base_url")


# 创建全局配置实例
config = ConfigLoader()