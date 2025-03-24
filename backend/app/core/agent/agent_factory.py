from typing import Dict, List, Optional, Any, Union
from app.core.model_client import ModelClient, create_client
from app.core.agent.agent import Agent, create_agent, run_agent
from app.core.agent.dual_agent import DualAgentSystem, create_dual_agent_system, run_dual_agent_system
from app.core.agent.dual_agent_factory import create_dual_agent, run_dual_agent
from app.schemas.config import ModelConfig
from app.utils.logger import get_logger

logger = get_logger(__name__)


def create_agent_system(model_config: ModelConfig, conversation_id: str, use_dual_agent: bool = False,
                       user_model_config: Optional[ModelConfig] = None) -> Union[Agent, DualAgentSystem]:
    """
    创建智能体系统，支持单智能体模式和双智能体模式
    
    Args:
        model_config: 模型配置（单智能体模式下使用，或双智能体模式下作为工具调用智能体的模型配置）
        conversation_id: 对话ID
        use_dual_agent: 是否使用双智能体模式
        user_model_config: 用户代理智能体的模型配置（仅在双智能体模式下使用）
        
    Returns:
        Union[Agent, DualAgentSystem]: 智能体系统实例
    """
    if use_dual_agent:
        # 如果未提供用户代理模型配置，则使用与工具调用智能体相同的配置
        if user_model_config is None:
            user_model_config = model_config
            
        # 创建双智能体系统
        return create_dual_agent(user_model_config, model_config, conversation_id)
    else:
        # 创建单智能体系统
        model_client = create_client(model_config)
        return create_agent(model_client, conversation_id)
def create_dual_agent_from_single(agent: Agent) -> DualAgentSystem:
    """
    从单智能体创建双智能体系统

    Args:
        agent: 单智能体实例

    Returns:
        DualAgentSystem: 双智能体系统实例
    """
    # 获取单智能体的模型客户端和对话ID
    model_client = agent.model_client
    conversation_id = agent.conversation_id
    
    # 创建双智能体系统，使用相同的模型客户端作为用户代理和工具调用智能体
    dual_agent_system = create_dual_agent_system(model_client, model_client, conversation_id)
    
    # 将单智能体的消息历史复制到工具调用智能体
    dual_agent_system.tool_agent.messages = agent.messages.copy()
    
    return dual_agent_system

async def create_singal_agent_from_dual(agent_system: DualAgentSystem) -> Agent:
    """
    从双智能体系统创建单智能体

    Args:
        agent_system: 双智能体系统实例

    Returns:
        Agent: 单智能体实例
    """
    # 从双智能体系统中获取工具调用智能体
    tool_agent = agent_system.tool_agent
    
    # 创建新的单智能体，使用工具调用智能体的模型客户端和对话ID
    single_agent = create_agent(tool_agent.model_client, agent_system.conversation_id)
    
    # 将工具调用智能体的消息历史复制到新的单智能体
    single_agent.messages = tool_agent.messages.copy()
    
    return single_agent
async def run_agent_system(agent_system: Union[Agent, DualAgentSystem], user_message: str) -> str:
    """
    运行智能体系统
    
    Args:
        agent_system: 智能体系统实例
        user_message: 用户消息
        
    Returns:
        str: 系统响应
    """
    if isinstance(agent_system, DualAgentSystem):
        # 运行双智能体系统
        return await run_dual_agent(agent_system, user_message)
    else:
        # 运行单智能体系统
        return await run_agent(agent_system, user_message)