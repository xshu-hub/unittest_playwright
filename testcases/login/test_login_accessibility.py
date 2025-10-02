from playwright.sync_api import expect

from core.base_test import BaseTest
from pages.login_page import LoginPage


class TestLoginAccessibility(BaseTest):
    """测试登录页面可访问性"""

    def setUp(self):
        """测试前置设置"""
        super().setUp()
        self.login_page = LoginPage(self.page)

    def test_login_accessibility(self):
        """测试登录页面可访问性"""
        self.login_page.navigate()

        # 验证表单标签
        username_field = self.page.locator(self.login_page.username_input)
        password_field = self.page.locator(self.login_page.password_input)

        # 检查placeholder属性
        expect(username_field).to_have_attribute("placeholder", "用户名")
        expect(password_field).to_have_attribute("placeholder", "密码")

        # 验证按钮可访问性
        login_button = self.page.locator(self.login_page.login_button)
        expect(login_button).to_have_attribute("type", "submit")
