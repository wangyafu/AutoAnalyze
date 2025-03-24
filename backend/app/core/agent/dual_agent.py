from typing import Dict, List, Optional, Any, Union
from pydantic import BaseModel

from app.core.model_client import ModelClient
from app.core.agent.functions import tools, read_files, read_file, exec_code
from app.core.agent.prompts import get_system_prompt, format_function_descriptions
from app.core.agent.schema import FunctionCall, FunctionResult
from app.utils.logger import get_logger
import json
logger = get_logger(__name__)
from app.core.agent.functions import FunctionExecutor
import uuid
import datetime
from app.websocket.manager import manager
from string import Template
from app.core.agent.agent import Agent
import json
class UserAgent:
    """用户代理智能体，负责理解用户意图并制定行动计划"""
    
    def __init__(self, model_client: ModelClient, conversation_id: str):
        """初始化用户代理智能体
        
        Args:
            model_client: 模型客户端
            conversation_id: 对话ID
        """
        self.model_client = model_client
        self.conversation_id = conversation_id
        self.promptTemplate = Template("""
你是一个用户代理智能体，你需要帮助我实现任务目标。
我的任务目标是：【$user_message】
消息历史:【$messages_history】
系统中存在工具调用智能体，你不应该直接执行任务，而是细化、分解用户的任务，指定行动计划交给工具调用智能体。
工具调用智能体拥有的工具:
exec_code: 执行Python代码
read_directory: 读取目录
read_files: 读取文件内容
如果根据消息历史你发现用户的[任务目标]已经完成，你应该明确说明'任务已完成'并总结结果。
如果未完成，你应该提供下一步行动计划，明确任务目标和具体操作。行动计划应该使用第二人称。请不要指定任务的具体参数，保留工具调用智能体的灵活性。
如果任务因为某种原因无法完成，你应该明确说明'任务无法完成'并总结原因。
【关键】：不要过度延伸！不要过度追求完美！我的时间是宝贵的！

""")
        self.messages = []
        
    
    async def process_message(self, user_message: str, tool_agent_messages: List[Dict[str, Any]]) -> str:
        """处理用户消息并生成行动计划或判断任务是否完成
        
        Args:
            user_message: 用户消息或工具执行结果
            tool_agent_messages: 工具调用智能体的消息历史
            
        Returns:
            行动计划或任务完成状态
        """
        # 更新消息历史，包含工具调用智能体的历史和原始用户输入
        self.messages = []  # 保留系统提示
        
        # # 添加工具调用智能体的历史消息
        # for msg in tool_agent_messages:
        #     if msg.get("role") != "system":  # 不添加系统消息
        #         self.messages.append(msg)

        tool_agent_messages = [message for message in tool_agent_messages if (message.get("role", "")  in ["user","assistant"])]
        # 添加用户消息
        self.messages.append({"role": "user", "content": self.promptTemplate.substitute(user_message=user_message,messages_history=json.dumps(tool_agent_messages,ensure_ascii=False))})
        

        # 调用模型生成行动计划或判断任务完成状态
        response = await self.model_client.chat_completion(
            messages=self.messages,
            tools=[]  # 用户代理不使用工具
        )
        
        if response.get("status") == "error":
            return f"生成行动计划时出错: {response.get('error', '未知错误')}"
        
        action_plan = response.get("message", {}).get("content", "")
        
        # 添加助手回复到历史
        self.messages.append({
            "role": "assistant",
            "content": action_plan
        })
        
        # 广播助手消息
        await manager.broadcast_message({
            "type": "user_agent_message",
            "data": {
                "content": action_plan,
                "timestamp": datetime.datetime.now().isoformat(),
                "conversation_id": self.conversation_id
            }
        })
        
        return action_plan
    
    async def close(self):
        """关闭代理使用的资源"""
        if self.model_client:
            await self.model_client.close()


