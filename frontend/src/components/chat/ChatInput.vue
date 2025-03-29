<template>
  <div class="chat-input w-full">
    <el-input
      v-model="message"
      type="textarea"
      :rows="3"
      :disabled="conversationStore.loading"
      :placeholder="$t('chat.input.placeholder')"
      resize="none"
      @keydown.enter.ctrl.prevent="sendMessage"
    />
    <div class="flex justify-between items-center mt-2">
      <div class="text-xs text-gray-500">
        {{ $t('chat.input.sendHint') }}
      </div>
      <el-button 
        type="primary" 
        :disabled="!message.trim() || conversationStore.loading" 
        :loading="conversationStore.loading"
        @click="sendMessage"
      >
        {{ $t('chat.input.send') }}
      </el-button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, defineEmits } from 'vue'
import { useI18n } from 'vue-i18n'
import { useConversationStore } from '@/stores/conversation'

const { t } = useI18n()
const emit = defineEmits(['send'])
const message = ref('')
const conversationStore = useConversationStore()

function sendMessage() {
  if (!message.value.trim() || conversationStore.loading) return
  
  emit('send', message.value)
  message.value = ''
}
</script>

