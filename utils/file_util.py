# -*- coding: utf-8 -*-
"""
file_util - 文件通用处理工具
功能：目录创建、文件清理、压缩解压、临时文件管理
"""

import os
import shutil
import tempfile
import zipfile
from typing import List

import allure

from utils.log_util import get_logger
from utils.path_util import path_util

logger = get_logger("file_util")


class FileUtil:
    """文件操作工具类"""

    # ========== 目录操作 ==========

    @staticmethod
    def ensure_dir(dir_path: str) -> str:
        """确保目录存在，不存在则创建"""
        path_util.ensure(dir_path)
        return dir_path

    @staticmethod
    def clean_dir(dir_path: str):
        """清空目录下所有文件（保留空目录）"""
        # dir_path used as-is
        if dir_path.exists():
            for item in dir_path.iterdir():
                if item.is_file():
                    item.unlink()
                elif item.is_dir():
                    shutil.rmtree(item)
            logger.debug(f"目录已清空: {dir_path}")

    @staticmethod
    def delete_dir(dir_path: str):
        """删除整个目录"""
        shutil.rmtree(dir_path, ignore_errors=True)
        logger.debug(f"目录已删除: {dir_path}")

    # ========== 文件操作 ==========

    @staticmethod
    def delete_file(file_path: str):
        """删除文件"""
        try:
            path_util.exists(file_path) and os.remove(file_path)
            logger.debug(f"文件已删除: {file_path}")
        except Exception as e:
            logger.warning(f"文件删除失败: {file_path}, {e}")

    @staticmethod
    def copy_file(src: str, dst: str):
        """复制文件"""
        shutil.copy2(src, dst)
        logger.debug(f"文件已复制: {src} -> {dst}")

    @staticmethod
    def move_file(src: str, dst: str):
        """移动文件"""
        shutil.move(src, dst)
        logger.debug(f"文件已移动: {src} -> {dst}")

    @staticmethod
    def file_exists(file_path: str) -> bool:
        """检查文件是否存在"""
        return path_util.exists(file_path)

    @staticmethod
    def file_size(file_path: str) -> int:
        """获取文件大小（字节）"""
        return path_util.size(file_path)

    @staticmethod
    def file_md5(file_path: str) -> str:
        """计算文件 MD5"""
        import hashlib
        hash_md5 = hashlib.md5()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()

    # ========== 压缩解压 ==========

    @staticmethod
    def zip_files(file_paths: List[str], zip_path: str):
        """将多个文件打包为 zip"""
        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
            for file_path in file_paths:
                arcname = path_util.name(file_path)
                zf.write(file_path, arcname)
        logger.info(f"压缩包已创建: {zip_path} ({len(file_paths)} 个文件)")

    @staticmethod
    def zip_dir(dir_path: str, zip_path: str):
        """压缩整个目录"""
        # dir_path used as-is
        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
            for file_path in dir_path.rglob("*"):
                if file_path.is_file():
                    arcname = str(file_path.relative_to(dir_path))
                    zf.write(file_path, arcname)
        logger.info(f"目录已压缩: {dir_path} -> {zip_path}")

    @staticmethod
    def unzip_file(zip_path: str, extract_dir: str = None):
        """解压 zip 文件"""
        if extract_dir is None:
            extract_dir = str(path_util.parent(zip_path))
        with zipfile.ZipFile(zip_path, "r") as zf:
            zf.extractall(extract_dir)
        logger.info(f"压缩包已解压: {zip_path} -> {extract_dir}")

    # ========== 临时文件管理 ==========

    @staticmethod
    @allure.step("文件-创建临时文件")
    def create_temp_file(suffix: str = ".tmp", content: str = "") -> str:
        """创建临时文件"""
        tmp_dir = path_util.tmp_dir
        tmp_dir.mkdir(parents=True, exist_ok=True)
        with tempfile.NamedTemporaryFile(
                mode="w", suffix=suffix, dir=str(tmp_dir), delete=False, encoding="utf-8"
        ) as f:
            f.write(content)
            temp_path = f.name
        logger.debug(f"临时文件已创建: {temp_path}")
        return temp_path

    @staticmethod
    def create_temp_image(width: int = 100, height: int = 100, filename: str = None) -> str:
        """创建临时测试图片"""
        try:
            from PIL import Image
        except ImportError:
            logger.error("Pillow 未安装，请执行: pip install Pillow")
            raise

        if filename is None:
            from utils.time_util import time_util
            filename = f"test_img_{time_util.now_compact_str()}.png"

        tmp_dir = path_util.tmp_dir
        file_path = str(tmp_dir / filename)

        img = Image.new("RGB", (width, height), color=(255, 0, 0))
        img.save(file_path)
        logger.debug(f"临时图片已创建: {file_path}")
        return file_path

    @staticmethod
    def cleanup_temp_files():
        """清理临时目录所有文件"""
        tmp_dir = path_util.tmp_dir
        if tmp_dir.exists():
            for f in tmp_dir.iterdir():
                if f.is_file():
                    f.unlink()
            logger.info("Temp files cleaned up")

    # ========== 文件查找 ==========

    @staticmethod
    def find_files(pattern: str, search_dir: str = None) -> List[str]:
        """递归查找匹配模式的文件"""
        if search_dir is None:
            search_dir = str(path_util.root)
        return [str(p) for p in path_util.rglob(pattern, base=Path(search_dir) if search_dir else None)]


# 全局实例
file_util = FileUtil()
