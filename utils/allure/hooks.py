import os
import json
import logging
import io
import platform
from typing import Optional, Dict, Any, List

from allure_commons.model2 import Status, StatusDetails, Label
from allure_commons.types import AttachmentType

from .helper import allure_helper
from config.allure_config import allure_config
from utils.logger import get_logger

logger = get_logger(__name__)


class AllureTestHooks:
    """封装 BaseTest 中的 Allure 集成逻辑，减少 BaseTest 体积。

    提供类级与方法级的钩子：
    - on_class_setup / on_class_teardown
    - on_test_setup / on_test_teardown
    """

    @classmethod
    def on_class_setup(cls, cls_name: str, browser_config_data: Dict[str, Any]) -> None:
        try:
            # 容器与环境信息
            allure_helper.start_class_container(cls_name, description=f"测试类 {cls_name}")
            env = {
                "os": platform.system(),
                "os_version": platform.version(),
                "python_version": platform.python_version(),
                "browser_type": browser_config_data.get("type", "chromium"),
                "headless": browser_config_data.get("headless", False),
                "locale": browser_config_data.get("locale", "zh-CN"),
                "timezone": browser_config_data.get("timezone", "Asia/Shanghai"),
                "viewport": str(browser_config_data.get("viewport")),
            }
            # 追加环境配置中的自定义键值
            extra_env = allure_config.get_environment_extra() or {}
            try:
                for k, v in extra_env.items():
                    env[k] = v
            except Exception:
                pass
            allure_helper.write_environment(env)

            # 分类规则（已合并等待/定位失败）
            categories_file = allure_config.get_categories_file()
            categories: List[Dict[str, Any]]
            if categories_file and os.path.exists(categories_file):
                try:
                    with open(categories_file, "r", encoding="utf-8") as f:
                        categories = json.load(f)
                except Exception:
                    categories = []
            else:
                categories = [
                    {
                        "name": "断言失败",
                        "matchedStatuses": ["failed"],
                        "messageRegex": "(?s).*AssertionError.*",
                    },
                    {
                        "name": "等待/定位失败",
                        "matchedStatuses": ["failed", "broken"],
                        "messageRegex": "(?s).*(Timeout|等待超时|No node found|strict mode violation|selector .+ not found).*",
                    },
                ]
            allure_helper.write_categories(categories)

            # 执行器信息（可选）
            executor = allure_config.get_executor()
            if isinstance(executor, dict) and executor:
                allure_helper.write_executor(executor)
        except Exception as e:
            logger.debug(f"Allure 类容器启动失败: {str(e)}")
            pass

    @staticmethod
    def on_class_teardown(cls_name: str) -> None:
        try:
            allure_helper.stop_class_container(cls_name)
        except Exception as e:
            logger.debug(f"Allure 类容器关闭失败: {str(e)}")
            pass

    @classmethod
    def on_test_setup(cls, test_obj: object) -> None:
        """启动测试用例，写入 parentSuite/package 等标签。"""
        try:
            # 解析元信息
            method_name = getattr(test_obj, "_testMethodName", None)
            class_name = test_obj.__class__.__name__
            module = test_obj.__class__.__module__ or ""
            doc = getattr(test_obj, method_name).__doc__ if (method_name and hasattr(test_obj, method_name)) else None
            full_name = f"{module}.{class_name}.{method_name}"

            # 计算父套件与包名：优先 testcases 后一级，否则模块首段
            parent_suite: Optional[str] = None
            package_name: Optional[str] = None
            try:
                parts = module.split(".") if module else []
                if parts:
                    if "testcases" in parts:
                        idx = parts.index("testcases")
                        if idx + 1 < len(parts):
                            parent_suite = parts[idx + 1]
                            package_name = parts[idx + 1]
                    else:
                        parent_suite = parts[0]
                        package_name = parts[0]
            except Exception as e:
                logger.debug(f"Allure 测试用例标签计算失败: {str(e)}")
                parent_suite = None
                package_name = None

            # 构造标签
            labels = [
                Label(name="suite", value=class_name),
                Label(name="framework", value="unittest"),
                Label(name="language", value="python"),
            ]
            if parent_suite:
                labels.insert(0, Label(name="parentSuite", value=parent_suite))
            if package_name:
                labels.insert(0, Label(name="package", value=package_name))

            # 启动用例并记录初始化步骤
            allure_helper.start_test_case(
                class_name=class_name,
                method_name=method_name or "",
                full_name=full_name,
                description=(doc or ""),
                labels=labels,
            )
            allure_helper.add_step("测试初始化", Status.PASSED)

            # 启用按用例采集日志：在 root logger 上挂载一个内存 handler（固定 per-test）
            try:
                buffer = io.StringIO()
                handler = logging.StreamHandler(buffer)
                # 使用与全局相近的格式，避免依赖内部formatter
                formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s", "%Y-%m-%d %H:%M:%S")
                handler.setFormatter(formatter)
                handler.setLevel(logging.DEBUG)
                root_logger = logging.getLogger()
                root_logger.addHandler(handler)
                # 绑定到测试对象，tearDown 时移除并附加
                setattr(test_obj, "__allure_log_handler", handler)
                setattr(test_obj, "__allure_log_buffer", buffer)
            except Exception as e:
                logger.debug(f"按用例日志采集启动失败: {str(e)}")
        except Exception as e:
            logger.debug(f"Allure 测试用例启动失败: {str(e)}")
            pass

    @classmethod
    def on_test_teardown(
            cls,
            test_obj: object,
            result: object,
            screenshot_path: Optional[str],
            video_path: Optional[str],
    ) -> None:
        """结束测试用例，添加附件并写入状态。"""
        try:
            attach_cfg = allure_config.get_attachments() or {}
            do_attach_screenshot = bool(attach_cfg.get("screenshot_on_failure", True))
            do_attach_video = bool(attach_cfg.get("video_on_failure", True))

            # 附件：失败截图
            if do_attach_screenshot and screenshot_path:
                if screenshot_path.lower().endswith(".png"):
                    allure_helper.attach_file(screenshot_path, name="失败截图", attachment_type=AttachmentType.PNG)
                else:
                    allure_helper.attach_file(screenshot_path, name="失败截图")

            # 附件：视频
            if do_attach_video and video_path:
                allure_helper.attach_file(video_path, name="测试视频")

            # 附件：日志（固定 per-test）
            try:
                handler = getattr(test_obj, "__allure_log_handler", None)
                buffer = getattr(test_obj, "__allure_log_buffer", None)
                root_logger = logging.getLogger()
                if handler and buffer:
                    try:
                        handler.flush()
                    except Exception:
                        pass
                    # 从 root 移除 handler，避免泄漏
                    try:
                        root_logger.removeHandler(handler)
                    except Exception:
                        pass
                    content = buffer.getvalue()
                    if content:
                        allure_helper.attach_bytes(
                            data=content.encode("utf-8"),
                            name="test.log",
                            attachment_type=AttachmentType.TEXT,
                            extension="txt",
                        )
            except Exception as e:
                logger.debug(f"Allure 测试用例日志附件添加失败: {str(e)}")
                pass

            # 计算状态
            has_error = any(test is test_obj and err for test, err in list(getattr(result, "errors", [])))
            has_failure = any(test is test_obj and fail for test, fail in list(getattr(result, "failures", [])))
            if has_error:
                messages = [str(err) for test, err in list(getattr(result, "errors", [])) if test is test_obj and err]
                allure_helper.add_step("测试清理", Status.BROKEN)
                allure_helper.stop_test_case(Status.BROKEN, StatusDetails(message="\n".join(messages) if messages else None))
            elif has_failure:
                messages = [str(fail) for test, fail in list(getattr(result, "failures", [])) if test is test_obj and fail]
                allure_helper.add_step("测试清理", Status.FAILED)
                allure_helper.stop_test_case(Status.FAILED, StatusDetails(message="\n".join(messages) if messages else None))
            else:
                allure_helper.add_step("测试清理", Status.PASSED)
                allure_helper.stop_test_case(Status.PASSED)
        except Exception as e:
            logger.debug(f"Allure 测试用例关闭失败: {str(e)}")
            pass


# 全局钩子实例，供 BaseTest 直接使用
allure_hooks = AllureTestHooks()