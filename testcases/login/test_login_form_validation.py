from playwright.sync_api import expect

from core.base_test import BaseTest
from pages.login_page import LoginPage


class TestLoginFormValidation(BaseTest):
    """测试登录表单验证"""
    def setUp(self):
        """测试前置设置"""
        super().setUp()
        self.login_page = LoginPage(self.page)

    def test_login_form_validation(self):
        """测试登录表单验证"""
        self.login_page.navigate()

        # 测试用户名长度验证
        self.login_page.enter_username("a")  # 太短
        self.login_page.enter_password("password123")
        self.login_page.click_login_button()

        # 验证用户名最小长度要求
        username_field = self.page.locator(self.login_page.username_input)
        expect(username_field).to_have_attribute("minlength", "3")