from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from ..websocket.manager import manager
from ..websocket.handlers import handle_message
import logging

# 获取日志记录器
logger = logging.getLogger(__name__)

# 创建WebSocket路由
router = APIRouter()


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket连接端点"""
    # 接受WebSocket连接
    await manager.connect(websocket)
    
    try:
        # 发送连接成功消息
        await manager.send_personal_message({
            "type": "connection_established",
            "data": {
                "message": "WebSocket连接已建立"
            }
        }, websocket)
        
        # 持续接收消息
        while True:
            message = await websocket.receive_text()
            await handle_message(message, websocket, manager)
            
    except WebSocketDisconnect:
        # 客户端断开连接
        logger.info("WebSocket客户端断开连接")
    except Exception as e:
        # 其他错误
        logger.exception(f"WebSocket连接处理时出错: {str(e)}")
    finally:
        # 断开连接
        manager.disconnect(websocket)