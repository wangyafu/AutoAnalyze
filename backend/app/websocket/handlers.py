import json
from fastapi import WebSocket
from typing import Dict, Any
from ..websocket.manager import ConnectionManager
from ..services.execution_service import execute_code, cancel_execution
from ..services.conversation_service import add_message
from ..services.model_service import send_message
import logging

# 获取日志记录器
logger = logging.getLogger(__name__)


async def handle_message(message: str, websocket: WebSocket, manager: ConnectionManager):
    """处理接收到的WebSocket消息"""
    try:
        # 解析消息
        data = json.loads(message)
        message_type = data.get("type")
        
        # 根据消息类型分发处理
        if message_type == "user_message":
            await handle_user_message(data.get("data", {}), websocket, manager)
        elif message_type == "subscribe_execution":
            await handle_subscribe_execution(data.get("data", {}), websocket, manager)
        elif message_type == "unsubscribe":
            await handle_unsubscribe(data.get("data", {}), websocket, manager)
        elif message_type == "cancel_execution":
            await handle_cancel_execution(data.get("data", {}), websocket, manager)
        else:
            # 未知消息类型
            await manager.send_personal_message({
                "type": "error",
                "data": {
                    "code": "invalid_request",
                    "message": f"未知的消息类型: {message_type}"
                }
            }, websocket)
    except json.JSONDecodeError:
        # JSON解析错误
        await manager.send_personal_message({
            "type": "error",
            "data": {
                "code": "invalid_request",
                "message": "无效的JSON格式"
            }
        }, websocket)
    except Exception as e:
        # 其他错误
        logger.exception(f"处理WebSocket消息时出错: {str(e)}")
        await manager.send_personal_message({
            "type": "error",
            "data": {
                "code": "server_error",
                "message": "服务器处理消息时出错",
                "details": str(e)
            }
        }, websocket)


async def handle_user_message(data: Dict[str, Any], websocket: WebSocket, manager: ConnectionManager):
    """处理用户消息"""
    conversation_id = data.get("conversation_id")
    content = data.get("content")
    
    if not conversation_id or not content:
        await manager.send_personal_message({
            "type": "error",
            "data": {
                "code": "invalid_request",
                "message": "缺少必要参数: conversation_id 或 content"
            }
        }, websocket)
        return
    
    try:
        # 保存用户消息到数据库
        user_message = await add_message(conversation_id, "user", content)
        
        # 发送消息到模型并获取回复
        response = await send_message(conversation_id, content)
        
        # 保存助手消息到数据库
        assistant_message = await add_message(conversation_id, "assistant", response)
        
        # 发送助手消息回客户端
        await manager.send_personal_message({
            "type": "assistant_message",
            "data": {
                "conversation_id": conversation_id,
                "message_id": assistant_message.id,
                "content": response,
                "timestamp": assistant_message.created_at.isoformat()
            }
        }, websocket)
        
    except Exception as e:
        logger.exception(f"处理用户消息时出错: {str(e)}")
        await manager.send_personal_message({
            "type": "error",
            "data": {
                "code": "message_processing_error",
                "message": "处理消息时出错",
                "details": str(e)
            }
        }, websocket)


async def handle_subscribe_execution(data: Dict[str, Any], websocket: WebSocket, manager: ConnectionManager):
    """处理执行订阅"""
    execution_id = data.get("execution_id")
    
    if not execution_id:
        await manager.send_personal_message({
            "type": "error",
            "data": {
                "code": "invalid_request",
                "message": "缺少必要参数: execution_id"
            }
        }, websocket)
        return
    
    # 订阅执行结果
    manager.subscribe_execution(execution_id, websocket)
    
    # 确认订阅成功
    await manager.send_personal_message({
        "type": "subscription_confirmed",
        "data": {
            "topic": f"execution_{execution_id}",
            "message": "订阅成功"
        }
    }, websocket)


async def handle_unsubscribe(data: Dict[str, Any], websocket: WebSocket, manager: ConnectionManager):
    """处理取消订阅"""
    topic = data.get("topic")
    
    if not topic or not topic.startswith("execution_"):
        await manager.send_personal_message({
            "type": "error",
            "data": {
                "code": "invalid_request",
                "message": "无效的主题格式"
            }
        }, websocket)
        return
    
    # 从主题中提取执行ID
    execution_id = topic[10:]  # 去掉 "execution_" 前缀
    
    # 取消订阅
    manager.unsubscribe_execution(execution_id, websocket)
    
    # 确认取消订阅成功
    await manager.send_personal_message({
        "type": "unsubscription_confirmed",
        "data": {
            "topic": topic,
            "message": "已取消订阅"
        }
    }, websocket)


async def handle_cancel_execution(data: Dict[str, Any], websocket: WebSocket, manager: ConnectionManager):
    """处理取消执行"""
    execution_id = data.get("execution_id")
    
    if not execution_id:
        await manager.send_personal_message({
            "type": "error",
            "data": {
                "code": "invalid_request",
                "message": "缺少必要参数: execution_id"
            }
        }, websocket)
        return
    
    try:
        # 取消代码执行
        result = await cancel_execution(execution_id)
        
        # 发送取消结果
        await manager.send_personal_message({
            "type": "execution_cancelled",
            "data": {
                "execution_id": execution_id,
                "status": "cancelled" if result else "cancel_failed",
                "message": "执行已取消" if result else "取消执行失败"
            }
        }, websocket)
        
    except Exception as e:
        logger.exception(f"取消执行时出错: {str(e)}")
        await manager.send_personal_message({
            "type": "error",
            "data": {
                "code": "cancel_execution_error",
                "message": "取消执行时出错",
                "details": str(e)
            }
        }, websocket)