from playwright.sync_api import expect

from core.base_test import BaseTest
from pages.dashboard_page import DashboardPage
from pages.login_page import LoginPage


class TestDirectAccessWithoutLogin(BaseTest):
    """测试未登录直接访问仪表板"""
    def setUp(self):
        """测试前置设置"""
        super().setUp()
        self.login_page = LoginPage(self.page)
        self.dashboard_page = DashboardPage(self.page)

    def test_direct_access_without_login(self):
        """测试未登录直接访问仪表板"""
        self.dashboard_page.navigate()
        expect(self.page).to_have_url(self.login_page.url)
