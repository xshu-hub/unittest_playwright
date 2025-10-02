"""
项目通用工具模块（utils.common）

定位：提供跨模块可复用的通用函数与适配层，减少重复代码。

当前包含：
- is_failed(result, class_name, method_name): 基于 unittest TestCase.id() 的失败判断。
- load_yaml_with_default(config_file, default_provider, logger, context): 通用 YAML 配置加载。
"""

import os
import yaml
from pathlib import Path
from typing import Any, Callable, Dict


def is_failed(result: Any, class_name: str, method_name: str) -> bool:
    """判断指定类与方法的用例是否在本次结果中失败或错误。

    通过比较 TestCase.id() 的后缀是否为 "ClassName.methodName" 来定位该用例。
    """
    suffix = f"{class_name}.{method_name}"

    try:
        errors = list(getattr(result, "errors", []))
        failures = list(getattr(result, "failures", []))
    except Exception:
        errors = []
        failures = []

    has_error = any(
        (getattr(test, "id", None) and str(test.id()).endswith(suffix)) and err
        for test, err in errors
    )
    has_failure = any(
        (getattr(test, "id", None) and str(test.id()).endswith(suffix)) and fail
        for test, fail in failures
    )
    return bool(has_error or has_failure)


def load_yaml_with_default(
    config_file: str,
    default_provider: Callable[[], Dict[str, Any]],
    logger: Any,
    context: str,
) -> Dict[str, Any]:
    """加载 YAML 配置：存在则解析，缺失或异常回退默认，并记录统一日志。

    - config_file: 配置文件路径
    - default_provider: 返回默认配置的回调
    - logger: 日志记录器
    - context: 文本前缀（如 "Screenshots"、"Videos"、"Browser"）
    """
    try:
        if os.path.exists(config_file):
            with open(config_file, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f) or {}
            logger.debug(f"{context} 配置文件加载成功: {config_file}")
            return data
        else:
            logger.warning(f"{context} 配置文件不存在: {config_file}，使用默认配置")
            return default_provider()
    except Exception as e:
        logger.error(f"加载 {context} 配置失败: {str(e)}")
        return default_provider()


def default_config_path() -> str:
    """返回项目根目录下的默认配置文件路径 `config.yaml`。

    约定：公共模块位于 `utils/`，其上一级为项目根目录。
    """
    project_root = Path(__file__).resolve().parent.parent
    return str(project_root / "config.yaml")