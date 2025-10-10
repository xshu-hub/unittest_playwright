"""
测试基类
基于Python unittest框架，提供Web UI自动化测试的基础功能
统一接入项目日志系统
"""
import unittest
import traceback
import time
from typing import Optional

from playwright.sync_api import Page

from core.browser_manager import BrowserManager
from config.browser_config import browser_config
from utils.cmbird_logger import logger, set_current_logger, clear_current_logger
from utils.screenshot import ScreenshotHelper
from utils.video import VideoRecorder
from config.videos_config import videos_config
screenshot_helper = ScreenshotHelper()
video_recorder = VideoRecorder()


class BaseTest(unittest.TestCase):
    """测试基类"""
    
    # 类级别的浏览器管理器
    browser_manager: Optional[BrowserManager] = None
    page: Optional[Page] = None

    # ---------- 私有工具方法 ----------
    def _init_browser_if_needed(self) -> None:
        """按需初始化浏览器与上下文，并设置默认超时。"""
        if not self.browser_manager:
            logger.debug("检测到未初始化的浏览器管理器，执行按需初始化")
            self.__class__.browser_manager = BrowserManager()
            browser_config_data = browser_config.get_browser_config()
            self.__class__.page = self.browser_manager.start_browser(
                browser_type=browser_config_data.get("type", "chromium"),
                headless=browser_config_data.get("headless", False),
                viewport=browser_config_data.get("viewport"),
                no_viewport=browser_config_data.get("no_viewport", False),
                user_agent=browser_config_data.get("user_agent"),
                locale=browser_config_data.get("locale", "zh-CN"),
                timezone=browser_config_data.get("timezone", "Asia/Shanghai"),
                extra_http_headers=browser_config_data.get("extra_http_headers"),
                ignore_https_errors=browser_config_data.get("ignore_https_errors", True),
                slow_mo=browser_config_data.get("slow_mo", 0),
                args=browser_config_data.get("args", [])
            )
            timeout_config = browser_config.get_timeout_config()
            self.browser_manager.set_default_timeout(timeout_config.get("default", 10000))
            self.browser_manager.set_default_navigation_timeout(timeout_config.get("navigation", 30000))

    def _init_page_for_test(self) -> None:
        """为当前测试方法准备独立页面（视频启用或页面已关闭时）。"""
        if videos_config.enabled() or (not self.page or self.page.is_closed()):
            # 若已有页面未关闭，先关闭以避免同一测试产生两个视频
            if self.page and not self.page.is_closed():
                try:
                    logger.debug("关闭上一页面以避免重复视频")
                    self.browser_manager.close_page(self.page)
                except Exception as e:
                    logger.debug(f"关闭旧页面时出现异常: {str(e)}")
                    logger.debug(traceback.format_exc())
            logger.debug("创建新页面用于当前测试")
            self.page = self.browser_manager.new_page()
            self.__class__.page = self.page

    def _clear_storage_and_cookies(self) -> None:
        """清理本地存储与 Cookies，减少状态残留。"""
        try:
            if self.page and (not self.page.is_closed()):
                self.page.evaluate("localStorage.clear(); sessionStorage.clear();")
            if self.browser_manager and self.browser_manager.context:
                self.browser_manager.context.clear_cookies()
        except Exception as e:
            logger.debug(f"清理存储或 Cookies 时出现异常: {str(e)}")
            logger.debug(traceback.format_exc())

    def setUp(self) -> None:
        """
        测试方法级别的初始化
        在每个测试方法执行前执行
        """
        try:
            # 将 cmbird 的 logger 注册为当前上下文 logger（若不存在则为 no-op）
            set_current_logger(getattr(self, "logger", None))
            logger.info(f"开始执行测试方法: {self._testMethodName}")
            # 记录测试开始时间
            self._test_start_time = time.perf_counter()
            # 初始化浏览器与页面
            self._init_browser_if_needed()
            self._init_page_for_test()
            
        except Exception as e:
            logger.error(f"测试方法 {self._testMethodName} 初始化失败: {str(e)}")
            logger.debug(traceback.format_exc())
            raise
    
    def tearDown(self) -> None:
        """
        测试方法级别的清理
        在每个测试方法执行后执行
        """
        try:
            # logger.info(f"测试方法 {self._testMethodName} 执行完成")
            pass
        except Exception as e:
            logger.error(f"测试方法 {self._testMethodName} 清理失败: {str(e)}")
            logger.debug(traceback.format_exc())
        finally:
            # 记录失败详情与结果摘要
            outcome = getattr(self, "_outcome", None)
            result = getattr(outcome, "result", None)
            try:
                if result:
                    self._record_failure_details(result)
                    # 在失败场景下捕获截图（使用工具类）
                    screenshot_path = screenshot_helper.capture_on_failure(
                        page=self.page,
                        class_name=self.__class__.__name__,
                        method_name=self._testMethodName,
                        result=result,
                        logger=logger,
                    )
                    # 在页面关闭生成视频之前，先清理存储与 Cookies，避免参数化用例状态残留
                    self._clear_storage_and_cookies()
                    # 视频处理：保存或丢弃视频（需在页面关闭后）
                    try:
                        video_path = video_recorder.handle_test_teardown(
                            page=self.page,
                            class_name=self.__class__.__name__,
                            method_name=self._testMethodName,
                            result=result,
                        )
                    except Exception as e:
                        logger.debug(f"处理测试视频时出现异常: {str(e)}")
                        logger.debug(traceback.format_exc())
                        video_path = None
                    # 取消 Allure 集成：不再添加 Allure 附件或状态

                    self._log_test_summary(result)
            except Exception as e:
                # 防御性处理：不影响测试结果
                logger.debug(f"记录失败信息到日志时出现异常: {str(e)}")
                logger.debug(traceback.format_exc())
            finally:
                # 清理当前上下文 logger
                clear_current_logger()

    def _record_failure_details(self, result) -> None:
        """
        将本测试用例的异常与断言失败完整文本写入 error 日志
        """
        # 错误（异常）
        for test, err in list(getattr(result, "errors", [])):
            if test is self and err:
                logger.error(f"测试方法 {self._testMethodName} 异常失败:\n{err}")
        # 断言失败
        for test, fail in list(getattr(result, "failures", [])):
            if test is self and fail:
                logger.error(f"测试方法 {self._testMethodName} 断言失败:\n{fail}")

    def _log_test_summary(self, result) -> None:
        """
        输出本测试用例的结果摘要（通过/失败 + 耗时）
        """
        start = getattr(self, "_test_start_time", None)
        duration_ms = None
        if start is not None:
            duration_ms = int((time.perf_counter() - start) * 1000)

        has_error = any(test is self and err for test, err in list(getattr(result, "errors", [])))
        has_failure = any(test is self and fail for test, fail in list(getattr(result, "failures", [])))
        status = "失败" if (has_error or has_failure) else "通过"

        msg = f"测试方法 {self._testMethodName} 结果: {status}"
        if duration_ms is not None:
            msg += f"，耗时 {duration_ms}ms"

        if status == "通过":
            logger.info(msg)
        else:
            logger.error(msg)