import os
import json
from pathlib import Path
from typing import Dict, Any, Optional
from functools import lru_cache
from pydantic import BaseModel
from app.schemas.config import ModelConfig, SecurityConfig, DatabaseConfig, ServerConfig, SystemConfig

# 默认配置文件路径
DEFAULT_CONFIG_PATH = Path(os.path.dirname(os.path.abspath(__file__))).parent / "config.json"

class Settings(BaseModel):
    """应用配置类"""
    # 应用版本
    version: str = "1.0.0"
    
    # 当前工作目录
    workspace: Optional[str] = None
    
    # 配置文件路径
    config_path: str = str(DEFAULT_CONFIG_PATH)
    
    # 模型配置
    model: ModelConfig = ModelConfig(
        type="openai",
        api_key="",
        endpoint="https://api.openai.com/v1",
        model="gpt-4"
    )
    
    # 安全配置
    security: SecurityConfig = SecurityConfig(
        max_execution_time=300,
        max_memory=1024
    )
    
    # 数据库配置
    database: DatabaseConfig = DatabaseConfig(
        type="sqlite",
        path="./data/history.db"
    )
    
    # 服务器配置
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
            if "security" in config_data and isinstance(config_data["security"], dict):
                settings.security = SecurityConfig(**config_data["security"])
            if "database" in config_data and isinstance(config_data["database"], dict):
                settings.database = DatabaseConfig(**config_data["database"])
            if "server" in config_data and isinstance(config_data["server"], dict):
                settings.server = ServerConfig(**config_data["server"])
            
            # 处理其他非嵌套配置
            for key, value in config_data.items():
                if key not in ["model", "security", "database", "server"] and hasattr(settings, key):
                    setattr(settings, key, value)
        except Exception as e:
            print(f"加载配置文件失败: {str(e)}")
    else:
        # 配置文件不存在，创建默认配置文件
        try:
            save_config_to_file(settings, settings.config_path)
        except Exception as e:
            print(f"创建默认配置文件失败: {str(e)}")
    
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
        return json.load(f)


def save_config_to_file(config: Settings, path: str) -> None:
    """保存配置到文件
    
    Args:
        config: 配置实例
        path: 配置文件路径
        
    Raises:
        Exception: 保存失败时抛出异常
    """
    # 确保目录存在
    os.makedirs(os.path.dirname(path), exist_ok=True)
    
    # 将配置转换为字典
    config_dict = config.dict()
    
    # 保存到文件
    with open(path, "w", encoding="utf-8") as f:
        json.dump(config_dict, f, ensure_ascii=False, indent=4)


def reset_settings() -> None:
    """重置配置
    
    清除缓存并重新加载配置
    """
    get_settings.cache_clear()