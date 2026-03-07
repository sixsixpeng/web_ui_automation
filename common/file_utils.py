# -*- coding: UTF-8 -*-
"""
文件操作工具
提供 YAML、JSON、Excel 等格式的读写功能
"""

import os
import json
import yaml
import csv
from pathlib import Path
from typing import Any, Dict, List, Optional
import pandas as pd


class FileUtils:
    """文件操作工具类"""
    
    @staticmethod
    def ensure_dir(file_path: str):
        """
        确保文件所在目录存在
        
        Args:
            file_path: 文件路径
        """
        directory = os.path.dirname(file_path)
        if directory and not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)
    
    @staticmethod
    def read_yaml(file_path: str) -> Dict[str, Any]:
        """
        读取 YAML 文件
        
        Args:
            file_path: YAML 文件路径
            
        Returns:
            Dict: YAML 内容
            
        Raises:
            FileNotFoundError: 文件不存在
            yaml.YAMLError: YAML 解析错误
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"YAML 文件不存在: {file_path}")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    
    @staticmethod
    def write_yaml(data: Dict[str, Any], file_path: str):
        """
        写入 YAML 文件
        
        Args:
            data: 要写入的数据
            file_path: YAML 文件路径
        """
        FileUtils.ensure_dir(file_path)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            yaml.dump(data, f, allow_unicode=True, default_flow_style=False)
    
    @staticmethod
    def read_json(file_path: str) -> Dict[str, Any]:
        """
        读取 JSON 文件
        
        Args:
            file_path: JSON 文件路径
            
        Returns:
            Dict: JSON 内容
            
        Raises:
            FileNotFoundError: 文件不存在
            json.JSONDecodeError: JSON 解析错误
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"JSON 文件不存在: {file_path}")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    @staticmethod
    def write_json(data: Dict[str, Any], file_path: str, indent: int = 2):
        """
        写入 JSON 文件
        
        Args:
            data: 要写入的数据
            file_path: JSON 文件路径
            indent: 缩进空格数
        """
        FileUtils.ensure_dir(file_path)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=indent)
    
    @staticmethod
    def read_csv(file_path: str, delimiter: str = ',') -> List[Dict[str, Any]]:
        """
        读取 CSV 文件
        
        Args:
            file_path: CSV 文件路径
            delimiter: 分隔符
            
        Returns:
            List[Dict]: CSV 内容，每行一个字典
            
        Raises:
            FileNotFoundError: 文件不存在
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"CSV 文件不存在: {file_path}")
        
        data = []
        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f, delimiter=delimiter)
            for row in reader:
                data.append(row)
        
        return data
    
    @staticmethod
    def write_csv(data: List[Dict[str, Any]], file_path: str, fieldnames: Optional[List[str]] = None):
        """
        写入 CSV 文件
        
        Args:
            data: 要写入的数据（字典列表）
            file_path: CSV 文件路径
            fieldnames: 字段名列表，如果为 None 则从数据中获取
        """
        FileUtils.ensure_dir(file_path)
        
        if not data and fieldnames is None:
            raise ValueError("无法确定 CSV 字段名")
        
        if fieldnames is None:
            fieldnames = list(data[0].keys()) if data else []
        
        with open(file_path, 'w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(data)
    
    @staticmethod
    def read_excel(file_path: str, sheet_name: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        读取 Excel 文件
        
        Args:
            file_path: Excel 文件路径
            sheet_name: 工作表名称，如果为 None 则读取第一个工作表
            
        Returns:
            List[Dict]: Excel 内容，每行一个字典
            
        Raises:
            FileNotFoundError: 文件不存在
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Excel 文件不存在: {file_path}")
        
        # 使用 pandas 读取 Excel
        try:
            if sheet_name:
                df = pd.read_excel(file_path, sheet_name=sheet_name)
            else:
                df = pd.read_excel(file_path)
            
            # 将 DataFrame 转换为字典列表
            # 处理 NaN 值，转换为 None
            data = df.replace({pd.NA: None, pd.NaT: None, float('nan'): None}).to_dict('records')
            return data
        except Exception as e:
            raise ValueError(f"读取 Excel 文件失败: {str(e)}")
    
    @staticmethod
    def write_excel(data: List[Dict[str, Any]], file_path: str, 
                    sheet_name: str = "Sheet1", fieldnames: Optional[List[str]] = None):
        """
        写入 Excel 文件
        
        Args:
            data: 要写入的数据（字典列表）
            file_path: Excel 文件路径
            sheet_name: 工作表名称
            fieldnames: 字段名列表，如果为 None 则从数据中获取
        """
        FileUtils.ensure_dir(file_path)
        
        if not data and fieldnames is None:
            # 创建空 DataFrame 并写入
            df = pd.DataFrame()
            df.to_excel(file_path, sheet_name=sheet_name, index=False)
            return
        
        if fieldnames is None:
            fieldnames = list(data[0].keys()) if data else []
        
        # 使用 pandas 写入 Excel
        try:
            # 创建 DataFrame，确保列顺序与 fieldnames 一致
            df = pd.DataFrame(data, columns=fieldnames)
            # 写入 Excel 文件
            df.to_excel(file_path, sheet_name=sheet_name, index=False)
        except Exception as e:
            raise ValueError(f"写入 Excel 文件失败: {str(e)}")
    
    @staticmethod
    def read_text(file_path: str) -> str:
        """
        读取文本文件
        
        Args:
            file_path: 文本文件路径
            
        Returns:
            str: 文本内容
            
        Raises:
            FileNotFoundError: 文件不存在
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"文本文件不存在: {file_path}")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    
    @staticmethod
    def write_text(content: str, file_path: str):
        """
        写入文本文件
        
        Args:
            content: 文本内容
            file_path: 文本文件路径
        """
        FileUtils.ensure_dir(file_path)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
    
    @staticmethod
    def get_files_by_ext(directory: str, extension: str) -> List[str]:
        """
        获取指定目录下指定扩展名的所有文件
        
        Args:
            directory: 目录路径
            extension: 文件扩展名（如 '.yaml', '.json'）
            
        Returns:
            List[str]: 文件路径列表
        """
        if not os.path.exists(directory):
            return []
        
        files = []
        for root, _, filenames in os.walk(directory):
            for filename in filenames:
                if filename.endswith(extension):
                    files.append(os.path.join(root, filename))
        
        return files
    
    @staticmethod
    def load_test_data(data_dir: str, module: str) -> Dict[str, Any]:
        """
        加载测试数据
        
        Args:
            data_dir: 数据目录
            module: 模块名（如 'login', 'user'）
            
        Returns:
            Dict: 测试数据
        """
        data_files = []
        
        # 尝试不同格式的文件
        for ext in ['.yaml', '.yml', '.json']:
            file_path = os.path.join(data_dir, f"{module}_data{ext}")
            if os.path.exists(file_path):
                data_files.append(file_path)
        
        # 如果没有找到文件，尝试查找模块目录
        if not data_files:
            module_dir = os.path.join(data_dir, module)
            if os.path.exists(module_dir):
                for ext in ['.yaml', '.yml', '.json']:
                    data_files.extend(FileUtils.get_files_by_ext(module_dir, ext))
        
        if not data_files:
            return {}
        
        # 读取第一个找到的文件
        file_path = data_files[0]
        if file_path.endswith(('.yaml', '.yml')):
            return FileUtils.read_yaml(file_path)
        elif file_path.endswith('.json'):
            return FileUtils.read_json(file_path)
        else:
            raise ValueError(f"不支持的测试数据格式: {file_path}")


# 创建全局文件工具实例
file_utils = FileUtils()