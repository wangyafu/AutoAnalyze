import { defineStore } from 'pinia'
import { ref, reactive } from 'vue'
import { apiService } from '../services/api'

export interface Message {
  id: string
  type: 'user' | 'assistant' | 'tool_start' | 'tool_result'
  content: string
  timestamp: Date
  metadata?: any
}

export const useConversationStore = defineStore('conversation', () => {
  const messages = ref<Message[]>([])
  const loading = ref(false)
  const currentConversationId = ref('')
  
  // 创建新对话
  async function createConversation(title?: string) {
    try {
      const response = await apiService.createConversation(title)
      currentConversationId.value = response.id
      messages.value = []
      return response
    } catch (error) {
      console.error('Failed to create conversation:', error)
      throw error
    }
  }
  
  // 添加用户消息
  function addUserMessage(content: string) {
    const message: Message = {
      id: `user-${Date.now()}`,
      type: 'user',
      content,
      timestamp: new Date()
    }
    
    messages.value.push(message)
    loading.value = true
  }
  
  // 添加助手消息
  function addAssistantMessage(content: string) {
    const message: Message = {
      id: `assistant-${Date.now()}`,
      type: 'assistant',
      content,
      timestamp: new Date()
    }
    
    messages.value.push(message)
  }
  
  // 添加工具调用开始
  function addToolInvocationStart(data: any) {
    const message: Message = {
      id: `tool-start-${data.invocation_id}`,
      type: 'tool_start',
      content: '',
      timestamp: new Date(),
      metadata: {
        invocation_id: data.invocation_id,
        function: data.function,
        arguments: data.arguments
      }
    }
    
    messages.value.push(message)
  }
  
  // 添加工具调用结果
  function addToolInvocationResult(data: any) {
    const message: Message = {
      id: `tool-result-${data.invocation_id}`,
      type: 'tool_result',
      content: '',
      timestamp: new Date(),
      metadata: {
        invocation_id: data.invocation_id,
        function: data.function,
        result: data.result
      }
    }
    
    messages.value.push(message)
  }
  
  // 设置加载状态
  function setLoading(value: boolean) {
    loading.value = value
  }
  
  return {
    messages,
    loading,
    currentConversationId,
    createConversation,
    addUserMessage,
    addAssistantMessage,
    addToolInvocationStart,
    addToolInvocationResult,
    setLoading
  }
})