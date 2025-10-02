from playwright.sync_api import Page, expect
from typing import List, Dict

from core.base_page import BasePage


class ApprovalCreatePage(BasePage):
    """审批申请创建页面对象类"""
    
    @property
    def url(self) -> str:
        """页面URL"""
        return "http://localhost:8080/pages/approval-create.html"
    
    @property
    def title(self) -> str:
        """页面标题"""
        return "提交申请 - 测试系统"
    
    def __init__(self, page: Page):
        super().__init__(page)
        
        # 表单元素
        self.approval_form = "#approvalForm"
        self.title_input = "#title"
        self.type_select = "#type"
        self.priority_selector = ".priority-selector"
        self.description_textarea = "#description"
        self.submit_button = "button[type='submit']"
        self.cancel_button = "button[type='button']"
        
        # 消息提示
        self.success_message = ".success-message"
        self.error_message = ".error-message"
        
        # 页面导航
        self.breadcrumb = ".breadcrumb"
        self.back_to_dashboard = "a[href='dashboard.html']"
        
    def wait_for_approval_create_page_load(self):
        """等待审批创建页面加载完成"""
        self.wait_for_element(self.approval_form)
        self.wait_for_element(self.title_input)
        
    def fill_title(self, title: str):
        """填写申请标题"""
        self.fill(self.title_input, title)
        
    def select_type(self, type_value: str):
        """选择申请类型"""
        self.select_option(self.type_select, type_value)
        
    def select_priority(self, priority: str):
        """选择优先级"""
        # 点击对应的优先级选项
        priority_option = f".priority-option[data-priority='{priority}']"
        self.click(priority_option)
        
    def fill_description(self, description: str):
        """填写申请描述"""
        self.fill(self.description_textarea, description)
        
    def click_submit(self):
        """点击提交按钮"""
        self.click(self.submit_button)
        
    def click_cancel(self):
        """点击取消按钮"""
        self.click(self.cancel_button)
        
    def create_approval(self, title: str, type_value: str, priority: str, description: str):
        """创建完整的审批申请"""
        self.fill_title(title)
        self.select_type(type_value)
        self.select_priority(priority)
        self.fill_description(description)
        self.click_submit()
        
    def get_success_message(self) -> str:
        """获取成功消息"""
        return self.get_text(self.success_message)
        
    def get_error_message(self) -> str:
        """获取错误消息"""
        return self.get_text(self.error_message)
        
    def wait_for_success_message(self, timeout: int = 5000):
        """等待成功消息显示"""
        self.wait_for_element(self.success_message, timeout=timeout)
        
    def wait_for_error_message(self, timeout: int = 3000):
        """等待错误消息显示"""
        self.wait_for_element(self.error_message, timeout=timeout)
        
    def verify_form_elements(self):
        """验证表单元素"""
        expect(self.page.locator(self.title_input)).to_be_visible()
        expect(self.page.locator(self.type_select)).to_be_visible()
        expect(self.page.locator(".priority-selector")).to_be_visible()
        expect(self.page.locator(self.description_textarea)).to_be_visible()
        expect(self.page.locator(self.submit_button)).to_be_visible()
        expect(self.page.locator(self.cancel_button)).to_be_visible()


