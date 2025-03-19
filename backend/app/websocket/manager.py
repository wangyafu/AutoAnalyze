from fastapi import WebSocket
from typing import Dict, List, Any
import json


class ConnectionManager:
    """WebSocket连接管理器"""
    
    def __init__(self):
        # 活跃的WebSocket连接
        self.active_connections: List[WebSocket] = []
        # 执行ID到WebSocket连接的映射，用于执行结果订阅
        self.execution_subscribers: Dict[str, List[WebSocket]] = {}
        
    async def connect(self, websocket: WebSocket):
        """建立WebSocket连接"""
        await websocket.accept()
        self.active_connections.append(websocket)
        
    def disconnect(self, websocket: WebSocket):
        """断开WebSocket连接"""
        self.active_connections.remove(websocket)
        
        # 从所有执行订阅中移除该连接
        for execution_id, subscribers in list(self.execution_subscribers.items()):
            if websocket in subscribers:
                subscribers.remove(websocket)
                # 如果没有订阅者了，删除该执行ID的条目
                if not subscribers:
                    del self.execution_subscribers[execution_id]
    
    async def send_personal_message(self, message: Any, websocket: WebSocket):
        """发送个人消息"""
        if isinstance(message, dict) or isinstance(message, list):
            message = json.dumps(message)
        await websocket.send_text(message)
    
    async def broadcast(self, message: Any):
        """广播消息到所有连接"""
        if isinstance(message, dict) or isinstance(message, list):
            message = json.dumps(message)
        for connection in self.active_connections:
            await connection.send_text(message)
    
    def subscribe_execution(self, execution_id: str, websocket: WebSocket):
        """订阅执行结果"""
        if execution_id not in self.execution_subscribers:
            self.execution_subscribers[execution_id] = []
        if websocket not in self.execution_subscribers[execution_id]:
            self.execution_subscribers[execution_id].append(websocket)
    
    
    

    
    
    
    async def broadcast_filesystem_change(self, change_data: dict):
        """广播文件系统变更"""
        message = {
            "type": "filesystem_change",
            "data": change_data
        }
        await self.broadcast(message)
    async def broadcast_message(self,message:dict):
        await self.broadcast(message)


# 创建全局连接管理器实例
manager = ConnectionManager()