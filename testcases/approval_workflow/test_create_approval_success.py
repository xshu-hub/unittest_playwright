from playwright.sync_api import expect

from core.base_test import BaseTest
from pages.login_page import LoginPage
from pages.dashboard_page import DashboardPage
from pages.approval_pages import ApprovalCreatePage

# 初始化日志系统（幂等）
from utils.logger import get_logger

logger = get_logger(__name__)
class TestCreateApprovalSuccess(BaseTest):
    def setUp(self):
        """测试前置设置：初始化页面对象"""
        super().setUp()
        self.login_page = LoginPage(self.page)
        self.dashboard_page = DashboardPage(self.page)
        self.approval_create_page = ApprovalCreatePage(self.page)

    def login_as_user(self, username: str = "user1", password: str = "user123"):
        """以普通用户身份登录"""
        self.login_page.navigate()
        self.login_page.login(username, password)
        expect(self.page).to_have_url(self.dashboard_page.url)

    def test_create_approval_success(self):
        """测试成功创建审批申请"""
        self.login_as_user()
        self.approval_create_page.navigate()

        # 创建审批申请
        approval_data = {
            "title": "测试申请 - 请假申请",
            "type": "leave",
            "priority": "medium",
            "description": "因个人事务需要请假3天，请批准。"
        }

        self.approval_create_page.create_approval(
            approval_data["title"],
            approval_data["type"],
            approval_data["priority"],
            approval_data["description"]
        )

        # 验证成功消息
        try:
            # 先尝试等待成功消息（较短时间）
            self.approval_create_page.wait_for_success_message(timeout=3000)
        except Exception:
            # 如果没有找到成功消息，检查是否已跳转到列表页面
            if "approval-list.html" in self.page.url:
                logger.info("申请创建成功，页面已自动跳转到列表页面")
            elif self.approval_create_page.is_visible(".error-message"):
                error_msg = self.approval_create_page.get_error_message()
                raise Exception(f"创建申请失败: {error_msg}")
            else:
                logger.error(f"当前页面URL: {self.page.url}")
                raise Exception("申请创建状态未知")

        success_message = self.approval_create_page.get_success_message()
        self.assertIn("申请提交成功", success_message,"申请提交成功消息未显示")
