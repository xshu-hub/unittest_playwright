from core.base_test import BaseTest
from pages.login_page import LoginPage


class TestLoginResponsiveDesign(BaseTest):
    """测试登录页面响应式设计"""

    def setUp(self):
        """测试前置设置"""
        super().setUp()
        self.login_page = LoginPage(self.page)

    def test_login_responsive_design(self):
        """测试登录页面响应式设计"""
        self.login_page.navigate()

        # 测试桌面视图
        self.login_page.verify_responsive_design(1920, 1080)

        # 测试平板视图
        self.login_page.verify_responsive_design(768, 1024)

        # 测试手机视图
        self.login_page.verify_responsive_design(375, 667)
