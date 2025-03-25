import os
import json
from pathlib import Path
from typing import Dict, Any, Optional
from functools import lru_cache
from pydantic import BaseModel
from app.schemas.config import ModelConfig, SecurityConfig, DatabaseConfig, ServerConfig, SystemConfig
from app.utils.logger import get_logger
import yaml  # 新增导入
logger = get_logger(__name__)
# 默认配置文件路径
DEFAULT_CONFIG_PATH = Path(os.path.dirname(os.path.abspath(__file__))).parent / "config.yaml"

class Settings(BaseModel):
    """应用配置类"""
    # 应用版本
    version: str = "1.0.0"
    
    # 当前工作目录
    workspace: Optional[str] = None
    
    # 配置文件路径
    config_path: str = str(DEFAULT_CONFIG_PATH)
    
    # 单智能体模式下的智能体配和双智能体模式下的工具调用智能体所用的配置，必须有工具调用能力。
    model: ModelConfig = ModelConfig(
        type="openai",
        api_key="",
        endpoint="https://api.openai.com/v1",
        model="gpt-4"
    ) 
    #双智能体模式下的用户代理模型配置，不需要进行工具调用。
    user_model:ModelConfig = ModelConfig(
        type="openai",
        api_key="",
        endpoint="",
        model="gpt-4"
        
    )
    # 服务器配置，暂时不支持修改
    server: ServerConfig = ServerConfig(
        host="127.0.0.1",
        port=8000,
        frontend_port=5173  # 前端Vite默认端口
    )
    
    class Config:
        """Pydantic配置"""
        arbitrary_types_allowed = True


@lru_cache()
def get_settings() -> Settings:
    """获取应用配置实例
    
    使用lru_cache装饰器缓存配置实例，避免重复加载
    
    Returns:
        Settings: 应用配置实例
    """
    settings = Settings()
    
    # 如果配置文件存在，从文件加载配置
    if os.path.exists(settings.config_path):
        try:
            config_data = load_config_from_file(settings.config_path)
            # 修改这部分代码，正确处理嵌套配置
            if "model" in config_data and isinstance(config_data["model"], dict):
                settings.model = ModelConfig(**config_data["model"])
            if "user_model" in config_data and isinstance(config_data["user_model"], dict):
                settings.user_model = ModelConfig(**config_data["user_model"])
            # 处理其他非嵌套配置，跳过空值
            for key, value in config_data.items():
                if (key not in ["model", "user_model", "server"] and 
                    hasattr(settings, key) and 
                    value != ""):  # 添加空值检查
                    setattr(settings, key, value)
        except Exception as e:
            logger.error(f"加载配置文件失败: {str(e)}")
    else:
        # 配置文件不存在，创建默认配置文件
        try:
            save_config_to_file(settings, settings.config_path)
        except Exception as e:
            logger.error(f"创建默认配置文件失败: {str(e)}")
    
    return settings


def load_config_from_file(path: str) -> Dict[str, Any]:
    """从文件加载配置
    
    Args:
        path: 配置文件路径
        
    Returns:
        Dict[str, Any]: 配置数据
        
    Raises:
        Exception: 文件不存在或格式错误时抛出异常
    """
    if not os.path.exists(path):
        raise Exception(f"配置文件不存在: {path}")
    
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)  # 修改为yaml加载


def save_config_to_file(config: Settings, path: str) -> None:
    """保存配置到文件
    
    Args:
        config: 配置实例
        path: 配置文件路径
        
    Raises:
        Exception: 保存失败时抛出异常
    """
    # 确保目录存在
    logger.info(f"保存配置到文件: {path}")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    
    # 将配置转换为字典
    config_dict = config.model_dump(mode='json')
    
    # 保存到文件
    with open(path, "w", encoding="utf-8") as f:
        yaml.safe_dump(config_dict, f, allow_unicode=True, sort_keys=False)  # 修改为yaml保存


def reset_settings() -> None:
    """重置配置
    
    清除缓存并重新加载配置
    """
    get_settings.cache_clear()

if __name__ == "__main__":
    print(f"默认路径{DEFAULT_CONFIG_PATH}")
    # 获取配置实例
    settings = get_settings()
    print("当前配置:")
    print(f"版本: {settings.version}")
    print(f"工作目录: {settings.workspace}")
    print(f"模型类型: {settings.model.type}")
    print(f"模型: {settings.model.model}")
    
    print(settings)
    # 保存到新的配置文件
    test_config_path =  settings.config_path
    save_config_to_file(settings, test_config_path)
    print(f"\n配置已保存到: {test_config_path}")