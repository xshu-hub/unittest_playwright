from playwright.sync_api import expect

from core.base_test import BaseTest
from pages.dashboard_page import DashboardPage
from pages.login_page import LoginPage


class TestAssertionFailureWrongUserInfo(BaseTest):
    """测试断言失败：用户信息错误"""

    def setUp(self):
        """测试前置设置"""
        super().setUp()
        self.login_page = LoginPage(self.page)
        self.dashboard_page = DashboardPage(self.page)

    def test_assertion_failure_wrong_user_info(self):
        """测试断言失败场景2：验证错误的用户信息"""
        self.login_page.navigate()
        self.login_page.login("admin", "admin123")

        # 等待登录成功
        expect(self.page).to_have_url("http://localhost:8080/pages/dashboard.html")
        self.dashboard_page.wait_for_dashboard_page_load()

        # 获取用户信息并故意使用错误的断言
        user_info = self.dashboard_page.get_user_info()
        self.assertEqual(user_info["username"], "错误的用户名", f"实际用户名: {user_info['username']}")
