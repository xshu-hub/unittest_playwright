from playwright.sync_api import expect

from core.base_test import BaseTest
from pages.login_page import LoginPage
from pages.dashboard_page import DashboardPage
from pages.approval_pages import ApprovalCreatePage, ApprovalListPage, ApprovalDetailPage


class TestApprovalCreatePageElements(BaseTest):
    def setUp(self):
        """测试前置设置：初始化页面对象"""
        self.login_page = LoginPage(self.page)
        self.dashboard_page = DashboardPage(self.page)
        self.approval_create_page = ApprovalCreatePage(self.page)

    def login_as_user(self, username: str = "user1", password: str = "user123"):
        """以普通用户身份登录"""
        self.login_page.navigate()
        self.login_page.login(username, password)
        expect(self.page).to_have_url(self.dashboard_page.url)

    def test_approval_create_page_elements(self):
        """测试审批创建页面元素"""
        self.login_as_user()
        self.approval_create_page.navigate()

        # 验证页面标题
        expect(self.page).to_have_title(self.approval_create_page.title)

        # 验证表单元素
        self.approval_create_page.verify_form_elements()