class ToolAgent(Agent):
    """工具调用智能体，负责执行具体的工具调用，继承自Agent类"""
    
    def __init__(self, model_client: ModelClient, conversation_id: str):
        """初始化工具调用智能体
        
        Args:
            model_client: 模型客户端
            conversation_id: 对话ID
        """
        # 调用父类初始化方法
        super().__init__(model_client, conversation_id)
        

        # 更新消息历史中的系统提示
        self.messages = []
        self.messages.append({
            'role': "system",
            "content": self.system_prompt
        })
    
    async def process_message(self, action_plan: str) -> str:
        """处理用户代理的行动计划并执行工具调用
        
        Args:
            action_plan: 用户代理生成的行动计划
            
        Returns:
            执行结果
        """
        
        # 调用父类的process_message方法，但传入action_plan作为用户消息
        # 由于我们已经添加了用户消息，所以这里不需要再次添加
        # 直接使用父类的循环处理逻辑
        return await super().process_message(action_plan)
    async def done(self):
        return 
    
    # 不需要重写appendAiMessage方法，直接使用父类Agent中的实现
    
    async def close(self):
        """关闭代理使用的资源"""
        if self.model_client:
            await self.model_client.close()


class DualAgentSystem:
    """双智能体系统，协调用户代理和工具调用智能体"""
    
    def __init__(self, user_model_client: ModelClient, tool_model_client: ModelClient, conversation_id: str):
        """初始化双智能体系统
        
        Args:
            user_model_client: 用户代理使用的模型客户端
            tool_model_client: 工具调用智能体使用的模型客户端
            conversation_id: 对话ID
        """
        self.user_agent = UserAgent(user_model_client, conversation_id)
        self.tool_agent = ToolAgent(tool_model_client, conversation_id)
        self.conversation_id = conversation_id
        self.original_user_message = ""
    
    async def process_message(self, user_message: str) -> str:
        """处理用户消息，实现ReAct框架的推理-行动-观察-推理循环
        
        Args:
            user_message: 用户消息
            
        Returns:
            最终响应
        """
        # 保存原始用户消息
        self.original_user_message = user_message
        
        # 初始化循环变量
        max_iterations = 5  # 最大循环次数，防止无限循环
        current_iteration = 0
        task_completed = False
        final_response = ""
        
        # 初始行动计划由用户代理生成
        action_plan = await self.user_agent.process_message(user_message, self.tool_agent.messages)
        
        # ReAct循环：推理-行动-观察-推理
        while not task_completed and current_iteration < max_iterations:
            # 工具调用智能体执行行动计划（行动阶段）
            tool_response = await self.tool_agent.process_message(action_plan)
            
            # # 判断任务是否完成
            # # 方法1：检查工具响应中是否包含任务完成的标志
            # if "任务已完成" in tool_response or "已完成所有请求" in tool_response:
            #     task_completed = True
            #     final_response = tool_response
            #     break
            
            # 方法2：让用户代理判断是否需要继续
            # 将工具响应传回用户代理进行下一轮推理
            next_action_plan = await self.user_agent.process_message(self.original_user_message,self.tool_agent.messages)
            
            # 检查用户代理的响应是否表明任务已完成
            if "任务已完成" in next_action_plan or "任务无法完成" in next_action_plan:
                task_completed = True
                final_response =  next_action_plan
                break
            
            # 更新行动计划，继续循环
            action_plan = next_action_plan
            current_iteration += 1
        
        # 如果达到最大循环次数但任务未完成，返回当前结果
        if current_iteration >= max_iterations and not task_completed:
            final_response = f"已达到最大循环次数({max_iterations})，当前执行结果:\n{tool_response}"
        
        # 发送完成通知
        await manager.broadcast_message({
            "type": "done",
            "data": {
                "timestamp": datetime.datetime.now().isoformat(),
                "conversation_id": self.conversation_id
            }
        })
        
        return final_response
    
    async def close(self):
        """关闭系统使用的资源，确保所有资源都被正确释放"""
        # 确保即使其中一个关闭失败，另一个也会尝试关闭
        try:
            await self.user_agent.close()
        finally:
            await self.tool_agent.close()


def create_dual_agent_system(user_model_client: ModelClient, tool_model_client: ModelClient, conversation_id: str) -> DualAgentSystem:
    """创建双智能体系统
    
    Args:
        user_model_client: 用户代理使用的模型客户端
        tool_model_client: 工具调用智能体使用的模型客户端
        conversation_id: 对话ID
        
    Returns:
        DualAgentSystem: 双智能体系统实例
    """
    return DualAgentSystem(user_model_client, tool_model_client, conversation_id)


async def run_dual_agent_system(system: DualAgentSystem, user_message: str) -> str:
    """运行双智能体系统
    
    Args:
        system: 双智能体系统实例
        user_message: 用户消息
        
    Returns:
        str: 系统响应
    """
    try:
        return await system.process_message(user_message)
    finally:
        # 确保在出现异常时也能关闭资源
        await system.close()