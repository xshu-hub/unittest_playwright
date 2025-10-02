"""
视频录制配置管理类
负责读取与校验顶层 videos 配置段，并提供便捷访问方法。
"""
from __future__ import annotations

from typing import Dict, Any, Optional
from utils.logger import get_logger
from utils.common import load_yaml_with_default, default_config_path

logger = get_logger(__name__)


class VideosConfig:
    """视频录制配置管理类"""

    VALID_MODES = {"all", "failed_only", "disabled"}

    def __init__(self, config_file: Optional[str] = None) -> None:
        self._config_data: Dict[str, Any] = {}
        self._config_file = config_file or self._get_default_config_file()
        self._load_config()

    @staticmethod
    def _get_default_config_file() -> str:
        return default_config_path()

    def _load_config(self) -> None:
        self._config_data = load_yaml_with_default(
            self._config_file,
            self._get_default_config,
            logger,
            "Videos",
        )

    @staticmethod
    def _get_default_config() -> Dict[str, Any]:
        return {
            "videos": {
                "mode": "disabled",
                "directory": "videos",
                "size": {"width": 1280, "height": 720},
            }
        }

    def get(self, key: str, default: Any = None) -> Any:
        try:
            keys = key.split(".")
            value: Any = self._config_data
            for k in keys:
                if isinstance(value, dict) and k in value:
                    value = value[k]
                else:
                    return default
            return value
        except Exception as e:
            logger.error(f"获取 Videos 配置值失败: {key}, 错误: {str(e)}")
            return default

    # 访问器
    def mode(self) -> str:
        m = str(self.get("videos.mode", "disabled")).lower()
        if m not in self.VALID_MODES:
            logger.warning(f"非法视频模式: {m}，回退为 disabled")
            return "disabled"
        return m

    def enabled(self) -> bool:
        return self.mode() != "disabled"

    def record_all(self) -> bool:
        return self.mode() == "all"

    def record_failed_only(self) -> bool:
        return self.mode() == "failed_only"

    def directory(self) -> str:
        return str(self.get("videos.directory", "videos"))

    def size(self) -> Dict[str, int]:
        size = self.get("videos.size", {"width": 1280, "height": 720})
        try:
            w = int(size.get("width", 1280))
            h = int(size.get("height", 720))
            return {"width": max(1, w), "height": max(1, h)}
        except Exception as e:
            logger.warning(f"视频分辨率配置不合法，使用默认 1280x720, 错误: {str(e)}")
            return {"width": 1280, "height": 720}


videos_config = VideosConfig()