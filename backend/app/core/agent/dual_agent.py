from typing import Dict, List, Optional, Any, Union
from pydantic import BaseModel

from app.core.model_client import ModelClient
from app.core.agent.functions import tools, read_files, read_file, exec_code
from app.core.agent.prompts import get_system_prompt, get_user_agent_prompt
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

class UserAgent(Agent):
    """用户代理智能体，负责理解用户意图并制定行动计划"""
    
    def __init__(self, model_client: ModelClient, conversation_id: str):
        """初始化用户代理智能体
        
        Args:
            model_client: 模型客户端
            conversation_id: 对话ID
        """
        # 调用父类初始化，但不使用父类的系统提示词
        super().__init__(model_client, conversation_id)
        # 使用专用的用户代理系统提示词
        self.system_prompt = get_user_agent_prompt()
        # 重置消息历史，添加新的系统提示
        self.messages = []
        self.messages.append({
            'role': "system",
            "content": self.system_prompt
        })
        self.last_tool_history = []  # 存储上一轮工具调用历史

    async def process_message(self, user_message: str, tool_agent_messages: List[Dict[str, Any]]) -> str:
        """处理用户消息并生成行动计划或判断任务是否完成
        
        Args:
            user_message: 用户消息或工具执行结果
            tool_agent_messages: 工具调用智能体的消息历史
            
        Returns:
            行动计划或任务完成状态
        """
        # 更新上一轮工具调用历史
        self.last_tool_history = tool_agent_messages
        
        # 构建提示模板
        prompt = f"""
你需要帮助我实现以下任务目标。
上一轮工具调用结果：
<tool_agent_history>
{self._summarize_tool_history()}
</tool_agent_history>
工具调用智能体拥有的工具:
<tool_list>
exec_code: 执行Python代码
read_directory: 读取目录
read_files: 读取文件内容
</tool_list>
我的目标：
<target>
{user_message}
</target>
你的任务:
<task>
1. 整理上一轮工具调用过程中得到的信息
2. 给出当前的任务进展情况
3. 判断任务是否完成，如果完成，请输出"任务已完成"，如果任务无法完成，请输出"任务无法完成"并指出无法完成的原因
4. 如果未完成且有可能完成，制定下一轮行动计划
</task>
关于行动计划：
<action_plan_about>
- 行动计划将交给工具调用智能体，因此你应当使用第二人称
- 工具调用智能体没有过往轮次的记忆，他不了解任务目标和过往轮次的结果，因此你需要在行动计划中加入你认为必要的信息
- 为了解决复杂的数据科学问题，你的行动计划应当包含详细的数据处理步骤、分析方法选择和可视化策略
- 对于数据预处理，请考虑缺失值处理、异常值检测和特征工程等高级技术
- 对于分析方法，请根据问题性质选择合适的统计分析、机器学习或时间序列分析技术
- 对于可视化，请指导生成信息丰富且易于理解的图表
</action_plan_about>
请开始执行任务。
"""
        
        # 调用模型生成响应
        response = await self.model_client.chat_completion(
            messages=[{"role":"user","content":user_message}]+self.messages+[{"role": "user", "content": prompt}],
            tools=[]
        )
        
        if response.get("status") == "error":
            error_message = f"生成行动计划时出错: {response.get('error', '未知错误')}"
            await self.error(error_message)
            return error_message
        
        action_plan = response.get("message", {}).get("content", "")
        
        # 保存本轮输出到历史
        self.messages.append(
            {
            "role": "assistant",
            "content": action_plan,})
        
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

    def _summarize_tool_history(self) -> str:
        """整理工具调用历史"""
        if not self.last_tool_history:
            return "暂无工具调用结果"
        return "\n".join([
            f"{msg['role']}: {msg['content']}"
            for msg in self.last_tool_history
            if msg.get("role") in ["assistant", "tool"]
        ])

class ToolAgent(Agent):
    """工具调用智能体，负责执行具体的工具调用"""
    
    def __init__(self, model_client: ModelClient, conversation_id: str):
        super().__init__(model_client, conversation_id)
        self.previous_messages = []  # 存储上一轮的消息历史
    
    async def process_message(self, action_plan: str) -> str:
        """处理用户代理的行动计划并执行工具调用
        
        Args:
            action_plan: 用户代理生成的行动计划
            
        Returns:
            执行结果
        """
        # 保存当前消息历史为上一轮历史
        if len(self.messages) > 1:  # 确保有消息可以保存
            self.previous_messages = self.messages.copy()
        
        # 清空当前消息历史，但保留系统提示
        self.messages = [self.messages[0]]  # 保留系统提示
        
        # 如果有上一轮历史，需要保持完整的工具调用链
        if len(self.previous_messages) >= 3:
            # 查找所有助手消息及其对应的工具响应消息
            for i, msg in enumerate(self.previous_messages):
                if msg["role"] == "assistant" and msg.get("tool_calls"):
                    # 添加助手消息
                    self.messages.append(msg)
                    
                    # 查找并添加对应的工具响应消息
                    tool_call_ids = [tool_call["id"] for tool_call in msg.get("tool_calls", [])]
                    for j in range(i+1, len(self.previous_messages)):
                        if (self.previous_messages[j]["role"] == "tool" and 
                            self.previous_messages[j].get("tool_call_id") in tool_call_ids):
                            self.messages.append(self.previous_messages[j])
        
        # 添加本轮行动计划
        self.messages.append({"role": "user", "content": action_plan})
        
        # 调用父类处理逻辑
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
        # action_plan=user_message
        # ReAct循环：推理-行动-观察-推理
        while not task_completed and current_iteration < max_iterations:
            # 工具调用智能体执行行动计划（行动阶段）
            tool_response = await self.tool_agent.process_message(action_plan)
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
        await self.user_agent.done()
        
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