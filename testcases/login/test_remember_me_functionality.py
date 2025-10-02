from playwright.sync_api import expect

from core.base_test import BaseTest
from pages.dashboard_page import DashboardPage
from pages.login_page import LoginPage


class TestRememberMeFunctionality(BaseTest):
    """测试记住我功能"""
    def setUp(self):
        """测试前置设置"""
        super().setUp()
        self.login_page = LoginPage(self.page)
        self.dashboard_page =DashboardPage(self.page)

    def test_remember_me_functionality(self):
        """测试记住我功能"""
        self.login_page.navigate()

        # 勾选记住我并登录
        self.login_page.check_remember_login(True)
        self.login_page.login("admin", "admin123")

        # 验证登录成功
        expect(self.page).to_have_url(self.dashboard_page.url)

        # 登出并重新访问登录页面
        self.dashboard_page.click_logout()
        self.dashboard_page.wait_for_logout_redirect()
        self.login_page.navigate()

        # 验证用户名是否被记住
        username = self.login_page.get_username_value()
        self.assertEqual(username, "admin")
