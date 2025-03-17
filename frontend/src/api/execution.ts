// 代码执行相关API
import { httpClient } from './http';
import { createWebSocketClient } from './websocket';

// 执行代码
const executeCode = async (conversationId: string, code: string, executionId?: string) => {
  const response = await httpClient.post('/api/execute', {
    conversation_id: conversationId,
    code,
    execution_id: executionId
  });
  
  return response.data;
};

// 取消代码执行
const cancelExecution = async (executionId: string) => {
  const response = await httpClient.post(`/api/execute/${executionId}/cancel`);
  return response.data;
};

// 订阅执行结果
const subscribeExecution = (executionId: string, callback: (data: any) => void) => {
  const wsClient = createWebSocketClient();
  wsClient.connect();
  
  // 订阅执行结果
  wsClient.subscribe(`execution_${executionId}`, callback);
  
  // 发送订阅消息
  wsClient.sendMessage('subscribe_execution', {
    execution_id: executionId
  });
  
  return () => {
    wsClient.unsubscribe(`execution_${executionId}`);
  };
};

export {
  executeCode,
  cancelExecution,
  subscribeExecution
};