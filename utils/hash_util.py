# -*- coding: utf-8 -*-
"""hash_util - 哈希与编码工具（MD5/SHA/Base64/HMAC）"""
import base64
import hashlib
import hmac
import os


class HashUtil:

    # ===== MD5 ===== 
    @staticmethod
    def md5(text: str) -> str:
        """字符串 MD5（32位小写）"""
        return hashlib.md5(text.encode("utf-8")).hexdigest()

    @staticmethod
    def md5_file(path: str) -> str:
        """文件 MD5（大文件分块读取）"""
        h = hashlib.md5()
        with open(path, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                h.update(chunk)
        return h.hexdigest()

    @staticmethod
    def md5_upper(text: str) -> str:
        """字符串 MD5（32位大写）"""
        return hashlib.md5(text.encode("utf-8")).hexdigest().upper()

    @staticmethod
    def md5_salt(text: str, salt: str = "") -> str:
        """加盐 MD5"""
        return hashlib.md5((text + salt).encode("utf-8")).hexdigest()

    # ===== SHA ===== 
    @staticmethod
    def sha1(text: str) -> str:
        """计算 SHA1 哈希值"""
        """SHA1 hash of text"""
        return hashlib.sha1(text.encode("utf-8")).hexdigest()

    @staticmethod
    def sha256(text: str) -> str:
        """计算 SHA256 哈希值"""
        """SHA256 hash of text"""
        return hashlib.sha256(text.encode("utf-8")).hexdigest()

    @staticmethod
    def sha512(text: str) -> str:
        """计算 SHA512 哈希值"""
        """SHA512 hash of text"""
        return hashlib.sha512(text.encode("utf-8")).hexdigest()

    @staticmethod
    def sha256_file(path: str) -> str:
        """计算文件的 SHA256 哈希值"""
        """SHA256 hash of file (chunked read)"""
        h = hashlib.sha256()
        with open(path, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                h.update(chunk)
        return h.hexdigest()

    # ===== HMAC ===== 
    @staticmethod
    def hmac_md5(key: str, text: str) -> str:
        """计算 HMAC-MD5 签名"""
        """HMAC-MD5 signature"""
        return hmac.new(key.encode(), text.encode(), hashlib.md5).hexdigest()

    @staticmethod
    def hmac_sha256(key: str, text: str) -> str:
        """计算 HMAC-SHA256 签名"""
        """HMAC-SHA256 signature"""
        return hmac.new(key.encode(), text.encode(), hashlib.sha256).hexdigest()

    # ===== Base64 ===== 
    @staticmethod
    def b64_encode(text: str) -> str:
        """Base64 编码"""
        return base64.b64encode(text.encode("utf-8")).decode()

    @staticmethod
    def b64_decode(text: str) -> str:
        """Base64 解码"""
        return base64.b64decode(text).decode("utf-8")

    @staticmethod
    def b64url_encode(text: str) -> str:
        """URL 安全的 Base64 编码（替换 +/ 为 -_）"""
        return base64.urlsafe_b64encode(text.encode("utf-8")).decode()

    @staticmethod
    def b64url_decode(text: str) -> str:
        """URL 安全 Base64 解码"""
        """URL-safe Base64 decode"""
        return base64.urlsafe_b64decode(text).decode("utf-8")

    # ===== 快捷 ===== 
    @staticmethod
    def random_hash() -> str:
        """随机 SHA256（用于临时标识）"""
        return hashlib.sha256(os.urandom(32)).hexdigest()


hash_util = HashUtil()
