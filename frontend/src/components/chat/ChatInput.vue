<template>
  <div class="chat-input w-full">
    <el-input
      v-model="message"
      type="textarea"
      :rows="3"
      :disabled="loading"
      placeholder="输入您的问题或指令..."
      resize="none"
      @keydown.enter.ctrl.prevent="sendMessage"
    />
    <div class="flex justify-between items-center mt-2">
      <div class="text-xs text-gray-500">
        按 Ctrl+Enter 发送
      </div>
      <el-button 
        type="primary" 
        :disabled="!message.trim() || loading" 
        :loading="loading"
        @click="sendMessage"
      >
        发送
      </el-button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, defineProps, defineEmits } from 'vue'

const props = defineProps({
  loading: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['send'])
const message = ref('')

function sendMessage() {
  if (!message.value.trim() || props.loading) return
  
  emit('send', message.value)
  message.value = ''
}
</script>

