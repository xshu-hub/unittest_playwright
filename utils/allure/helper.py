import os
import json
import uuid
from datetime import datetime
from typing import Optional, Dict, Any, List, Iterable

from pathlib import Path

from allure_commons.lifecycle import AllureLifecycle
from allure_commons.reporter import AllureReporter
from allure_commons.logger import AllureFileLogger
from allure_commons._core import plugin_manager
from allure_commons.types import AttachmentType
from allure_commons.model2 import (
    Status,
    StatusDetails,
    Label,
)

from utils.logger import get_logger
from config.allure_config import allure_config
project_root = Path(__file__).parent.parent.parent
logger = get_logger(__name__)
class StepContext:
    """Allure 步骤上下文管理器，便于记录详细步骤。

    用法：
        with allure_helper.step("登录系统"):
            page.fill(...)
            page.click(...)
    """

    def __init__(self, lifecycle: AllureLifecycle, parent_uuid: Optional[str], name: str):
        self.lifecycle = lifecycle
        self.parent_uuid = parent_uuid
        self.name = name
        self._uuid = str(uuid.uuid4())

    def __enter__(self):
        # 使用 lifecycle 的上下文管理器启动步骤，并设置标题
        self._cm = self.lifecycle.start_step(parent_uuid=self.parent_uuid, uuid=self._uuid)
        step = self._cm.__enter__()
        step.name = self.name
        return self

    def __exit__(self, exc_type, exc, tb):
        status = Status.PASSED
        details = None
        if exc_type is not None:
            if issubclass(exc_type, AssertionError):
                status = Status.FAILED
            else:
                status = Status.BROKEN
            details = StatusDetails(message=str(exc) if exc else None)

        # 更新步骤状态信息
        with self.lifecycle.update_step(uuid=self._uuid) as step:
            step.status = status
            step.statusDetails = details

        # 结束步骤
        self.lifecycle.stop_step(uuid=self._uuid)
        # 返回 False 以便异常继续向外抛出（不吞掉异常）
        return False


