"""
Allure 配置管理类
负责读取与校验顶层 allure 配置段，并提供便捷访问方法。
"""
from __future__ import annotations

from typing import Dict, Any, Optional
from utils.logger import get_logger
from utils.common import load_yaml_with_default, default_config_path

logger = get_logger(__name__)


class AllureConfig:
    """Allure 配置管理类"""

    def __init__(self, config_file: Optional[str] = None):
        self._config_data: Dict[str, Any] = {}
        self._config_file = config_file or self._get_default_config_file()
        self._load_config()

    @staticmethod
    def _get_default_config_file() -> str:
        return default_config_path()

    @staticmethod
    def _get_default_allure() -> Dict[str, Any]:
        return {
            "results_dir": "allure-results",
            "report_dir": "allure-report",
            "labels": {
                "derive_parent_suite": "top_level_subpackage",
                "package_strategy": "top_level",
                "enable_subsuite": False,
            },
            "attachments": {
                "screenshot_on_failure": True,
                "video_on_failure": True,
            },
            "environment": {
                "extra": {},
            },
            "categories_file": None,
            "executor": None,
        }

    @staticmethod
    def _get_default_config() -> Dict[str, Any]:
        # 顶层默认返回包含 allure 段的对象
        return {"allure": AllureConfig._get_default_allure()}

    def _load_config(self) -> None:
        # 加载顶层配置（包含 allure 段），若不存在则使用默认
        self._config_data = load_yaml_with_default(
            self._config_file,
            self._get_default_config,
            logger,
            "Allure",
        )

    @staticmethod
    def _deep_merge(base: Dict[str, Any], ext: Dict[str, Any]) -> Dict[str, Any]:
        out = dict(base)
        for k, v in (ext or {}).items():
            if isinstance(v, dict) and isinstance(out.get(k), dict):
                out[k] = AllureConfig._deep_merge(out[k], v)
            else:
                out[k] = v
        return out

    def get_allure_config(self) -> Dict[str, Any]:
        defaults = self._get_default_allure()
        user = self._config_data.get("allure") or {}
        return self._deep_merge(defaults, user)

    # 便捷访问方法
    def get_results_dir(self) -> str:
        return str(self.get_allure_config().get("results_dir", "allure-results"))

    def get_report_dir(self) -> str:
        return str(self.get_allure_config().get("report_dir", "allure-report"))

    def get_labels(self) -> Dict[str, Any]:
        return dict(self.get_allure_config().get("labels", {}))

    def get_attachments(self) -> Dict[str, Any]:
        return dict(self.get_allure_config().get("attachments", {}))

    def get_environment_extra(self) -> Dict[str, Any]:
        env = self.get_allure_config().get("environment", {}) or {}
        return dict(env.get("extra", {}))

    def get_categories_file(self) -> Optional[str]:
        val = self.get_allure_config().get("categories_file")
        return str(val) if val else None

    def get_executor(self) -> Optional[Dict[str, Any]]:
        exec_ = self.get_allure_config().get("executor")
        return dict(exec_) if isinstance(exec_, dict) else None

    def get_all(self) -> Dict[str, Any]:
        return self.get_allure_config().copy()


# 全局单例
allure_config = AllureConfig()