import { defineStore } from 'pinia'
import { ref, reactive } from 'vue'
import { apiService } from '../services/api'
import { useWorkspaceStore } from './workspace'
export interface Message {
  id: string
  type: 'user' | 'assistant' | 'tool_start' | 'tool_result' | 'code_execution_start'|"user_assistant"
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
      // 如果没有提供标题，使用当前时间作为标题
      const defaultTitle = new Date().toLocaleString('zh-CN', { 
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit'
      })
      
      const response = await apiService.createConversation(title || defaultTitle)
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
  function addUserAssistantMessage(content: string) {
    const message: Message = {
      id: `assistant-${Date.now()}`,
      type: 'user_assistant',
      content,
      timestamp: new Date()
    }

    messages.value.push(message)
    loading.value = false
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
    const fileStore=useWorkspaceStore()
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
    if (message.metadata.function=='exec_code'){
      fileStore.loadFiles()
    }
    messages.value.push(message)
  }
  
  // 设置加载状态
  function setLoading(value: boolean) {
    loading.value = value
  }
  
  // 添加代码执行开始消息
  function addCodeExecutionStart(data: { execution_id: string; code: string }) {
    const message: Message = {
      id: `code-exec-start-${data.execution_id}`,
      type: 'code_execution_start',
      content: '',
      timestamp: new Date(),
      metadata: {
        execution_id: data.execution_id,
        code: data.code
      }
    }
    
    messages.value.push(message)
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
    setLoading,
    addCodeExecutionStart,
    addUserAssistantMessage
  }
})