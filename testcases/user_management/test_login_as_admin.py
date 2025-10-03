from playwright.sync_api import expect

from core.base_test import BaseTest
from pages.login_page import LoginPage
from pages.dashboard_page import DashboardPage
from pages.user_management_page import UserManagementPage


class TestLoginAsAdmin(BaseTest):
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

    def test_add_duplicate_username(self):
        """测试添加重复用户名"""
        self.login_as_admin()
        self.user_management_page.navigate()

        # 尝试创建与admin相同用户名的用户
        self.user_management_page.create_user(
            "重复管理员",
            "admin",  # 使用已存在的admin用户名
            "duplicate@example.com",
            "password123",
            "user",
            "active"
        )

        # 验证错误消息 - 先等待一下让错误消息显示
        self.page.wait_for_timeout(2000)

        # 检查是否有错误消息显示
        error_selectors = [
            ".alert.alert-error",
            ".error-message",
            "[class*='error']",
            "#userFormMessage .error-message"
        ]

        error_found = False
        for selector in error_selectors:
            try:
                if self.page.locator(selector).is_visible():
                    error_text = self.page.locator(selector).text_content()
                    print(f"找到错误消息: {error_text}")
                    error_found = True
                    break
            except:
                continue

        if not error_found:
            # 如果没找到错误消息，截图并打印页面内容
            self.page.screenshot(path="debug_error_message.png")
            print(f"页面HTML: {self.page.content()[-1000:]}")  # 记录最后1000个字符

        self.assertTrue(error_found, "应该显示重复用户名的错误消息")

