# -*- coding: utf-8 -*-
"""
crypto_util - AES 加密解密 & 日志脱敏工具
功能：AES-CBC+PKCS7 对称加密处理账号密码等敏感凭证
"""

import base64

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

from utils.log_util import get_logger
from utils.path_util import path_util

logger = get_logger("crypto_util")


class CryptoUtil:
    """AES 加密解密工具（单例）"""

    _instance = None

    def __new__(cls):
        """Singleton pattern for CryptoUtil"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        """Init crypto util, load AES key"""
        if self._initialized:
            return
        self._initialized = True
        self._key = self._load_key()
        self._iv = self._key[:16]  # 取密钥前16字节作为 IV
        logger.info("CryptoUtil 初始化完成")

    def _load_key(self) -> bytes:
        """从密钥文件加载 AES 密钥"""
        key_path = str(path_util.config_dir / "secret.key")
        try:
            with open(key_path, "r", encoding="utf-8") as f:
                key_text = f.read().strip()
            # 密钥必须为 32 字节（AES-256）
            key = key_text.encode("utf-8").ljust(32, b"\0")[:32]
            logger.debug("密钥文件加载成功")
            return key
        except FileNotFoundError:
            logger.error(f"密钥文件未找到: {key_path}")
            raise
        except Exception as e:
            logger.error(f"密钥加载失败: {e}")
            raise

    def encrypt_text(self, plain_text: str) -> str:
        """加密明文，返回 Base64 编码的密文"""
        try:
            # PKCS7 填充
            padder = padding.PKCS7(128).padder()
            padded_data = padder.update(plain_text.encode("utf-8")) + padder.finalize()

            # AES-CBC 加密
            cipher = Cipher(algorithms.AES(self._key), modes.CBC(self._iv), backend=default_backend())
            encryptor = cipher.encryptor()
            cipher_text = encryptor.update(padded_data) + encryptor.finalize()

            # Base64 编码
            return base64.b64encode(cipher_text).decode("utf-8")
        except Exception as e:
            logger.error(f"加密失败: {e}")
            raise

    def decrypt_text(self, cipher_text: str) -> str:
        """解密 Base64 编码的密文，返回明文"""
        try:
            # Base64 解码
            cipher_data = base64.b64decode(cipher_text)

            # AES-CBC 解密
            cipher = Cipher(algorithms.AES(self._key), modes.CBC(self._iv), backend=default_backend())
            decryptor = cipher.decryptor()
            padded_data = decryptor.update(cipher_data) + decryptor.finalize()

            # 去除 PKCS7 填充
            unpadder = padding.PKCS7(128).unpadder()
            plain_data = unpadder.update(padded_data) + unpadder.finalize()

            return plain_data.decode("utf-8")
        except Exception as e:
            logger.error(f"解密失败: {e}")
            raise

    def decrypt_yaml_file(self, file_path: str) -> dict:
        """解密 YAML 账户文件中的所有加密字段"""
        import yaml
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)
            return self._decrypt_dict(data)
        except Exception as e:
            logger.error(f"解密 YAML 文件失败: {e}")
            raise

    def _decrypt_dict(self, data) -> dict:
        """递归解密字典中的加密字段（以 _encrypted 结尾的字段）"""
        if isinstance(data, dict):
            return {k: self._decrypt_dict(v) for k, v in data.items()}
        elif isinstance(data, list):
            return [self._decrypt_dict(item) for item in data]
        elif isinstance(data, str) and len(data) > 20:
            try:
                return self.decrypt_text(data)
            except Exception:
                return data
        return data

    def encrypt_dict_values(self, data: dict, keys_to_encrypt: list) -> dict:
        """加密字典中指定 key 的值"""
        result = data.copy()
        for key in keys_to_encrypt:
            if key in result and result[key]:
                result[key] = self.encrypt_text(str(result[key]))
        return result


# 全局单例
crypto_util = CryptoUtil()
