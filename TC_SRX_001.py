import time
from cmbird.case import cmbird
from cmbird.enhance import information
from core.base_test import BaseTest
from pages.login_page import LoginPage
from pages.dashboard_page import DashboardPage


class TC_SRX_001(cmbird, BaseTest):
    @information(
        CaseID="TC_SRX_001",
        CaseName="SRX 示例用例 001",
        Level="0",
        Description="测试用例001"
    )
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    # 测试用例的前置条件
    def prepare(self):
        """
        测试用例的前置条件，供子类重写
        :return:
        """
        # 使用 BaseTest 已初始化的浏览器与页面
        self.logger.info("准备阶段：初始化测试页面")
        self.login_page = LoginPage(self.page)
        self.dashboard_page = DashboardPage(self.page)
    
    # 测试用例的主要业务流程
    def process(self):
        """
        测试用例的主要业务流程，供子类重写
        :return:
        """
        self.logger.info("执行登录流程并验证仪表盘元素")
        self.login_page.navigate()
        self.login_page.verify_login_page_elements()
        self.login_page.login_with_demo_user()
        self.login_page.wait_for_login_success(timeout=5000)

        self.dashboard_page.wait_for_dashboard_page_load()
        # 断言：用户信息可见
        username = self.dashboard_page.get_user_name()
        self.logger.info(f"当前用户：{username}")
        self.assertTrue(len(username) > 0, "登录后用户名应显示")

    # 测试用例的后置条件
    def postlude(self):
        """
        测试用例的后置条件，供子类重写
        :return:
        """
        self.logger.info("后置阶段：登出并返回登录页")
        self.dashboard_page.logout()
        # 确认返回登录页
        self.login_page.wait_for_login_page_load()
    
    # 测试用例的失败处理
    def failure(self):
        """
        测试用例的失败处理，供子类重写
        :return:
        """
        # BaseTest 的 tearDown 会处理截图与视频，这里补充日志
        self.logger.error("用例失败，已触发截图与视频处理")
    
    # 测试用例的恢复处理
    def restore(self):
        """
        测试用例的恢复处理，供子类重写
        :return:
        """
        # 恢复阶段可加入必要的清理；BaseTest 已清除存储与 Cookies
        self.logger.info("恢复阶段：完成环境清理")
