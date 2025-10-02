from playwright.sync_api import expect

from core.base_test import BaseTest
from pages.login_page import LoginPage
from pages.dashboard_page import DashboardPage
from pages.approval_pages import ApprovalCreatePage, ApprovalListPage


class TestApprovalListPagination(BaseTest):
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

    def test_approval_list_pagination(self):
        """测试审批列表分页功能"""
        self.login_as_user()

        # 创建多个申请以测试分页
        for i in range(5):
            self.approval_create_page.navigate()
            self.approval_create_page.create_approval(
                f"分页测试申请 {i + 1}",
                "other",
                "low",
                f"第 {i + 1} 个测试申请"
            )
            self.approval_create_page.wait_for_success_message()

        # 访问列表页面
        self.approval_list_page.navigate()

        # 验证申请数量
        approval_count = self.approval_list_page.get_approval_count()
        assert approval_count >= 5
        # 可补充分页控件验证（如：断言分页按钮可见、切换页码功能等，需结合实际页面逻辑调整）
