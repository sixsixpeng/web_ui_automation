# -*- coding: utf-8 -*-
"""log_util - Config-driven logging with colored console and multi-handler support"""
import logging
import re
import sys
from datetime import datetime
from logging.handlers import RotatingFileHandler

from utils.path_util import path_util

# yaml_json_util imported lazily in _load_config

# Default config (will be overridden by config.yaml)
_CONFIG = {
    "level": "",  # 仅由 config.yaml 覆盖，留空启用 INFO 兜底
    "console": {
        "enabled": True,
    },
    "file": {
        "enabled": True,
        "max_size_mb": 500,
        "backup_count": 7,
    },
    "format": {
        "file": "%(asctime)s.%(msecs)03d | %(levelname)-8s | %(name)s | %(process)d | %(filename)s:%(lineno)d | %(message)s",
    },
    "date_format": "%Y-%m-%d %H:%M:%S",
    "enable_desensitization": True,
}


def _load_config():
    from utils.yaml_json_util import yaml_json_util
    """Load logging config from config.yaml, fallback to defaults"""
    try:
        cfg = yaml_json_util.load_yaml(str(path_util.config_dir / "config.yaml"))
        lc = cfg.get("logging", {})
        for k, v in lc.items():
            if isinstance(v, dict) and k in _CONFIG and isinstance(_CONFIG[k], dict):
                _CONFIG[k].update(v)
            elif k == "format" and isinstance(v, str):
                _CONFIG["format"]["console"] = v
                _CONFIG["format"]["file"] = v
            else:
                _CONFIG[k] = v
    except Exception:
        pass


SENSITIVE_PATTERNS = [
    (re.compile(r"(1[3-9]\d)\d{4}(\d{4})"), r"\1****\2"),
    (re.compile(r"password[=:\\'\s]+\S+", re.I), "******"),
    (re.compile(r"token[=:\\'\s]+\S+", re.I), "******"),
    (re.compile(r"\\b\d{16,19}\\b"), "**** **** **** ****"),
]


class ColoredFormatter(logging.Formatter):
    """Formatter with ANSI color support for console output"""

    def __init__(self, fmt=None, datefmt=None, colors=None, enable=True):
        super().__init__(fmt, datefmt)
        self._colors = colors or {}
        self._reset = "\\033[0m"
        self._enable = enable

    def formatTime(self, record, datefmt=None):
        """格式化时间输出"""
        ct = datetime.fromtimestamp(record.created)
        return ct.strftime(datefmt) if datefmt else super().formatTime(record, datefmt)

    def format(self, record):
        """格式化日志记录"""
        msg = super().format(record)
        if self._enable:
            color = self._colors.get(record.levelno, self._reset)
            return f"{color}{msg}{self._reset}"
        return msg


class DesensitizeFormatter(logging.Formatter):
    """Formatter that desensitizes sensitive data in log messages"""

    def __init__(self, fmt=None, datefmt=None, enable=True):
        super().__init__(fmt, datefmt)
        self._enable = enable

    def format(self, record):
        """格式化日志记录"""
        msg = super().format(record)
        if self._enable:
            for pat, repl in SENSITIVE_PATTERNS:
                msg = pat.sub(repl, msg)
        return msg


class LogManager:
    _config_loaded = False
    """Global log manager — singleton, configured from config.yaml"""
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._ready = False
        return cls._instance

    def __init__(self):
        if self._ready:
            return
        self._ready = True
        self._loggers = {}
        if not LogManager._config_loaded:
            _load_config()
            LogManager._config_loaded = True
        self._setup()

    def _setup(self):
        root = logging.getLogger()
        root.handlers.clear()
        cfg = _CONFIG
        level_name = (cfg["level"] or "INFO").upper()
        root.setLevel(getattr(logging, level_name, logging.DEBUG))
        df = cfg["date_format"]
        log_fmt = cfg["format"]["file"]

        # Console handler
        try:
            ch = logging.StreamHandler(sys.stdout)
            ch.setLevel(getattr(logging, level_name, logging.INFO))
            ch.setFormatter(DesensitizeFormatter(fmt=log_fmt, datefmt=df, enable=cfg["enable_desensitization"]))
            root.addHandler(ch)
        except:
            pass

        # File handler with rotation
        try:
            log_file = str(path_util.logs_dir / "automation.log")
            path_util.ensure_dir(str(path_util.logs_dir))
            fh = RotatingFileHandler(
                log_file,
                maxBytes=cfg["file"]["max_size_mb"] * 1024 * 1024,
                backupCount=cfg["file"]["backup_count"],
                encoding="utf-8",
            )
            ds = DesensitizeFormatter(
                fmt=cfg["format"]["file"],
                datefmt=df,
                enable=cfg["enable_desensitization"],
            )
            fh.setFormatter(ds)
            fh.setLevel(getattr(logging, level_name, logging.DEBUG))
            root.addHandler(fh)
        except Exception:
            pass
    

    def get_logger(self, name=__name__):
        """获取指定名称的日志器"""
        if name not in self._loggers:
            self._loggers[name] = logging.getLogger(name)
        return self._loggers[name]


log_manager = LogManager()


def get_logger(name=__name__):
    """Shorthand: get a named logger from global LogManager"""
    return log_manager.get_logger(name)
