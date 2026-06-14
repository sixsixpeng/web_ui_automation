# -*- coding: utf-8 -*-
"""
mail_util - 邮件消息推送工具（框架唯一通知渠道）
功能：SMTP 发送汇总邮件、自动统计、附件挂载
"""

import smtplib
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path
from typing import List

from utils.config_util import get as cfg_get
from utils.log_util import get_logger
from utils.time_util import time_util

logger = get_logger("mail_util")


class MailSender:
    """邮件发送器（单例）"""

    _instance = None

    def __new__(cls):
        """Singleton pattern for MailSender"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        """Init MailSender"""
        if self._initialized:
            return
        self._initialized = True
        self._results = []  # 存储用例执行结果
        self._config = self._load_config()
        logger.info("MailSender 初始化完成")

    @staticmethod
    def _load_config() -> dict:
        """Load mail config from config.yaml"""
        return {
            "server": cfg_get("mail.smtp.server", "smtp.example.com"),
            "port": int(cfg_get("mail.smtp.port", 465)),
            "use_ssl": str(cfg_get("mail.smtp.use_ssl", "true")).lower() == "true",
            "user": cfg_get("mail.smtp.user", ""),
            "password": cfg_get("mail.smtp.password", ""),
            "to": cfg_get("mail.smtp.to", ""),
            "cc": cfg_get("mail.smtp.cc", ""),
            "prefix": cfg_get("mail.smtp.prefix", "[Web Automation]"),
        }

    def add_result(self, node_id: str, status: str, duration: float, error: str = ""):
        """添加用例执行结果到缓存"""
        self._results.append({
            "node_id": node_id,
            "status": status,
            "duration": duration,
            "error": error,
        })

    def clear_results(self):
        """清空结果缓存"""
        self._results.clear()

    def send_report(self, extra_attachments: List[str] = None) -> bool:
        """发送测试汇总报告邮件"""
        config = self._config
        if not config["user"] or config["user"] == "your_email@example.com":
            logger.warning("Mail not configured, skip sending")
            return False

        if not self._results:
            logger.warning("无测试结果，跳过发送")
            return False

        try:
            # 统计
            total = len(self._results)
            passed = sum(1 for r in self._results if r["status"] == "passed")
            failed = sum(1 for r in self._results if r["status"] == "failed")
            skipped = sum(1 for r in self._results if r["status"] == "skipped")
            total_duration = sum(r["duration"] for r in self._results)

            # 构建邮件
            msg = MIMEMultipart("mixed")
            env = cfg_get("run.env", "unknown")
            msg["Subject"] = f'{config["prefix"]} {env.upper()} 环境测试报告 - {time_util.now_datetime_str()}'
            msg["From"] = config["user"]
            msg["To"] = config["to"]
            if config["cc"]:
                msg["Cc"] = config["cc"]

            # HTML 正文
            html_body = self._build_html_body(total, passed, failed, skipped, total_duration)
            msg.attach(MIMEText(html_body, "html", "utf-8"))

            # 附加附件
            if extra_attachments:
                for file_path in extra_attachments:
                    self._attach_file(msg, file_path)

            # 发送
            recipients = [r.strip() for r in config["to"].split(",") if r.strip()]
            if config["cc"]:
                recipients += [r.strip() for r in config["cc"].split(",") if r.strip()]

            if config["use_ssl"]:
                with smtplib.SMTP_SSL(config["server"], config["port"], timeout=30) as server:
                    server.login(config["user"], config["password"])
                    server.sendmail(config["user"], recipients, msg.as_string())
            else:
                with smtplib.SMTP(config["server"], config["port"], timeout=30) as server:
                    server.starttls()
                    server.login(config["user"], config["password"])
                    server.sendmail(config["user"], recipients, msg.as_string())

            logger.info(f"测试报告邮件已发送至 {config['to']}")
            return True

        except Exception as e:
            logger.error(f"邮件发送失败: {e}")
            return False

    def _build_html_body(self, total, passed, failed, skipped, duration) -> str:
        """构建 HTML 邮件正文"""
        pass_rate = round(passed / total * 100, 2) if total > 0 else 0
        failed_items = ""
        for r in self._results:
            if r["status"] == "failed":
                failed_items += f"<tr><td>{r['node_id']}</td><td>{r['error'][:200]}</td><td>{r['duration']:.2f}s</td></tr>"

        return f"""
        <html>
        <head><meta charset="utf-8"></head>
        <body style="font-family: Arial, sans-serif;">
            <h2>Web UI Automation Test Report</h2>
            <table border="1" cellpadding="8" cellspacing="0" style="border-collapse:collapse; margin-bottom:20px;">
                <tr style="background:#4472C4; color:white;"><th>指标</th><th>数值</th></tr>
                <tr><td>环境</td><td>{cfg_get("run.env", "unknown")}</td></tr>
                <tr><td>总用例</td><td>{total}</td></tr>
                <tr><td>通过</td><td style="color:green;">{passed}</td></tr>
                <tr><td>失败</td><td style="color:red;">{failed}</td></tr>
                <tr><td>跳过</td><td style="color:orange;">{skipped}</td></tr>
                <tr><td>通过率</td><td>{pass_rate}%</td></tr>
                <tr><td>总耗时</td><td>{duration:.2f}s</td></tr>
            </table>
            <h3>失败用例清单</h3>
            <table border="1" cellpadding="6" cellspacing="0" style="border-collapse:collapse;">
                <tr style="background:#D9534F; color:white;"><th>用例路径</th><th>错误摘要</th><th>耗时</th></tr>
                {failed_items or "<tr><td colspan='3' style='color:green;'>✅ 无失败用例</td></tr>"}
            </table>
            <p style="color:#888; font-size:12px; margin-top:30px;">
                此邮件由 Web UI Automation Framework 自动发送
            </p>
        </body>
        </html>
        """

    @staticmethod
    def _attach_file(msg: MIMEMultipart, file_path: str):
        """添加附件"""
        path = Path(file_path)
        if not path.exists():
            logger.warning(f"附件不存在: {file_path}")
            return

        with open(file_path, "rb") as f:
            part = MIMEBase("application", "octet-stream")
            part.set_payload(f.read())
            encoders.encode_base64(part)
            part.add_header("Content-Disposition", f'attachment; filename="{path.name}"')
            msg.attach(part)


# 全局单例
mail_sender = MailSender()
