// WebSocket连接管理
import { ref } from 'vue';
import { createWebSocketClient } from '../api/websocket';

export function useWebSocket() {
  const isConnected = ref(false);
  const wsClient = createWebSocketClient();
  
  // 连接状态回调
  const handleConnect = () => {
    isConnected.value = true;
  };
  
  // 断开连接回调
  const handleDisconnect = () => {
    isConnected.value = false;
  };
  
  // 建立连接
  const connect = () => {
    wsClient.connect();
  };
  
  // 断开连接
  const disconnect = () => {
    wsClient.disconnect();
  };
  
  // 订阅主题
  const subscribe = (topic: string, callback: (data: any) => void) => {
    wsClient.subscribe(topic, callback);
  };
  
  // 取消订阅
  const unsubscribe = (topic: string) => {
    wsClient.unsubscribe(topic);
  };
  
  // 发送消息
  const sendMessage = (type: string, data: any) => {
    wsClient.sendMessage(type, data);
  };
  
  return {
    isConnected,
    connect,
    disconnect,
    subscribe,
    unsubscribe,
    sendMessage
  };
}