class ApprovalListPage(BasePage):
    """审批申请列表页面对象类"""
    
    @property
    def url(self) -> str:
        """页面URL"""
        return "http://localhost:8080/pages/approval-list.html"
    
    @property
    def title(self) -> str:
        """页面标题"""
        return "申请列表 - 测试系统"
    
    def __init__(self, page: Page):
        super().__init__(page)
        
        # 筛选器
        self.filters = ".filters"
        self.status_filter = "#statusFilter"
        self.type_filter = "#typeFilter"
        self.priority_filter = "#priorityFilter"
        self.search_filter = "#searchFilter"
        self.refresh_button = "#refreshBtn"
        
        # 申请列表
        self.approvals_container = ".approvals-container"
        self.approvals_list = "#approvalsList"
        self.approval_item = ".approval-item"
        self.approval_title = ".approval-title"
        self.approval_type = ".approval-type"
        self.approval_priority = ".approval-priority"
        self.approval_status = ".approval-status"
        self.approval_submitter = ".approval-submitter"
        self.approval_date = ".approval-date"
        self.approval_actions = ".approval-actions"
        
        # 操作按钮
        self.view_button = "button:has-text('查看详情')"
        self.approve_button = ".btn-approve"
        self.reject_button = ".btn-reject"
        
        # 空状态
        self.empty_state = ".empty-state"
        
        # 分页
        self.pagination = ".pagination"
        self.page_info = ".page-info"

        
    def wait_for_approval_list_page_load(self):
        """等待页面加载完成"""
        self.wait_for_element(self.filters)
        self.wait_for_element(self.approvals_list)
        
    def filter_by_status(self, status: str):
        """按状态筛选"""
        self.select_option(self.status_filter, status)
        
    def filter_by_type(self, type_value: str):
        """按类型筛选"""
        self.select_option(self.type_filter, type_value)
        
    def filter_by_priority(self, priority: str):
        """按优先级筛选"""
        self.select_option(self.priority_filter, priority)
        
    def search_approvals(self, search_term: str):
        """搜索申请"""
        self.fill(self.search_filter, search_term)
        
    def click_refresh(self):
        """点击刷新按钮"""
        self.click(self.refresh_button)
        
    def get_approval_count(self) -> int:
        """获取申请数量"""
        return self.page.locator(self.approval_item).count()
        
    def get_approval_titles(self) -> List[str]:
        """获取所有申请标题"""
        titles = []
        items = self.page.locator(self.approval_item)
        for i in range(items.count()):
            title = items.nth(i).locator(self.approval_title).text_content()
            titles.append(title)
        return titles
        
    def click_view_approval(self, index: int = 0):
        """点击查看申请详情"""
        items = self.page.locator(self.approval_item)
        if index < items.count():
            # 点击申请项内的查看详情按钮
            items.nth(index).locator(self.view_button).click()
        else:
            raise IndexError(f"申请索引 {index} 超出范围")
            
    def click_approve_approval(self, index: int = 0):
        """点击批准申请"""
        items = self.page.locator(self.approval_item)
        if index < items.count():
            items.nth(index).locator(self.approve_button).click()
        else:
            raise IndexError(f"申请索引 {index} 超出范围")
            
    def click_reject_approval(self, index: int = 0):
        """点击拒绝申请"""
        items = self.page.locator(self.approval_item)
        if index < items.count():
            items.nth(index).locator(self.reject_button).click()
        else:
            raise IndexError(f"申请索引 {index} 超出范围")
            
    def get_approval_info(self, index: int = 0) -> Dict[str, str]:
        """获取指定申请的信息"""
        # 等待申请列表加载
        self.page.wait_for_selector(self.approval_item, timeout=10000)
        
        items = self.page.locator(self.approval_item)
        if index >= items.count():
            raise IndexError(f"申请索引 {index} 超出范围")
            
        item = items.nth(index)
        
        # 等待每个元素可见后再获取文本
        item.locator(self.approval_title).wait_for(state="visible", timeout=5000)
        
        # 获取类型信息 - 从meta-item中查找包含"类型"的项目
        type_text = ""
        try:
            meta_items = item.locator('.meta-item')
            for i in range(meta_items.count()):
                meta_item = meta_items.nth(i)
                label_text = meta_item.locator('.meta-label').text_content(timeout=1000) or ""
                if '类型' in label_text:
                    type_text = meta_item.locator('.meta-value').text_content(timeout=1000) or ""
                    break
        except:
            type_text = ""
        
        # 获取提交时间 - 从meta-item中查找包含"提交时间"的项目
        date_text = ""
        try:
            meta_items = item.locator('.meta-item')
            for i in range(meta_items.count()):
                meta_item = meta_items.nth(i)
                label_text = meta_item.locator('.meta-label').text_content(timeout=1000) or ""
                if '提交时间' in label_text:
                    date_text = meta_item.locator('.meta-value').text_content(timeout=1000) or ""
                    break
        except:
            date_text = ""
        
        return {
            "title": item.locator(self.approval_title).text_content(timeout=5000) or "",
            "type": type_text,
            "priority": item.locator('.priority-badge').text_content(timeout=5000) or "",
            "status": item.locator('.status-badge').text_content(timeout=5000) or "",
            "submitter": "",  # 提交者信息不在当前HTML结构中
            "date": date_text
        }
        
    def is_empty_state_visible(self) -> bool:
        """检查是否显示空状态"""
        return self.is_visible(self.empty_state)
        
    def wait_for_approval_update(self, timeout: int = 5000):
        """等待申请状态更新"""
        self.page.wait_for_timeout(timeout)  # 等待状态更新
        
    def verify_list_elements(self):
        """验证列表页面元素"""
        expect(self.page.locator(self.filters)).to_be_visible()
        expect(self.page.locator(self.status_filter)).to_be_visible()
        expect(self.page.locator(self.type_filter)).to_be_visible()
        expect(self.page.locator(self.priority_filter)).to_be_visible()
        expect(self.page.locator(self.search_filter)).to_be_visible()
        expect(self.page.locator(self.refresh_button)).to_be_visible()


