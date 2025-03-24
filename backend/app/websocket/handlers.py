import json
from fastapi import WebSocket
from typing import Dict, Any
from ..websocket.manager import ConnectionManager
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
    print(data)
    conversation_id = data.get("conversation_id")
    content = data.get("content")
    use_dual_agent=data.get("use_dual_agent")
    print(conversation_id,content,use_dual_agent)
    if (not conversation_id) or (not content) or  (use_dual_agent==None):
        await manager.send_personal_message({
            "type": "error",
            "data": {
                "code": "invalid_request",
                "message": "缺少必要参数"
            }
        }, websocket)
        return
    
    try:
        # 保存用户消息到数据库
        # user_message = await add_message(conversation_id, "user", content)
        
        # 发送消息到模型并获取回复
        response = await send_message(conversation_id, content,use_dual_agent)

        
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


async def handle_cancel_execution(data: Dict[str, Any], websocket: WebSocket, manager: ConnectionManager):
    """处理取消代码执行请求"""
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
        # 导入执行引擎
        from ..core.jupyter_execution import jupyter_execution_engine
        
        # 取消执行
        success = await jupyter_execution_engine.cancel_execution(execution_id)
        
        # 发送取消结果
        if success:
            await manager.send_personal_message({
                "type": "execution_cancelled",
                "data": {
                    "execution_id": execution_id,
                    "message": "代码执行已取消"
                }
            }, websocket)
        else:
            await manager.send_personal_message({
                "type": "error",
                "data": {
                    "code": "cancel_failed",
                    "message": "取消执行失败，可能执行ID不存在或执行已完成"
                }
            }, websocket)
    except Exception as e:
        logger.exception(f"取消代码执行时出错: {str(e)}")
        await manager.send_personal_message({
            "type": "error",
            "data": {
                "code": "cancel_error",
                "message": "取消执行时出错",
                "details": str(e)
            }
        }, websocket)



