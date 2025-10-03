from playwright.sync_api import expect

from core.base_test import BaseTest
from pages.login_page import LoginPage
from pages.dashboard_page import DashboardPage
from pages.approval_pages import ApprovalCreatePage, ApprovalListPage, ApprovalDetailPage


class TestCreateApprovalValidation(BaseTest):
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

    def test_create_approval_validation(self):
        """测试审批申请表单验证"""
        self.login_as_user()
        self.approval_create_page.navigate()

        # 测试空标题提交
        self.approval_create_page.select_type("leave")
        self.approval_create_page.select_priority("high")
        self.approval_create_page.fill_description("测试描述")
        self.approval_create_page.click_submit()

        # 验证标题字段必填
        title_field = self.page.locator(self.approval_create_page.title_input)
        expect(title_field).to_have_attribute("required", "")