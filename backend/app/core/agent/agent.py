from typing import Dict, List, Optional, Any, Union
from pydantic import BaseModel

from app.core.model_client import ModelClient,OpenAIClient
from app.core.agent.functions import tools, read_files, read_file, exec_code
from app.core.agent.prompts import get_system_prompt, format_function_descriptions
from app.core.agent.schema import FunctionCall, FunctionResult
from app.utils.logger import get_logger
import json
logger=get_logger(__name__)
from app.core.agent.functions import FunctionExecutor
import uuid
import datetime
from app.websocket.manager import manager

class Agent:
    """Base Agent class for AutoAnalyze"""
    
    def __init__(self, model_client: ModelClient, conversation_id: str):
        # 初始化函数执行器
        self.function_executor = FunctionExecutor(conversation_id=conversation_id)
        """Initialize the agent with a model client and conversation ID
        
        Args:
            model_client: The model client to use for generating responses
            conversation_id: The ID of the conversation this agent is associated with
        """
        self.model_client = model_client
        self.conversation_id = conversation_id
        self.system_prompt = get_system_prompt()
        self.function_descriptions = format_function_descriptions()
        self.messages = []
        self.messages.append({
            'role':"system",
            "content":self.system_prompt
        })

        self.tools = tools
    
    async def process_message(self, user_message: str) -> str:
        """处理用户消息并维护会话历史"""
        # 添加用户消息到历史
        self.messages.append({"role": "user", "content": user_message})
    
        while True:  # 循环处理可能的多轮函数调用
            # 调用模型客户端
            response = await self.model_client.chat_completion(
                messages=self.messages,
                tools=self.tools
            )
    
            # 如果响应中包含函数调用
            if response.get("message", {}).get("tool_calls"):
                tool_calls = response["message"]["tool_calls"]
                await self.appendAiMessage(response["message"]["content"],tool_calls)
                
                # 处理所有函数调用
                for tool_call in tool_calls:
                    function_call = tool_call["function"]
                    invocation_id = str(uuid.uuid4())  # 生成唯一调用ID
                    
                    # 发送工具调用开始通知
                    await manager.broadcast_message(
                        
                        {
                            "type": "tool_invocation_start",
                            "data":{
                            "invocation_id": invocation_id,
                            "function": function_call["name"],
                            "arguments": json.loads(function_call["arguments"]),
                            "timestamp": datetime.datetime.now().isoformat()
                            }
                            
                        }
                    )
                    
                    # 执行函数调用
                    result = await self.function_executor.execute(
                        function_call["name"],
                        json.loads(function_call["arguments"])
                    )
                    
                    # 发送工具调用结果通知
                    await manager.broadcast_message(
                     
                        {
                            "type": "tool_invocation_result",
                            "data":{
                            "invocation_id": invocation_id,
                            "function": function_call["name"],
                            "result": result,
                            "timestamp": datetime.datetime.now().isoformat()
                            }
                            
                        }
                    )
                    
                    self.messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call["id"],
                        "name": function_call["name"],
                        "content": str(result)
                    })
                
                # 继续循环，让AI处理函数调用的结果
                continue
            await self.appendAiMessage(response["message"]["content"])
            # 如果没有函数调用，则是最终回复
            self.messages.append({
                "role": "assistant",
                "content": response["message"]["content"]
            })
            await manager.broadcast_message(
                {
                    "type": "done",
                    "data":{
                    "timestamp": datetime.datetime.now().isoformat(),
                    "conversation_id":self.conversation_id
                    }
                }
            )
            return response["message"]["content"]
    async def appendAiMessage(self,message:str,tool_calls:List[Dict[str,Any]]=None):
        self.messages.append({
                "role": "assistant",
                "content": message,
                "tool_calls":tool_calls
                
            })
        if len(message)>0:
         # 广播助手消息到WebSocket客户端
            await manager.broadcast_message(

                {
                    "type": "assistant_message",
                    "data":{
                    "content": message,
                    "timestamp": datetime.datetime.now().isoformat(),
                    "conversation_id":self.conversation_id
                }
                }
            )
        
        
   
    
    async def close(self):
        """关闭代理使用的资源"""
        if self.model_client:
            await self.model_client.close()


def create_agent(model_client: ModelClient, conversation_id: str) -> Agent:
    """Factory function to create an appropriate agent instance
    
    Args:
        model_client: The model client to use
        conversation_id: The conversation ID
        
    Returns:
        An instance of Agent
    """
    # For now, always create an AnalysisAgent as it's our primary use case
    return Agent(model_client, conversation_id)


async def run_agent(agent: Agent, user_message: str) -> str:
    """Run the agent with a user message
    
    Args:
        agent: The agent instance
        user_message: The user's message
        
    Returns:
        The agent's response
    """
    try:
        return await agent.process_message(user_message)
    finally:
        # 确保在出现异常时也能关闭资源
        # 注意：在实际应用中，你可能不想在每次消息处理后都关闭客户端
        # 这里仅用于测试场景
        await agent.close() 


if __name__ == "__main__":
    import asyncio
    from app.core.model_client import ModelClient,create_client
    from app.config import get_settings
    from app.core.filesystem import filesystem_manager
    import os
    current_file_path = os.path.abspath(__file__)
    #获取项目根目录
    root_path=os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(current_file_path))))
    root_path=os.path.dirname(root_path)
    filesystem_manager.set_workspace(root_path+"\\examples\\exam")
    async def test_agent():
        # 创建一个测试用的ModelClient实例
        settings=get_settings()
        model_client = create_client(settings.model)
        
        # 创建一个Agent实例
        agent = create_agent(model_client, "test_conversation_id")
        
        # 测试消息
        test_message = "谁是全班成绩最好的人"
        
        # 运行Agent并获取响应
        print("发送测试消息:", test_message)
        response = await run_agent(agent, test_message)
        print("Agent响应:", response)
        
        # 打印消息历史
        print("\n消息历史:")
        for msg in agent.messages:
            role = msg.get("role", "unknown")
            content = msg.get("content", "")
            if role == "tool":
                print(f"[{role}:{msg.get('name', '')}] {content}")
            elif "function_call" in msg:
                func_call = msg["function_call"]
                print(f"[{role}] 调用函数: {func_call['name']}({func_call['arguments']})")
            else:
                print(f"[{role}] {content}")
    
    # 运行测试函数
    asyncio.run(test_agent())