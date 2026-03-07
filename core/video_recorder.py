# -*- coding: UTF-8 -*-
"""
视频录制器
封装 Playwright 视频录制功能
"""

import os
import time
import allure
import shutil
from pathlib import Path
from typing import Optional, List, Dict, Any
from playwright.sync_api import Page, BrowserContext

from config.config_loader import config


class VideoRecorder:
    """视频录制器"""
    
    def __init__(self, context: BrowserContext):
        """
        初始化视频录制器
        
        Args:
            context: BrowserContext 对象
        """
        self._context = context
        self._video_dir = config.get("video_dir", "./videos")
        self._videos: List[str] = []
        self._is_recording = False
        
        # 确保视频目录存在
        os.makedirs(self._video_dir, exist_ok=True)
    
    # ========== 配置方法 ==========
    def set_video_dir(self, video_dir: str):
        """
        设置视频保存目录
        
        Args:
            video_dir: 视频目录路径
        """
        self._video_dir = video_dir
        os.makedirs(video_dir, exist_ok=True)
        
        with allure.step(f"设置视频保存目录: {video_dir}"):
            pass
    
    def enable_recording(self, **kwargs):
        """
        启用视频录制
        
        Args:
            **kwargs: 录制选项，如：
                record_video_dir: 视频保存目录
                record_video_size: 视频尺寸，如 {"width": 1280, "height": 720}
                record_video_scale: 视频缩放比例
        """
        if self._is_recording:
            print("视频录制已在进行中")
            return
        
        # 设置录制选项
        record_options = {
            "record_video_dir": self._video_dir,
            **kwargs
        }
        
        # 更新上下文选项（需要重新创建上下文）
        print("启用视频录制需要重新创建浏览器上下文")
        
        with allure.step("启用视频录制"):
            pass
    
    def disable_recording(self):
        """禁用视频录制"""
        if not self._is_recording:
            print("视频录制未启用")
            return
        
        # 停止录制（通过关闭页面或上下文）
        print("停止视频录制")
        self._is_recording = False
        
        with allure.step("禁用视频录制"):
            pass
    
    # ========== 视频管理 ==========
    def get_videos(self) -> List[str]:
        """
        获取录制的视频文件列表
        
        Returns:
            List[str]: 视频文件路径列表
        """
        if not os.path.exists(self._video_dir):
            return []
        
        # 查找视频文件
        video_extensions = ['.mp4', '.webm', '.avi', '.mov']
        videos = []
        
        for file in os.listdir(self._video_dir):
            file_path = os.path.join(self._video_dir, file)
            if os.path.isfile(file_path):
                ext = os.path.splitext(file)[1].lower()
                if ext in video_extensions:
                    videos.append(file_path)
        
        return videos
    
    def get_latest_video(self) -> Optional[str]:
        """
        获取最新的视频文件
        
        Returns:
            Optional[str]: 最新的视频文件路径
        """
        videos = self.get_videos()
        if not videos:
            return None
        
        # 按修改时间排序
        videos.sort(key=os.path.getmtime, reverse=True)
        return videos[0]
    
    def save_video(self, video_path: str, new_name: Optional[str] = None) -> str:
        """
        保存视频文件（复制到指定位置）
        
        Args:
            video_path: 原始视频文件路径
            new_name: 新文件名，如果为 None 则使用原始文件名
            
        Returns:
            str: 保存的视频文件路径
        """
        if not os.path.exists(video_path):
            raise FileNotFoundError(f"视频文件不存在: {video_path}")
        
        # 确定新文件名
        if new_name is None:
            new_name = os.path.basename(video_path)
        
        # 确保新文件名有扩展名
        if not os.path.splitext(new_name)[1]:
            ext = os.path.splitext(video_path)[1]
            new_name = f"{new_name}{ext}"
        
        # 构建目标路径
        save_dir = self._video_dir
        save_path = os.path.join(save_dir, new_name)
        
        # 如果文件已存在，添加时间戳
        if os.path.exists(save_path):
            name, ext = os.path.splitext(new_name)
            timestamp = int(time.time())
            new_name = f"{name}_{timestamp}{ext}"
            save_path = os.path.join(save_dir, new_name)
        
        # 复制文件
        shutil.copy2(video_path, save_path)
        
        with allure.step(f"保存视频: {save_path}"):
            # 附加视频到 Allure 报告
            try:
                allure.attach.file(
                    save_path,
                    name="录制视频",
                    attachment_type=allure.attachment_type.WEBM  # 或根据实际格式调整
                )
            except Exception as e:
                print(f"无法附加视频到报告: {e}")
        
        return save_path
    
    def save_all_videos(self, prefix: str = "video") -> List[str]:
        """
        保存所有视频文件
        
        Args:
            prefix: 文件名前缀
            
        Returns:
            List[str]: 保存的视频文件路径列表
        """
        videos = self.get_videos()
        saved_paths = []
        
        for i, video_path in enumerate(videos):
            try:
                new_name = f"{prefix}_{i+1}_{int(time.time())}.mp4"
                saved_path = self.save_video(video_path, new_name)
                saved_paths.append(saved_path)
            except Exception as e:
                print(f"保存视频失败 {video_path}: {e}")
        
        return saved_paths
    
    def cleanup_old_videos(self, max_age_days: int = 7):
        """
        清理旧视频文件
        
        Args:
            max_age_days: 最大保留天数
        """
        if not os.path.exists(self._video_dir):
            return
        
        current_time = time.time()
        cutoff_time = current_time - (max_age_days * 24 * 60 * 60)
        
        for file in os.listdir(self._video_dir):
            file_path = os.path.join(self._video_dir, file)
            try:
                if os.path.isfile(file_path):
                    file_mtime = os.path.getmtime(file_path)
                    if file_mtime < cutoff_time:
                        os.unlink(file_path)
                        print(f"删除旧视频: {file_path}")
            except Exception as e:
                print(f"删除旧视频失败 {file_path}: {e}")
    
    # ========== 页面视频录制 ==========
    def start_page_recording(self, page: Page, video_name: Optional[str] = None) -> str:
        """
        开始页面录制
        
        Args:
            page: Page 对象
            video_name: 视频名称
            
        Returns:
            str: 视频文件路径
        """
        # Playwright 的视频录制是在上下文级别配置的
        # 这里我们模拟页面级别的录制
        if video_name is None:
            video_name = f"page_{int(time.time())}"
        
        # 记录开始时间
        start_time = time.time()
        
        with allure.step(f"开始页面录制: {video_name}"):
            # 这里可以添加自定义的录制逻辑
            # 例如，使用外部工具或屏幕录制
            pass
        
        # 返回虚拟路径（实际实现需要集成真正的录制工具）
        video_path = os.path.join(self._video_dir, f"{video_name}.mp4")
        self._videos.append(video_path)
        self._is_recording = True
        
        return video_path
    
    def stop_page_recording(self, page: Page, save: bool = True) -> Optional[str]:
        """
        停止页面录制
        
        Args:
            page: Page 对象
            save: 是否保存视频
            
        Returns:
            Optional[str]: 保存的视频文件路径，如果不保存则返回 None
        """
        if not self._is_recording:
            print("没有正在进行的录制")
            return None
        
        self._is_recording = False
        
        with allure.step("停止页面录制"):
            pass
        
        if save and self._videos:
            video_path = self._videos[-1]
            return self.save_video(video_path)
        
        return None
    
    # ========== 屏幕截图序列（伪视频） ==========
    def capture_screenshot_sequence(self, page: Page, interval: float = 1.0,
                                   duration: float = 10.0,
                                   sequence_name: Optional[str] = None) -> List[str]:
        """
        捕获截图序列（模拟视频）
        
        Args:
            page: Page 对象
            interval: 截图间隔（秒）
            duration: 总时长（秒）
            sequence_name: 序列名称
            
        Returns:
            List[str]: 截图文件路径列表
        """
        if sequence_name is None:
            sequence_name = f"sequence_{int(time.time())}"
        
        screenshots_dir = os.path.join(self._video_dir, sequence_name)
        os.makedirs(screenshots_dir, exist_ok=True)
        
        screenshots = []
        num_frames = int(duration / interval)
        
        with allure.step(f"捕获截图序列: {sequence_name} ({num_frames} 帧)"):
            for i in range(num_frames):
                # 等待间隔
                time.sleep(interval)
                
                # 截图
                screenshot_name = f"frame_{i:04d}.png"
                screenshot_path = os.path.join(screenshots_dir, screenshot_name)
                
                try:
                    page.screenshot(path=screenshot_path)
                    screenshots.append(screenshot_path)
                    
                    # 附加第一帧到报告
                    if i == 0:
                        allure.attach.file(
                            screenshot_path,
                            name="截图序列第一帧",
                            attachment_type=allure.attachment_type.PNG
                        )
                except Exception as e:
                    print(f"截图失败 (帧 {i}): {e}")
        
        return screenshots
    
    # ========== 视频处理 ==========
    def compress_video(self, video_path: str, quality: str = "medium") -> str:
        """
        压缩视频文件
        
        Args:
            video_path: 视频文件路径
            quality: 质量等级（"low", "medium", "high"）
            
        Returns:
            str: 压缩后的视频文件路径
        """
        # 这是一个示例实现，实际需要安装视频处理工具
        # 例如使用 ffmpeg
        
        if not os.path.exists(video_path):
            raise FileNotFoundError(f"视频文件不存在: {video_path}")
        
        # 构建压缩后的文件路径
        name, ext = os.path.splitext(video_path)
        compressed_path = f"{name}_compressed{ext}"
        
        print(f"视频压缩功能需要安装 ffmpeg")
        print(f"原始文件: {video_path}")
        print(f"压缩文件: {compressed_path}")
        print(f"质量等级: {quality}")
        
        # 这里可以添加 ffmpeg 命令
        # ffmpeg -i input.mp4 -vcodec libx264 -crf 28 output_compressed.mp4
        
        return compressed_path
    
    def extract_frames(self, video_path: str, output_dir: Optional[str] = None,
                      frame_rate: int = 1) -> List[str]:
        """
        从视频中提取帧
        
        Args:
            video_path: 视频文件路径
            output_dir: 输出目录
            frame_rate: 每秒提取帧数
            
        Returns:
            List[str]: 提取的帧文件路径列表
        """
        if output_dir is None:
            name = os.path.splitext(os.path.basename(video_path))[0]
            output_dir = os.path.join(self._video_dir, f"{name}_frames")
        
        os.makedirs(output_dir, exist_ok=True)
        
        print(f"提取视频帧功能需要安装 ffmpeg")
        print(f"视频文件: {video_path}")
        print(f"输出目录: {output_dir}")
        print(f"帧率: {frame_rate} fps")
        
        # 这里可以添加 ffmpeg 命令
        # ffmpeg -i input.mp4 -vf fps=1 frame_%04d.png
        
        # 返回示例文件列表
        frames = []
        for i in range(10):  # 示例：10帧
            frame_path = os.path.join(output_dir, f"frame_{i:04d}.png")
            frames.append(frame_path)
        
        return frames
    
    # ========== 断言方法 ==========
    def assert_video_recorded(self, timeout: int = 10000):
        """
        断言视频已录制
        
        Args:
            timeout: 超时时间（毫秒）
            
        Raises:
            AssertionError: 如果没有视频被录制
        """
        start_time = time.time()
        
        while time.time() - start_time < timeout / 1000:
            videos = self.get_videos()
            if videos:
                with allure.step(f"断言视频已录制: {len(videos)} 个视频"):
                    return True
            time.sleep(1)  # 1秒轮询
        
        raise AssertionError(f"在 {timeout}ms 内没有视频被录制")
    
    # ========== 清理 ==========
    def clear_videos(self):
        """清除所有视频文件"""
        videos = self.get_videos()
        for video_path in videos:
            try:
                os.unlink(video_path)
            except Exception as e:
                print(f"删除视频失败 {video_path}: {e}")
        
        self._videos.clear()
        
        with allure.step("清除所有视频文件"):
            pass
    
    def cleanup(self):
        """清理资源"""
        self.clear_videos()
        
        # 删除空目录
        try:
            if os.path.exists(self._video_dir) and not os.listdir(self._video_dir):
                os.rmdir(self._video_dir)
        except Exception as e:
            print(f"删除目录失败 {self._video_dir}: {e}")