class ApprovalDetailPage(BasePage):
    """审批申请详情页面对象类"""
    
    @property
    def url(self) -> str:
        """页面URL"""
        return "http://localhost:8080/pages/approval-detail.html"
    
    @property
    def title(self) -> str:
        """页面标题"""
        return "申请详情 - 测试系统"
    
    def __init__(self, page: Page):
        super().__init__(page)
        self.base_url = "http://localhost:8080/pages/approval-detail.html"
        
        # 页面头部
        self.approval_header = ".page-header"
        self.approval_title = "#pageTitle"
        self.approval_status = ".status-badge"
        self.approval_info = ".detail-grid"
        self.approval_description = ".description-content"
        
        # 申请信息字段
        self.submitter_info = ".submitter-info"
        self.submit_time = ".submit-time"
        self.approval_type = ".approval-type"
        self.approval_priority = ".approval-priority"
        
        # 审批历史
        self.approval_history = ".approval-history"
        self.history_item = ".history-item"
        self.history_action = ".history-action"
        self.history_user = ".history-user"
        self.history_time = ".history-time"
        self.history_comment = ".history-comment"
        
        # 审批操作
        self.approval_actions = ".approval-actions"
        self.approve_button = "button:has-text('通过申请')"
        self.reject_button = "button:has-text('拒绝申请')"
        self.comment_textarea = "#approvalComment"
        
        # 导航
        self.back_button = "a.btn.btn-secondary"
        self.breadcrumb = ".breadcrumb"
        
    def navigate_with_id(self, approval_id: str):
        """导航到指定ID的申请详情页面"""
        url = f"{self.url}?id={approval_id}"
        self.page.goto(url)
        self.wait_for_page_load()
        
    def wait_for_approval_detail_page_load(self):
        """等待页面加载完成"""
        self.wait_for_element(self.approval_header)
        self.wait_for_element(self.approval_info)
        
    def get_approval_title(self) -> str:
        """获取申请标题"""
        return self.get_text(self.approval_title)
        
    def get_approval_status(self) -> str:
        """获取申请状态"""
        return self.get_text(self.approval_status)
        
    def get_approval_description(self) -> str:
        """获取申请描述"""
        return self.get_text(self.approval_description)
        
    def get_submitter_info(self) -> str:
        """获取提交者信息"""
        return self.get_text(self.submitter_info)
        
    def get_submit_time(self) -> str:
        """获取提交时间"""
        return self.get_text(self.submit_time)
        
    def fill_comment(self, comment: str):
        """填写审批意见"""
        self.fill(self.comment_textarea, comment)
        
    def click_approve(self):
        """点击批准按钮"""
        self.click(self.approve_button)
        
    def click_reject(self):
        """点击拒绝按钮"""
        self.click(self.reject_button)
        
    def approve_with_comment(self, comment: str = ""):
        """批准申请并添加意见"""
        # 点击通过申请按钮显示审批表单
        self.click_approve()
        # 等待审批表单显示
        self.wait_for_element(self.comment_textarea, timeout=5000)
        # 填写审批意见
        if comment:
            self.fill_comment(comment)
        # 提交审批表单
        self.page.locator("button[type='submit']").click()
        # 等待审批处理完成
        self.page.wait_for_timeout(2000)
        
    def reject_with_comment(self, comment: str = ""):
        """拒绝申请并添加意见"""
        # 点击拒绝申请按钮显示审批表单
        self.click_reject()
        # 等待审批表单显示
        self.wait_for_element(self.comment_textarea, timeout=5000)
        # 填写审批意见
        if comment:
            self.fill_comment(comment)
        # 提交审批表单
        self.page.locator("button[type='submit']").click()
        # 等待审批处理完成
        self.page.wait_for_timeout(2000)
        
    def click_back(self):
        """点击返回按钮"""
        self.click(self.back_button)
        
    def get_history_count(self) -> int:
        """获取审批历史记录数量"""
        return self.page.locator(self.history_item).count()
        
    def get_history_items(self) -> List[Dict[str, str]]:
        """获取所有审批历史记录"""
        items = []
        history_elements = self.page.locator(self.history_item)
        
        for i in range(history_elements.count()):
            item = history_elements.nth(i)
            items.append({
                "action": item.locator(self.history_action).text_content(),
                "user": item.locator(self.history_user).text_content(),
                "time": item.locator(self.history_time).text_content(),
                "comment": item.locator(self.history_comment).text_content() or ""
            })
        return items
        
    def is_approval_actions_visible(self) -> bool:
        """检查审批操作区域是否可见"""
        return self.is_visible(self.approval_actions)
        
    def wait_for_approval_processed(self, timeout: int = 5000):
        """等待审批处理完成"""
        # 等待页面状态更新
        self.page.wait_for_timeout(timeout)
        
    def verify_detail_elements(self):
        """验证详情页面元素"""
        expect(self.page.locator(self.approval_header)).to_be_visible()
        expect(self.page.locator(self.approval_title)).to_be_visible()
        expect(self.page.locator(self.approval_status)).to_be_visible()
        expect(self.page.locator(self.approval_info)).to_be_visible()
        expect(self.page.locator(self.approval_description)).to_be_visible()
        expect(self.page.locator(self.back_button)).to_be_visible()