import time

from playwright.sync_api import expect

from core.base_test import BaseTest
from pages.login_page import LoginPage
from pages.dashboard_page import DashboardPage
from pages.approval_pages import ApprovalCreatePage, ApprovalListPage, ApprovalDetailPage


class TestApprovalWorkflowCompleteCycle(BaseTest):
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

    def test_approval_workflow_complete_cycle(self):
        """测试完整的审批工作流程"""
        # 第一步：普通用户创建申请
        self.login_as_user()
        self.approval_create_page.navigate()

        approval_title = f"完整流程测试申请 - {int(time.time())}"
        self.approval_create_page.create_approval(
            approval_title,
            "leave",
            "high",
            "测试完整审批流程的申请"
        )
        # 等待成功消息或页面跳转
        try:
            # 先尝试等待成功消息（较短时间）
            self.approval_create_page.wait_for_success_message(timeout=3000)
        except Exception:
            # 如果没有找到成功消息，检查是否已跳转到列表页面
            if "approval-list.html" in self.page.url:
                print("申请创建成功，页面已自动跳转到列表页面")
            elif self.approval_create_page.is_visible(".error-message"):
                error_msg = self.approval_create_page.get_error_message()
                raise Exception(f"创建申请失败: {error_msg}")
            else:
                print(f"当前页面URL: {self.page.url}")
                raise Exception("申请创建状态未知")

        # 第二步：查看申请列表，确认申请已创建
        # 如果页面还没有跳转到列表页面，则手动导航
        if "approval-list.html" not in self.page.url:
            self.approval_list_page.navigate()
        else:
            # 页面已经在列表页面，等待加载完成
            self.approval_list_page.wait_for_page_load()

        titles = self.approval_list_page.get_approval_titles()
        assert any(approval_title in title for title in titles)

        # 第三步：切换到管理员账号处理申请
        # 只清除用户会话，保留申请数据
        self.page.evaluate("() => { localStorage.removeItem('currentUser'); localStorage.removeItem('loginTime'); }")
        self.page.goto(self.login_page.url, wait_until="networkidle")
        self.page.wait_for_timeout(1000)  # 等待页面稳定
        print(f"导航后页面URL: {self.page.url}")
        print(f"导航后页面标题: {self.page.title()}")
        self.login_as_admin()

        # 访问审批列表
        self.approval_list_page.navigate()

        # 调试：打印审批列表信息
        approval_count = self.approval_list_page.get_approval_count()
        print(f"审批列表中共有 {approval_count} 个申请")
        print(f"要查找的申请标题: {approval_title}")

        # 查找并查看申请详情
        approval_found = False
        for i in range(approval_count):
            approval_info = self.approval_list_page.get_approval_info(i)
            print(f"申请 {i}: {approval_info}")
            if approval_title in approval_info["title"]:
                self.approval_list_page.click_view_approval(i)
                approval_found = True
                break

        if not approval_found:
            print("未找到匹配的申请，可能的原因：")
            print("1. 数据没有持久化")
            print("2. 用户会话隔离")
            print("3. 申请标题不匹配")

        assert approval_found, "未找到创建的申请"

        # 第四步：管理员批准申请
        self.approval_detail_page.approve_with_comment("申请已批准，同意请假。")
        self.approval_detail_page.wait_for_approval_processed()

        # 验证申请状态已更新
        status = self.approval_detail_page.get_approval_status()
        print(f"申请状态: {status}")
        assert "已批准" in status or "approved" in status.lower() or "approve" in status.lower()

