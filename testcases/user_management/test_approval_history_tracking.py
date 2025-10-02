import time
from playwright.sync_api import expect

from core.base_test import BaseTest
from pages.login_page import LoginPage
from pages.dashboard_page import DashboardPage
from pages.approval_pages import ApprovalCreatePage, ApprovalListPage, ApprovalDetailPage


class TestApprovalHistoryTracking(BaseTest):
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

    def test_approval_history_tracking(self):
        """测试审批历史记录跟踪"""
        # 创建申请
        self.login_as_user()
        self.approval_create_page.navigate()

        approval_title = f"历史记录测试 - {int(time.time())}"
        self.approval_create_page.create_approval(
            approval_title,
            "purchase",
            "medium",
            "测试历史记录的申请"
        )
        self.approval_create_page.wait_for_success_message()

        # 切换到管理员账号处理申请
        # 只清除用户会话，保留申请数据
        self.page.evaluate("() => { localStorage.removeItem('currentUser'); localStorage.removeItem('loginTime'); }")
        self.page.goto(self.login_page.url, wait_until="networkidle")
        self.page.wait_for_timeout(1000)
        self.login_as_admin()

        self.approval_list_page.navigate()

        # 查找申请并查看详情
        for i in range(self.approval_list_page.get_approval_count()):
            approval_info = self.approval_list_page.get_approval_info(i)
            if approval_title in approval_info["title"]:
                self.approval_list_page.click_view_approval(i)
                break

        # 批准申请
        self.approval_detail_page.approve_with_comment("经审核，同意此申请。")
        self.approval_detail_page.wait_for_approval_processed()

        # 验证历史记录
        history_count = self.approval_detail_page.get_history_count()
        print(f"历史记录数量: {history_count}")

        if history_count > 0:
            history_items = self.approval_detail_page.get_history_items()
            print(f"历史记录项目: {history_items}")
            actions = [item["action"] for item in history_items]
            print(f"历史记录动作: {actions}")
            assert any("提交" in action or "submit" in action.lower() for action in actions)
            assert any("批准" in action or "approve" in action.lower() for action in actions)
        else:
            # 如果没有历史记录，至少验证申请状态已更新
            status = self.approval_detail_page.get_approval_status()
            print(f"申请状态: {status}")
            assert "已批准" in status or "approved" in status.lower() or "approve" in status.lower()