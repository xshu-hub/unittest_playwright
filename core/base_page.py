import fnmatch
import time
from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any, Union, Callable, Literal

from playwright.sync_api import Page, Locator, expect, Error, Cookie, FrameLocator
from utils.cmbird_logger import logger

# 定义选择器类型
SelectorType = Union[str, Locator]


class BasePage(ABC):
    """页面对象模型基类"""

    def __init__(self, page: Page):
        """
        初始化基础页面

        Args:
            page: Playwright 页面实例
        """
        self.page = page
        self.timeout = 10000  # 默认超时时间 10 秒
        self.short_timeout = 3000  # 短超时时间 3 秒
        self.long_timeout = 30000  # 长超时时间 30 秒

    @property
    @abstractmethod
    def url(self) -> str:
        """页面 URL"""
        pass

    @property
    @abstractmethod
    def title(self) -> str:
        """页面标题"""
        pass

    def navigate(self, url: Optional[str] = None, wait_until: Literal[
        "commit", "domcontentloaded", "load", "networkidle"] = "domcontentloaded") -> 'BasePage':
        """
        导航到页面

        Args:
            url: 目标 URL，如果为空则使用页面默认 URL
            wait_until: 等待条件

        Returns:
            页面实例
        """
        target_url = url or self.url
        try:
            self.page.goto(target_url, wait_until=wait_until, timeout=self.long_timeout)
            self.wait_for_page_load()
            logger.info(f"页面导航成功: {target_url}")
            return self
        except Exception as e:
            logger.error(f"页面导航失败: {target_url} | 错误: {str(e)}")
            raise

    def wait_for_page_load(self, timeout: Optional[int] = None) -> None:
        """
        等待页面加载完成

        Args:
            timeout: 超时时间
        """
        timeout = timeout or self.long_timeout
        try:
            self.page.wait_for_load_state("domcontentloaded", timeout=timeout)
            self.page.wait_for_load_state("networkidle", timeout=timeout)
        except Exception as e:
            logger.warning(f"等待页面加载超时: {str(e)}")

    def _resolve_selector(self, selector: SelectorType) -> Locator | None:
        """
        解析选择器，支持字符串选择器和Playwright内置选择器

        Args:
            selector: 元素选择器（字符串或Locator对象）

        Returns:
            Locator对象
        """
        if isinstance(selector, str):
            return self.page.locator(selector)
        elif isinstance(selector, Locator):
            return selector
        return None

    def get_element(self, selector: SelectorType, timeout: Optional[int] = None) -> Locator:
        """
        获取页面元素

        Args:
            selector: 元素选择器（字符串或Playwright内置选择器）
            timeout: 超时时间

        Returns:
            元素定位器
        """
        timeout = timeout or self.timeout

        try:
            element = self._resolve_selector(selector)
            element.wait_for(state="visible", timeout=timeout)
            return element
        except Exception as e:
            selector_desc = str(selector) if isinstance(selector, str) else f"Locator({selector})"
            logger.error(f"获取元素失败: {selector_desc}, 错误: {str(e)}")
            raise

    def click(self, selector: SelectorType, timeout: Optional[int] = None, force: bool = False) -> 'BasePage':
        """
        点击元素

        Args:
            selector: 元素选择器（字符串或Playwright内置选择器）
            timeout: 超时时间
            force: 是否强制点击

        Returns:
            页面实例
        """
        timeout = timeout or self.timeout
        selector_desc = str(selector) if isinstance(selector, str) else f"Locator({selector})"

        try:
            element = self.get_element(selector, timeout)
            element.click(force=force, timeout=timeout)
            logger.info(f"元素点击成功: {selector_desc}")
            return self
        except Exception as e:
            logger.error(f"元素点击失败: {selector_desc} | 错误: {str(e)}")
            raise

    def double_click(self, selector: SelectorType, timeout: Optional[int] = None) -> 'BasePage':
        """
        双击元素

        Args:
            selector: 元素选择器（字符串或Playwright内置选择器）
            timeout: 超时时间

        Returns:
            页面实例
        """
        timeout = timeout or self.timeout
        selector_desc = str(selector) if isinstance(selector, str) else f"Locator({selector})"

        try:
            element = self.get_element(selector, timeout)
            element.dblclick(timeout=timeout)
            logger.info(f"元素双击成功: {selector_desc}")
            return self
        except Exception as e:
            logger.error(f"元素双击失败: {selector_desc} | 错误: {str(e)}")
            raise

    def fill(self, selector: SelectorType, value: str, timeout: Optional[int] = None, clear: bool = True) -> 'BasePage':
        """
        填充输入框

        Args:
            selector: 元素选择器（字符串或Playwright内置选择器）
            value: 输入值
            timeout: 超时时间
            clear: 是否先清空

        Returns:
            页面实例
        """
        timeout = timeout or self.timeout
        selector_desc = str(selector) if isinstance(selector, str) else f"Locator({selector})"

        try:
            element = self.get_element(selector, timeout)
            if clear:
                element.clear(timeout=timeout)
            element.fill(value, timeout=timeout)
            logger.info(f"元素填充成功: {selector_desc} = '{value}'")
            return self
        except Exception as e:
            logger.error(f"元素填充失败: {selector_desc} = '{value}' | 错误: {str(e)}")
            raise

    def type_text(self, selector: SelectorType, text: str, delay: int = 100,
                  timeout: Optional[int] = None) -> 'BasePage':
        """
        逐字符输入文本

        Args:
            selector: 元素选择器（字符串或Playwright内置选择器）
            text: 输入文本
            delay: 字符间延迟(毫秒)
            timeout: 超时时间

        Returns:
            页面实例
        """
        timeout = timeout or self.timeout
        selector_desc = str(selector) if isinstance(selector, str) else f"Locator({selector})"

        try:
            element = self.get_element(selector, timeout)
            element.type(text, delay=delay, timeout=timeout)
            logger.info(f"文本输入成功: {selector_desc} = '{text}'")
            return self
        except Exception as e:
            logger.error(f"文本输入失败: {selector_desc} = '{text}' | 错误: {str(e)}")
            raise

    def select_option(self, selector: SelectorType, value: Union[str, List[str]],
                      timeout: Optional[int] = None) -> 'BasePage':
        """
        选择下拉框选项

        Args:
            selector: 元素选择器（字符串或Playwright内置选择器）
            value: 选项值
            timeout: 超时时间

        Returns:
            页面实例
        """
        timeout = timeout or self.timeout
        selector_desc = str(selector) if isinstance(selector, str) else f"Locator({selector})"

        try:
            element = self.get_element(selector, timeout)
            element.select_option(value, timeout=timeout)
            logger.info(f"选项选择成功: {selector_desc} = '{value}'")
            return self
        except Exception as e:
            logger.error(f"选项选择失败: {selector_desc} = '{value}' | 错误: {str(e)}")
            raise

    def check(self, selector: SelectorType, timeout: Optional[int] = None) -> 'BasePage':
        """
        勾选复选框或单选框

        Args:
            selector: 元素选择器（字符串或Playwright内置选择器）
            timeout: 超时时间

        Returns:
            页面实例
        """
        timeout = timeout or self.timeout
        selector_desc = str(selector) if isinstance(selector, str) else f"Locator({selector})"

        try:
            element = self.get_element(selector, timeout)
            element.check(timeout=timeout)
            logger.info(f"复选框勾选成功: {selector_desc}")
            return self
        except Exception as e:
            logger.error(f"复选框勾选失败: {selector_desc} | 错误: {str(e)}")
            raise

    def uncheck(self, selector: SelectorType, timeout: Optional[int] = None) -> 'BasePage':
        """
        取消勾选复选框

        Args:
            selector: 元素选择器（字符串或Playwright内置选择器）
            timeout: 超时时间

        Returns:
            页面实例
        """
        timeout = timeout or self.timeout
        selector_desc = str(selector) if isinstance(selector, str) else f"Locator({selector})"

        try:
            element = self.get_element(selector, timeout)
            element.uncheck(timeout=timeout)
            logger.info(f"☐ 复选框取消勾选成功: {selector_desc}")
            return self
        except Exception as e:
            logger.error(f"复选框取消勾选失败: {selector_desc} | 错误: {str(e)}")
            raise

    def hover(self, selector: SelectorType, timeout: Optional[int] = None) -> 'BasePage':
        """
        悬停在元素上

        Args:
            selector: 元素选择器（字符串或Playwright内置选择器）
            timeout: 超时时间

        Returns:
            页面实例
        """
        timeout = timeout or self.timeout
        selector_desc = str(selector) if isinstance(selector, str) else f"Locator({selector})"

        try:
            element = self.get_element(selector, timeout)
            element.hover(timeout=timeout)
            logger.info(f"元素悬停成功: {selector_desc}")
            return self
        except Exception as e:
            logger.error(f"元素悬停失败: {selector_desc} | 错误: {str(e)}")
            raise

    def scroll_to(self, selector: Optional[SelectorType] = None, x: Optional[int] = None,
                  y: Optional[int] = None) -> 'BasePage':
        """
        滚动到指定位置或元素

        Args:
            selector: 元素选择器（字符串或Playwright内置选择器）
            x: X 坐标
            y: Y 坐标

        Returns:
            页面实例
        """
        try:
            if selector:
                element = self.get_element(selector)
                element.scroll_into_view_if_needed()
                selector_desc = str(selector) if isinstance(selector, str) else f"Locator({selector})"
                logger.info(f"成功滚动到元素: {selector_desc}")
            elif x is not None and y is not None:
                self.page.evaluate(f"window.scrollTo({x}, {y})")
                logger.info(f"成功滚动到坐标: ({x}, {y})")
            return self
        except Exception as e:
            logger.error(f"滚动失败, 错误: {str(e)}")
            raise

    def wait_for_element(self, selector: SelectorType,
                         state: Literal["attached", "detached", "hidden", "visible"] = "visible",
                         timeout: Optional[int] = None) -> Locator:
        """
        等待元素出现

        Args:
            selector: 元素选择器（字符串或Playwright内置选择器）
            state: 等待状态 (visible, hidden, attached, detached)
            timeout: 超时时间

        Returns:
            元素定位器
        """
        timeout = timeout or self.timeout
        try:
            element = self._resolve_selector(selector)
            element.wait_for(state=state, timeout=timeout)
            selector_desc = str(selector) if isinstance(selector, str) else f"Locator({selector})"
            logger.info(f"元素状态满足条件: {selector_desc}, 状态: {state}")
            return element
        except Exception as e:
            selector_desc = str(selector) if isinstance(selector, str) else f"Locator({selector})"
            logger.error(f"等待元素失败: {selector_desc}, 状态: {state}, 错误: {str(e)}")
            raise

    def wait_for_element_stable(self, selector: SelectorType, stable_time: int = 500,
                                timeout: Optional[int] = None) -> Locator:
        """
        等待元素稳定(位置和大小不再变化)

        Args:
            selector: 元素选择器（字符串或Playwright内置选择器）
            stable_time: 稳定时间(毫秒)
            timeout: 超时时间

        Returns:
            元素定位器
        """
        timeout = timeout or self.timeout
        try:
            element = self._resolve_selector(selector)
            # 先等待元素可见
            element.wait_for(state="visible", timeout=timeout)

            # 等待元素位置稳定
            last_box = None
            stable_start = None

            while True:
                current_box = element.bounding_box()
                current_time = time.time() * 1000

                if last_box == current_box:
                    if stable_start is None:
                        stable_start = current_time
                    elif current_time - stable_start >= stable_time:
                        break
                else:
                    stable_start = None
                    last_box = current_box

                time.sleep(0.1)

            selector_desc = str(selector) if isinstance(selector, str) else f"Locator({selector})"
            logger.info(f"元素已稳定: {selector_desc}")
            return element
        except Exception as e:
            selector_desc = str(selector) if isinstance(selector, str) else f"Locator({selector})"
            logger.error(f"等待元素稳定失败: {selector_desc}, 错误: {str(e)}")
            raise

    def wait_for_text(self, selector: SelectorType, text: str, timeout: Optional[int] = None) -> bool:
        """
        等待元素包含指定文本

        Args:
            selector: 元素选择器（字符串或Playwright内置选择器）
            text: 期望文本
            timeout: 超时时间

        Returns:
            是否找到文本
        """
        timeout = timeout or self.timeout
        try:
            element = self._resolve_selector(selector)
            expect(element).to_contain_text(text, timeout=timeout)
            selector_desc = str(selector) if isinstance(selector, str) else f"Locator({selector})"
            logger.info(f"元素包含期望文本: {selector_desc}, 文本: {text}")
            return True
        except Exception as e:
            selector_desc = str(selector) if isinstance(selector, str) else f"Locator({selector})"
            logger.error(f"等待文本失败: {selector_desc}, 文本: {text}, 错误: {str(e)}")
            return False

    def get_text(self, selector: SelectorType, timeout: Optional[int] = None) -> str:
        """
        获取元素文本

        Args:
            selector: 元素选择器（字符串或Playwright内置选择器）
            timeout: 超时时间

        Returns:
            元素文本
        """
        timeout = timeout or self.timeout
        try:
            element = self.get_element(selector, timeout)
            text = element.text_content()
            selector_desc = str(selector) if isinstance(selector, str) else f"Locator({selector})"
            logger.info(f"元素文本获取成功: {selector_desc} = '{text}'")
            return text or ""
        except Exception as e:
            selector_desc = str(selector) if isinstance(selector, str) else f"Locator({selector})"
            logger.error(f"元素文本获取失败: {selector_desc} | 错误: {str(e)}")
            raise

    def get_attribute(self, selector: SelectorType, attribute: str, timeout: Optional[int] = None) -> Optional[str]:
        """
        获取元素属性

        Args:
            selector: 元素选择器（字符串或Playwright内置选择器）
            attribute: 属性名
            timeout: 超时时间

        Returns:
            属性值
        """
        timeout = timeout or self.timeout
        try:
            element = self.get_element(selector, timeout)
            value = element.get_attribute(attribute)
            selector_desc = str(selector) if isinstance(selector, str) else f"Locator({selector})"
            logger.info(f"元素属性获取成功: {selector_desc}[{attribute}] = '{value}'")
            return value
        except Exception as e:
            selector_desc = str(selector) if isinstance(selector, str) else f"Locator({selector})"
            logger.error(f"元素属性获取失败: {selector_desc}[{attribute}] | 错误: {str(e)}")
            raise

    def is_visible(self, selector: SelectorType, timeout: Optional[int] = None) -> bool:
        """
        检查元素是否可见

        Args:
            selector: 元素选择器（字符串或Playwright内置选择器）
            timeout: 超时时间

        Returns:
            是否可见
        """
        timeout = timeout or self.short_timeout
        try:
            element = self._resolve_selector(selector)
            return element.is_visible(timeout=timeout)
        except (Error, TimeoutError):
            return False

    def is_enabled(self, selector: SelectorType, timeout: Optional[int] = None) -> bool:
        """
        检查元素是否可用

        Args:
            selector: 元素选择器（字符串或Playwright内置选择器）
            timeout: 超时时间

        Returns:
            是否可用
        """
        timeout = timeout or self.short_timeout
        try:
            element = self.get_element(selector, timeout)
            return element.is_enabled(timeout=timeout)
        except (Error, TimeoutError):
            return False

    def get_current_url(self) -> str:
        """
        获取当前页面 URL

        Returns:
            当前 URL
        """
        return self.page.url

    def get_current_title(self) -> str:
        """
        获取当前页面标题

        Returns:
            当前标题
        """
        return self.page.title()

    def refresh(self) -> 'BasePage':
        """
        刷新页面

        Returns:
            页面实例
        """
        try:
            self.page.reload(wait_until="domcontentloaded", timeout=self.long_timeout)
            logger.info("页面刷新成功")
            return self
        except Exception as e:
            logger.error(f"页面刷新失败: {str(e)}")
            raise

    def go_back(self) -> 'BasePage':
        """
        返回上一页

        Returns:
            页面实例
        """
        try:
            self.page.go_back(wait_until="domcontentloaded", timeout=self.long_timeout)
            logger.info("返回上一页成功")
            return self
        except Exception as e:
            logger.error(f"返回上一页失败: {str(e)}")
            raise

    def go_forward(self) -> 'BasePage':
        """
        前进到下一页

        Returns:
            页面实例
        """
        try:
            self.page.go_forward(wait_until="domcontentloaded", timeout=self.long_timeout)
            logger.info("前进到下一页成功")
            return self
        except Exception as e:
            logger.error(f"前进到下一页失败: {str(e)}")
            raise

    def execute_script(self, script: str, *args) -> Any:
        """
        执行 JavaScript 脚本

        Args:
            script: JavaScript 代码
            *args: 脚本参数

        Returns:
            脚本执行结果
        """
        try:
            result = self.page.evaluate(script, *args)
            logger.info(f"执行脚本成功: {script[:100]}...")
            return result
        except Exception as e:
            logger.error(f"执行脚本失败: {script[:100]}..., 错误: {str(e)}")
            raise

    def wait(self, seconds: float) -> 'BasePage':
        """
        等待指定时间

        Args:
            seconds: 等待秒数

        Returns:
            页面实例
        """
        logger.info(f"等待 {seconds} 秒")
        time.sleep(seconds)
        return self

    def smart_wait(self, condition_func, timeout: Optional[int] = None, poll_interval: float = 0.5) -> 'BasePage':
        """
        智能等待，基于条件函数

        Args:
            condition_func: 条件函数，返回True时停止等待
            timeout: 超时时间(毫秒)
            poll_interval: 轮询间隔(秒)

        Returns:
            页面实例
        """
        timeout = timeout or self.timeout
        start_time = time.time() * 1000

        while True:
            try:
                if condition_func():
                    logger.info("智能等待条件满足")
                    return self
            except (Error, TimeoutError, AssertionError):
                pass

            current_time = time.time() * 1000
            if current_time - start_time >= timeout:
                logger.warning("智能等待超时")
                raise TimeoutError(f"智能等待超时: {timeout}ms")

            time.sleep(poll_interval)

    def wait_for_network_idle(self, timeout: Optional[int] = None) -> 'BasePage':
        """
        等待网络空闲

        Args:
            timeout: 超时时间

        Returns:
            页面实例
        """
        timeout = timeout or self.long_timeout
        try:
            self.page.wait_for_load_state("networkidle", timeout=timeout)
            logger.info("网络已空闲")
            return self
        except Exception as e:
            logger.warning(f"等待网络空闲超时: {str(e)}")
            return self

    # ==================== 增强功能方法 ====================

    def wait_for_condition(self, condition_func: Callable[[], bool],
                           timeout: Optional[int] = None, poll_interval: float = 0.5,
                           error_message: str = "条件等待超时") -> 'BasePage':
        """
        等待条件满足

        Args:
            condition_func: 条件检查函数，返回True时停止等待
            timeout: 超时时间(毫秒)
            poll_interval: 轮询间隔(秒)
            error_message: 超时错误消息

        Returns:
            页面实例

        Raises:
            TimeoutError: 等待超时
        """
        timeout = timeout or self.timeout
        start_time = time.time() * 1000

        while True:
            try:
                if condition_func():
                    logger.info("等待条件已满足")
                    return self
            except Exception as e:
                logger.error(f"条件检查异常: {str(e)}")

            current_time = time.time() * 1000
            if current_time - start_time >= timeout:
                logger.warning(f"等待条件超时: {error_message}")
                raise TimeoutError(f"{error_message} (超时: {timeout}ms)")

            time.sleep(poll_interval)

    def get_elements(self, selector: SelectorType, timeout: Optional[int] = None) -> List[Locator]:
        """
        获取多个元素

        Args:
            selector: 元素选择器（字符串或Playwright内置选择器）
            timeout: 超时时间(毫秒)

        Returns:
            元素列表
        """
        timeout = timeout or self.timeout
        try:
            locator = self._resolve_selector(selector)
            # 等待至少一个元素出现
            locator.first.wait_for(state="attached", timeout=timeout)
            elements = locator.all()
            selector_desc = str(selector) if isinstance(selector, str) else f"Locator({selector})"
            logger.info(f"找到 {len(elements)} 个元素: {selector_desc}")
            return elements
        except Exception as e:
            selector_desc = str(selector) if isinstance(selector, str) else f"Locator({selector})"
            logger.error(f"获取元素列表失败 {selector_desc}: {str(e)}")
            return []

    def get_elements_count(self, selector: SelectorType, timeout: Optional[int] = None) -> int:
        """
        获取元素数量

        Args:
            selector: 元素选择器（字符串或Playwright内置选择器）
            timeout: 超时时间(毫秒)

        Returns:
            元素数量
        """
        timeout = timeout or self.short_timeout  # 使用短超时，因为只是计数
        try:
            locator = self._resolve_selector(selector)
            locator.wait_for(timeout=timeout)
            count = locator.count()
            selector_desc = str(selector) if isinstance(selector, str) else f"Locator({selector})"
            logger.info(f"元素数量 {selector_desc}: {count}")
            return count
        except Exception as e:
            selector_desc = str(selector) if isinstance(selector, str) else f"Locator({selector})"
            logger.error(f"获取元素数量失败 {selector_desc}: {str(e)}")
            return 0
        # 未使用局部变量 'timeout' 的值

    def wait_for_element_count(self, selector: SelectorType, expected_count: int,
                               timeout: Optional[int] = None) -> 'BasePage':
        """
        等待元素数量达到期望值

        Args:
            selector: 元素选择器（字符串或Playwright内置选择器）
            expected_count: 期望的元素数量
            timeout: 超时时间(毫秒)

        Returns:
            页面实例
        """

        def check_count():
            return self.get_elements_count(selector) == expected_count

        selector_desc = str(selector) if isinstance(selector, str) else f"Locator({selector})"
        self.wait_for_condition(
            check_count,
            timeout,
            error_message=f"等待元素数量 {selector_desc} 达到 {expected_count}"
        )
        return self

    def drag_and_drop(self, source_selector: SelectorType, target_selector: SelectorType,
                      timeout: Optional[int] = None) -> 'BasePage':
        """
        拖拽操作

        Args:
            source_selector: 源元素选择器（字符串或Playwright内置选择器）
            target_selector: 目标元素选择器（字符串或Playwright内置选择器）
            timeout: 超时时间(毫秒)

        Returns:
            页面实例
        """
        timeout = timeout or self.timeout
        try:
            source = self.get_element(source_selector, timeout)
            target = self.get_element(target_selector, timeout)

            source_desc = str(source_selector) if isinstance(source_selector, str) else f"Locator({source_selector})"
            target_desc = str(target_selector) if isinstance(target_selector, str) else f"Locator({target_selector})"
            logger.info(f"拖拽元素: {source_desc} -> {target_desc}")
            source.drag_to(target)

            return self
        except Exception as e:
            logger.error(f"拖拽操作失败: {str(e)}")
            raise

    def upload_file(self, selector: SelectorType, file_path: str, timeout: Optional[int] = None) -> 'BasePage':
        """
        文件上传

        Args:
            selector: 文件输入框选择器（字符串或Playwright内置选择器）
            file_path: 文件路径
            timeout: 超时时间(毫秒)

        Returns:
            页面实例
        """
        timeout = timeout or self.timeout
        try:
            selector_desc = str(selector) if isinstance(selector, str) else f"Locator({selector})"
            logger.info(f"上传文件: {file_path} 到 {selector_desc}")
            element = self.get_element(selector, timeout)
            element.set_input_files(file_path)

            return self
        except Exception as e:
            logger.error(f"文件上传失败: {str(e)}")
            raise

    def switch_to_frame(self, frame_selector: SelectorType, timeout: Optional[int] = None) -> FrameLocator:
        """
        切换到iframe

        Args:
            frame_selector: iframe选择器（字符串选择器）
            timeout: 超时时间(毫秒)

        Returns:
            iframe定位器
        """
        timeout = timeout or self.timeout
        try:
            # 先等待iframe元素可见
            self.wait_for_element(frame_selector, timeout=timeout)

            # 获取选择器字符串
            if isinstance(frame_selector, str):
                selector_str = frame_selector
            else:
                # 如果是Locator对象，需要转换为字符串（这里简化处理）
                selector_str = str(frame_selector)

            selector_desc = selector_str
            logger.info(f"切换到iframe: {selector_desc}")

            # 使用page.frame_locator来获取frame
            frame_locator = self.page.frame_locator(selector_str)
            return frame_locator

        except Exception as e:
            logger.error(f"切换iframe失败: {str(e)}")
            raise

    def get_page_source(self) -> str:
        """
        获取页面源码

        Returns:
            页面HTML源码
        """
        try:
            source = self.page.content()
            logger.info(f"获取页面源码，长度: {len(source)}")
            return source
        except Exception as e:
            logger.error(f"获取页面源码失败: {str(e)}")
            return ""

    def clear_cookies(self) -> 'BasePage':
        """
        清除所有cookies

        Returns:
            页面实例
        """
        try:
            logger.info("清除所有cookies")
            self.page.context.clear_cookies()
            return self
        except Exception as e:
            logger.error(f"清除cookies失败: {str(e)}")
            return self

    def set_cookie(self, name: str, value: str, domain: Optional[str] = None,
                   path: str = "/", expires: Optional[int] = None) -> 'BasePage':
        """
        设置cookie

        Args:
            name: cookie名称
            value: cookie值
            domain: 域名
            path: 路径
            expires: 过期时间(时间戳)

        Returns:
            页面实例
        """
        try:
            cookie_data: Dict[str, Any] = {
                'name': name,
                'value': value,
                'path': path
            }

            if domain:
                cookie_data['domain'] = domain
            if expires:
                cookie_data['expires'] = expires

            logger.info(f"设置cookie: {name}={value}")
            self.page.context.add_cookies([cookie_data])  # type: ignore[list-item]
            return self
        except Exception as e:
            logger.error(f"设置cookie失败: {str(e)}")
            return self

    def get_cookies(self) -> List[Cookie]:
        """
        获取所有cookies

        Returns:
            cookies列表
        """
        try:
            cookies = self.page.context.cookies()
            logger.info(f"获取到 {len(cookies)} 个cookies")
            return cookies
        except Exception as e:
            logger.error(f"获取cookies失败: {str(e)}")
            return []

    def set_viewport_size(self, width: int, height: int) -> 'BasePage':
        """
        设置视口大小

        Args:
            width: 宽度
            height: 高度

        Returns:
            页面实例
        """
        try:
            logger.info(f"设置视口大小: {width}x{height}")
            self.page.set_viewport_size({"width": width, "height": height})
            return self
        except Exception as e:
            logger.error(f"设置视口大小失败: {str(e)}")
            return self

    def get_viewport_size(self) -> Dict[str, int]:
        """
        获取视口大小

        Returns:
            视口大小字典 {'width': int, 'height': int}
        """
        try:
            viewport = self.page.viewport_size
            logger.info(f"当前视口大小: {viewport}")
            return viewport or {'width': 0, 'height': 0}
        except Exception as e:
            logger.error(f"获取视口大小失败: {str(e)}")
            return {'width': 0, 'height': 0}

    def click_and_wait_for_new_tab(self, selector: SelectorType, timeout: Optional[int] = None) -> Page:
        """
        点击元素并等待新标签页打开

        Args:
            selector: 要点击的元素选择器
            timeout: 等待超时时间

        Returns:
            新打开的页面对象

        Raises:
            TimeoutError: 等待新标签页超时
            Exception: 点击操作失败
        """
        timeout = timeout or self.timeout
        logger.info(f"点击并等待新标签页 {str(selector)}")

        try:
            # 监听新页面事件
            with self.page.context.expect_page(timeout=timeout) as new_page_info:
                # 执行点击操作
                element = self._resolve_selector(selector)
                element.click()

            # 获取新页面
            new_page = new_page_info.value
            # 等待新页面加载完成
            new_page.wait_for_load_state("domcontentloaded", timeout=timeout)

            logger.info(f"成功打开新标签页: {new_page.url}")
            return new_page

        except Exception as e:
            logger.error(f"点击并等待新标签页失败: {str(e)}")
            raise

    def switch_to_new_tab(self, action_callback: Callable[[], None], timeout: Optional[int] = None) -> Page:
        """
        执行操作并切换到新打开的标签页

        Args:
            action_callback: 触发新标签页的操作回调函数
            timeout: 等待超时时间

        Returns:
            新打开的页面对象

        Example:
            # 点击链接打开新标签页
            new_page = base_page.switch_to_new_tab(
                lambda: base_page.click("a[target='_blank']")
            )
        """
        timeout = timeout or self.timeout
        logger.info(f"执行操作并切换到新标签页 {str(action_callback)}")

        try:
            # 监听新页面事件
            with self.page.context.expect_page(timeout=timeout) as new_page_info:
                # 执行触发新标签页的操作
                action_callback()

            # 获取新页面
            new_page = new_page_info.value

            # 等待新页面加载完成
            new_page.wait_for_load_state("domcontentloaded", timeout=timeout)

            logger.info(f"成功切换到新标签页: {new_page.url}")
            return new_page

        except Exception as e:
            logger.error(f"切换到新标签页失败: {str(e)}")
            raise

    def get_all_pages(self) -> List[Page]:
        """
        获取当前浏览器上下文中的所有页面

        Returns:
            页面列表
        """
        try:
            pages = self.page.context.pages
            logger.info(f"当前共有 {len(pages)} 个页面")
            for i, page in enumerate(pages):
                logger.info(f"  页面 {i}: {page.url}")
            return pages
        except Exception as e:
            logger.error(f"获取所有页面失败: {str(e)}")
            return []

    def switch_to_page_by_url(self, url_pattern: str) -> Optional[Page]:
        """
        根据URL模式切换到指定页面

        Args:
            url_pattern: URL模式（支持通配符）

        Returns:
            匹配的页面对象，如果未找到则返回None
        """
        try:
            pages = self.get_all_pages()
            for page in pages:
                if url_pattern in page.url or fnmatch.fnmatch(page.url, url_pattern):
                    logger.info(f"切换到页面: {page.url}")
                    return page

            logger.warning(f"未找到匹配URL模式的页面: {url_pattern}")
            return None

        except Exception as e:
            logger.error(f"切换页面失败: {str(e)}")
            return None

    def switch_to_page_by_title(self, title_pattern: str) -> Optional[Page]:
        """
        根据标题模式切换到指定页面

        Args:
            title_pattern: 标题模式

        Returns:
            匹配的页面对象，如果未找到则返回None
        """
        try:
            pages = self.get_all_pages()
            for page in pages:
                page_title = page.title()
                if title_pattern in page_title:
                    logger.info(f"切换到页面: {page_title} ({page.url})")
                    return page

            logger.warning(f"未找到匹配标题模式的页面: {title_pattern}")
            return None

        except Exception as e:
            logger.error(f"根据标题切换页面失败: {str(e)}")
            return None

    def close_other_pages(self, keep_current: bool = True) -> None:
        """
        关闭其他页面，只保留当前页面或指定页面

        Args:
            keep_current: 是否保留当前页面
        """
        try:
            pages = self.get_all_pages()
            current_page = self.page if keep_current else None

            closed_count = 0
            for page in pages:
                if page != current_page:
                    try:
                        page.close()
                        closed_count += 1
                        logger.info(f"已关闭页面: {page.url}")
                    except Exception as e:
                        logger.error(f"关闭页面失败: {page.url} | {str(e)}")

            logger.info(f"已关闭 {closed_count} 个页面")

        except Exception as e:
            logger.error(f"关闭其他页面失败: {str(e)}")

    def wait_for_new_page(self, timeout: Optional[int] = None) -> Page:
        """
        等待新页面打开（不执行任何操作，只是等待）

        Args:
            timeout: 等待超时时间

        Returns:
            新打开的页面对象
        """
        timeout = timeout or self.timeout
        logger.info("等待新页面打开")

        try:
            with self.page.context.expect_page(timeout=timeout) as new_page_info:
                pass  # 只等待，不执行任何操作

            new_page = new_page_info.value
            new_page.wait_for_load_state("domcontentloaded", timeout=timeout)

            logger.info(f"检测到新页面: {new_page.url}")
            return new_page

        except Exception as e:
            logger.warning(f"等待新页面超时: {str(e)}")
            raise
