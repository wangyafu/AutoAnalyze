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


async def get_model_status() -> Dict[str, Any]:
    """
    获取模型状态，每次都使用最新配置进行连接测试
    
    Returns:
        Dict[str, Any]: 模型状态信息，包含所有模型的状态
    """
    try:
        settings = get_settings()
        status = {
            "ok": False,
            "models": {
                "main": {"ok": False, "error": None},
                "user": {"ok": False, "error": None},
                "vision": {"ok": False, "error": None}
            }
        }
        
        # 测试主模型
        try:
            main_client = create_client(settings.model)
            main_status = await main_client.test_connection()
            status["models"]["main"] = main_status
            status["ok"] = main_status["connected"]  # 主模型状态决定整体状态
        except Exception as e:
            status["models"]["main"]["error"] = str(e)
            
        # 测试用户代理模型（如果配置了）
        if settings.user_model.api_key:
            try:
                user_client = create_client(settings.user_model)
                user_status = await user_client.test_connection()
                status["models"]["user"] = user_status
            except Exception as e:
                status["models"]["user"]["error"] = str(e)
                
        # 测试视觉模型（如果配置了）
        if settings.vision_model.api_key:
            try:
                vision_client = create_client(settings.vision_model)
                vision_status = await vision_client.test_connection()
                status["models"]["vision"] = vision_status
            except Exception as e:
                status["models"]["vision"]["error"] = str(e)
        
        return status
    except Exception as e:
        return {
            "ok": False,
            "error": str(e),
            "models": {
                "main": {"ok": False, "error": str(e)},
                "user": {"ok": False, "error": None},
                "vision": {"ok": False, "error": None}
            }
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



if __name__ == "__main__":
    async def test_model_service():
        print("开始测试模型服务...")
        await send_message("111","你好",True)

    # 运行测试
    asyncio.run(test_model_service())