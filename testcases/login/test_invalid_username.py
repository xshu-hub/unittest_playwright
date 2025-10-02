from playwright.sync_api import expect

from core.base_test import BaseTest
from pages.login_page import LoginPage


class TestInvalidUsername(BaseTest):
    """测试无效用户名登录"""
    def setUp(self):
        """测试前置设置"""
        super().setUp()
        self.login_page = LoginPage(self.page)

    def test_invalid_username(self):
        """测试无效用户名登录"""
        self.login_page.navigate()

        # 使用无效用户名
        self.login_page.login("invalid_user", "password123")

        # 验证错误消息显示
        self.login_page.wait_for_login_error()
        error_message = self.login_page.get_error_message()
        self.assertIn("用户名不存在", error_message)

        # 验证仍在登录页面
        expect(self.page).to_have_url(self.login_page.url)
