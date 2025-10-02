from playwright.sync_api import expect

from core.base_test import BaseTest
from pages.login_page import LoginPage


class TestInvalidPassword(BaseTest):
    """测试无效密码登录"""
    def setUp(self):
        """测试前置设置"""
        super().setUp()
        self.login_page = LoginPage(self.page)

    def test_invalid_password(self):
        """测试无效密码登录"""
        self.login_page.navigate()

        # 使用正确用户名但错误密码
        self.login_page.login("admin", "wrong_password")

        # 验证错误消息显示
        self.login_page.wait_for_login_error()
        error_message = self.login_page.get_error_message()
        self.assertIn("密码错误", error_message)

        # 验证仍在登录页面
        expect(self.page).to_have_url(self.login_page.url)
