import time
from playwright.sync_api import expect

from core.base_test import BaseTest
from pages.login_page import LoginPage
from pages.dashboard_page import DashboardPage
from pages.approval_pages import ApprovalCreatePage, ApprovalListPage, ApprovalDetailPage


class TestApprovalRejectionWorkflow(BaseTest):
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

    def login_as_admin(self, username: str = "admin", password: str = "admin123"):
        """管理员登录"""
        try:
            # 确保页面已经完全加载
            self.page.wait_for_load_state('networkidle')
            self.page.wait_for_timeout(1000)  # 额外等待确保页面元素加载完成

            # 等待登录表单加载
            try:
                self.page.wait_for_selector("#username", timeout=15000)
            except Exception as e:
                print(f"等待用户名输入框超时，当前页面URL: {self.page.url}")
                print(f"页面HTML内容: {self.page.content()[:500]}...")  # 记录前500字符
                raise e

            # 填写登录表单
            self.page.fill("#username", username)
            self.page.fill("#password", password)
            self.page.click("button[type='submit']")

            # 等待页面跳转，增加错误处理
            try:
                self.page.wait_for_url("**/dashboard.html", timeout=15000)
            except Exception as e:
                print(f"管理员登录后页面跳转超时，当前URL: {self.page.url}")
                # 检查是否有错误消息
                if self.page.is_visible(".error-message"):
                    error_msg = self.page.text_content(".error-message")
                    print(f"登录错误消息: {error_msg}")
                raise e

            expect(self.page).to_have_url(self.dashboard_page.url)
        except Exception as e:
            print(f"管理员登录失败: {str(e)}")
            print(f"当前页面URL: {self.page.url}")
            print(f"页面标题: {self.page.title()}")
            raise e

    def test_approval_rejection_workflow(self):
        """测试审批拒绝工作流程"""
        # 普通用户创建申请
        self.login_as_user()
        self.approval_create_page.navigate()

        approval_title = f"拒绝测试申请 - {int(time.time())}"
        self.approval_create_page.create_approval(
            approval_title,
            "expense",
            "low",
            "测试拒绝流程的申请"
        )
        # 增加超时时间并添加错误处理
        try:
            self.approval_create_page.wait_for_success_message(timeout=10000)
        except Exception as e:
            print(f"创建申请时出现错误，当前页面URL: {self.page.url}")
            raise e

        # 切换到管理员账号处理申请
        # 只清除用户会话，保留申请数据
        self.page.evaluate("() => { localStorage.removeItem('currentUser'); localStorage.removeItem('loginTime'); }")
        self.page.goto(self.login_page.url, wait_until="networkidle")
        self.page.wait_for_timeout(1000)
        self.login_as_admin()

        self.approval_list_page.navigate()

        # 查找并处理申请
        for i in range(self.approval_list_page.get_approval_count()):
            approval_info = self.approval_list_page.get_approval_info(i)
            if approval_title in approval_info["title"]:
                self.approval_list_page.click_view_approval(i)
                break

        # 拒绝申请
        self.approval_detail_page.reject_with_comment("申请不符合要求，已拒绝。")
        self.approval_detail_page.wait_for_approval_processed()

        # 验证申请状态已更新
        status = self.approval_detail_page.get_approval_status()
        print(f"拒绝申请状态: {status}")
        assert "已拒绝" in status or "rejected" in status.lower() or "reject" in status.lower()