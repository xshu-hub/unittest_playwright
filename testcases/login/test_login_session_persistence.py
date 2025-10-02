from playwright.sync_api import expect

from core.base_test import BaseTest
from pages.login_page import LoginPage

from pages.dashboard_page import DashboardPage


class TestLoginSessionPersistence(BaseTest):
    """测试登录会话持久化"""

    def setUp(self):
        """测试前置设置"""
        super().setUp()
        self.login_page = LoginPage(self.page)
        self.dashboard_page = DashboardPage(self.page)

    def test_login_session_persistence(self):
        """测试登录会话持久性"""
        # 登录
        self.login_page.navigate()
        self.login_page.login("admin", "admin123")
        expect(self.page).to_have_url(self.dashboard_page.url)

        # 刷新页面
        self.page.reload()

        # 验证仍然保持登录状态
        self.dashboard_page.wait_for_dashboard_page_load()
        user_info = self.dashboard_page.get_user_info()
        self.assertEqual(user_info["username"], "管理员")
