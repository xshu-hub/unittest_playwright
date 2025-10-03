from playwright.sync_api import expect

from core.base_test import BaseTest
from pages.login_page import LoginPage
from pages.dashboard_page import DashboardPage
from pages.approval_pages import ApprovalCreatePage, ApprovalListPage, ApprovalDetailPage


class TestApprovalDetailPageElements(BaseTest):
    def setUp(self):
        """测试前置设置：初始化页面对象"""
        super().setUp()
        self.login_page = LoginPage(self.page)
        self.dashboard_page = DashboardPage(self.page)
        self.approval_create_page = ApprovalCreatePage(self.page)
        self.approval_list_page = ApprovalListPage(self.page)
        self.approval_detail_page = ApprovalDetailPage(self.page)

    def login_as_user(self, username: str = "user1", password: str = "user123"):
        """以普通用户身份登录"""
        self.login_page.navigate()
        self.login_page.login(username, password)
        expect(self.page).to_have_url(self.dashboard_page.url)

    def test_approval_detail_page_elements(self):
        """测试审批详情页面元素"""
        self.login_as_user()

        # 创建测试申请
        self.approval_create_page.navigate()
        self.approval_create_page.create_approval("详情测试申请", "leave", "medium", "用于测试详情页面的申请")
        self.approval_create_page.wait_for_success_message()

        # 访问列表页面并查看详情
        self.approval_list_page.navigate()
        if self.approval_list_page.get_approval_count() > 0:
            self.approval_list_page.click_view_approval(0)

            # 验证详情页面元素
            self.approval_detail_page.verify_detail_elements()