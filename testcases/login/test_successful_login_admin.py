from playwright.sync_api import expect

from core.base_test import BaseTest
from pages.dashboard_page import DashboardPage
from pages.login_page import LoginPage


class TestSuccessfulLoginAdmin(BaseTest):
    """测试管理员成功登录"""

    def setUp(self):
        """测试前置设置"""
        self.login_page = LoginPage(self.page)
        self.dashboard_page = DashboardPage(self.page)

    def test_successful_login_admin(self):
        """测试管理员账号成功登录"""
        self.login_page.navigate()

        # 使用管理员账号登录
        self.login_page.login("admin", "admin123")

        # 等待登录成功消息出现（动态创建的alert元素）
        self.page.wait_for_selector(".alert.alert-success", timeout=5000)

        # 验证跳转到仪表板（等待跳转完成）
        expect(self.page).to_have_url("http://localhost:8080/pages/dashboard.html", timeout=15000)

        # 验证仪表板页面加载
        self.dashboard_page.wait_for_dashboard_page_load()

        # 验证用户信息显示
        user_info = self.dashboard_page.get_user_info()
        assert user_info["username"] == "管理员"  # 页面显示的是name字段，不是username
        assert user_info["role"] == "管理员"
