from typing import Dict, Any, Optional, Union, List
import asyncio
from app.core.model_client import create_client, ModelClient
from app.config import get_settings
from app.schemas.config import ModelConfig
from app.core.agent.agent import Agent
from app.core.agent.dual_agent import DualAgentSystem
from app.core.agent.agent_factory import create_agent_system, run_agent_system,create_dual_agent_from_single,create_singal_agent_from_dual
# 全局变量，存储模型客户端实例
from app.utils.logger import get_logger
logger=get_logger(__name__)
_model_client = None
Agents: List[Union[Agent, DualAgentSystem]] = []
async def initialize_model(config: ModelConfig = None) -> (bool,ModelClient):
    """
    初始化模型
    
    Args:
        config: 模型配置，为None时使用系统配置
        
    Returns:
        bool: 初始化是否成功
    """
    global _model_client
    
    try:
        # 获取配置
        settings = get_settings()
        model_config = config or settings.model
        
        # 创建模型客户端
        _model_client = create_client(model_config)
        
        # 测试连接
        status = await _model_client.test_connection()
        
        return status["connected"],_model_client
    except Exception as e:
        print(f"初始化模型失败: {str(e)}")
        return False,None

async def get_model_client() -> ModelClient:
    """
    获取模型客户端实例
    
    Returns:
        ModelClient: 模型客户端实例
        
    Raises:
        Exception: 模型未初始化时抛出异常
    """
    global _model_client
    
    if _model_client is None:
        # 尝试初始化
        if not await initialize_model():
            raise Exception("模型未初始化或初始化失败")
    
    return _model_client

async def get_model_status() -> Dict[str, Any]:
    """
    获取模型状态
    
    Returns:
        Dict[str, Any]: 模型状态信息
    """
    try:
        client = await get_model_client()
        status=await client.get_status()
        return status
    except Exception as e:
        return {
            "ok": False,
            "error": str(e)
        }

async def send_message(conversation_id: str, content: str, use_dual_agent: bool = False) -> Dict[str, Any]:
    try:

        logger.info(f"接收到用户消息:{content}")
        # 查找或创建Agent
        existing_agents = list(filter(lambda a: a.conversation_id == conversation_id, Agents))
        if not existing_agents:
            # 根据use_dual_agent参数创建相应的智能体系统
            settings = get_settings()
            agent = create_agent_system(settings.model, conversation_id, use_dual_agent, settings.user_model)
            Agents.append(agent)
        else:
            agent = existing_agents[0]
            # 检查是否需要切换智能体模式
            current_is_dual = isinstance(agent, DualAgentSystem)
            if current_is_dual != use_dual_agent:
                # 使用转换函数而不是重新创建智能体
                if use_dual_agent:
                    # 从单智能体转换为双智能体
                    new_agent = create_dual_agent_from_single(agent)
                else:
                    # 从双智能体转换为单智能体
                    new_agent = await create_singal_agent_from_dual(agent)
                
                # 从列表中移除旧的智能体并添加新的智能体
                Agents.remove(agent)
                Agents.append(new_agent)
                agent = new_agent
        
        # 运行智能体系统处理用户消息
        response = await run_agent_system(agent, content)
        
        # 返回简化后的响应（暂时隐藏数据库操作）
        return {
            "conversation_id": conversation_id,
            "content": response,
            "agent_status": "existing" if existing_agents else "new",
            "agent_mode": "dual" if use_dual_agent else "single"
        }
    except Exception as e:
        print(f"发送消息失败: {str(e)}")
        return {"error": str(e)}

async def update_model_config(config: Dict[str, Any]) -> bool:
    """
    更新模型配置
    
    Args:
        config: 新的模型配置
        
    Returns:
        bool: 更新是否成功
    """
    try:
        # 更新配置
        settings = get_settings()
        for key, value in config.items():
            if hasattr(settings.model, key):
                setattr(settings.model, key, value)
        
        # 重新初始化模型
        return await initialize_model(settings.model)
    except Exception as e:
        print(f"更新模型配置失败: {str(e)}")
        return False


if __name__ == "__main__":
    async def test_model_service():
        print("开始测试模型服务...")
        await send_message("111","你好",True)

    # 运行测试
    asyncio.run(test_model_service())