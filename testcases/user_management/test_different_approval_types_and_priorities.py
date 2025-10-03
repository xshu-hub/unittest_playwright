from parameterized import parameterized
from playwright.sync_api import expect

from core.base_test import BaseTest
from pages.login_page import LoginPage
from pages.dashboard_page import DashboardPage
from pages.approval_pages import ApprovalCreatePage, ApprovalListPage


class TestDifferentApprovalTypesAndPriorities(BaseTest):
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

    @parameterized.expand([
        ("leave", "high"),
        ("expense", "medium"),
        ("purchase", "low"),
        ("other", "high")
    ])
    def test_different_approval_types_and_priorities(self, approval_type: str, priority: str):
        """测试不同类型和优先级的审批申请"""
        self.login_as_user()
        self.approval_create_page.navigate()

        self.approval_create_page.create_approval(
            f"参数化测试 - {approval_type} - {priority}",
            approval_type,
            priority,
            f"测试 {approval_type} 类型，{priority} 优先级的申请"
        )

        # 验证创建成功
        self.approval_create_page.wait_for_success_message()

        # 验证在列表中显示
        self.approval_list_page.navigate()
        titles = self.approval_list_page.get_approval_titles()
        assert any(f"{approval_type} - {priority}" in title for title in titles)