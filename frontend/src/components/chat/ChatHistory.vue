<template>
  <div class="chat-history space-y-4;">
    <MessageItem 
      v-for="message in messages" 
      :key="message.id" 
      :message="message" 
    />
  </div>
</template>

<script setup lang="ts">
import { defineProps } from 'vue'
import type { Message } from '../../stores/conversation'
import MessageItem from './MessageItem.vue'

const props = defineProps({
  messages: {
    type: Array as () => Message[],
    required: true
  }
})
</script>

<style scoped>
/* 可以添加额外的样式 */
</style>