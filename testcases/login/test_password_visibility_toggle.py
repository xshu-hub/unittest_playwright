from playwright.sync_api import expect

from core.base_test import BaseTest
from pages.login_page import LoginPage


class TestPasswordVisibilityToggle(BaseTest):
    """测试密码字段类型"""

    def setUp(self):
        """测试前置设置"""
        super().setUp()
        self.login_page = LoginPage(self.page)

    def test_password_visibility_toggle(self):
        """测试密码字段类型"""
        self.login_page.navigate()

        # 填写密码
        self.login_page.enter_password("test123")

        # 验证密码字段类型为password（隐藏输入）
        password_field = self.page.locator(self.login_page.password_input)
        expect(password_field).to_have_attribute("type", "password")
