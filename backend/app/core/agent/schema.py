from typing import Dict, Any, Optional, Union
from pydantic import BaseModel, Field

class FunctionCall(BaseModel):
    """函数调用数据结构
    
    用于表示模型请求调用的函数及其参数
    """
    name: str = Field(..., description="函数名称")
    
    class Config:
        extra = "allow"  # 允许额外字段，用于存储不同函数的特定参数

class FunctionResult(BaseModel):
    """函数调用结果
    
    用于表示函数调用的结果或错误
    """
    name: str = Field(..., description="函数名称")
    result: Optional[Dict[str, Any]] = Field(None, description="函数调用成功时的结果")
    error: Optional[str] = Field(None, description="函数调用失败时的错误信息")
    
    class Config:
        extra = "allow"  # 允许额外字段，用于存储不同函数的特定结果