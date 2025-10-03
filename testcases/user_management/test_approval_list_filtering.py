import time
from playwright.sync_api import expect

from core.base_test import BaseTest
from pages.login_page import LoginPage
from pages.dashboard_page import DashboardPage
from pages.approval_pages import ApprovalCreatePage, ApprovalListPage


class TestApprovalListFiltering(BaseTest):
    def setUp(self):
        """测试前置设置：初始化页面对象"""
        super().setUp()
        self.login_page = LoginPage(self.page)
        self.dashboard_page = DashboardPage(self.page)
        self.approval_create_page = ApprovalCreatePage(self.page)
        self.approval_list_page = ApprovalListPage(self.page)

    def login_as_user(self, username: str = "user1", password: str = "user123"):
        """以普通用户身份登录"""
        self.login_page.navigate()
        self.login_page.login(username, password)
        expect(self.page).to_have_url(self.dashboard_page.url)

    def test_approval_list_filtering(self):
        """测试审批列表筛选功能"""
        self.login_as_user()

        # 先创建一些测试数据
        self.approval_create_page.navigate()
        self.approval_create_page.create_approval("高优先级申请", "leave", "high", "紧急请假")
        self.approval_create_page.wait_for_success_message()

        # 访问列表页面
        self.approval_list_page.navigate()

        # 测试按优先级筛选
        self.approval_list_page.filter_by_priority("high")
        time.sleep(1)  # 等待筛选结果

        # 验证筛选结果
        if self.approval_list_page.get_approval_count() > 0:
            titles = self.approval_list_page.get_approval_titles()
            self.assertTrue(any("高优先级" in title for title in titles))
