// 对话状态管理
import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import type { Conversation, Message } from '../types/conversation';
import { getConversations, getConversation, createConversation as apiCreateConversation, deleteConversation as apiDeleteConversation, sendUserMessage } from '../api/conversation';

export const useConversationStore = defineStore('conversation', () => {
  // 状态
  const conversations = ref<Conversation[]>([]);
  const currentConversation = ref<Conversation | null>(null);
  const loading = ref(false);
  const error = ref<string | null>(null);
  
  // 计算属性
  const hasConversations = computed(() => conversations.value.length > 0);
  const currentMessages = computed(() => currentConversation.value?.messages || []);
  
  // 加载对话列表
  async function loadConversations() {
    loading.value = true;
    error.value = null;
    
    try {
      const response = await getConversations();
      conversations.value = response.conversations;
    } catch (err) {
      console.error('加载对话列表失败:', err);
      error.value = '加载对话列表失败';
    } finally {
      loading.value = false;
    }
  }
  
  // 加载单个对话
  async function loadConversation(id: string) {
    loading.value = true;
    error.value = null;
    
    try {
      const conversation = await getConversation(id);
      currentConversation.value = conversation;
    } catch (err) {
      console.error('加载对话失败:', err);
      error.value = '加载对话失败';
    } finally {
      loading.value = false;
    }
  }
  
  // 创建对话
  async function createConversation(title: string) {
    loading.value = true;
    error.value = null;
    
    try {
      const conversation = await apiCreateConversation(title);
      conversations.value.unshift(conversation);
      currentConversation.value = conversation;
      return conversation;
    } catch (err) {
      console.error('创建对话失败:', err);
      error.value = '创建对话失败';
      return null;
    } finally {
      loading.value = false;
    }
  }
  
  // 删除对话
  async function deleteConversation(id: string) {
    loading.value = true;
    error.value = null;
    
    try {
      await apiDeleteConversation(id);
      conversations.value = conversations.value.filter(conv => conv.id !== id);
      
      if (currentConversation.value?.id === id) {
        currentConversation.value = null;
      }
    } catch (err) {
      console.error('删除对话失败:', err);
      error.value = '删除对话失败';
    } finally {
      loading.value = false;
    }
  }
  
  // 发送消息
  async function sendMessage(content: string) {
    if (!currentConversation.value) return;
    
    const conversationId = currentConversation.value.id;
    
    // 创建用户消息
    const userMessage: Message = {
      id: `temp-${Date.now()}`,
      role: 'user',
      content,
      timestamp: new Date().toISOString()
    };
    
    // 添加到当前对话
    addMessage(userMessage);
    
    try {
      // 发送消息并等待回复
      const response = await sendUserMessage(conversationId, content);
      
      // 添加助手回复
      if (response) {
        const assistantMessage: Message = {
          id: response.message_id,
          role: 'assistant',
          content: response.content,
          timestamp: response.timestamp,
          code_blocks: extractCodeBlocks(response.content)
        };
        
        addMessage(assistantMessage);
      }
    } catch (err) {
      console.error('发送消息失败:', err);
      error.value = '发送消息失败';
    }
  }
  
  // 添加消息到当前对话
  function addMessage(message: Message) {
    if (!currentConversation.value) return;
    
    currentConversation.value.messages.push(message);
  }
  
  // 从消息内容中提取代码块
  function extractCodeBlocks(content: string) {
    const codeBlockRegex = /```(\w*)\n([\s\S]*?)```/g;
    const codeBlocks = [];
    let match;
    
    while ((match = codeBlockRegex.exec(content)) !== null) {
      const language = match[1] || 'text';
      const code = match[2];
      
      codeBlocks.push({
        id: `code-${Date.now()}-${codeBlocks.length}`,
        language,
        code
      });
    }
    
    return codeBlocks;
  }
  
  return {
    // 状态
    conversations,
    currentConversation,
    loading,
    error,
    
    // 计算属性
    hasConversations,
    currentMessages,
    
    // 方法
    loadConversations,
    loadConversation,
    createConversation,
    deleteConversation,
    sendMessage
  };
});