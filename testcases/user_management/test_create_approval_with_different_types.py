from playwright.sync_api import expect

from core.base_test import BaseTest
from pages.login_page import LoginPage
from pages.dashboard_page import DashboardPage
from pages.approval_pages import ApprovalCreatePage


class TestCreateApprovalWithDifferentTypes(BaseTest):
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

    def test_create_approval_with_different_types(self):
        """测试创建不同类型的审批申请"""
        self.login_as_user()

        approval_types = [
            {"type": "leave", "title": "请假申请", "description": "个人事务请假"},
            {"type": "expense", "title": "报销申请", "description": "差旅费报销"},
            {"type": "purchase", "title": "采购申请", "description": "办公用品采购"},
            {"type": "other", "title": "其他申请", "description": "其他事务申请"}
        ]

        for i, approval in enumerate(approval_types):
            self.approval_create_page.navigate()

            self.approval_create_page.create_approval(
                f"{approval['title']} - {i + 1}",
                approval["type"],
                "medium",
                approval["description"]
            )

            # 验证创建成功
            self.approval_create_page.wait_for_success_message()