<template>
  <div class="h-full overflow-y-auto p-4" ref="listRef">
    <div v-if="messages.length === 0" class="flex flex-col items-center justify-center h-full text-gray-500">
      <el-empty description="没有消息" />
      <p class="mt-2 text-sm opacity-70">发送消息开始对话</p>
    </div>
    
    <template v-else>
      <message-item 
        v-for="message in messages" 
        :key="message.id" 
        :message="message"
        @execute-code="$emit('execute-code', $event.code, $event.codeBlockId)"
      />
    </template>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, nextTick } from 'vue';
import type { Message } from '../../types/conversation';
import MessageItem from './MessageItem.vue';

// Props
const props = defineProps<{
  messages: Message[];
}>();

// Emits
const emit = defineEmits<{
  (e: 'execute-code', code: string, codeBlockId: string): void;
}>();

// Refs
const listRef = ref<HTMLElement | null>(null);

// 监听消息变化，自动滚动到底部
watch(() => props.messages.length, async () => {
  await nextTick();
  scrollToBottom();
});

// 滚动到底部
const scrollToBottom = () => {
  if (listRef.value) {
    listRef.value.scrollTop = listRef.value.scrollHeight;
  }
};
</script>

