import time
from playwright.sync_api import expect

from core.base_test import BaseTest
from pages.login_page import LoginPage
from pages.dashboard_page import DashboardPage
from pages.approval_pages import ApprovalCreatePage, ApprovalListPage, ApprovalDetailPage


class TestApprovalStatusUpdates(BaseTest):
    def setUp(self):
        """测试前置设置：初始化页面对象"""
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

    def test_approval_status_updates(self):
        """测试审批状态更新"""
        # 创建申请
        self.login_as_user()
        self.approval_create_page.navigate()

        approval_title = f"状态更新测试 - {int(time.time())}"
        self.approval_create_page.create_approval(
            approval_title,
            "leave",
            "high",
            "测试状态更新的申请"
        )
        self.approval_create_page.wait_for_success_message()

        # 检查初始状态
        self.approval_list_page.navigate()
        initial_info = self.approval_list_page.get_approval_info(0)
        initial_status = initial_info["status"]
        assert "待审批" in initial_status or "pending" in initial_status.lower()

        # 切换到管理员账号处理申请
        # 只清除用户会话，保留申请数据
        self.page.evaluate("() => { localStorage.removeItem('currentUser'); localStorage.removeItem('loginTime'); }")
        self.page.goto(self.login_page.url, wait_until="networkidle")
        self.page.wait_for_timeout(1000)
        self.login_as_admin()

        self.approval_list_page.navigate()
        self.approval_list_page.click_view_approval(0)
        self.approval_detail_page.approve_with_comment("状态更新测试通过")
        self.approval_detail_page.wait_for_approval_processed()

        # 返回列表检查状态更新
        self.approval_detail_page.click_back()
        self.approval_list_page.wait_for_approval_update()

        updated_info = self.approval_list_page.get_approval_info(0)
        updated_status = updated_info["status"]
        print(f"更新后申请状态: {updated_status}")
        assert "已批准" in updated_status or "approved" in updated_status.lower() or "approve" in updated_status.lower()