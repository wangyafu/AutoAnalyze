import os
import json
import time
from typing import Dict, List, Any, Optional, Callable, Union
import asyncio
import aiohttp
from abc import ABC, abstractmethod
from app.schemas.config import ModelConfig
from ..utils.logger import get_logger

logger = get_logger(__name__)

class ModelClient(ABC):
    """大模型客户端基类"""
    
    @abstractmethod
    async def chat_completion(self, messages: List[Dict[str, Any]], tools: List[Dict[str, Any]]) -> Dict[str, Any]:
        """发送消息到模型
        
        Args:
            conversation_id: 对话ID
            message: 消息内容
            
        Returns:
            Dict: 模型响应
        """
        pass
    
    @abstractmethod
    async def get_status(self) -> Dict[str, Any]:
        """获取模型状态
        
        Returns:
            Dict: 状态信息
        """
        pass
    @abstractmethod
    async def test_connection(self)->Dict[str,Any]:
        pass
    @abstractmethod
    async def close(self):
        pass


class OpenAIClient(ModelClient):
    """OpenAI客户端"""
    
    def __init__(self, api_key: str, model: str = "gpt-4", api_base: Optional[str] = None):
        self.conversations = {}
        """初始化OpenAI客户端
        
        Args:
            api_key: OpenAI API密钥
            model: 模型名称
            api_base: API基础URL，如果为None则使用默认URL
        """
        self.api_key = api_key
        self.model = model
        self.api_base = api_base or "https://api.openai.com/v1"
        self.conversations: Dict[str, List[Dict[str, Any]]] = {}
        self.session: Optional[aiohttp.ClientSession] = None
    
    async def _ensure_session(self):
        """确保会话已创建"""
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession(headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            })
    
    async def chat_completion(self, messages: List[Dict[str, Any]], tools: List[Dict[str, Any]]) -> Dict[str, Any]:
        """发送消息到OpenAI模型"""
        await self._ensure_session()
        
        # 构造请求数据
        request_data = {
            "model": self.model,
            "messages": messages,
            "tools": tools,
            "temperature": 0.7
        }
        
        # 发送请求到OpenAI API
        try:
            async with self.session.post(
                f"{self.api_base}/chat/completions",
                json=request_data
            ) as response:
                if response.status != 200:
                    error_text = await response.text()
                    logger.error(f"OpenAI API错误: {response.status} - {error_text}")
                    return {
                        "status": "error",
                        "error": f"API错误: {response.status}",
                        "details": error_text
                    }
                
                result = await response.json()
                
                return {
                    "status": "success",
                    "message": result["choices"][0]["message"],
                    "usage": result.get("usage", {})
                }
                
        except Exception as e:
            logger.error(f"发送消息到OpenAI时出错: {str(e)}")
            return {
                "status": "error",
                "error": f"发送消息失败: {str(e)}"
            }
    
    async def get_status(self) -> Dict[str, Any]:
        """获取OpenAI模型状态
        
        Returns:
            Dict: 状态信息
        """
        await self._ensure_session()
        
        try:
            # 简单的模型可用性检查
            async with self.session.get(f"{self.api_base}/models") as response:
                if response.status == 200:
                    models = await response.json()
                    logger.info(f"当前检查的服务可用的模型共有{len(models.get('data',[]))}个。")
                    return {
                        "ok": True,
                        "model": self.model,
                        "api_base": self.api_base,
                        "models_available": len(models.get("data", []))
                    }
                else:
                    error_text = await response.text()
                    return {
                        "ok": False,
                        "error": f"API错误: {response.status}",
                        "details": error_text
                    }
        except Exception as e:
            return {
                "status": "error",
                "error": f"检查状态失败: {str(e)}"
            }
    async def test_connection(self)-> Dict[str, Any]:
        """测试与OpenAI模型的连接"""
        try:
            # 尝试获取OpenAI模型状态
            status = await self.get_status()

            # 检查状态是否成功
            if status["ok"]:
                return {
                    "connected": True,
                    "model": status["model"],
                    "api_base": status["api_base"],
                    "models_available": status["models_available"]
                }
            else:
                return {
                    "connected": False,
                    "error": status.get("error", "未知错误")
                }
        except Exception as e:
            logger.error(f"测试OpenAI连接时出错: {str(e)}")
            return {
                "connected": False,
                "error": f"连接测试失败: {str(e)}"
            }
    async def close(self):
        """关闭客户端会话"""
        if self.session and not self.session.closed:
            await self.session.close()


def create_client(config: ModelConfig) -> ModelClient:
    """创建模型客户端
    
    Args:
        config: 模型配置
        
    Returns:
        ModelClient: 模型客户端实例
    """
    client_type = config.type.lower()
    
    if client_type == "openai":
        return OpenAIClient(
            api_key=config.api_key,
            model=config.model,
            api_base=config.endpoint
        )
    else:
        raise ValueError(f"不支持的模型类型: {client_type}。目前支持openai系列!")