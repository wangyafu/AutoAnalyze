import { ref } from 'vue'
import { configService } from './config'
import { useConversationStore } from '../stores/conversation'
import { useCodeExecutionStore } from '../stores/codeExecution'
import { ElMessage } from 'element-plus'
import type { OutputItem, ImageItem, ExecutionStatus } from '../types'

// 删除原有的 WS_URL 常量
// const WS_URL = 'ws://127.0.0.1:8000/ws'

export const websocketService = {
  socket: null as WebSocket | null,
  connected: ref(false),
  reconnectAttempts: 0,
  maxReconnectAttempts: 5,
  reconnectTimeout: null as ReturnType<typeof setTimeout> | null,
  executionStatus: ref<{[key: string]: ExecutionStatus}>({}),
  
  /**
   * 建立WebSocket连接
   */
  connect() {
    if (this.socket?.readyState === WebSocket.OPEN) return
    
    // 使用 configService 获取 WebSocket URL
    this.socket = new WebSocket(configService.getWebsocketUrl())
    
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
  sendUserMessage(data: { conversation_id: string; content: string;use_dual_agent: boolean;}) {
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
    const codeExecutionStore = useCodeExecutionStore()
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
        if (message.data.function === 'exec_code') {
          // 使用codeExecutionStore初始化执行状态
          codeExecutionStore.initExecution(message.data.invocation_id)
          // 保持兼容性，同时更新本地状态
          this.executionStatus.value[message.data.invocation_id] = {
            status: 'running',
            output: [],
            images: []
          }
        }
        break
        
      case 'tool_invocation_result':
        conversationStore.addToolInvocationResult(message.data)
        if (message.data.function === 'exec_code') {
          const executionId = message.data.invocation_id
          // 使用codeExecutionStore更新执行状态
          codeExecutionStore.updateExecutionStatus(executionId, message.data.result.status)
          if (message.data.result.error) {
            codeExecutionStore.setError(executionId, message.data.result.error)
          }
          // 保持兼容性，同时更新本地状态
          this.executionStatus.value[executionId] = {
            status: message.data.result.status,
            output: message.data.result.output || [],
            images: message.data.result.images || [],
            error: message.data.result.error
          }
        }
        break
        
      case 'code_execution_start':
        // 处理代码执行开始消息
        const startExecutionId = message.data.execution_id
        codeExecutionStore.initExecution(startExecutionId)
        // 保持兼容性，同时更新本地状态
        this.executionStatus.value[startExecutionId] = {
          status: 'running',
          output: [],
          images: []
        }
        // 添加到会话中显示
        conversationStore.addCodeExecutionStart({
          execution_id: startExecutionId,
          code: message.data.code
        })
        break
        
      case 'code_execution_output':
        const executionId = message.data.execution_id
        // 使用codeExecutionStore添加输出
        codeExecutionStore.addOutput(executionId, message.data.output)
        // 保持兼容性，同时更新本地状态
        if (this.executionStatus.value[executionId]) {
          // 添加到输出列表
          this.executionStatus.value[executionId].output.push(message.data.output)
          
          // 如果是图片类型，也添加到图片列表
          if (message.data.output.type === 'image') {
            this.executionStatus.value[executionId].images.push(message.data.output)
          }
        }
        break
        
      case 'code_execution_image':
        // 处理专门的图片消息类型
        const imgExecutionId = message.data.execution_id
        const imageData: ImageItem = {
          type: 'image',
          format: message.data.image_format || 'png',
          data: message.data.image_data
        }
        // 使用codeExecutionStore添加图片
        codeExecutionStore.addImage(imgExecutionId, imageData)
        // 保持兼容性，同时更新本地状态
        if (this.executionStatus.value[imgExecutionId]) {
          this.executionStatus.value[imgExecutionId].images.push(imageData)
        }
        break
        
      case 'code_execution_end':
        // 处理代码执行结束消息
        const endExecutionId = message.data.execution_id
        codeExecutionStore.updateExecutionStatus(endExecutionId, message.data.status)
        // 保持兼容性，同时更新本地状态
        if (this.executionStatus.value[endExecutionId]) {
          this.executionStatus.value[endExecutionId].status = message.data.status
        }
        break
      case 'user_agent_message':
        conversationStore.addUserAssistantMessage(message.data.content)
        break
      case 'done':
        conversationStore.setLoading(false)
        ElMessage.success("智能体回复完毕")
        console.log("智能体回复完毕")
        break
      case 'error':
        // 处理服务器返回的错误消息
        console.error('服务器错误:', message.data)
        // 显示错误提示
        ElMessage.error(
          message.data.message || '服务器发生错误',)
          
        // 如果有详细错误信息，在控制台输出
        if (message.data.details) {
          console.error('错误详情:', message.data.details)
        }
        // 如果正在加载中，取消加载状态
        conversationStore.setLoading(false)
        break
      
        
      default:
        console.log('未处理的WebSocket消息类型:', message.type)
    }
  }
}
  