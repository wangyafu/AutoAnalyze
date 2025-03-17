from typing import Dict, Any, Optional
import asyncio
from app.core.model_client import create_client, ModelClient
from app.config import get_settings
from app.db.session import get_db
from app.services.conversation_service import add_message
from app.core.agent.agent import create_agent, run_agent
from app.schemas.config import ModelConfig
from app.core.agent.agent import Agent
# 全局变量，存储模型客户端实例
_model_client = None
Agents:list[Agent]=[]
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

def get_model_client() -> ModelClient:
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
        if not initialize_model():
            raise Exception("模型未初始化或初始化失败")
    
    return _model_client

async def get_model_status() -> Dict[str, Any]:
    """
    获取模型状态
    
    Returns:
        Dict[str, Any]: 模型状态信息
    """
    try:
        client = get_model_client()
        status=await client.get_status()
        return status
    except Exception as e:
        return {
            "connected": False,
            "error": str(e)
        }

async def send_message(conversation_id: str, content: str) -> Dict[str, Any]:
    try:
        client = get_model_client()
        
        # 查找或创建Agent
        existing_agents = list(filter(lambda a: a.conversation_id == conversation_id, Agents))
        if not existing_agents:
            agent = create_agent(client, conversation_id)
            Agents.append(agent)
        else:
            agent = existing_agents[0]
        
        # 运行Agent处理用户消息
        response = await run_agent(agent, content)
        
        # 返回简化后的响应（暂时隐藏数据库操作）
        return {
            "conversation_id": conversation_id,
            "content": response,
            "agent_status": "existing" if existing_agents else "new"
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
        return await initialize_model(settings.model.dict())
    except Exception as e:
        print(f"更新模型配置失败: {str(e)}")
        return False


if __name__ == "__main__":
    async def test_model_service():
        print("开始测试模型服务...")
        
        # 初始化模型
        print("正在初始化模型...")
        init_success,_model_client = await initialize_model()
        
        if not init_success:
            print("模型初始化失败，请检查配置和网络连接")
            return
        
        print("模型初始化成功!")
        
        # 获取模型状态
        print("获取模型状态...")
        status = await _model_client.get_status()
        print(f"模型状态: {status}")
        
        # 测试发送消息
        try:
            print("测试发送消息...")
            test_conversation_id = "test_conversation"
            test_message = "你好，这是一条测试消息。请简要回复。"
            
            print(f"发送消息: {test_message}")
            response = await _model_client.chat_completion(messages=[{'role': 'user', 'content': test_message}])
            
            if response.get("status") == "success":
                print("收到回复:")
                print(f"内容: {response['message']['content']}")
                print(f"Token使用: {response.get('usage', {})}")
            else:
                print(f"发送消息失败: {response.get('error', '未知错误')}")
        except Exception as e:
            print(f"测试发送消息时出错: {str(e)}")
        
        # 关闭客户端
        if _model_client:
            print("关闭模型客户端...")
            await _model_client.close()
        
        print("测试完成")

    # 运行测试
    asyncio.run(test_model_service())