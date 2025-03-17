<template>
  <div class="flex flex-col h-full bg-white rounded-lg shadow-lg overflow-hidden">
    <div class="flex justify-between items-center px-4 py-3 bg-gradient-to-r from-blue-500 to-blue-600 text-white">
      <h2 class="text-xl font-semibold">{{ conversation ? conversation.title : '对话' }}</h2>
      <div class="flex gap-2">
        <el-button
          @click="$emit('close')"
          type="danger"
          size="small"
          :icon="Close"
          circle
        />
      </div>
    </div>
    
    <message-list 
      :messages="messages" 
      class="message-list"
      @execute-code="handleExecuteCode"
    />
    
    <message-input 
      :placeholder="'输入消息...'"
      :disabled="isLoading"
      @submit="handleSendMessage"
      class="message-input"
    />
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue';
import type { Conversation } from '../../types/conversation';
import MessageList from './MessageList.vue';
import MessageInput from './MessageInput.vue';
import { useConversationStore } from '../../stores/conversation';
import { Close } from '@element-plus/icons-vue';
// Props
const props = defineProps<{
  conversation?: Conversation;
}>();

// Emits
const emit = defineEmits<{
  (e: 'send-message', content: string): void;
  (e: 'execute-code', code: string, codeBlockId: string): void;
  (e: 'close'): void;
}>();

// Store
const conversationStore = useConversationStore();

// State
const isLoading = ref(false);

// Computed
const messages = computed(() => props.conversation?.messages || []);

// Methods
const handleSendMessage = async (content: string) => {
  if (!content.trim() || !props.conversation) return;
  
  isLoading.value = true;
  
  try {
    await conversationStore.sendMessage(content);
    emit('send-message', content);
  } catch (error) {
    console.error('发送消息失败:', error);
  } finally {
    isLoading.value = false;
  }
};

const handleExecuteCode = (code: string, codeBlockId: string) => {
  emit('execute-code', code, codeBlockId);
};
</script>


