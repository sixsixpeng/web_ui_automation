#!/usr/bin/env python3
"""
替换项目中剩余的print语句为日志输出
"""
import os
import re
import sys
from pathlib import Path

def replace_prints_in_file(file_path):
    """替换文件中的print语句为logger.info"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 记录原始内容
        original = content
        
        # 替换所有print(...)为logger.info(...)
        # 使用正则表达式匹配 print(任意内容)
        # 注意：这不会处理多行print，但我们的print语句通常都是单行的
        pattern = r'print\((.*?)\)'
        
        def replacement(match):
            # 获取print内部的参数
            inner = match.group(1)
            # 如果内部字符串以f开头，需要保留f前缀
            # 但我们需要确保替换为logger.info调用
            return f'logger.info({inner})'
        
        new_content = re.sub(pattern, replacement, content, flags=re.DOTALL)
        
        # 如果内容发生变化，写入文件
        if new_content != original:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print(f"已更新: {file_path}")
            return True
        return False
    except Exception as e:
        print(f"处理文件 {file_path} 时出错: {e}")
        return False

def main():
    # 处理核心模块中的文件
    core_dir = Path(__file__).parent / "core"
    files_to_process = [
        core_dir / "video_recorder.py",
        core_dir / "page_wrapper.py", 
        core_dir / "event_helper.py",
        core_dir / "download_helper.py",
        core_dir / "debug_helper.py",
    ]
    
    for file_path in files_to_process:
        if file_path.exists():
            replace_prints_in_file(file_path)
        else:
            print(f"文件不存在: {file_path}")
    
    print("替换完成")

if __name__ == "__main__":
    main()