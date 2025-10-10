"""
截图配置管理类
"""
from typing import Dict, Any, Optional, List
from utils.cmbird_logger import logger
from utils.common import load_yaml_with_default, default_config_path

# 使用 cmbird 日志代理（由 BaseTest 在运行时注册）


class ScreenshotsConfig:
    """截图配置管理类"""

    def __init__(self, config_file: Optional[str] = None):
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
            "Screenshots",
        )

    @staticmethod
    def _get_default_config() -> Dict[str, Any]:
        return {
            "screenshots": {
                "enabled": True,
                "directory": "screenshots",
                "full_page": True,
                "type": "png",
                "mask_selectors": []
            }
        }

    def get(self, key: str, default: Any = None) -> Any:
        try:
            keys = key.split('.')
            value: Any = self._config_data
            for k in keys:
                if isinstance(value, dict) and k in value:
                    value = value[k]
                else:
                    return default
            return value
        except Exception as e:
            logger.error(f"获取 Screenshots 配置值失败: {key}, 错误: {str(e)}")
            return default

    # 截图配置访问方法
    def get_screenshot_config(self) -> Dict[str, Any]:
        return self.get("screenshots", {})

    def screenshots_enabled(self) -> bool:
        return bool(self.get("screenshots.enabled", True))

    def screenshots_directory(self) -> str:
        return str(self.get("screenshots.directory", "screenshots"))

    def screenshots_full_page(self) -> bool:
        return bool(self.get("screenshots.full_page", True))

    def screenshots_type(self) -> str:
        t = str(self.get("screenshots.type", "png")).lower()
        return t if t in {"png", "jpeg"} else "png"

    def screenshots_mask_selectors(self) -> List[str]:
        v = self.get("screenshots.mask_selectors", [])
        return v if isinstance(v, list) else []


screenshots_config = ScreenshotsConfig()