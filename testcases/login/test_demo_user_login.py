from playwright.sync_api import expect

from core.base_test import BaseTest
from pages.dashboard_page import DashboardPage
from pages.login_page import LoginPage


class TestDemoUserLogin(BaseTest):
    """测试演示普通用户账号登录"""

    def setUp(self):
        """测试前置设置"""
        super().setUp()
        self.login_page = LoginPage(self.page)
        self.dashboard_page = DashboardPage(self.page)

    def test_demo_user_login(self):
        """测试演示普通用户账号登录"""
        self.login_page.navigate()

        # 点击演示普通用户账号
        self.login_page.click_demo_user_button()

        # 等待表单填充完成
        self.page.wait_for_timeout(500)

        # 验证表单自动填充
        username = self.login_page.get_username_value()
        password = self.login_page.get_password_value()
        self.assertEqual(username, "user1")
        self.assertEqual(password, "user123")

        # 提交登录
        self.login_page.click_login_button()

        # 验证登录成功
        expect(self.page).to_have_url(self.dashboard_page.url)
