import os
import time
import threading
from datetime import datetime
from typing import Optional

from utils.logger import get_logger
from utils.common import is_failed as _is_failed
from config.videos_config import videos_config

logger = get_logger(__name__)


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

            # 根据模式决定是否保留成功用例视频
            keep_success = videos_config.record_all()

            # 关闭页面以确保视频文件生成
            try:
                page.close()
            except Exception as e:
                logger.warning(f"关闭页面时出现异常: {e}")
                # 即便关闭失败，继续尝试访问 video 信息
                pass

            # 视频对象获取
            video = getattr(page, "video", None)
            if not video:
                return None

            # 失败判断（统一调用公共工具）
            failed = _is_failed(result, class_name, method_name)

            # 获取临时路径
            try:
                tmp_path = video.path()
            except Exception as e:
                logger.warning(f"获取视频路径时出现异常: {e}")
                tmp_path = None

            # 目录与目标路径
            self.ensure_dir()
            target_path = self._target_path(class_name, method_name, failed)

            # 失败或保存所有：保留视频
            if failed or keep_success:
                try:
                    # 优先使用 save_as 以提高原子性
                    if hasattr(video, "save_as"):
                        video.save_as(target_path)
                    elif tmp_path and os.path.exists(tmp_path):
                        # 回退到文件复制
                        from shutil import copyfile
                        copyfile(tmp_path, target_path)
                    # 保存到目标路径后，删除原始哈希文件以避免重复
                    try:
                        if hasattr(video, "delete"):
                            video.delete()
                        elif tmp_path and os.path.exists(tmp_path) and tmp_path != target_path:
                            self._retry_delete(tmp_path)
                    except Exception as e:
                        logger.warning(f"删除临时视频文件时出现异常: {e}")
                    logger.error(f"测试方法 {method_name} 视频保存: {target_path}")
                    return target_path
                except Exception as e:
                    logger.debug(f"保存视频时出现异常: {e}")
                    import traceback as tb
                    logger.debug(tb.format_exc())
                    return None
            else:
                # 成功用例且仅失败模式：删除临时文件（节省空间）
                try:
                    if hasattr(video, "delete"):
                        video.delete()
                    elif tmp_path and os.path.exists(tmp_path):
                        self._retry_delete(tmp_path)
                except Exception as e:
                    logger.error(f"删除临时视频文件时出现异常: {e}")
                    # 删除失败不影响测试流程
                    pass
                return None
        except Exception as e:
            logger.error(f"视频处理时出现异常: {e}")
            import traceback as tb
            logger.debug(tb.format_exc())
            return None