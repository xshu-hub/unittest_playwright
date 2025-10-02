from playwright.sync_api import expect

from core.base_test import BaseTest
from pages.login_page import LoginPage


class TestEmptyUsername(BaseTest):
    """测试空用户名登录"""

    def setUp(self):
        """测试前置设置"""
        super().setUp()
        self.login_page = LoginPage(self.page)

    def test_empty_username(self):
        """测试空用户名登录"""
        self.login_page.navigate()

        # 只填写密码，用户名为空
        self.login_page.enter_password("admin123")
        self.login_page.click_login_button()

        # 验证表单验证消息
        username_field = self.page.locator(self.login_page.username_input)
        expect(username_field).to_have_attribute("required", "")
