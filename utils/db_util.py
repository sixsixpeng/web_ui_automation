# -*- coding: utf-8 -*-
"""
db_util - 数据库操作工具
功能：MySQL 连接池封装、SQL 执行、数据备份还原
"""

from typing import List

from utils.config_util import get as cfg_get
from utils.log_util import get_logger

logger = get_logger("db_util")


class DbUtil:
    """数据库操作工具（单例）"""

    _instance = None

    def __new__(cls):
        """Singleton pattern for DbUtil"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        """Init DB util"""
        if self._initialized:
            return
        self._initialized = True
        self._connection = None
        self._config = self._load_config()

    @staticmethod
    def _load_config() -> dict:
        """Load database config from config.yaml"""
        return {
            "host": cfg_get("database.host", "localhost"),
            "port": int(cfg_get("database.port", 3306)),
            "user": cfg_get("database.user", "root"),
            "password": cfg_get("database.password", "root"),
            "database": cfg_get("database.name", "test_db"),
        }

    def _get_connection(self):
        """获取数据库连接（惰性连接）"""
        if self._connection is None or not self._connection.open:
            try:
                import pymysql
                self._connection = pymysql.connect(
                    host=self._config["host"],
                    port=self._config["port"],
                    user=self._config["user"],
                    password=self._config["password"],
                    database=self._config["database"],
                    charset="utf8mb4",
                    cursorclass=pymysql.cursors.DictCursor,
                )
                logger.info(f"数据库连接成功: {self._config['host']}:{self._config['port']}/{self._config['database']}")
            except ImportError:
                logger.error("pymysql 未安装，请执行: pip install pymysql")
                raise
            except Exception as e:
                logger.error(f"数据库连接失败: {e}")
                raise
        return self._connection

    def execute_query(self, sql: str, params: tuple = None) -> List[dict]:
        """执行查询 SQL"""
        conn = self._get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute(sql, params)
                result = cursor.fetchall()
            logger.debug(f"SQL 查询: {self._desensitize_sql(sql)}, 返回 {len(result)} 行")
            return result
        except Exception as e:
            logger.error(f"SQL 执行失败: {e}, SQL: {sql}")
            raise

    def execute(self, sql: str, params: tuple = None) -> int:
        """执行增删改 SQL"""
        conn = self._get_connection()
        try:
            with conn.cursor() as cursor:
                affected = cursor.execute(sql, params)
            conn.commit()
            logger.debug(f"SQL 执行: {self._desensitize_sql(sql)}, 影响 {affected} 行")
            return affected
        except Exception as e:
            conn.rollback()
            logger.error(f"SQL 执行失败: {e}, SQL: {sql}")
            raise

    def execute_many(self, sql: str, params_list: List[tuple]) -> int:
        """批量执行 SQL"""
        conn = self._get_connection()
        try:
            with conn.cursor() as cursor:
                affected = cursor.executemany(sql, params_list)
            conn.commit()
            logger.debug(f"批量 SQL 执行: {self._desensitize_sql(sql)}, 影响 {affected} 行")
            return affected
        except Exception as e:
            conn.rollback()
            logger.error(f"批量 SQL 执行失败: {e}")
            raise

    def insert(self, table: str, data: dict) -> int:
        """插入单条数据"""
        columns = ", ".join(data.keys())
        placeholders = ", ".join(["%s"] * len(data))
        sql = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"
        return self.execute(sql, tuple(data.values()))

    def update(self, table: str, data: dict, where: str, where_params: tuple = None) -> int:
        """更新数据"""
        set_clause = ", ".join([f"{k}=%s" for k in data.keys()])
        sql = f"UPDATE {table} SET {set_clause} WHERE {where}"
        params = tuple(data.values()) + (where_params or ())
        return self.execute(sql, params)

    def delete(self, table: str, where: str, params: tuple = None) -> int:
        """删除数据"""
        sql = f"DELETE FROM {table} WHERE {where}"
        return self.execute(sql, params)

    @staticmethod
    def _desensitize_sql(sql: str) -> str:
        """SQL 脱敏（隐藏敏感值）"""
        import re
        return re.sub(r"'[^']*'", "'***'", sql)

    def close(self):
        """关闭数据库连接"""
        if self._connection and self._connection.open:
            self._connection.close()
            logger.info("数据库连接已关闭")

    def backup_table(self, table: str, where: str = "1=1") -> List[dict]:
        """备份表数据（用于测试后恢复）"""
        return self.execute_query(f"SELECT * FROM {table} WHERE {where}")

    def restore_from_backup(self, table: str, backup_data: List[dict]):
        """从备份恢复表数据"""
        if not backup_data:
            return
        self.execute(f"DELETE FROM {table} WHERE 1=1")
        for row in backup_data:
            self.insert(table, row)
        logger.info(f"表 {table} 已从备份恢复，共 {len(backup_data)} 条")


# 全局单例
db_util = DbUtil()
