// 封装WebSocket连接和消息处理

type MessageCallback = (data: any) => void;
type ConnectionCallback = () => void;

interface WebSocketClient {
  connect: () => void;
  disconnect: () => void;
  subscribe: (topic: string, callback: MessageCallback) => void;
  unsubscribe: (topic: string) => void;
  sendMessage: (type: string, data: any) => void;
}

interface Subscription {
  topic: string;
  callback: MessageCallback;
}

const createWebSocketClient = (url: string = 'ws://127.0.0.1:8000/ws'): WebSocketClient => {
  let socket: WebSocket | null = null;
  let subscriptions: Subscription[] = [];
  let reconnectAttempts = 0;
  let reconnectTimeout: number | null = null;
  let onOpenCallback: ConnectionCallback | null = null;
  let onCloseCallback: ConnectionCallback | null = null;
  
  // 创建WebSocket连接
  const connect = (): void => {
    if (socket && (socket.readyState === WebSocket.OPEN || socket.readyState === WebSocket.CONNECTING)) {
      return;
    }
    
    socket = new WebSocket(url);
    
    socket.onopen = () => {
      console.log('WebSocket连接已建立');
      reconnectAttempts = 0;
      if (onOpenCallback) onOpenCallback();
      
      // 重新订阅之前的主题
      subscriptions.forEach(sub => {
        const message = JSON.stringify({
          type: 'subscribe',
          data: { topic: sub.topic }
        });
        socket?.send(message);
      });
    };
    
    socket.onclose = () => {
      console.log('WebSocket连接已关闭');
      if (onCloseCallback) onCloseCallback();
      
      // 尝试重新连接
      if (reconnectTimeout === null) {
        const delay = Math.min(1000 * Math.pow(2, reconnectAttempts), 30000);
        reconnectTimeout = window.setTimeout(() => {
          reconnectTimeout = null;
          reconnectAttempts++;
          connect();
        }, delay);
      }
    };
    
    socket.onerror = (error) => {
      console.error('WebSocket错误:', error);
    };
    
    socket.onmessage = (event) => {
      try {
        const message = JSON.parse(event.data);
        const { type, data } = message;
        
        // 查找匹配的订阅并调用回调
        subscriptions.forEach(sub => {
          if (type === sub.topic || `${type}_${data?.execution_id}` === sub.topic) {
            sub.callback(data);
          }
        });
      } catch (error) {
        console.error('解析WebSocket消息错误:', error);
      }
    };
  };
  
  // 断开WebSocket连接
  const disconnect = (): void => {
    if (socket) {
      socket.close();
      socket = null;
    }
    
    if (reconnectTimeout !== null) {
      clearTimeout(reconnectTimeout);
      reconnectTimeout = null;
    }
  };
  
  // 订阅主题
  const subscribe = (topic: string, callback: MessageCallback): void => {
    // 检查是否已订阅
    const existingSubscription = subscriptions.find(sub => sub.topic === topic);
    if (existingSubscription) {
      existingSubscription.callback = callback;
      return;
    }
    
    // 添加新订阅
    subscriptions.push({ topic, callback });
    
    // 如果已连接，发送订阅消息
    if (socket && socket.readyState === WebSocket.OPEN) {
      const message = JSON.stringify({
        type: 'subscribe',
        data: { topic }
      });
      socket.send(message);
    }
  };
  
  // 取消订阅
  const unsubscribe = (topic: string): void => {
    subscriptions = subscriptions.filter(sub => sub.topic !== topic);
    
    // 如果已连接，发送取消订阅消息
    if (socket && socket.readyState === WebSocket.OPEN) {
      const message = JSON.stringify({
        type: 'unsubscribe',
        data: { topic }
      });
      socket.send(message);
    }
  };
  
  // 发送消息
  const sendMessage = (type: string, data: any): void => {
    if (socket && socket.readyState === WebSocket.OPEN) {
      const message = JSON.stringify({ type, data });
      socket.send(message);
    } else {
      console.error('WebSocket未连接，无法发送消息');
      // 尝试重新连接
      connect();
    }
  };
  
  // 设置连接回调
  const setOnOpen = (callback: ConnectionCallback): void => {
    onOpenCallback = callback;
  };
  
  // 设置断开连接回调
  const setOnClose = (callback: ConnectionCallback): void => {
    onCloseCallback = callback;
  };
  
  return {
    connect,
    disconnect,
    subscribe,
    unsubscribe,
    sendMessage
  };
};

export {
  createWebSocketClient
};