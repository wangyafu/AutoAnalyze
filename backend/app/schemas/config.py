from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any


class ModelConfig(BaseModel):
    """模型配置"""
    type: str = Field(..., description="模型类型，如'openai', 'claude', 'local'")
    api_key: Optional[str] = Field(None, description="API密钥")
    endpoint: Optional[str] = Field(None, description="API端点URL")
    model: str = Field("gpt-4", description="模型名称")


class SecurityConfig(BaseModel):
    """安全配置"""
    max_execution_time: int = Field(300, description="最大执行时间（秒）")
    max_memory: int = Field(1024, description="最大内存使用（MB）")


class DatabaseConfig(BaseModel):
    """数据库配置"""
    type: str = Field("sqlite", description="数据库类型")
    path: str = Field("./data/history.db", description="数据库路径")


class ServerConfig(BaseModel):
    """服务器配置"""
    host: str = Field("127.0.0.1", description="服务器主机")
    port: int = Field(8000, description="服务器端口")
    frontend_port: int = Field(3000, description="前端服务器端口")


class SystemConfig(BaseModel):
    """系统配置"""
    model: Optional[ModelConfig] = Field(None, description="主模型配置")
    user_model: Optional[ModelConfig] = Field(None, description="用户代理模型配置")
    vision_model: Optional[ModelConfig] = Field(None, description="视觉模型配置")


class ModelStatusResponse(BaseModel):
    """模型状态响应"""
    status: str = Field(..., description="模型状态")
    type: str = Field(..., description="模型类型")

class StatusResponse(BaseModel):
    """状态响应"""
    status: str = Field(..., description="状态，'ok'或'error'")
    version: str = Field(..., description="应用版本")
    model: ModelStatusResponse = Field(..., description="模型状态")
    workspace: Optional[str] = Field(None, description="当前工作目录")
    config: Dict[str, Any] = Field(..., description="当前配置")
    tag:str