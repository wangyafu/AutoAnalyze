from typing import Dict, List, Optional, Any, Union
from app.core.model_client import ModelClient, create_client
from app.core.agent.dual_agent import create_dual_agent_system, run_dual_agent_system, DualAgentSystem
from app.schemas.config import ModelConfig
from app.utils.logger import get_logger
from app.core.filesystem import filesystem_manager
logger = get_logger(__name__)

def create_dual_agent(user_model_config: ModelConfig, tool_model_config: ModelConfig, conversation_id: str) -> DualAgentSystem:
    """
    创建双智能体系统
    
    Args:
        user_model_config: 用户代理使用的模型配置
        tool_model_config: 工具调用智能体使用的模型配置
        conversation_id: 对话ID
        
    Returns:
        DualAgentSystem: 双智能体系统实例
    """
    # 创建用户代理模型客户端
    user_model_client = create_client(user_model_config)
    
    # 创建工具调用智能体模型客户端
    tool_model_client = create_client(tool_model_config)
    
    # 创建双智能体系统
    return create_dual_agent_system(user_model_client, tool_model_client, conversation_id)

async def run_dual_agent(system: DualAgentSystem, user_message: str) -> str:
    """
    运行双智能体系统
    
    Args:
        system: 双智能体系统实例
        user_message: 用户消息
        
    Returns:
        str: 系统响应
    """
    return await run_dual_agent_system(system, user_message)

