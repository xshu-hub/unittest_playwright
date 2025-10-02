from parameterized import parameterized
from playwright.sync_api import expect

from core.base_test import BaseTest
from pages.dashboard_page import DashboardPage
from pages.login_page import LoginPage


class TestMultipleUserLogin(BaseTest):
    """测试多个用户登录"""

    def setUp(self):
        """测试前置设置"""
        super().setUp()
        self.login_page = LoginPage(self.page)
        self.dashboard_page = DashboardPage(self.page)

    @parameterized.expand([
        ("admin", "admin123", "管理员", "管理员"),
        ("user1", "user123", "张三", "普通用户"),
        ("user2", "user123", "李四", "普通用户")
    ])
    def test_multiple_user_login(self, username: str, password: str, expected_name: str, expected_role: str):
        self.login_page.navigate()
        self.login_page.login(username, password)

        # 验证登录成功
        expect(self.page).to_have_url(self.dashboard_page.url)

        # 验证用户信息
        self.dashboard_page.wait_for_dashboard_page_load()
        user_info = self.dashboard_page.get_user_info()
        self.assertEqual(user_info["username"], expected_name, "用户姓名显示不正确")
        self.assertEqual(user_info["role"], expected_role, "用户角色显示不正确")
