from playwright.sync_api import Page, expect
from typing import List, Dict, Optional, Literal

from core.base_page import BasePage


class UserManagementPage(BasePage):
    """用户管理页面对象"""
    
    @property
    def url(self) -> str:
        return "http://localhost:8080/pages/user-management.html"
        
    @property
    def title(self) -> str:
        return "用户管理 - 测试系统"
        
    def __init__(self, page: Page):
        super().__init__(page)
        
        # 页面头部
        self.page_header = ".page-header"
        self.page_title = ".page-title"
        self.add_user_button = "#addUserBtn"
        self.refresh_button = "#refreshBtn"
        
        # 筛选器
        self.role_filter = "#roleFilter"
        self.status_filter = "#statusFilter"
        self.search_filter = "#searchFilter"
        
        # 用户列表
        self.users_container = ".users-container"
        self.users_table = "#usersTable"
        self.users_table_body = "#usersTableBody"
        self.users_count = "#usersCount"
        self.user_row = "#usersTableBody tr"
        
        # 用户信息
        self.user_avatar = ".user-avatar"
        self.user_name = ".user-name"
        self.user_username = ".user-username"
        self.user_email = "td:nth-child(2)"
        self.role_badge = ".role-badge"
        self.status_badge = ".status-badge"
        
        # 用户操作
        self.user_actions = ".user-actions"
        self.edit_user_button = ".btn-sm:has-text('编辑')"
        self.delete_user_button = ".btn-sm:has-text('删除')"
        self.toggle_status_button = ".btn-sm:has-text('禁用'), .btn-sm:has-text('启用')"
        
        # 模态框
        self.user_modal = "#userModal"
        self.modal_title = "#modalTitle"
        self.user_form = "#userForm"
        self.save_user_button = "#saveUserBtn"
        self.close_modal_button = ".close"
        
        # 表单字段
        self.username_input = "#username"
        self.name_input = "#name"
        self.email_input = "#email"
        self.password_input = "#password"
        self.role_select = "#role"
        self.status_select = "#status"
        self.form_message = "#userFormMessage"
        
        # 空状态
        self.empty_state = ".empty-state"
        
    def navigate(self, url: Optional[str] = None, wait_until: Literal["commit", "domcontentloaded", "load", "networkidle"] = "domcontentloaded") -> 'BasePage':
        """导航到用户管理页面"""
        return super().navigate(url, wait_until)
        
    def wait_for_page_load(self, timeout: Optional[int] = None) -> None:
        """等待页面加载完成"""
        super().wait_for_page_load(timeout)
        self.wait_for_element(self.page_header)
        self.wait_for_element(self.users_container)
        
    def click_add_user(self):
        """点击添加用户按钮"""
        self.click(self.add_user_button)
        self.wait_for_element(self.user_modal)
        
    def search_users(self, search_term: str):
        """搜索用户"""
        self.fill(self.search_filter, search_term)
        
    def filter_by_role(self, role: str):
        """按角色筛选"""
        self.select_option(self.role_filter, role)
        
    def filter_by_status(self, status: str):
        """按状态筛选"""
        self.select_option(self.status_filter, status)
        
    def click_refresh(self):
        """点击刷新按钮"""
        self.click(self.refresh_button)
        
    def get_user_count(self) -> int:
        """获取用户数量"""
        return self.page.locator(self.user_row).count()
        
    def get_user_names(self) -> List[str]:
        """获取所有用户姓名"""
        names = []
        rows = self.page.locator(self.user_row)
        for i in range(rows.count()):
            name = rows.nth(i).locator(self.user_name).text_content()
            names.append(name or "")
        return names
        
    def get_user_info(self, index: int = 0) -> Dict[str, Optional[str]]:
        """获取指定用户的信息"""
        rows = self.page.locator(self.user_row)
        if index >= rows.count():
            raise IndexError(f"用户索引 {index} 超出范围")
            
        row = rows.nth(index)
        return {
            "name": row.locator(self.user_name).text_content(),
            "username": row.locator(self.user_username).text_content(),
            "email": row.locator(self.user_email).text_content(),
            "role": row.locator(self.role_badge).text_content(),
            "status": row.locator(self.status_badge).text_content(),
            "last_login": row.locator("td:nth-child(6)").text_content()
        }
        
    def click_edit_user(self, index: int = 0):
        """点击编辑用户"""
        rows = self.page.locator(self.user_row)
        if index < rows.count():
            rows.nth(index).locator(self.edit_user_button).click()
            self.wait_for_element(self.user_modal)
        else:
            raise IndexError(f"用户索引 {index} 超出范围")
            
    def click_delete_user(self, index: int = 0):
        """点击删除用户"""
        rows = self.page.locator(self.user_row)
        if index < rows.count():
            rows.nth(index).locator(self.delete_user_button).click()
            self.page.locator("#deleteModal").wait_for(state="visible")
        else:
            raise IndexError(f"用户索引 {index} 超出范围")
            
    def click_toggle_user_status(self, index: int = 0):
        """点击切换用户状态"""
        rows = self.page.locator(self.user_row)
        if index < rows.count():
            rows.nth(index).locator(self.toggle_status_button).click()
        else:
            raise IndexError(f"用户索引 {index} 超出范围")
            
    def fill_user_form(self, name: str, username: str, email: str, password: str = "", role: str = "user", status: str = "active"):
        """填写用户表单"""
        self.fill(self.name_input, name)
        self.fill(self.username_input, username)
        self.fill(self.email_input, email)
        if password:
            self.fill(self.password_input, password)
        self.select_option(self.role_select, role)
        self.select_option(self.status_select, status)
        
    def click_save_user(self):
        """点击保存用户"""
        self.click(self.save_user_button)
        
    def click_cancel_user_form(self):
        """点击取消用户表单"""
        self.click(self.close_modal_button)
        
    def create_user(self, name: str, username: str, email: str, password: str, role: str = "user", status: str = "active"):
        """创建新用户"""
        self.click_add_user()
        self.fill_user_form(name, username, email, password, role, status)
        self.click_save_user()
        
    def edit_user(self, index: int, name: Optional[str] = None, username: Optional[str] = None, email: Optional[str] = None, password: Optional[str] = None, role: Optional[str] = None, status: Optional[str] = None):
        """编辑用户信息"""
        self.click_edit_user(index)
        
        if name is not None:
            self.fill(self.name_input, name)
        if username is not None:
            self.fill(self.username_input, username)
        if email is not None:
            self.fill(self.email_input, email)
        if password is not None:
            self.fill(self.password_input, password)
        if role is not None:
            self.select_option(self.role_select, role)
        if status is not None:
            self.select_option(self.status_select, status)
            
        self.click_save_user()
        
    def confirm_delete_user(self):
        """确认删除用户"""
        self.click(".btn-danger:has-text('确认删除')")
        
    def cancel_delete_user(self):
        """取消删除用户"""
        self.click(".btn-secondary:has-text('取消')")
        
    def delete_user(self, index: int):
        """删除用户"""
        self.click_delete_user(index)
        self.confirm_delete_user()
        
    def close_modal(self):
        """关闭模态框"""
        self.click(self.close_modal_button)
        
    def get_modal_title(self) -> Optional[str]:
        """获取模态框标题"""
        return self.page.locator(self.modal_title).text_content()
        
    def is_user_modal_visible(self) -> bool:
        """检查用户模态框是否可见"""
        return self.page.locator(self.user_modal).is_visible()
        
    def is_delete_modal_visible(self) -> bool:
        """检查删除确认模态框是否可见"""
        return self.page.locator("#deleteModal").is_visible()
        
    def is_empty_state_visible(self) -> bool:
        """检查是否显示空状态"""
        return self.page.locator(self.empty_state).is_visible()
        
    def get_success_message(self) -> Optional[str]:
        """获取成功消息"""
        return self.page.locator(".alert-success").text_content()
        
    def get_error_message(self) -> Optional[str]:
        """获取错误消息"""
        return self.page.locator(".alert-error").text_content()
        
    def wait_for_success_message(self, timeout: int = 5000):
        """等待成功消息显示"""
        self.page.locator(".alert-success").wait_for(state="visible", timeout=timeout)
        
    def wait_for_error_message(self, timeout: int = 3000):
        """等待错误消息显示"""
        self.page.locator(".alert-error").wait_for(state="visible", timeout=timeout)
        
    def wait_for_user_update(self, timeout: int = 5000):
        """等待用户信息更新"""
        self.page.wait_for_timeout(timeout)  # 等待状态更新
        
    def get_form_values(self) -> Dict[str, str]:
        """获取表单当前值"""
        return {
            "name": self.page.locator(self.name_input).input_value() or "",
            "username": self.page.locator(self.username_input).input_value() or "",
            "email": self.page.locator(self.email_input).input_value() or "",
            "role": self.page.locator(self.role_select).input_value() or "",
            "status": self.page.locator(self.status_select).input_value() or ""
        }
        
    def verify_page_elements(self):
        """验证页面元素"""
        expect(self.page.locator(self.page_header)).to_be_visible()
        expect(self.page.locator(self.add_user_button)).to_be_visible()
        expect(self.page.locator(self.search_filter)).to_be_visible()
        expect(self.page.locator(self.role_filter)).to_be_visible()
        expect(self.page.locator(self.status_filter)).to_be_visible()
        expect(self.page.locator(self.refresh_button)).to_be_visible()
        expect(self.page.locator(self.users_container)).to_be_visible()
        
    def verify_user_form_elements(self):
        """验证用户表单元素"""
        expect(self.page.locator(self.name_input)).to_be_visible()
        expect(self.page.locator(self.username_input)).to_be_visible()
        expect(self.page.locator(self.email_input)).to_be_visible()
        expect(self.page.locator(self.password_input)).to_be_visible()
        expect(self.page.locator(self.role_select)).to_be_visible()
        expect(self.page.locator(self.status_select)).to_be_visible()
        expect(self.page.locator(self.save_user_button)).to_be_visible()
        expect(self.page.locator(self.close_modal_button)).to_be_visible()
        
    def verify_user_in_list(self, username: str) -> bool:
        """验证用户是否在列表中"""
        usernames = []
        rows = self.page.locator(self.user_row)
        for i in range(rows.count()):
            user_username = rows.nth(i).locator(self.user_username).text_content()
            # 移除@符号
            if user_username and user_username.startswith('@'):
                user_username = user_username[1:]
            usernames.append(user_username)
        return username in usernames
        
    def find_user_index_by_username(self, username: str) -> int:
        """根据用户名查找用户索引"""
        rows = self.page.locator(self.user_row)
        for i in range(rows.count()):
            user_username = rows.nth(i).locator(self.user_username).text_content()
            # 移除@符号
            if user_username and user_username.startswith('@'):
                user_username = user_username[1:]
            if user_username == username:
                return i
        return -1