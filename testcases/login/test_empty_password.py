from playwright.sync_api import expect

from core.base_test import BaseTest
from pages.login_page import LoginPage


class TestEmptyPassword(BaseTest):
    """测试空密码登录"""
    def setUp(self):
        """测试前置设置"""
        super().setUp()
        self.login_page = LoginPage(self.page)
    def test_empty_password(self):
        """测试空密码登录"""
        self.login_page.navigate()

        # 只填写用户名，密码为空
        self.login_page.enter_username("admin")
        self.login_page.click_login_button()

        # 验证表单验证消息
        password_field = self.page.locator(self.login_page.password_input)
        expect(password_field).to_have_attribute("required", "")
