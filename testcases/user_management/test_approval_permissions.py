import time
from playwright.sync_api import expect

from core.base_test import BaseTest
from pages.login_page import LoginPage
from pages.dashboard_page import DashboardPage
from pages.approval_pages import ApprovalCreatePage, ApprovalListPage, ApprovalDetailPage


class TestApprovalPermissions(BaseTest):
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

    def test_approval_permissions(self):
        """测试审批权限控制"""
        # 普通用户登录
        self.login_as_user()

        # 创建申请
        self.approval_create_page.navigate()
        approval_title = f"权限测试申请 - {int(time.time())}"
        self.approval_create_page.create_approval(
            approval_title,
            "leave",
            "medium",
            "测试权限控制的申请"
        )
        # 增加超时时间并添加错误处理
        try:
            self.approval_create_page.wait_for_success_message(timeout=10000)
        except Exception as e:
            print(f"创建申请时出现错误，当前页面URL: {self.page.url}")
            raise e

        # 查看自己的申请详情
        self.approval_list_page.navigate()
        if self.approval_list_page.get_approval_count() > 0:
            self.approval_list_page.click_view_approval(0)

            # 普通用户不应该看到审批操作按钮
            has_approval_actions = self.approval_detail_page.is_approval_actions_visible()
            # 根据业务逻辑，普通用户可能看不到审批按钮，或者只能看到自己的申请
            self.assertFalse(has_approval_actions, "普通用户看到了审批操作按钮")
