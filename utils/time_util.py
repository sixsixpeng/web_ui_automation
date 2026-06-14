# -*- coding: utf-8 -*-
"""
time_util - 时间日期工具
功能：时间戳转换、日期偏移、耗时计算、时区校正、格式化输出
"""

import datetime
import time


class TimeUtil:
    """时间日期工具类（全局单例）"""

    DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
    DATE_FORMAT = "%Y-%m-%d"
    TIME_FORMAT = "%H:%M:%S"
    COMPACT_FORMAT = "%Y%m%d_%H%M%S"
    COMPACT_DATE = "%Y%m%d"
    FILE_PREFIX = "%Y%m%d_%H%M%S"

    @staticmethod
    def now():
        """获取当前 datetime 对象"""
        """Get current datetime object"""
        return datetime.datetime.now()

    @staticmethod
    def timestamp() -> float:
        """获取当前时间戳（秒）"""
        return time.time()

    @staticmethod
    def timestamp_ms() -> int:
        """获取当前时间戳（毫秒）"""
        return int(time.time() * 1000)

    @staticmethod
    def format(ts=None, fmt=DATETIME_FORMAT) -> str:
        """格式化时间戳为字符串，ts=None表示当前时间"""
        if ts is None:
            return datetime.datetime.now().strftime(fmt)
        return datetime.datetime.fromtimestamp(ts).strftime(fmt)

    @staticmethod
    def datetime_str(fmt=DATETIME_FORMAT) -> str:
        """获取当前日期时间字符串"""
        return datetime.datetime.now().strftime(fmt)

    @staticmethod
    def date_str() -> str:
        """获取当前日期字符串"""
        """Get current date as YYYY-MM-DD"""
        return datetime.datetime.now().strftime(TimeUtil.DATE_FORMAT)

    @staticmethod
    def time_str() -> str:
        """获取当前时间字符串"""
        """Get current time as HH:MM:SS"""
        return datetime.datetime.now().strftime(TimeUtil.TIME_FORMAT)

    @staticmethod
    def filename_prefix() -> str:
        """文件名时间前缀: YYYYMMDD_HHMMSS_"""
        return datetime.datetime.now().strftime(TimeUtil.FILE_PREFIX) + chr(95)

    @staticmethod
    def compact() -> str:
        """获取紧凑格式时间戳"""
        """Get compact timestamp YYYYMMDD_HHMMSS"""
        return datetime.datetime.now().strftime(TimeUtil.COMPACT_FORMAT)

    @staticmethod
    def ts_to_str(ts, fmt=DATETIME_FORMAT) -> str:
        """时间戳转格式化字符串"""
        """Convert unix timestamp to formatted string"""
        return datetime.datetime.fromtimestamp(ts).strftime(fmt)

    @staticmethod
    def str_to_ts(date_str, fmt=DATETIME_FORMAT) -> float:
        """时间字符串转时间戳"""
        """Parse datetime string to unix timestamp"""
        return datetime.datetime.strptime(date_str, fmt).timestamp()

    @staticmethod
    def str_to_dt(date_str, fmt=DATETIME_FORMAT):
        """时间字符串转 datetime 对象"""
        """Parse datetime string to datetime object"""
        return datetime.datetime.strptime(date_str, fmt)

    @staticmethod
    def dt_to_str(dt, fmt=DATETIME_FORMAT) -> str:
        """datetime 对象转字符串"""
        """Convert datetime object to string"""
        return dt.strftime(fmt)

    @staticmethod
    def days_ago(days, fmt=DATE_FORMAT) -> str:
        """获取 N 天前的日期"""
        """Get date N days ago as string"""
        return (datetime.datetime.now() - datetime.timedelta(days=days)).strftime(fmt)

    @staticmethod
    def days_later(days, fmt=DATE_FORMAT) -> str:
        """获取 N 天后的日期"""
        """Get date N days later as string"""
        return (datetime.datetime.now() + datetime.timedelta(days=days)).strftime(fmt)

    @staticmethod
    def hours_later(hours, fmt=DATETIME_FORMAT) -> str:
        """获取 N 小时后的时间"""
        """Get datetime N hours later"""
        return (datetime.datetime.now() + datetime.timedelta(hours=hours)).strftime(fmt)

    @staticmethod
    def minutes_later(minutes, fmt=DATETIME_FORMAT) -> str:
        """获取 N 分钟后的时间"""
        """Get datetime N minutes later"""
        return (datetime.datetime.now() + datetime.timedelta(minutes=minutes)).strftime(fmt)

    @staticmethod
    def offset(days=0, hours=0, minutes=0, seconds=0, fmt=DATETIME_FORMAT) -> str:
        """获取偏移指定时长后的时间"""
        """Get datetime with offset (days/hours/minutes/seconds)"""
        delta = datetime.timedelta(days=days, hours=hours, minutes=minutes, seconds=seconds)
        return (datetime.datetime.now() + delta).strftime(fmt)

    @staticmethod
    def elapsed(start, end=None) -> float:
        """计算耗时（秒）"""
        if end is None:
            end = time.time()
        return round(end - start, 3)

    @staticmethod
    def elapsed_ms(start, end=None) -> int:
        """计算耗时（毫秒）"""
        if end is None:
            end = time.time()
        return int((end - start) * 1000)

    @staticmethod
    def elapsed_str(start, end=None) -> str:
        """耗时转为可读字符串（如 1.23s）"""
        s = TimeUtil.elapsed(start, end)
        if s < 60:
            return f"{s:.2f}s"
        return f'{int(s // 60)}m {s % 60:.1f}s'

    @staticmethod
    def sleep(seconds):
        """休眠指定秒数"""
        """Sleep for N seconds"""
        time.sleep(seconds)

    @staticmethod
    def sleep_ms(milliseconds):
        """休眠指定毫秒数"""
        """Sleep for N milliseconds"""
        time.sleep(milliseconds / 1000.0)

    @staticmethod
    def is_before(d1, d2, fmt=DATETIME_FORMAT) -> bool:
        """判断时间是否早于另一个时间"""
        """Check if first time string is before second"""
        return datetime.datetime.strptime(d1, fmt) < datetime.datetime.strptime(d2, fmt)

    @staticmethod
    def is_after(d1, d2, fmt=DATETIME_FORMAT) -> bool:
        """判断时间是否晚于另一个时间"""
        """Check if first time string is after second"""
        return datetime.datetime.strptime(d1, fmt) > datetime.datetime.strptime(d2, fmt)

    @staticmethod
    def time_diff(d1, d2, fmt=DATETIME_FORMAT) -> float:
        """计算两个时间字符串的差值（秒）"""
        dt1 = datetime.datetime.strptime(d1, fmt)
        dt2 = datetime.datetime.strptime(d2, fmt)
        return abs((dt2 - dt1).total_seconds())

    @staticmethod
    def human_readable(seconds) -> str:
        """秒数转为人类可读格式（2h 3m 5s）"""
        secs = int(seconds)
        h = secs // 3600
        m = (secs % 3600) // 60
        s = secs % 60
        parts = []
        if h: parts.append(f'{h}h')
        if m: parts.append(f'{m}m')
        parts.append(f'{s}s')
        return " ".join(parts)


time_util = TimeUtil()
