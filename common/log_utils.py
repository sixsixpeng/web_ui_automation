# -*- coding: UTF-8 -*-
"""
高级日志工具模块
支持彩色输出、自定义格式、模块化日志级别控制、按天分割日志
"""

import os
import sys
import logging
import platform
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional
from logging.handlers import TimedRotatingFileHandler

# 平台和编码检测
IS_WINDOWS = platform.system().lower() == 'windows'
SUPPORTS_UNICODE = not IS_WINDOWS  # Windows控制台默认可能不支持所有Unicode
try:
    # 尝试设置Windows控制台编码
    if IS_WINDOWS:
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
except:
    SUPPORTS_UNICODE = False

from config.config_loader import config


class ColoredFormatter(logging.Formatter):
    """彩色日志格式化器，使用 ANSI 转义码"""
    
    # ANSI 颜色方案
    COLORS = {
        logging.DEBUG: '\033[96m',      # 亮青色，加粗
        logging.INFO: '\033[92m',       # 亮绿色，加粗
        logging.WARNING: '\033[93;1m',  # 亮黄色，加粗
        logging.ERROR: '\033[91;1;5m',  # 亮红色，加粗，闪烁
        logging.CRITICAL: '\033[97;101;1;5m',  # 亮白色文本，亮红色背景，加粗，闪烁
    }
    RESET = '\033[0m'  # 重置颜色
    
    # 从配置获取颜色（保持向后兼容）
    CONFIG_COLORS = {
        'DEBUG': 'cyan',
        'INFO': 'green',
        'WARNING': 'yellow',
        'ERROR': 'red',
        'CRITICAL': 'bold_red',
    }
    
    def __init__(self, fmt=None, datefmt=None, style='%', use_color=True):
        super().__init__(fmt, datefmt, style)
        self.use_color = use_color
        self._load_color_config()
    
    def _load_color_config(self):
        """从配置加载颜色设置（保持向后兼容）"""
        config_colors = config.get("log_colors", {})
        if config_colors:
            # 可以扩展支持配置自定义颜色，但当前使用固定ANSI
            pass
    
    def formatTime(self, record, datefmt=None):
        """自定义时间格式"""
        from datetime import datetime
        ct = datetime.fromtimestamp(record.created)
        if datefmt:
            return ct.strftime(datefmt)
        else:
            return super().formatTime(record, datefmt)
    
    def format(self, record):
        """格式化日志记录，添加颜色"""
        # 保存原始级别名称
        original_levelname = record.levelname
        
        if self.use_color and record.levelno in self.COLORS:
            # 添加颜色到整个消息
            color = self.COLORS[record.levelno]
            message = super().format(record)
            return f"{color}{message}{self.RESET}"
        
        # 调用父类格式化
        return super().format(record)


