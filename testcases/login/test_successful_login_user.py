from playwright.sync_api import expect

from core.base_test import BaseTest
from pages.dashboard_page import DashboardPage
from pages.login_page import LoginPage


class TestSuccessfulLoginUser(BaseTest):
    """测试普通用户成功登录"""
    def setUp(self):
        """测试前置设置"""
        super().setUp()
        self.login_page = LoginPage(self.page)
        self.dashboard_page = DashboardPage(self.page)

    def test_successful_login_user(self):
        """测试普通用户账号成功登录"""
        self.login_page.navigate()

        # 使用普通用户账号登录
        self.login_page.login("user1", "user123")

        # 验证跳转到仪表板
        expect(self.page).to_have_url(self.dashboard_page.url)

        # 验证仪表板页面加载
        self.dashboard_page.wait_for_dashboard_page_load()

        # 验证用户信息显示
        user_info = self.dashboard_page.get_user_info()
        self.assertEqual(user_info["username"], "张三", "用户姓名显示不正确")
        self.assertEqual(user_info["role"], "普通用户", "用户角色显示不正确")
