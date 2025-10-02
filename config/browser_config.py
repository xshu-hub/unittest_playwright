"""
浏览器配置管理类
用于读取和管理Playwright浏览器相关的配置参数
"""
import os
import yaml
from typing import Dict, Any, Optional
from utils.logger import get_logger
from utils.common import load_yaml_with_default, default_config_path

# 初始化日志系统
logger = get_logger(__name__)


class BrowserConfig:
    """浏览器配置管理类"""
    
    def __init__(self, config_file: Optional[str] = None):
        """
        初始化浏览器配置管理器
        
        Args:
            config_file: 配置文件路径，如果为None则使用默认配置文件
        """
        self._config_data: Dict[str, Any] = {}
        self._config_file = config_file or self._get_default_config_file()
        self._load_config()

    @staticmethod
    def _get_default_config_file() -> str:
        """
        获取默认配置文件路径

        Returns:
            str: 默认配置文件路径
        """
        return default_config_path()

    def _load_config(self) -> None:
        """加载配置文件"""
        self._config_data = load_yaml_with_default(
            self._config_file,
            self._get_default_config,
            logger,
            "Browser",
        )
    
    @staticmethod
    def _get_default_config() -> Dict[str, Any]:
        """
        获取默认配置
        
        Returns:
            Dict[str, Any]: 默认配置字典
        """
        return {
            "browser": {
                "type": "chromium",
                "headless": False,
                "viewport": {
                    "width": 1920,
                    "height": 1080
                },
                "locale": "zh-CN",
                "timezone": "Asia/Shanghai",
                "slow_mo": 0,
                "args": []
            },
            "timeouts": {
                "default": 10000,
                "short": 3000,
                "long": 30000,
                "navigation": 30000
            }
        }
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        获取配置值
        
        Args:
            key: 配置键，支持点号分隔的嵌套键，如 "browser.type"
            default: 默认值
            
        Returns:
            Any: 配置值
        """
        try:
            keys = key.split('.')
            value = self._config_data
            
            for k in keys:
                if isinstance(value, dict) and k in value:
                    value = value[k]
                else:
                    return default
                    
            return value
        except Exception as e:
            logger.error(f"获取配置值失败: {key}, 错误: {str(e)}")
            return default
    
    def set(self, key: str, value: Any) -> None:
        """
        设置配置值
        
        Args:
            key: 配置键，支持点号分隔的嵌套键
            value: 配置值
        """
        try:
            keys = key.split('.')
            current_config  = self._config_data
            
            # 导航到最后一级的父级
            for k in keys[:-1]:
                if k not in current_config:
                    current_config[k] = {}
                current_config = current_config[k]
            
            # 设置最后一级的值
            current_config[keys[-1]] = value
            logger.info(f"配置值设置成功: {key} = {value}")

        except Exception as e:
            logger.error(f"设置配置值失败: {key}, 错误: {str(e)}")
    
    def get_browser_config(self) -> Dict[str, Any]:
        """
        获取浏览器配置
        
        Returns:
            Dict[str, Any]: 浏览器配置字典
        """
        return self.get("browser", {})
    
    def get_timeout_config(self) -> Dict[str, int]:
        """
        获取超时配置
        
        Returns:
            Dict[str, int]: 超时配置字典
        """
        return self.get("timeouts", {})
    
    def get_browser_type(self) -> str:
        """
        获取浏览器类型
        
        Returns:
            str: 浏览器类型
        """
        return self.get("browser.type", "chromium")
    
    def get_headless(self) -> bool:
        """
        获取是否无头模式
        
        Returns:
            bool: 是否无头模式
        """
        return self.get("browser.headless", False)
    
    def get_viewport(self) -> Dict[str, int]:
        """
        获取视口大小
        
        Returns:
            Dict[str, int]: 视口大小
        """
        return self.get("browser.viewport", {"width": 1920, "height": 1080})
    
    def get_default_timeout(self) -> int:
        """
        获取默认超时时间
        
        Returns:
            int: 默认超时时间(毫秒)
        """
        return self.get("timeouts.default", 10000)
    
    def get_short_timeout(self) -> int:
        """
        获取短超时时间
        
        Returns:
            int: 短超时时间(毫秒)
        """
        return self.get("timeouts.short", 3000)
    
    def get_long_timeout(self) -> int:
        """
        获取长超时时间
        
        Returns:
            int: 长超时时间(毫秒)
        """
        return self.get("timeouts.long", 30000)
    
    def get_navigation_timeout(self) -> int:
        """
        获取导航超时时间
        
        Returns:
            int: 导航超时时间(毫秒)
        """
        return self.get("timeouts.navigation", 30000)
    
    def save_config(self, file_path: Optional[str] = None) -> None:
        """
        保存配置到文件
        
        Args:
            file_path: 保存路径，如果为None则保存到当前配置文件
        """
        try:
            save_path = file_path or self._config_file
            
            # 确保目录存在
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            
            with open(save_path, 'w', encoding='utf-8') as file:
                yaml.dump(self._config_data, file, default_flow_style=False, 
                         allow_unicode=True, indent=2)
            logger.info(f"配置文件保存成功: {save_path}")

        except Exception as e:
            logger.error(f"保存配置文件失败: {str(e)}")
    
    def reload_config(self) -> None:
        """重新加载配置文件"""
        self._load_config()
        logger.info("配置文件重新加载完成")
    
    def update_from_env(self) -> None:
        """从环境变量更新配置"""
        env_mappings = {
            "BROWSER_TYPE": "browser.type",
            "BROWSER_HEADLESS": "browser.headless",
            "DEFAULT_TIMEOUT": "timeouts.default"
        }
        
        for env_key, config_key in env_mappings.items():
            env_value = os.getenv(env_key)
            if env_value is not None:
                # 类型转换
                if config_key in ["browser.headless"]:
                    env_value = env_value.lower() in ('true', '1', 'yes', 'on')
                elif config_key in ["timeouts.default"]:
                    env_value = int(env_value)
                
                self.set(config_key, env_value)
                logger.info(f"从环境变量更新配置: {config_key} = {env_value}")

    def get_all_config(self) -> Dict[str, Any]:
        """
        获取所有配置
        
        Returns:
            Dict[str, Any]: 所有配置字典
        """
        return self._config_data.copy()
    
    def __str__(self) -> str:
        """字符串表示"""
        return f"Config(file={self._config_file})"
    
    def __repr__(self) -> str:
        """对象表示"""
        return self.__str__()


# 全局浏览器配置实例
browser_config = BrowserConfig()