"""
浏览器管理类
负责浏览器的启动、关闭和上下文管理
"""
from typing import Optional, Dict, List
from playwright.sync_api import Playwright, Browser, BrowserContext, Page, sync_playwright
from utils.logger import get_logger, setup_logging
from config.videos_config import videos_config
import os

# 初始化日志系统（幂等）
setup_logging()
logger = get_logger(__name__)


class BrowserManager:
    """浏览器管理类"""
    
    def __init__(self):
        """初始化浏览器管理器"""
        self.playwright: Optional[Playwright] = None
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
        self._is_started = False
        
    def start_browser(self, 
                     browser_type: str = "chromium",
                     headless: bool = False,
                     viewport: Optional[Dict[str, int]] = None,
                     no_viewport: bool = False,
                     user_agent: Optional[str] = None,
                     locale: str = "zh-CN",
                     timezone: str = "Asia/Shanghai",
                     extra_http_headers: Optional[Dict[str, str | int | bool]] = None,
                     ignore_https_errors: bool = True,
                     slow_mo: int = 0,
                     args: Optional[List[str]] = None,
                     **kwargs) -> Page:
        """
        启动浏览器并创建页面
        
        Args:
            browser_type: 浏览器类型 (chromium, firefox, webkit)
            headless: 是否无头模式
            viewport: 视口大小 {"width": 1920, "height": 1080}
            no_viewport: 是否禁用视口 (全屏模式)
            user_agent: 用户代理
            locale: 语言环境
            timezone: 时区
            extra_http_headers: 额外的HTTP头
            ignore_https_errors: 是否忽略HTTPS错误
            slow_mo: 操作延迟时间(毫秒)
            args: 浏览器启动参数
            **kwargs: 其他浏览器选项
            
        Returns:
            Page: 页面实例
        """
        try:
            if self._is_started:
                logger.warning("浏览器已经启动，将先关闭现有浏览器")
                self.close_browser()
                
            # 启动 Playwright
            self.playwright = sync_playwright().start()
            
            # 获取浏览器类型
            if browser_type.lower() == "chromium":
                browser_launcher = self.playwright.chromium
            elif browser_type.lower() == "firefox":
                browser_launcher = self.playwright.firefox
            elif browser_type.lower() == "webkit":
                browser_launcher = self.playwright.webkit
            else:
                raise ValueError(f"不支持的浏览器类型: {browser_type}")
            
            # 设置默认视口
            if viewport is None:
                viewport = {"width": 1920, "height": 1080}

            # 禁用视口 (全屏模式)
            if no_viewport is None:
                no_viewport = False
                
            # 设置默认启动参数
            if args is None:
                args = []
                
            # 启动浏览器
            browser_options = {
                "headless": headless,
                "slow_mo": slow_mo,
                "args": args,
                **kwargs
            }
            
            self.browser = browser_launcher.launch(**browser_options)
            logger.debug(f"浏览器 {browser_type} 启动成功")
            
            # 创建浏览器上下文
            context_options = {
                "viewport": viewport,
                "locale": locale,
                "timezone_id": timezone,
                "ignore_https_errors": ignore_https_errors,
                "no_viewport": no_viewport
            }
            
            if user_agent:
                context_options["user_agent"] = user_agent
                
            if extra_http_headers:
                context_options["extra_http_headers"] = extra_http_headers
                
            # 视频录制：根据配置启用上下文视频目录
            try:
                if videos_config.enabled():
                    project_root = os.path.dirname(os.path.dirname(__file__))
                    vdir = videos_config.directory()
                    record_dir = vdir if os.path.isabs(vdir) else os.path.join(project_root, vdir)
                    os.makedirs(record_dir, exist_ok=True)
                    context_options["record_video_dir"] = record_dir
                    size = videos_config.size()
                    if isinstance(size, dict) and "width" in size and "height" in size:
                        context_options["record_video_size"] = {
                            "width": int(size["width"]),
                            "height": int(size["height"]),
                        }
            except Exception as e:
                logger.warning(f"视频录制上下文配置失败，将不启用视频: {str(e)}")

            self.context = self.browser.new_context(**context_options)
            logger.debug("浏览器上下文创建成功")
            
            # 创建页面
            self.page = self.context.new_page()
            logger.debug("页面创建成功")
            
            self._is_started = True
            return self.page
            
        except Exception as e:
            logger.error(f"启动浏览器失败: {str(e)}")
            self.close_browser()
            raise
    
    def new_page(self) -> Page:
        """
        创建新页面
        
        Returns:
            Page: 新页面实例
        """
        if not self.context:
            raise RuntimeError("浏览器上下文未初始化，请先启动浏览器")
            
        page = self.context.new_page()
        logger.debug("创建新页面成功")
        return page
    
    def close_page(self, page: Optional[Page] = None) -> None:
        """
        关闭页面
        
        Args:
            page: 要关闭的页面，如果为None则关闭当前页面
        """
        try:
            target_page = page or self.page
            if target_page and not target_page.is_closed():
                target_page.close()
                logger.debug("页面关闭成功")
                
                # 如果关闭的是当前页面，清空引用
                if target_page == self.page:
                    self.page = None
                    
        except Exception as e:
            logger.error(f"关闭页面失败: {str(e)}")
    
    def close_context(self) -> None:
        """关闭浏览器上下文"""
        try:
            if self.context:
                self.context.close()
                self.context = None
                self.page = None
                logger.debug("浏览器上下文关闭成功")
        except Exception as e:
            logger.error(f"关闭浏览器上下文失败: {str(e)}")
    
    def close_browser(self) -> None:
        """关闭浏览器"""
        try:
            if self.browser:
                self.browser.close()
                self.browser = None
                self.context = None
                self.page = None
                logger.debug("浏览器关闭成功")
                
            if self.playwright:
                self.playwright.stop()
                self.playwright = None
                logger.debug("Playwright 停止成功")
                
            self._is_started = False
            
        except Exception as e:
            logger.error(f"关闭浏览器失败: {str(e)}")
    
    def get_current_page(self) -> Optional[Page]:
        """
        获取当前页面
        
        Returns:
            Page: 当前页面实例
        """
        return self.page
    
    def get_all_pages(self) -> List[Page]:
        """
        获取所有页面
        
        Returns:
            List[Page]: 所有页面列表
        """
        if not self.context:
            return []
        return self.context.pages
    
    def switch_to_page(self, page_index: int) -> Optional[Page]:
        """
        切换到指定索引的页面
        
        Args:
            page_index: 页面索引
            
        Returns:
            Page: 切换后的页面实例
        """
        pages = self.get_all_pages()
        if 0 <= page_index < len(pages):
            self.page = pages[page_index]
            logger.debug(f"切换到页面索引 {page_index}")
            return self.page
        else:
            logger.warning(f"无效的页面索引: {page_index}")
            return None
    
    def is_browser_started(self) -> bool:
        """
        检查浏览器是否已启动
        
        Returns:
            bool: 浏览器是否已启动
        """
        return self._is_started and self.browser is not None
    
    def set_default_timeout(self, timeout: int) -> None:
        """
        设置默认超时时间
        
        Args:
            timeout: 超时时间(毫秒)
        """
        if self.context:
            self.context.set_default_timeout(timeout)
            logger.debug(f"设置默认超时时间: {timeout}ms")
    
    def set_default_navigation_timeout(self, timeout: int) -> None:
        """
        设置默认导航超时时间
        
        Args:
            timeout: 超时时间(毫秒)
        """
        if self.context:
            self.context.set_default_navigation_timeout(timeout)
            logger.debug(f"设置默认导航超时时间: {timeout}ms")
    
    def __enter__(self):
        """上下文管理器入口"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器出口"""
        self.close_browser()