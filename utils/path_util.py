"""path_util - Cross-platform path manager (pathlib)"""
import os
from datetime import datetime
from pathlib import Path


class _PathUtil:
    _inst = None

    def __new__(cls):
        """Singleton: ensure only one instance"""
        if cls._inst is None:
            cls._inst = super().__new__(cls)
            cls._inst._root = cls._find()
        return cls._inst

    @staticmethod
    def _find():
        """Auto-locate project root by searching for .env/config markers"""
        env = os.environ.get("PROJECT_ROOT")
        if env: return Path(env).resolve()
        cur = Path(__file__).resolve().parent.parent
        for p in [cur] + list(cur.parents):
            if any((p / m).exists() for m in [".env", "config"]):
                return p
        return Path.cwd().resolve()

    @property
    def root(self):
        """获取项目根目录路径"""
        """Project root directory"""
        return self._root

    @property
    def config_dir(self):
        """获取配置目录路径"""
        """Configuration file directory"""
        return self._ensure(self._root / "config")

    @property
    def data_dir(self):
        """获取测试数据目录路径"""
        """Test data file directory"""
        return self._ensure(self._root / "data")

    @property
    def logs_dir(self):
        """获取日志输出目录路径"""
        """Log output directory (auto-created)"""
        return self._ensure(self._root / "logs")

    @property
    def reports_dir(self):
        """获取报告输出目录路径"""
        """Reports output directory (auto-created)"""
        return self._ensure(self._root / "reports")

    @property
    def screenshots_dir(self):
        """获取截图存储目录路径"""
        """Screenshot storage directory (auto-created). Uses RUN_TIMESTAMP env var or date."""
        ts = os.environ.get("RUN_TIMESTAMP")
        folder = ts if ts else datetime.now().strftime("%Y%m%d")
        return self._ensure(self._root / "screenshots" / folder)

    @property
    def tmp_dir(self):
        """获取临时文件目录路径（仅返回路径，不自动创建）"""
        return self._root / "tmp"

    @property
    def allure_raw_dir(self):
        """获取 Allure 原始数据目录路径"""
        """Allure raw result path (not auto-created)"""
        return self._root / "reports" / "allure" / "raw"

    @property
    def allure_static_dir(self):
        """获取 Allure 静态报告目录路径"""
        """Allure static report path (not auto-created)"""
        return self._root / "reports" / "allure" / "static"

    def _ensure(self, p):
        """Ensure directory exists, create if not"""
        p.mkdir(parents=True, exist_ok=True)
        return p

    def join(self, *parts):
        """拼接路径段，返回 Path 对象"""
        """Join path segments relative to root -> Path"""
        return self._root.joinpath(*parts)

    def join_str(self, *parts):
        """拼接路径段，返回字符串"""
        """Join path segments relative to root -> str"""
        return str(self._root.joinpath(*parts))

    @staticmethod
    def ext(p):
        """获取文件扩展名"""
        """Get lowercase file extension (e.g. .png)"""
        return Path(p).suffix.lower()

    @staticmethod
    def stem(p):
        """获取文件名（不含扩展名）"""
        """Get filename without extension"""
        return Path(p).stem

    @staticmethod
    def name(p):
        """获取完整文件名"""
        """Get full filename with extension"""
        return Path(p).name

    @staticmethod
    def size(p):
        """获取文件大小（字节）"""
        """Get file size in bytes (0 if not exists)"""
        return Path(p).stat().st_size if Path(p).exists() else 0

    @staticmethod
    def exists(p):
        """判断路径是否存在"""
        """Check if path exists on filesystem"""
        return Path(p).exists()

    @staticmethod
    def is_dir(p):
        """判断路径是否为目录"""
        """Check if path is a directory"""
        return Path(p).is_dir()

    @staticmethod
    def is_file(p):
        """判断路径是否为文件"""
        """Check if path is a file"""
        return Path(p).is_file()

    @staticmethod
    def ensure_dir(p):
        """确保目录存在不存在则创建"""
        """Ensure directory exists, create parents if needed"""
        Path(p).mkdir(parents=True, exist_ok=True)
        return Path(p)

    @staticmethod
    def ts_file(base, prefix="", ext=".png"):
        """生成带时间戳的文件路径"""
        """Generate timestamped filename: base/prefix_YYYYMMDD_HHMMSS.ext"""
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        fn = f"{prefix}_{ts}{ext}" if prefix else f"{ts}{ext}"
        p = Path(base) / fn
        p.parent.mkdir(parents=True, exist_ok=True)
        return p

    def find(self, name, base=None):
        """递归查找第一个匹配的文件"""
        """Recursively find first file by name, returns Path or None"""
        for p in (base or self._root).rglob(name): return p
        return None

    def find_all(self, pat, base=None):
        """递归查找所有匹配的文件"""
        """Recursively find all files matching pattern, returns sorted list"""
        return sorted((base or self._root).rglob(pat))


path_util = _PathUtil()
