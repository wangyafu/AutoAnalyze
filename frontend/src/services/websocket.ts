import { ref } from 'vue'
import { useConversationStore } from '../stores/conversation'
import { ElMessage } from 'element-plus'

const WS_URL = 'ws://127.0.0.1:8000/ws'

export const websocketService = {
  socket: null as WebSocket | null,
  connected: ref(false),
  reconnectAttempts: 0,
  maxReconnectAttempts: 5,
  reconnectTimeout: null as ReturnType<typeof setTimeout> | null,
  
  /**
   * 建立WebSocket连接
   */
  connect() {
    if (this.socket?.readyState === WebSocket.OPEN) return
    
    this.socket = new WebSocket(WS_URL)
    
    this.socket.onopen = () => {
      console.log('WebSocket连接已建立')
      this.connected.value = true
      this.reconnectAttempts = 0
    }
    
    this.socket.onclose = (event) => {
      console.log('WebSocket连接已关闭', event)
      ElMessage.error('WebSocket连接已关闭')
      this.connected.value = false
      this.attemptReconnect()
    }
    
    this.socket.onerror = (error) => {
      console.error('WebSocket错误:', error)
    }
    
    this.socket.onmessage = (event) => {
      try {
        const message = JSON.parse(event.data)
        this.handleMessage(message)
      } catch (error) {
        console.error('解析WebSocket消息失败:', error)
      }
    }
  },
  
  /**
   * 关闭WebSocket连接
   */
  disconnect() {
    if (this.socket) {
      this.socket.close()
      this.socket = null
    }
    
    if (this.reconnectTimeout) {
      clearTimeout(this.reconnectTimeout)
      this.reconnectTimeout = null
    }
  },
  
  /**
   * 尝试重新连接
   */
  attemptReconnect() {
    if (this.reconnectAttempts >= this.maxReconnectAttempts) {
      console.error('WebSocket重连失败，已达到最大尝试次数')
      return
    }
    
    this.reconnectAttempts++
    const delay = Math.min(1000 * Math.pow(2, this.reconnectAttempts), 30000)
    
    console.log(`WebSocket将在${delay}ms后尝试重连...`)
    
    this.reconnectTimeout = setTimeout(() => {
      console.log(`正在尝试WebSocket重连 (${this.reconnectAttempts}/${this.maxReconnectAttempts})`)
      this.connect()
    }, delay)
  },
  
  /**
   * 发送用户消息
   */
  sendUserMessage(data: { conversation_id: string; content: string }) {
    if (!this.socket || this.socket.readyState !== WebSocket.OPEN) {
      console.error('WebSocket未连接，无法发送消息')
      ElMessage.error('WebSocket未连接，无法发送消息')
      return
    }
    
    this.socket.send(JSON.stringify({
      type: 'user_message',
      data
    }))
  },
  
  /**
   * 处理接收到的消息
   */
  handleMessage(message: any) {
    const conversationStore = useConversationStore()
    console.log("接收到websocket消息",message)
    switch (message.type) {
      case 'connection_established':
        console.log('WebSocket连接已成功建立:', message.data.message)
        // 显示Element Plus消息提示
        ElMessage({
          message: '已成功和服务器建立websocket连接',
          type: 'success',
          duration: 3000
        })
        break
        
      case 'assistant_message':
        conversationStore.addAssistantMessage(message.data.content)
        break
        
      case 'tool_invocation_start':
        conversationStore.addToolInvocationStart(message.data)
        break
        
      case 'tool_invocation_result':
        conversationStore.addToolInvocationResult(message.data)
        
        break
        
      case 'done':
        conversationStore.setLoading(false)
        break
        
      default:
        console.log('未处理的WebSocket消息类型:', message.type)
    }
  }
}