class AllureHelper:
    """Allure 集成工具（仅依赖 allure-python-commons）。

    功能：
    - 测试步骤详细记录（上下文管理器 / 显式方法）
    - 添加附件（截图、视频、日志、任意文件）
    - 写入环境信息（environment.properties）
    - 写入结果分类规则（categories.json）
    - 管理测试容器（类维度）与测试用例生命周期（unittest 集成）
    """

    def __init__(self, results_dir: Optional[str] = None) -> None:
        self.results_dir = Path(f"{project_root}/{results_dir}" or f"{project_root}/allure-results")
        self.results_dir.mkdir(parents=True, exist_ok=True)

        # 注册 AllureReporter 与文件写入器，驱动 commons 生命周期
        plugin_manager.register(AllureReporter())
        plugin_manager.register(AllureFileLogger(str(self.results_dir)))

        self.lifecycle = AllureLifecycle()
        self._class_containers: Dict[str, str] = {}
        self._current_test_uuid: Optional[str] = None

    # ---------- 环境 & 分类 ----------
    def write_environment(self, env: Dict[str, Any]) -> None:
        """写入 Allure 环境文件 environment.properties（key=value）。"""
        try:
            lines: List[str] = []
            for k, v in env.items():
                lines.append(f"{k}={v}")
            path = self.results_dir / "environment.properties"
            path.write_text("\n".join(lines), encoding="utf-8")
        except Exception as e:
            logger.debug(f"写入环境文件失败: {str(e)}")
            pass

    def write_categories(self, categories: Iterable[Dict[str, Any]]) -> None:
        """写入分类规则 categories.json。"""
        try:
            path = self.results_dir / "categories.json"
            path.write_text(json.dumps(list(categories), ensure_ascii=False, indent=2), encoding="utf-8")
        except Exception as e:
            logger.debug(f"写入分类规则失败: {str(e)}")
            pass

    def write_executor(self, executor: Dict[str, Any]) -> None:
        """写入执行器信息 executor.json（用于在报告显示构建来源等）。"""
        try:
            path = self.results_dir / "executor.json"
            path.write_text(json.dumps(executor, ensure_ascii=False, indent=2), encoding="utf-8")
        except Exception as e:
            logger.debug(f"写入执行器信息失败: {str(e)}")
            pass

    # ---------- 容器（测试类） ----------
    def start_class_container(self, class_name: str, description: Optional[str] = None) -> None:
        if class_name in self._class_containers:
            return
        container_uuid = str(uuid.uuid4())
        with self.lifecycle.start_container(uuid=container_uuid) as container:
            container.name = class_name
            container.description = description
        self._class_containers[class_name] = container_uuid

    def stop_class_container(self, class_name: str) -> None:
        uuid_ = self._class_containers.get(class_name)
        if not uuid_:
            return
        # 写入容器（仅当包含 befores/afters 时会生成容器文件）
        self.lifecycle.write_container(uuid_)
        del self._class_containers[class_name]

    # ---------- 用例（测试方法） ----------
    def start_test_case(
        self,
        class_name: str,
        method_name: str,
        full_name: Optional[str] = None,
        description: Optional[str] = None,
        labels: Optional[List[Label]] = None,
    ) -> None:
        self._current_test_uuid = str(uuid.uuid4())
        # 注册测试用例并设置属性
        with self.lifecycle.schedule_test_case(uuid=self._current_test_uuid) as test:
            test.name = method_name
            test.fullName = full_name or f"{class_name}.{method_name}"
            test.description = description
            test.historyId = f"{class_name}.{method_name}"
            test.labels = labels or [
                Label(name="suite", value=class_name),
                Label(name="framework", value="unittest"),
                Label(name="language", value="python"),
            ]
            # 记录开始时间用于计算耗时
            test.start = int(datetime.now().timestamp() * 1000)
        # 绑定到所属容器
        container_uuid = self._class_containers.get(class_name)
        if container_uuid:
            with self.lifecycle.update_container(uuid=container_uuid) as container:
                container.children.append(self._current_test_uuid)

    def stop_test_case(self, status: Status, details: Optional[StatusDetails] = None) -> None:
        if not self._current_test_uuid:
            return
        # 更新并写出测试用例
        with self.lifecycle.update_test_case(uuid=self._current_test_uuid) as test:
            test.status = status
            test.statusDetails = details
            test.stop = int(datetime.now().timestamp() * 1000)
        self.lifecycle.write_test_case(uuid=self._current_test_uuid)
        self._current_test_uuid = None

    # ---------- 步骤 ----------
    def step(self, name: str) -> StepContext:
        return StepContext(self.lifecycle, self._current_test_uuid, name)

    def add_step(self, name: str, status: Status = Status.PASSED, details: Optional[str] = None) -> None:
        """非上下文方式直接记录一步。"""
        s_uuid = str(uuid.uuid4())
        # 开始步骤并设置标题
        with self.lifecycle.start_step(parent_uuid=self._current_test_uuid, uuid=s_uuid) as step:
            step.name = name
        # 更新步骤状态
        with self.lifecycle.update_step(uuid=s_uuid) as step:
            step.status = status
            if details:
                step.statusDetails = StatusDetails(message=details)
        # 结束步骤
        self.lifecycle.stop_step(uuid=s_uuid)

    # ---------- 附件 ----------
    def attach_file(self, file_path: str, name: Optional[str] = None, attachment_type: Optional[AttachmentType] = None) -> None:
        try:
            if not file_path or (not os.path.exists(file_path)):
                return
            # 根据扩展名为视频设置正确的 mime 与扩展，便于在 Allure 中直接播放
            ext = os.path.splitext(file_path)[1].lower()
            if attachment_type is None and ext in {".webm", ".mp4"}:
                mime = "video/webm" if ext == ".webm" else "video/mp4"
                self.lifecycle.attach_file(
                    uuid=self._current_test_uuid,
                    source=file_path,
                    name=name or os.path.basename(file_path),
                    attachment_type=mime,  # 传入字符串 mime，将在结果中显示为视频类型
                    extension=ext[1:],      # 设置扩展，避免默认 .attach
                )
                return
            # 其他类型保持原逻辑（如 PNG、TXT 等由调用方或默认策略处理）
            self.lifecycle.attach_file(
                uuid=self._current_test_uuid,
                source=file_path,
                name=name or os.path.basename(file_path),
                attachment_type=attachment_type,
            )
        except Exception as e:
            logger.debug(f"写入附件失败: {str(e)}")
            # 附件写入失败不影响测试流程
            pass

    def attach_bytes(self, data: bytes, name: str, attachment_type: Optional[AttachmentType] = None, extension: Optional[str] = None) -> None:
        try:
            self.lifecycle.attach_data(
                uuid=self._current_test_uuid,
                body=data,
                name=name,
                attachment_type=attachment_type,
                extension=extension,
            )
        except Exception as e:
            logger.debug(f"写入附件失败: {str(e)}")
            pass


# 全局单例，便于项目各处调用（从配置读取结果目录）
allure_helper = AllureHelper(results_dir=allure_config.get_results_dir())