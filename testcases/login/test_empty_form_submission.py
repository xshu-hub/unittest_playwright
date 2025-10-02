from playwright.sync_api import expect

from core.base_test import BaseTest
from pages.login_page import LoginPage


class TestEmptyFormSubmission(BaseTest):
    """测试空表单提交"""

    def setUp(self):
        """测试前置设置"""
        super().setUp()
        self.login_page = LoginPage(self.page)

    def test_empty_form_submission(self):
        """测试空表单提交"""
        self.login_page.navigate()

        # 点击登录按钮，不填写任何内容
        self.login_page.click_login_button()

        # 验证表单验证消息
        username_field = self.page.locator(self.login_page.username_input)
        expect(username_field).to_have_attribute("required", "")
        password_field = self.page.locator(self.login_page.password_input)
        expect(password_field).to_have_attribute("required", "")
