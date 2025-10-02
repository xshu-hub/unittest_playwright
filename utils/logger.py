"""
模块化日志系统

功能特性：
- 统一格式：时间戳、级别、模块名、消息
- 多级别日志：DEBUG/INFO/WARNING/ERROR，可按级别分类存储
- 文件轮转：按大小或按时间，支持保留历史与自动清理
- 简洁接口：setup_logging() 与 get_logger(name)

使用方法：
1) 在项目启动或首次导入处调用 setup_logging()（幂等）
2) 在模块中：
   from utils.logger import get_logger
   logger = get_logger(__name__)
   logger.info("消息")
"""

import logging
import os
from pathlib import Path
from typing import Optional, Dict, Any

import yaml
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler


_LOGGING_CONFIGURED = False


class _LevelFilter(logging.Filter):
    """只允许某个固定级别的日志通过的过滤器"""

    def __init__(self, level: int):
        super().__init__()
        self.level = level

    def filter(self, record: logging.LogRecord) -> bool:  # type: ignore[override]
        return record.levelno == self.level


def _load_logging_config(config_path: Optional[str] = None) -> Dict[str, Any]:
    """从项目根目录下的 config.yaml 加载日志配置，若不存在则使用默认配置"""
    if config_path is None:
        project_root = Path(__file__).parent.parent
        config_path = str(project_root / "config.yaml")

    defaults: Dict[str, Any] = {
        "logging": {
            "level": "INFO",
            "directory": "logs",
            "console": {"enabled": True, "level": "INFO"},
            "rotation": {
                "type": "size",  # size | time
                "max_bytes": 5_000_000,
                "backup_count": 7,
                "when": "D",
                "interval": 1,
                "encoding": "utf-8",
            },
            "format": {
                "fmt": "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S",
            },
            "per_level_files": True,
        }
    }

    try:
        if os.path.exists(config_path):
            with open(config_path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f) or {}
        else:
            data = {}
    except Exception as e:
        print(f"加载日志配置失败: {str(e)}")
        data = {}

    # 合并默认配置
    cfg = defaults
    user = data.get("logging") or {}
    cfg["logging"].update(user)
    return cfg["logging"]


def setup_logging(config_path: Optional[str] = None) -> None:
    """初始化项目日志系统（幂等）"""
    global _LOGGING_CONFIGURED
    if _LOGGING_CONFIGURED:
        return

    log_cfg = _load_logging_config(config_path)

    # 解析级别
    level_name = str(log_cfg.get("level", "INFO")).upper()
    level = getattr(logging, level_name, logging.INFO)

    fmt = log_cfg.get("format", {}).get("fmt",
                   "%(asctime)s [%(levelname)s] %(name)s: %(message)s")
    datefmt = log_cfg.get("format", {}).get("datefmt", "%Y-%m-%d %H:%M:%S")
    formatter = logging.Formatter(fmt=fmt, datefmt=datefmt)

    # 基础 root 配置
    logging.captureWarnings(True)
    root_logger = logging.getLogger()
    root_logger.setLevel(level)

    # 日志目录
    log_dir = Path(log_cfg.get("directory", "logs"))
    log_dir.mkdir(parents=True, exist_ok=True)

    rotation = log_cfg.get("rotation", {})
    rotation_type = rotation.get("type", "size")
    encoding = rotation.get("encoding", "utf-8")
    backup_count = int(rotation.get("backup_count", 7))

    # 创建文件 handler 工厂
    def file_handler(path: Path) -> logging.Handler:
        if rotation_type == "time":
            when = rotation.get("when", "D")
            interval = int(rotation.get("interval", 1))
            h = TimedRotatingFileHandler(
                filename=str(path), when=when, interval=interval,
                backupCount=backup_count, encoding=encoding
            )
        else:
            max_bytes = int(rotation.get("max_bytes", 5_000_000))
            h = RotatingFileHandler(
                filename=str(path), maxBytes=max_bytes,
                backupCount=backup_count, encoding=encoding
            )
        h.setFormatter(formatter)
        return h

    # Console handler
    console_cfg = log_cfg.get("console", {})
    if console_cfg.get("enabled", True):
        console_level_name = str(console_cfg.get("level", level_name)).upper()
        console_level = getattr(logging, console_level_name, level)
        ch = logging.StreamHandler()
        ch.setLevel(console_level)
        ch.setFormatter(formatter)
        root_logger.addHandler(ch)

    # 文件按级别分类
    per_level_files = bool(log_cfg.get("per_level_files", True))
    if per_level_files:
        for lvl_name in ("DEBUG", "INFO", "WARNING", "ERROR"):
            lvl = getattr(logging, lvl_name)
            handler = file_handler(log_dir / f"{lvl_name.lower()}.log")
            handler.setLevel(logging.DEBUG)  # 让过滤器控制实际级别
            handler.addFilter(_LevelFilter(lvl))
            root_logger.addHandler(handler)
    else:
        # 单文件（包含所有级别）
        handler = file_handler(log_dir / "app.log")
        handler.setLevel(level)
        root_logger.addHandler(handler)

    _LOGGING_CONFIGURED = True


def get_logger(name: Optional[str] = None) -> logging.Logger:
    """获取模块/类专用 logger；确保已初始化配置"""
    setup_logging()
    return logging.getLogger(name or "unittest_playwright")