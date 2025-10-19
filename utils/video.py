import os
import time
import threading
from datetime import datetime
from typing import Optional

from utils.cmbird_logger import logger
from utils.common import is_failed as _is_failed
from config.videos_config import videos_config

# 使用 cmbird 日志代理（由 BaseTest 在运行时注册）


class VideoRecorder:
    """
    视频录制管理：根据配置模式在测试结束时保存或丢弃视频。
    - 模式 all：保存所有测试用例视频
    - 模式 failed_only：仅保留失败测试用例视频（成功则删除）
    - 模式 disabled：不处理视频录制

    进程/线程安全：
    - 使用唯一文件名（类名.方法名.时间戳）避免并发覆盖
    - 目录创建幂等（exist_ok=True）
    - 文件操作在 try/except 内防御性处理
    """

    _dir_lock = threading.Lock()

    def __init__(self, project_root: Optional[str] = None) -> None:
        if project_root is None:
            project_root = os.path.dirname(os.path.dirname(__file__))
        self.project_root = project_root
        d = videos_config.directory()
        self.videos_dir = d if os.path.isabs(d) else os.path.join(project_root, d)

    def ensure_dir(self) -> None:
        with self._dir_lock:
            os.makedirs(self.videos_dir, exist_ok=True)


    @staticmethod
    def _retry_delete(path: Optional[str], attempts: int = 6, delay_ms: int = 250) -> bool:
        """在 Windows 上删除可能被占用的文件，进行重试。"""
        if not path:
            return True
        if not os.path.exists(path):
            return True
        last_exc = None
        for i in range(attempts):
            try:
                os.remove(path)
                return True
            except Exception as e:
                last_exc = e
                # 等待一段时间再尝试，给 Playwright 写入/关闭句柄的时间
                if i < attempts - 1:
                    time.sleep(delay_ms / 1000.0)
        # 如果最终仍失败，抛出异常给调用方记录
        if last_exc:
            raise last_exc
        return False

    @staticmethod
    def _timestamp() -> str:
        return datetime.now().strftime("%Y%m%d-%H%M%S")

    def _target_path(self, class_name: str, method_name: str, failed: bool) -> str:
        prefix = "failed_" if failed else ""
        base = f"{prefix}{class_name}.{method_name}.{self._timestamp()}"
        return os.path.join(self.videos_dir, base + ".webm")

    def handle_test_teardown(self, page, class_name: str, method_name: str, result):
        """
        在测试结束时处理视频文件：保存或删除。
        注意：Playwright 仅在页面关闭后生成视频文件。
        本方法在启用模式下会尝试关闭页面以确保视频落盘。
        """
        try:
            if not videos_config.enabled():
                return None

            if (not page) or page.is_closed():
                return None

            # 先获取 video 对象，再关闭页面（避免某些实现中关闭后 video 访问为 None）
            video = getattr(page, "video", None)
            if not video:
                # 仍需关闭页面以落盘可能的录像，但无 video 对象则无法命名保存
                self._safe_close_page(page)
                return None

            keep_success = videos_config.record_all()
            self._safe_close_page(page)

            failed = _is_failed(result, class_name, method_name)
            tmp_path = self._safe_get_video_path(video)

            self.ensure_dir()
            target_path = self._target_path(class_name, method_name, failed)

            # 仅失败模式且用例成功：删除临时视频并返回
            if not (failed or keep_success):
                self._safe_delete_tmp(video, tmp_path)
                return None

            # 保存视频（save_as 或复制临时文件）
            if self._safe_save_video(video, tmp_path, target_path):
                # 保存成功后清理临时文件
                self._safe_delete_tmp(video, tmp_path, target_path)
                logger.error(f"测试方法 {method_name} 视频保存: {target_path}")
                return target_path

            return None
        except Exception as e:
            logger.error(f"视频处理时出现异常: {e}")
            import traceback as tb
            logger.debug(tb.format_exc())
            return None

    # 辅助方法：降低主流程嵌套深度
    def _safe_close_page(self, page) -> None:
        try:
            page.close()
        except Exception as e:
            logger.warning(f"关闭页面时出现异常: {e}")

    def _safe_get_video_path(self, video) -> Optional[str]:
        try:
            return video.path()
        except Exception as e:
            logger.warning(f"获取视频路径时出现异常: {e}")
            return None

    def _safe_save_video(self, video, tmp_path: Optional[str], target_path: str) -> bool:
        try:
            if hasattr(video, "save_as"):
                video.save_as(target_path)
                return True
            if tmp_path and os.path.exists(tmp_path):
                from shutil import copyfile
                copyfile(tmp_path, target_path)
                return True
            return False
        except Exception as e:
            logger.debug(f"保存视频时出现异常: {e}")
            import traceback as tb
            logger.debug(tb.format_exc())
            return False

    def _safe_delete_tmp(self, video, tmp_path: Optional[str], target_path: Optional[str] = None) -> None:
        try:
            if hasattr(video, "delete"):
                video.delete()
                return
            if tmp_path and os.path.exists(tmp_path) and (not target_path or tmp_path != target_path):
                self._retry_delete(tmp_path)
        except Exception as e:
            # 删除失败不影响测试流程
            logger.warning(f"删除临时视频文件时出现异常: {e}")