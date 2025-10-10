from __future__ import annotations

"""
cmbird 日志代理

目标：
- 去除项目自定义日志模块依赖，统一改用 cmbird 的 `self.logger`
- 在非用例类（如工具类、页面对象、配置模块）中，也能使用同一套日志接口

实现要点：
- 使用 ContextVar 持有“当前用例”的 logger（由 BaseTest 在 setUp 时注册）
- 提供 LoggerProxy：接口与常见 logger 相同（debug/info/warning/error），若无当前 logger 则静默（no-op）
- 提供 set_current_logger()/clear_current_logger() 助手，供 BaseTest 管理
"""

from contextvars import ContextVar
from typing import Optional, Any


_current_logger: ContextVar[Optional[Any]] = ContextVar("cmbird_current_logger", default=None)


class _NoopLogger:
    def debug(self, *args, **kwargs):
        pass

    def info(self, *args, **kwargs):
        pass

    def warning(self, *args, **kwargs):
        pass

    def error(self, *args, **kwargs):
        pass


_noop = _NoopLogger()


def set_current_logger(logger: Any) -> None:
    """注册当前用例 logger（通常为 cmbird 提供的 self.logger）。"""
    _current_logger.set(logger)


def clear_current_logger() -> None:
    """清除当前用例 logger，上下文退出时调用。"""
    _current_logger.set(None)


def get_current_logger() -> Any:
    """获取当前用例 logger；若不存在则返回 no-op。"""
    return _current_logger.get() or _noop


class LoggerProxy:
    """代理对象：将日志调用转发到当前用例的 logger。"""

    def _delegate(self):
        return get_current_logger()

    def debug(self, *args, **kwargs):
        return self._delegate().debug(*args, **kwargs)

    def info(self, *args, **kwargs):
        return self._delegate().info(*args, **kwargs)

    def warning(self, *args, **kwargs):
        return self._delegate().warning(*args, **kwargs)

    def error(self, *args, **kwargs):
        return self._delegate().error(*args, **kwargs)


# 单例代理，供各模块直接导入使用：
# from utils.cmbird_logger import logger
logger = LoggerProxy()