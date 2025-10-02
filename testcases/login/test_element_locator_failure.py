from core.base_test import BaseTest
from pages.login_page import LoginPage


class TestElementLocatorFailure(BaseTest):
    """测试元素定位失败"""

    def setUp(self):
        """测试前置设置"""
        super().setUp()
        self.login_page = LoginPage(self.page)

    def test_element_locator_failure(self):
        """测试定位失败场景：尝试定位不存在的元素"""
        self.login_page.navigate()

        # 故意尝试定位一个不存在的元素，用于测试定位失败场景
        non_existent_element = self.page.locator("#non-existent-element-id-12345")
        # 设置较短的超时时间以快速失败
        non_existent_element.click(timeout=2000)
