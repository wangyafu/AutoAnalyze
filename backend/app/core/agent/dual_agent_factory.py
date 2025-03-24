from typing import Dict, List, Optional, Any, Union
from app.core.model_client import ModelClient, create_client
from app.core.agent.dual_agent import create_dual_agent_system, run_dual_agent_system, DualAgentSystem
from app.schemas.config import ModelConfig
from app.utils.logger import get_logger

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

if __name__ == "__main__":
    import asyncio
    import sys
    import os
    import uuid
    from app.schemas.config import ModelConfig
    from app.config import get_settings
    from app.core.filesystem import filesystem_manager
    
    async def main():
        # 设置工作目录
        test_workspace="D:\\fakedata\\sale"
        result = filesystem_manager.set_workspace(test_workspace)
        print(f"设置工作目录结果: {result}")
       
        tool_model_config = get_settings().model
        user_model_config=get_settings().userModel
        # 创建双智能体系统
        conversation_id = "test-conversation-" + str(uuid.uuid4())
        system = create_dual_agent(user_model_config, tool_model_config, conversation_id)
        
        # 测试用户消息
        user_message = "帮我分析过去12个月的销售趋势，找出增长最快的产品类别，并预测下个季度的销售情况"
        
        print(f"发送用户消息: {user_message}")
        response = await run_dual_agent(system, user_message)
        print(f"系统响应:\n{response}")
    
    # 运行主函数
    asyncio.run(main())