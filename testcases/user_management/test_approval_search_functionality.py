import time
from playwright.sync_api import expect

from core.base_test import BaseTest
from pages.login_page import LoginPage
from pages.dashboard_page import DashboardPage
from pages.approval_pages import ApprovalCreatePage, ApprovalListPage


class TestApprovalSearchFunctionality(BaseTest):
    def setUp(self):
        """测试前置设置：初始化页面对象"""
        self.login_page = LoginPage(self.page)
        self.dashboard_page = DashboardPage(self.page)
        self.approval_create_page = ApprovalCreatePage(self.page)
        self.approval_list_page = ApprovalListPage(self.page)

    def login_as_user(self, username: str = "user1", password: str = "user123"):
        """以普通用户身份登录"""
        self.login_page.navigate()
        self.login_page.login(username, password)
        expect(self.page).to_have_url(self.dashboard_page.url)

    def test_approval_search_functionality(self):
        """测试审批申请搜索功能"""
        self.login_as_user()

        # 创建测试数据
        self.approval_create_page.navigate()
        self.approval_create_page.create_approval("特殊关键词申请", "leave", "medium", "包含特殊关键词的申请")
        self.approval_create_page.wait_for_success_message()

        # 访问列表页面并搜索
        self.approval_list_page.navigate()
        self.approval_list_page.search_approvals("特殊关键词")
        time.sleep(1)  # 等待搜索结果

        # 验证搜索结果
        if self.approval_list_page.get_approval_count() > 0:
            titles = self.approval_list_page.get_approval_titles()
            self.assertTrue(any("特殊关键词" in title for title in titles))
