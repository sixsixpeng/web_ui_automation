# -*- coding: UTF-8 -*-
"""
下载助手
处理文件下载，管理下载的文件
"""

import os
import time
import allure
import shutil
from pathlib import Path
from typing import Optional, List, Dict, Any, Callable
from playwright.sync_api import Page, Download

from core.exception_handle import TimeoutException, BrowserException


class DownloadHelper:
    """下载助手"""
    
    def __init__(self, page: Page, download_dir: Optional[str] = None):
        """
        初始化下载助手
        
        Args:
            page: Playwright Page 对象
            download_dir: 下载目录，如果为 None 则使用临时目录
        """
        self._page = page
        self._downloads: List[Download] = []
        self._download_dir = download_dir or "./downloads"
        self._auto_save = False
        self._auto_save_dir: Optional[str] = None
        self._download_complete_callbacks: List[Callable[[Download, str], None]] = []
        
        # 确保下载目录存在
        os.makedirs(self._download_dir, exist_ok=True)
        
        # 监听下载事件
        self._page.on("download", self._handle_download)
    
    def _handle_download(self, download: Download):
        """
        处理下载事件
        
        Args:
            download: 下载对象
        """
        self._downloads.append(download)
        
        # 记录下载信息
        download_info = f"下载开始: {download.url} -> {download.suggested_filename}"
        print(download_info)
        
        with allure.step(download_info):
            # 附加下载信息到报告
            allure.attach(
                f"URL: {download.url}\n"
                f"建议文件名: {download.suggested_filename}",
                name="下载信息",
                attachment_type=allure.attachment_type.TEXT
            )
        
        # 自动保存逻辑
        if self._auto_save:
            save_dir = self._auto_save_dir or self._download_dir
            self._save_download(download, save_dir)
    
    def _save_download(self, download: Download, save_dir: str) -> str:
        """
        保存下载的文件
        
        Args:
            download: 下载对象
            save_dir: 保存目录
            
        Returns:
            str: 保存的文件路径
        """
        # 等待下载完成
        download.path()  # 这会阻塞直到下载完成
        
        # 确定文件名
        suggested_filename = download.suggested_filename
        if not suggested_filename:
            suggested_filename = f"download_{int(time.time())}"
        
        # 确保文件名安全
        safe_filename = self._sanitize_filename(suggested_filename)
        
        # 构建保存路径
        save_path = os.path.join(save_dir, safe_filename)
        
        # 如果文件已存在，添加时间戳
        if os.path.exists(save_path):
            name, ext = os.path.splitext(safe_filename)
            timestamp = int(time.time())
            safe_filename = f"{name}_{timestamp}{ext}"
            save_path = os.path.join(save_dir, safe_filename)
        
        # 保存文件
        download.save_as(save_path)
        
        # 记录保存信息
        save_info = f"文件已保存: {save_path}"
        print(save_info)
        
        with allure.step(save_info):
            # 附加文件到报告
            try:
                allure.attach.file(
                    save_path,
                    name="下载的文件",
                    attachment_type=allure.attachment_type.from_file_path(save_path)
                )
            except Exception as e:
                print(f"无法附加文件到报告: {e}")
        
        # 调用完成回调
        for callback in self._download_complete_callbacks:
            try:
                callback(download, save_path)
            except Exception as e:
                print(f"下载完成回调执行失败: {e}")
        
        return save_path
    
    def _sanitize_filename(self, filename: str) -> str:
        """
        清理文件名，移除非法字符
        
        Args:
            filename: 原始文件名
            
        Returns:
            str: 清理后的文件名
        """
        # 移除非法字符
        illegal_chars = ['<', '>', ':', '"', '|', '?', '*', '\\', '/']
        for char in illegal_chars:
            filename = filename.replace(char, '_')
        
        # 限制文件名长度
        if len(filename) > 255:
            name, ext = os.path.splitext(filename)
            filename = name[:250 - len(ext)] + ext
        
        return filename
    
    # ========== 配置方法 ==========
    def set_download_dir(self, download_dir: str):
        """
        设置下载目录
        
        Args:
            download_dir: 下载目录路径
        """
        self._download_dir = download_dir
        os.makedirs(download_dir, exist_ok=True)
        
        with allure.step(f"设置下载目录: {download_dir}"):
            pass
    
    def auto_save(self, save_dir: Optional[str] = None):
        """
        启用自动保存
        
        Args:
            save_dir: 自动保存目录，如果为 None 则使用默认下载目录
        """
        self._auto_save = True
        self._auto_save_dir = save_dir
        
        with allure.step("启用自动保存下载文件"):
            pass
    
    def disable_auto_save(self):
        """禁用自动保存"""
        self._auto_save = False
        self._auto_save_dir = None
        
        with allure.step("禁用自动保存下载文件"):
            pass
    
    def add_completion_callback(self, callback: Callable[[Download, str], None]):
        """
        添加下载完成回调函数
        
        Args:
            callback: 回调函数，接收下载对象和保存路径作为参数
        """
        self._download_complete_callbacks.append(callback)
        
        with allure.step("添加下载完成回调函数"):
            pass
    
    def remove_completion_callback(self, callback: Callable[[Download, str], None]):
        """
        移除下载完成回调函数
        
        Args:
            callback: 要移除的回调函数
        """
        if callback in self._download_complete_callbacks:
            self._download_complete_callbacks.remove(callback)
            
            with allure.step("移除下载完成回调函数"):
                pass
    
    # ========== 下载检查 ==========
    def has_downloads(self) -> bool:
        """
        检查是否有下载
        
        Returns:
            bool: 是否有下载
        """
        return len(self._downloads) > 0
    
    def get_download_count(self) -> int:
        """
        获取下载数量
        
        Returns:
            int: 下载数量
        """
        return len(self._downloads)
    
    def get_download(self, index: int = 0) -> Optional[Download]:
        """
        获取指定索引的下载
        
        Args:
            index: 下载索引
            
        Returns:
            Optional[Download]: 下载对象，如果不存在则返回 None
        """
        if 0 <= index < len(self._downloads):
            return self._downloads[index]
        return None
    
    def get_latest_download(self) -> Optional[Download]:
        """
        获取最新的下载
        
        Returns:
            Optional[Download]: 最新的下载对象
        """
        if self._downloads:
            return self._downloads[-1]
        return None
    
    def get_download_info(self, index: int = 0) -> Optional[Dict[str, Any]]:
        """
        获取下载信息
        
        Args:
            index: 下载索引
            
        Returns:
            Optional[Dict]: 下载信息字典
        """
        download = self.get_download(index)
        if download:
            return {
                "url": download.url,
                "suggested_filename": download.suggested_filename,
                "failure": download.failure()
            }
        return None
    
    # ========== 等待下载 ==========
    def wait_for_download(self, timeout: int = 60000) -> Download:
        """
        等待下载完成
        
        Args:
            timeout: 超时时间（毫秒）
            
        Returns:
            Download: 下载对象
            
        Raises:
            TimeoutException: 等待超时
        """
        start_time = time.time()
        
        while time.time() - start_time < timeout / 1000:
            if self._downloads:
                download = self._downloads[0]
                # 检查下载是否完成
                try:
                    # 尝试获取路径，这会阻塞直到下载完成
                    download.path()
                    return download
                except Exception as e:
                    # 下载可能还在进行中，继续等待
                    pass
            time.sleep(0.1)  # 100ms 轮询
        
        raise TimeoutException("等待下载完成", timeout)
    
    def wait_for_download_count(self, count: int, timeout: int = 60000):
        """
        等待下载数量达到指定值
        
        Args:
            count: 期望的下载数量
            timeout: 超时时间（毫秒）
            
        Raises:
            TimeoutException: 等待超时
        """
        start_time = time.time()
        
        while time.time() - start_time < timeout / 1000:
            if len(self._downloads) >= count:
                return
            time.sleep(0.1)
        
        raise TimeoutException(f"等待下载数量达到 {count}", timeout)
    
    # ========== 下载操作 ==========
    def save_download(self, index: int = 0, filename: Optional[str] = None, 
                     save_dir: Optional[str] = None) -> str:
        """
        保存下载的文件
        
        Args:
            index: 下载索引
            filename: 自定义文件名，如果为 None 则使用建议的文件名
            save_dir: 保存目录，如果为 None 则使用默认下载目录
            
        Returns:
            str: 保存的文件路径
        """
        if not self._downloads:
            raise BrowserException("没有待处理的下载")
        
        if index >= len(self._downloads):
            raise BrowserException(f"下载索引 {index} 超出范围，共有 {len(self._downloads)} 个下载")
        
        download = self._downloads.pop(index)
        save_dir = save_dir or self._download_dir
        
        # 确保保存目录存在
        os.makedirs(save_dir, exist_ok=True)
        
        return self._save_download(download, save_dir)
    
    def save_latest_download(self, filename: Optional[str] = None,
                            save_dir: Optional[str] = None) -> str:
        """
        保存最新的下载
        
        Args:
            filename: 自定义文件名
            save_dir: 保存目录
            
        Returns:
            str: 保存的文件路径
        """
        if not self._downloads:
            raise BrowserException("没有待处理的下载")
        
        return self.save_download(len(self._downloads) - 1, filename, save_dir)
    
    def save_all_downloads(self, save_dir: Optional[str] = None) -> List[str]:
        """
        保存所有下载的文件
        
        Args:
            save_dir: 保存目录
            
        Returns:
            List[str]: 保存的文件路径列表
        """
        save_dir = save_dir or self._download_dir
        os.makedirs(save_dir, exist_ok=True)
        
        saved_paths = []
        while self._downloads:
            try:
                saved_path = self.save_download(0, save_dir=save_dir)
                saved_paths.append(saved_path)
            except Exception as e:
                print(f"保存下载失败: {e}")
        
        return saved_paths
    
    def cancel_download(self, index: int = 0):
        """
        取消下载
        
        Args:
            index: 下载索引
        """
        if not self._downloads:
            raise BrowserException("没有待处理的下载")
        
        if index >= len(self._downloads):
            raise BrowserException(f"下载索引 {index} 超出范围，共有 {len(self._downloads)} 个下载")
        
        # 从列表中移除，但无法真正取消 Playwright 的下载
        download = self._downloads.pop(index)
        
        with allure.step(f"取消下载: {download.url}"):
            pass
    
    # ========== 文件管理 ==========
    def get_saved_files(self) -> List[str]:
        """
        获取已保存的文件列表
        
        Returns:
            List[str]: 文件路径列表
        """
        if not os.path.exists(self._download_dir):
            return []
        
        return [os.path.join(self._download_dir, f) 
                for f in os.listdir(self._download_dir) 
                if os.path.isfile(os.path.join(self._download_dir, f))]
    
    def clear_saved_files(self):
        """清除所有已保存的文件"""
        if os.path.exists(self._download_dir):
            for filename in os.listdir(self._download_dir):
                file_path = os.path.join(self._download_dir, filename)
                try:
                    if os.path.isfile(file_path):
                        os.unlink(file_path)
                    elif os.path.isdir(file_path):
                        shutil.rmtree(file_path)
                except Exception as e:
                    print(f"删除文件失败 {file_path}: {e}")
        
        with allure.step("清除所有已保存的下载文件"):
            pass
    
    def cleanup_old_files(self, max_age_days: int = 7):
        """
        清理旧文件
        
        Args:
            max_age_days: 最大保留天数
        """
        if not os.path.exists(self._download_dir):
            return
        
        current_time = time.time()
        cutoff_time = current_time - (max_age_days * 24 * 60 * 60)
        
        for filename in os.listdir(self._download_dir):
            file_path = os.path.join(self._download_dir, filename)
            try:
                if os.path.isfile(file_path):
                    file_mtime = os.path.getmtime(file_path)
                    if file_mtime < cutoff_time:
                        os.unlink(file_path)
                        print(f"删除旧文件: {file_path}")
            except Exception as e:
                print(f"删除旧文件失败 {file_path}: {e}")
    
    # ========== 断言方法 ==========
    def assert_download_started(self, url_contains: Optional[str] = None,
                               filename_contains: Optional[str] = None,
                               timeout: int = 30000):
        """
        断言下载已开始
        
        Args:
            url_contains: 期望 URL 包含的文本
            filename_contains: 期望文件名包含的文本
            timeout: 超时时间（毫秒）
            
        Raises:
            AssertionError: 断言失败
        """
        try:
            download = self.wait_for_download(timeout)
            
            if url_contains and url_contains not in download.url:
                raise AssertionError(
                    f"下载 URL 不包含期望文本。期望包含: '{url_contains}'，实际: '{download.url}'"
                )
            
            if filename_contains and download.suggested_filename:
                if filename_contains not in download.suggested_filename:
                    raise AssertionError(
                        f"下载文件名不包含期望文本。期望包含: '{filename_contains}'，实际: '{download.suggested_filename}'"
                    )
            
            with allure.step(f"断言下载已开始: {download.suggested_filename}"):
                pass
                
        except TimeoutException:
            raise AssertionError(f"在 {timeout}ms 内没有下载开始")
    
    def assert_download_completed(self, timeout: int = 60000):
        """
        断言下载已完成
        
        Args:
            timeout: 超时时间（毫秒）
            
        Raises:
            AssertionError: 断言失败
        """
        try:
            download = self.wait_for_download(timeout)
            # 如果 wait_for_download 成功返回，说明下载已完成
            with allure.step(f"断言下载已完成: {download.suggested_filename}"):
                pass
                
        except TimeoutException:
            raise AssertionError(f"在 {timeout}ms 内下载未完成")
        except Exception as e:
            raise AssertionError(f"下载失败: {str(e)}")
    
    # ========== 清理 ==========
    def clear_downloads(self):
        """清除所有下载记录"""
        self._downloads.clear()
        
        with allure.step("清除下载记录"):
            pass
    
    def remove_listeners(self):
        """移除下载监听器"""
        self._page.remove_listener("download", self._handle_download)
        
        with allure.step("移除下载监听器"):
            pass