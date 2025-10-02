from playwright.sync_api import expect

from core.base_test import BaseTest
from pages.dashboard_page import DashboardPage
from pages.login_page import LoginPage


class TestAssertionFailureWrongTitle(BaseTest):
    """测试断言失败：标题错误"""

    def setUp(self):
        """测试前置设置"""
        super().setUp()
        self.login_page = LoginPage(self.page)
        self.dashboard_page = DashboardPage(self.page)

    def test_assertion_failure_wrong_title(self):
        """测试断言失败场景1：验证错误的页面标题"""
        self.login_page.navigate()
        # 故意使用错误的页面标题进行断言，用于测试失败场景
        expect(self.page).to_have_title("错误的页面标题 - 这应该会失败")
