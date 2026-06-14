# -*- coding: utf-8 -*-
"""
Web UI Automation Framework - 工具类统一入口
用法:
    from utils.path_util import path_util
from utils.time_util import time_util, assert_util
    from utils import data_util, faker_util, validate_util
    from utils.log_util import get_logger, uuid_util, hash_util
    from utils import ScreenshotSyncUtil, ApiClient
"""

# ========== 报告 & 附件 ==========
from utils.allure_attach_util import AllureAttachUtil as AllureAttachUtil  # Allure 附件挂载：文本/JSON/图片/文件/HTML
# ========== API 请求（接口 + UI 混合测试） ==========
from utils.api_util import ApiClient as ApiClient  # HTTP 客户端：GET/POST/PUT/DELETE/Session复用/Token自动刷新/Allure日志
from utils.assert_util import AssertUtil as AssertUtil  # 增强断言：URL/文本/元素状态/数值/列表断言/软断言模式
from utils.cache_util import cache_util  # 内存缓存：键值存储/过期时间/同步异步隔离/全局单例
from utils.captcha_util import CaptchaAsyncUtil  # 异步验证码：同上，async/await 版本
# ========== 验证码 ==========
from utils.captcha_util import CaptchaSyncUtil  # 同步验证码：万能验证码跳过/图片获取/第三方识别接口
from utils.config_util import get as _cfg
from utils.crypto_util import crypto_util  # AES 加解密：账号密码加密存储、批量解密 yaml、敏感信息脱敏
# ========== 数据 & 配置（数据处理） ==========
from utils.data_util import data_util  # 多格式数据读取：YAML/Excel/CSV 加载、参数化数据源、用户账号解密读取
# ========== 数据库 & 邮件 ==========
from utils.db_util import DbUtil, DbUtil as db_util  # 数据库操作：MySQL 连接池/增删改查/事务/SQL日志/数据备份恢复
from utils.faker_util import faker_util  # 随机测试数据生成：合规手机号/身份证/订单号、边界非法数据、批量生成
# ========== 文件 & 缓存 ==========
from utils.file_util import file_util  # 文件操作：目录创建清理/文件复制移动/zip压缩解压/临时文件管理
# ========== 编码 & 加密 ==========
from utils.hash_util import hash_util  # 哈希编码工具：MD5/SHA1/SHA256/SHA512/Base64/HMAC
# ========== 日志 & 断言 ==========
from utils.log_util import get_logger  # 获取日志器：统一日志格式/文件按日期切割/敏感信息自动脱敏
from utils.mail_util import MailSender
from utils.mail_util import mail_sender  # 邮件推送：SMTP发送测试报告/统计/附件/失败清单/多收件人
from utils.network_util import NetworkAsyncUtil  # 异步网络拦截：同上，async/await 版本
# ========== 网络拦截 & Mock ==========
from utils.network_util import NetworkSyncUtil  # 同步网络拦截：XHR/Fetch 捕获/Mock 接口/报文导出 JSON
# ========== 路径 & 时间 & 唯一ID（基础三件套） ==========
from utils.path_util import path_util  # 项目路径管理：root/config_dir/logs_dir/screenshots_dir 等所有关键路径
from utils.performance_util import PerformanceAsyncUtil  # 异步性能采集：同上，async/await 版本
# ========== 页面性能采集 ==========
from utils.performance_util import PerformanceSyncUtil  # 同步性能采集：FP/FCP/LCP/CLS/页面总加载耗时/阈值告警
from utils.popup_util import PopupAsyncUtil  # 异步弹窗处理：同上，async/await 版本
# ========== 弹窗自动处理 ==========
from utils.popup_util import PopupSyncUtil  # 同步弹窗处理：alert/confirm/prompt 捕获、广告浮窗自动关闭
# ========== 重试容错装饰器 ==========
from utils.screenshot_util import ScreenshotAsyncUtil  # 异步截图：同上，async/await 版本
# ========== 截图（同步 + 异步，含 URL 水印） ==========
from utils.screenshot_util import ScreenshotSyncUtil  # 同步截图：窗口截图/整页长截图/元素截图/Pillow 地址栏水印
from utils.storage_util import StorageAsyncUtil  # 异步浏览器存储：同上，async/await 版本
# ========== 浏览器存储 ==========
from utils.storage_util import StorageSyncUtil  # 同步浏览器存储：Cookie/LocalStorage/SessionStorage 增删改查
from utils.time_util import time_util  # 时间日期工具：时间戳/格式化/偏移/耗时计算/文件名时间前缀
from utils.uuid_util import uuid_util  # 唯一ID生成：uuid4/hex/short/order_no/ts_uuid/批量生成
from utils.validate_util import validate_util  # 数据格式校验：is_phone/is_email/is_id_card/is_url/is_money
from utils.yaml_json_util import yaml_json_util  # YAML/JSON 解析转换：文件加载、深层字段提取、JSON差异比对、配置合并

# ====== 导出列表 ======
__all__ = [
    # 路径 & 时间 & 唯一ID
    "path_util", "time_util", "uuid_util",
    # 数据 & 配置
    "data_util", "yaml_json_util", "faker_util", "validate_util",
    # 编码 & 加密
    "hash_util", "crypto_util",
    # 文件 & 缓存
    "file_util", "cache_util",
    # 日志 & 断言
    "get_logger", "AssertUtil",
    # 报告
    "AllureAttachUtil",
    # API
    "ApiClient",
    # 数据库 & 邮件
    "DbUtil", "MailSender",
    # 截图
    "ScreenshotSyncUtil", "ScreenshotAsyncUtil",
    # 网络
    "NetworkSyncUtil", "NetworkAsyncUtil",
    # 弹窗
    "PopupSyncUtil", "PopupAsyncUtil",
    # 存储
    "StorageSyncUtil", "StorageAsyncUtil",
    # 性能
    "PerformanceSyncUtil", "PerformanceAsyncUtil",
    # 验证码
    "CaptchaSyncUtil", "CaptchaAsyncUtil",
    # 重试
]
