// 对话相关API
import { httpClient } from './http';
import { createWebSocketClient } from './websocket';

// 获取对话列表
const getConversations = async (limit?: number, offset?: number) => {
  const params: Record<string, number> = {};
  if (limit !== undefined) params.limit = limit;
  if (offset !== undefined) params.offset = offset;
  
  const response = await httpClient.get('/api/conversations', { params });
  return response.data;
};

// 获取单个对话详情
const getConversation = async (id: string) => {
  const response = await httpClient.get(`/api/conversations/${id}`);
  return response.data;
};

// 创建新对话
const createConversation = async (title: string) => {
  const response = await httpClient.post('/api/conversations', { title });
  return response.data;
};

// 删除对话
const deleteConversation = async (id: string) => {
  const response = await httpClient.delete(`/api/conversations/${id}`);
  return response.data;
};

// 发送用户消息
const sendUserMessage = async (conversationId: string, content: string) => {
  // 使用WebSocket发送消息
  const wsClient = createWebSocketClient();
  wsClient.connect();
  wsClient.sendMessage('user_message', {
    conversation_id: conversationId,
    content
  });
  
  // 返回一个Promise，在收到回复时解析
  return new Promise((resolve) => {
    wsClient.subscribe(`assistant_message`, (data) => {
      if (data.conversation_id === conversationId) {
        resolve(data);
        wsClient.unsubscribe(`assistant_message`);
      }
    });
  });
};

export {
  getConversations,
  getConversation,
  createConversation,
  deleteConversation,
  sendUserMessage
};