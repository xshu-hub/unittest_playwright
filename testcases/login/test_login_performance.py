from playwright.sync_api import expect

from core.base_test import BaseTest
from pages.dashboard_page import DashboardPage
from pages.login_page import LoginPage


class TestLoginPerformance(BaseTest):
    """测试登录性能"""

    def setUp(self):
        """测试前置设置"""
        super().setUp()
        self.login_page = LoginPage(self.page)
        self.dashboard_page = DashboardPage(self.page)

    def test_login_performance(self):
        """测试登录性能"""
        self.login_page.navigate()

        # 记录登录开始时间
        import time
        start_time = time.time()

        # 执行登录
        self.login_page.login("admin", "admin123")

        # 等待页面跳转完成
        expect(self.page).to_have_url(self.dashboard_page.url)
        self.dashboard_page.wait_for_dashboard_page_load()

        # 计算登录耗时
        end_time = time.time()
        login_duration = end_time - start_time

        # 验证登录时间在合理范围内（小于5秒）
        self.assertLess(login_duration, 5.0, f"登录耗时过长: {login_duration}秒")
