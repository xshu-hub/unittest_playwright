from playwright.sync_api import expect

from core.base_test import BaseTest
from pages.dashboard_page import DashboardPage
from pages.login_page import LoginPage


class TestLoginRedirectAfterLogout(BaseTest):
    """测试登出后重新登录"""

    def setUp(self):
        """测试前置设置"""
        super().setUp()
        self.login_page = LoginPage(self.page)
        self.dashboard_page = DashboardPage(self.page)

    def test_login_redirect_after_logout(self):
        """测试登出后重新登录"""
        # 先登录
        self.login_page.navigate()
        self.login_page.login("admin", "admin123")
        expect(self.page).to_have_url(self.dashboard_page.url)

        # 登出
        self.dashboard_page.click_logout()
        self.dashboard_page.wait_for_logout_redirect()

        # 验证跳转到登录页面
        expect(self.page).to_have_url(self.login_page.url)

        # 重新登录
        self.login_page.login("user1", "user123")
        expect(self.page).to_have_url(self.dashboard_page.url)
