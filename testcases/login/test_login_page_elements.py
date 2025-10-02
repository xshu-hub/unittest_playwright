from playwright.sync_api import expect

from core.base_test import BaseTest
from pages.login_page import LoginPage


class TestLoginPageElements(BaseTest):
    """登录页面元素测试类"""

    def setUp(self):
        """测试前置设置"""
        super().setUp()
        self.login_page = LoginPage(self.page)

    def test_login_page_elements(self):
        """测试登录页面元素显示"""
        self.login_page.navigate()

        # 验证页面标题
        expect(self.page).to_have_title("用户登录 - 测试系统")

        # 验证登录页面元素
        self.login_page.verify_login_page_elements()


