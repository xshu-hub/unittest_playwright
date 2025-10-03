import time

from core.base_test import BaseTest
from pages.dashboard_page import DashboardPage
from pages.login_page import LoginPage
from pages.user_management_page import UserManagementPage


class TestAddNewUserSuccess(BaseTest):
    def setUp(self):
        """测试前置设置：初始化页面对象"""
        super().setUp()
        self.login_page = LoginPage(self.page)
        self.dashboard_page = DashboardPage(self.page)
        self.user_management_page = UserManagementPage(self.page)

    def login_as_admin(self):
        """以管理员身份登录"""
        self.login_page.navigate()
        self.login_page.login("admin", "admin123")

        # 等待登录成功消息出现
        self.page.wait_for_selector(".alert.alert-success", timeout=5000)

        # 验证跳转到仪表板
        self.page.wait_for_timeout(2000)
        self.assertEqual(self.page.url, self.dashboard_page.url, "超时: 未成功跳转到仪表板页面")

    def test_add_new_user_success(self):
        """测试成功添加新用户"""
        self.login_as_admin()
        self.user_management_page.navigate()

        # 生成唯一用户名
        unique_username = f"newuser{int(time.time())}"

        # 创建新用户
        self.user_management_page.create_user(
            "新用户",
            unique_username,
            "newuser@example.com",
            "password123",
            "user",
            "active"
        )

        # 等待成功消息
        self.user_management_page.wait_for_success_message()

        # 验证用户已添加到列表中
        self.user_management_page.verify_user_in_list(unique_username)