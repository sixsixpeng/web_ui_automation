# -*- coding: utf-8 -*-
"""config_util - Unified config reader (yaml + env override)"""
import os

import allure

from utils.path_util import path_util
from utils.yaml_json_util import yaml_json_util

_CONFIG = None


def _load():
    global _CONFIG
    if _CONFIG is None:
        _CONFIG = yaml_json_util.load_yaml(
            str(path_util.config_dir / "config.yaml")
        )
    return _CONFIG


@allure.step("配置-读取")
def get(key: str, default=None):
    """
    Get config value by dot-separated key.
    Falls back to environment variable UPPER_CASE.
    Example: get("run.mode") -> config["run"]["mode"] or os.environ["RUN_MODE"]
    """
    cfg = _load()
    keys = key.split(".")
    val = cfg
    try:
        for k in keys:
            val = val[k]
        return val
    except (KeyError, TypeError):
        env_key = key.upper().replace(".", "_")
        return os.environ.get(env_key, default)


def get_env():
    """Get current environment name (dev/test/pre/prod)"""
    env = os.environ.get("ENV") or get("run.env", "test")
    return env


def get_env_config():
    """Get current environment-specific config"""
    env = get_env()
    return get(f"environments.{env}", {})


# Quick access
config = _load