class AdvancedLogUtils:
    """高级日志工具类"""
    
    _initialized = False
    _loggers_cache = {}
    
    # 图标配置（Unicode和ASCII备选）
    _ICONS = {
        # Unicode图标
        'unicode': {
            'test_start': '🚀',
            'test_pass': '✅',
            'test_fail': '❌',
            'test_warn': '⚠️',
            'api_success': '✅',
            'api_warning': '⚠️',
            'browser_success': '✅',
            'browser_warning': '⚠️',
            'element_found': '🔍',
            'element_not_found': '❌',
            'performance_fast': '⚡',
            'performance_slow': '🐌',
            'step': '📝',
            'data': '📊',
            'config': '⚙️',
            'update': '📊',
        },
        # ASCII备选
        'ascii': {
            'test_start': '[START]',
            'test_pass': '[PASS]',
            'test_fail': '[FAIL]',
            'test_warn': '[WARN]',
            'api_success': '[OK]',
            'api_warning': '[WARN]',
            'browser_success': '[OK]',
            'browser_warning': '[WARN]',
            'element_found': '[FOUND]',
            'element_not_found': '[NOT FOUND]',
            'performance_fast': '[FAST]',
            'performance_slow': '[SLOW]',
            'step': '[STEP]',
            'data': '[DATA]',
            'config': '[CONFIG]',
            'update': '[UPDATE]',
        }
    }
    
    @classmethod
    def _get_icon(cls, icon_name: str) -> str:
        """获取图标，根据平台自动选择Unicode或ASCII"""
        icon_set = 'unicode' if SUPPORTS_UNICODE else 'ascii'
        return cls._ICONS[icon_set].get(icon_name, '')
    
    @classmethod
    def setup_logging(cls):
        """配置高级日志系统"""
        if cls._initialized:
            return
        
        # 获取基础配置
        log_dir = config.get("log_dir", "log")
        log_formats = config.get("log_formats", {})
        log_modules = config.get("log_modules", {})
        
        # 确保日志目录存在
        Path(log_dir).mkdir(parents=True, exist_ok=True)
        
        # 检查是否启用颜色（终端支持）
        use_color = sys.stdout.isatty() if hasattr(sys.stdout, 'isatty') else True
        
        # 设置日志文件名（固定名称，按天自动分割）
        log_file = Path(log_dir) / "automation.log"
        
        # 获取格式配置
        console_format_str = log_formats.get("console", 
            "%(asctime)s | %(levelname)-8s | %(module)-15s | %(name)-25s | %(message)s")
        file_format_str = log_formats.get("file",
            "%(asctime)s | %(levelname)-8s | %(module)-15s | %(name)-25s | %(filename)s:%(lineno)d | %(message)s")
        
        # 配置根日志记录器
        root_logger = logging.getLogger()
        root_logger.setLevel(logging.DEBUG)  # 根记录器设置为最低级别
        
        # 清除已有的处理器
        root_logger.handlers.clear()
        
        # 控制台处理器
        if config.get("console_log_enabled", True):
            console_handler = logging.StreamHandler(sys.stdout)
            console_formatter = ColoredFormatter(
                fmt=console_format_str,
                datefmt='%Y-%m-%d %H:%M:%S',
                use_color=use_color
            )
            console_handler.setFormatter(console_formatter)
            console_handler.setLevel(cls._get_log_level(config.get("console_log_level", "INFO")))
            root_logger.addHandler(console_handler)
        
        # 文件处理器（按天自动分割）
        if config.get("file_log_enabled", True):
            file_handler = TimedRotatingFileHandler(
                filename=log_file,
                when='midnight',  # 每天午夜分割
                interval=1,       # 每天一次
                backupCount=config.get("log_file_backup_count", 5),
                encoding='utf-8',
                utc=False         # 使用本地时间
            )
            file_formatter = logging.Formatter(
                fmt=file_format_str,
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            file_handler.setFormatter(file_formatter)
            file_handler.setLevel(cls._get_log_level(config.get("file_log_level", "DEBUG")))
            root_logger.addHandler(file_handler)
        
        # 配置模块特定日志级别
        for module_name, level_str in log_modules.items():
            module_logger = logging.getLogger(module_name)
            module_logger.setLevel(cls._get_log_level(level_str))
            # 设置传播（不传播到根记录器，避免重复）
            module_logger.propagate = False
        
        # 设置第三方库日志级别
        third_party_modules = {
            "urllib3": "WARNING",
            "playwright": "WARNING",
            "selenium": "WARNING",
            "requests": "WARNING",
            "faker": "WARNING",
        }
        
        for lib_name, default_level in third_party_modules.items():
            lib_logger = logging.getLogger(lib_name)
            lib_logger.setLevel(cls._get_log_level(log_modules.get(lib_name, default_level)))
            lib_logger.propagate = False
        
        cls._initialized = True
        
        # 记录日志系统启动信息
        startup_logger = cls.get_logger("log_system")
        startup_logger.info("=" * 80)
        startup_logger.info("高级日志系统已初始化")
        startup_logger.info(f"日志文件: {log_file}")
        startup_logger.info(f"控制台日志: {'启用' if config.get('console_log_enabled', True) else '禁用'}")
        startup_logger.info(f"文件日志: {'启用' if config.get('file_log_enabled', True) else '禁用'}")
        startup_logger.info(f"颜色支持: {'启用' if use_color else '禁用'}")
        startup_logger.info("=" * 80)
    
    @classmethod
    def _get_log_level(cls, level_str: str) -> int:
        """将字符串日志级别转换为 logging 常量"""
        level_str = level_str.upper()
        level_map = {
            'DEBUG': logging.DEBUG,
            'INFO': logging.INFO,
            'WARNING': logging.WARNING,
            'ERROR': logging.ERROR,
            'CRITICAL': logging.CRITICAL,
        }
        return level_map.get(level_str, logging.INFO)
    
    @classmethod
    def get_logger(cls, name: str, module_type: str = None) -> logging.Logger:
        """
        获取指定名称的日志记录器
        
        Args:
            name: 日志记录器名称，通常使用 __name__
            module_type: 模块类型（test/api/browser等），用于应用特定配置
            
        Returns:
            logging.Logger: 日志记录器实例
        """
        if not cls._initialized:
            cls.setup_logging()
        
        # 如果提供了模块类型，使用模块类型作为记录器名称的一部分
        if module_type:
            logger_name = f"{module_type}.{name}"
        else:
            logger_name = name
        
        # 缓存记录器
        if logger_name not in cls._loggers_cache:
            logger = logging.getLogger(logger_name)
            
            # 应用模块特定配置
            if module_type:
                module_config = config.get("log_modules", {}).get(module_type)
                if module_config:
                    logger.setLevel(cls._get_log_level(module_config))
                    logger.propagate = False
            
            cls._loggers_cache[logger_name] = logger
        
        return cls._loggers_cache[logger_name]
    
    @classmethod
    def get_module_logger(cls, module_type: str, submodule: str = None) -> logging.Logger:
        """
        获取模块化日志记录器
        
        Args:
            module_type: 模块类型（test/api/browser/element/performance）
            submodule: 子模块名称
            
        Returns:
            logging.Logger: 模块化日志记录器
        """
        logger_name = module_type
        if submodule:
            logger_name = f"{module_type}.{submodule}"
        
        return cls.get_logger(logger_name, module_type)
    
    @classmethod
    def log_test_start(cls, test_name: str, test_module: str = ""):
        """
        记录测试用例开始
        """
        logger = cls.get_module_logger("test", test_module)
        icon = cls._get_icon('test_start')
        if test_module:
            logger.info(f"{icon} 开始执行测试用例: {test_module}.{test_name}")
        else:
            logger.info(f"{icon} 开始执行测试用例: {test_name}")
    
    @classmethod
    def log_test_end(cls, test_name: str, test_module: str = "", status: str = "完成"):
        """
        记录测试用例结束
        """
        logger = cls.get_module_logger("test", test_module)
        # 根据状态选择图标
        if status == "完成":
            status_icon = cls._get_icon('test_pass')
        elif status == "失败":
            status_icon = cls._get_icon('test_fail')
        else:
            status_icon = cls._get_icon('test_warn')
        if test_module:
            logger.info(f"{status_icon} 测试用例 {test_module}.{test_name} {status}")
        else:
            logger.info(f"{status_icon} 测试用例 {test_name} {status}")
    
    @classmethod
    def log_test_failure(cls, test_name: str, error_message: str, test_module: str = ""):
        """
        记录测试用例失败
        """
        logger = cls.get_module_logger("test", test_module)
        icon = cls._get_icon('test_fail')
        if test_module:
            logger.error(f"{icon} 测试用例 {test_module}.{test_name} 失败: {error_message}")
        else:
            logger.error(f"{icon} 测试用例 {test_name} 失败: {error_message}")
    
    @classmethod
    def log_api_call(cls, method: str, url: str, status_code: int, duration: float):
        """
        记录 API 调用
        """
        logger = cls.get_module_logger("api")
        status_icon = cls._get_icon('api_success') if 200 <= status_code < 300 else cls._get_icon('api_warning')
        level = logging.INFO if 200 <= status_code < 300 else logging.WARNING
        logger.log(level, f"{status_icon} {method} {url} - {status_code} ({duration:.3f}s)")
    
    @classmethod
    def log_browser_action(cls, action: str, selector: str = "", success: bool = True):
        """
        记录浏览器操作
        """
        logger = cls.get_module_logger("browser")
        icon = cls._get_icon('browser_success') if success else cls._get_icon('browser_warning')
        if selector:
            message = f"{icon} {action}: {selector}"
        else:
            message = f"{icon} {action}"
        
        if success:
            logger.info(message)
        else:
            logger.warning(message)
    
    @classmethod
    def log_element_found(cls, selector: str, page_url: str = ""):
        """
        记录元素查找
        """
        logger = cls.get_module_logger("element")
        icon = cls._get_icon('element_found')
        if page_url:
            logger.debug(f"{icon} 找到元素: {selector} (页面: {page_url})")
        else:
            logger.debug(f"{icon} 找到元素: {selector}")
    
    @classmethod
    def log_element_not_found(cls, selector: str, page_url: str = ""):
        """
        记录元素未找到
        """
        logger = cls.get_module_logger("element")
        icon = cls._get_icon('element_not_found')
        if page_url:
            logger.warning(f"{icon} 元素未找到: {selector} (页面: {page_url})")
        else:
            logger.warning(f"{icon} 元素未找到: {selector}")
    
    @classmethod
    def log_performance(cls, operation: str, duration: float, threshold: float = 5.0):
        """
        记录性能信息
        """
        logger = cls.get_module_logger("performance")
        if duration > threshold:
            icon = cls._get_icon('performance_slow')
            logger.warning(f"{icon} 性能警告: {operation} 耗时 {duration:.3f}s (阈值: {threshold}s)")
        else:
            icon = cls._get_icon('performance_fast')
            logger.info(f"{icon} 性能正常: {operation} 耗时 {duration:.3f}s")
    
    @classmethod
    def log_step(cls, step_description: str, module: str = "test", level: str = "INFO"):
        """
        记录测试步骤
        """
        logger = cls.get_module_logger(module)
        log_method = getattr(logger, level.lower(), logger.info)
        icon = cls._get_icon('step')
        log_method(f"{icon} {step_description}")
    
    @classmethod
    def log_data(cls, data_description: str, data_value, module: str = "test"):
        """
        记录测试数据
        """
        logger = cls.get_module_logger(module)
        icon = cls._get_icon('data')
        logger.debug(f"{icon} {data_description}: {data_value}")
    
    @classmethod
    def log_config(cls, config_description: str, config_value, module: str = "config"):
        """
        记录配置信息
        """
        logger = cls.get_module_logger(module)
        icon = cls._get_icon('config')
        logger.info(f"{icon}  {config_description}: {config_value}")
    
    @classmethod
    def attach_log_to_allure(cls, log_file_path: str = None):
        """
        将日志文件附加到 Allure 报告
        """
        import allure
        
        if log_file_path is None:
            # 查找最新的日志文件
            log_dir = config.get("log_dir", "log")
            log_files = list(Path(log_dir).glob("*.log"))
            if not log_files:
                return
            
            log_file_path = max(log_files, key=lambda x: x.stat().st_mtime)
        
        if os.path.exists(log_file_path):
            with open(log_file_path, 'r', encoding='utf-8') as f:
                log_content = f.read()
            
            allure.attach(
                log_content,
                name="测试执行日志",
                attachment_type=allure.attachment_type.TEXT
            )
    
    @classmethod
    def update_log_level(cls, module_name: str, level: str):
        """
        动态更新模块日志级别
        
        Args:
            module_name: 模块名称
            level: 日志级别（DEBUG/INFO/WARNING/ERROR/CRITICAL）
        """
        logger = logging.getLogger(module_name)
        logger.setLevel(cls._get_log_level(level))
        
        config_logger = cls.get_module_logger("log_system")
        icon = cls._get_icon('update')
        config_logger.info(f"{icon} 更新模块 '{module_name}' 日志级别为: {level}")
    
    @classmethod
    def get_log_config_summary(cls) -> Dict[str, Any]:
        """
        获取日志配置摘要
        """
        return {
            "initialized": cls._initialized,
            "color_support": "ansi",  # 使用 ANSI 转义码
            "console_enabled": config.get("console_log_enabled", True),
            "file_enabled": config.get("file_log_enabled", True),
            "log_dir": config.get("log_dir", "log"),
            "module_levels": config.get("log_modules", {}),
        }


# 创建兼容的 LogUtils 类，保持向后兼容
class LogUtils(AdvancedLogUtils):
    """兼容性日志工具类（保持原有 API）"""
    pass


# 初始化日志系统
LogUtils.setup_logging()

# 创建常用日志记录器
logger = LogUtils.get_logger(__name__)