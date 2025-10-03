import os
import traceback
from datetime import datetime
from typing import List
from config.screenshots_config import screenshots_config
from utils.common import is_failed as _is_failed


class ScreenshotHelper:
    """
    失败自动截图工具类：在用例失败时保存截图。
    """

    def __init__(self, project_root: str | None = None) -> None:
        if project_root is None:
            # 默认以 utils/ 的上一级作为项目根
            project_root = os.path.dirname(os.path.dirname(__file__))

        self.project_root = project_root
        # 目录来自配置，可为绝对路径或相对项目根
        dir_cfg = screenshots_config.screenshots_directory()
        self.screenshots_dir = dir_cfg if os.path.isabs(dir_cfg) else os.path.join(project_root, dir_cfg)

    def ensure_dirs(self) -> None:
        os.makedirs(self.screenshots_dir, exist_ok=True)

    @staticmethod
    def _basename(class_name: str, method_name: str) -> str:
        ts = datetime.now().strftime("%Y%m%d-%H%M%S")
        return f"failed_{class_name}.{method_name}.{ts}"

    def capture_on_failure(self, page, class_name: str, method_name: str, result, logger):
        """
        如果当前用例失败，则根据配置捕获截图。
        """
        try:
            # 开关控制
            if not screenshots_config.screenshots_enabled():
                return

            # 统一调用公共失败判断工具
            if not _is_failed(result, class_name, method_name):
                return

            if (not page) or page.is_closed():
                logger.warning("失败时页面不可用，跳过截图保存")
                return

            self.ensure_dirs()
            base = self._basename(class_name, method_name)
            image_type = screenshots_config.screenshots_type()
            full_page = screenshots_config.screenshots_full_page()
            screenshot_path = os.path.join(self.screenshots_dir, base + (".jpeg" if image_type == "jpeg" else ".png"))

            # 构建遮挡（可选）
            mask_selectors: List[str] = screenshots_config.screenshots_mask_selectors()
            mask = []
            if mask_selectors:
                try:
                    mask = [page.locator(sel) for sel in mask_selectors]
                except Exception as e:
                    logger.debug(f"构建截图遮挡时出现异常: {e}")
                    logger.debug(traceback.format_exc())

            # 采集截图
            page.screenshot(path=screenshot_path, full_page=full_page, type=image_type, mask=mask or None)

            logger.error(f"测试方法 {method_name} 失败截图已保存: {screenshot_path}")
            return screenshot_path
        except Exception as e:
            logger.debug(f"失败截图采集时出现异常: {e}")
            logger.debug(traceback.format_exc())
            return None