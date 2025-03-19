<template>
  <div class="flex h-screen overflow-hidden">
    <!-- 左侧文件浏览器 -->
    <div class="w-1/4 bg-white border-r border-gray-200 overflow-y-auto">
      <div class="p-4 border-b border-gray-200">
        <h2 class="text-lg font-semibold">文件浏览器</h2>
        <p class="text-sm text-gray-500 mt-1">{{ workspaceStore.currentWorkspace }}</p>
      </div>
      <FileExplorer @filePreview="handleFilePreview"/>
    </div>
    
    <!-- 右侧聊天区域 -->
    <div class="flex-1 flex flex-col overflow-hidden">
      <div class="p-4 border-b border-gray-200 flex justify-between items-center">
        <h2 class="text-lg font-semibold">数据分析助手</h2>
        <el-button size="small" @click="router.push('/')">返回首页</el-button>
      </div>
      
      <div class="flex-1 overflow-y-auto p-4" ref="chatContainer">
        <ChatHistory :messages="conversationStore.messages" />
      </div>
      
      <div class="border-t border-gray-200 p-4">
        <ChatInput 
          :loading="conversationStore.loading" 
          @send="sendMessage" 
        />
      </div>
    </div>
    
    <!-- 文件预览对话框 -->
    <el-dialog
      v-model="showPreview"
      :title="previewFile?.path"
      width="60%"
      destroy-on-close
    >
      <pre class="whitespace-pre-wrap break-words">{{ previewFile?.content }}</pre>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, nextTick, watch } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import FileExplorer from '../components/file/FileExplorer.vue'
import ChatHistory from '../components/chat/ChatHistory.vue'
import ChatInput from '../components/chat/ChatInput.vue'
import { useWorkspaceStore } from '../stores/workspace'
import { useConversationStore } from '../stores/conversation'
import { websocketService } from '../services/websocket'
import { apiService } from '../services/api'
import type { FilePreview } from '../types'
const router = useRouter()
const workspaceStore = useWorkspaceStore()
const conversationStore = useConversationStore()
const chatContainer = ref<HTMLElement | null>(null)

const showPreview = ref(false)
const previewFile = ref<FilePreview | null>(null)

// 如果没有设置工作目录，重定向到首页
onMounted(() => {
  if (!workspaceStore.currentWorkspace) {
    ElMessage.warning('请先选择工作目录')
    router.push('/')
    return
  }
  
  // 初始化WebSocket连接
  websocketService.connect()
})

async function handleFilePreview(path: string) {
  try {
    const response = await apiService.getFilePreview(path)
    
      const data = response as FilePreview
      console.log('File preview:', data)
      if (data.is_binary) {
        ElMessage.warning('二进制文件无法预览')
        return
      }
      previewFile.value = data
      showPreview.value = true
    
  } catch (error) {
    ElMessage.error('文件预览失败')
  }
}

// 监听消息变化，自动滚动到底部
watch(
  () => conversationStore.messages.length,
  async () => {
    await nextTick()
    if (chatContainer.value) {
      chatContainer.value.scrollTop = chatContainer.value.scrollHeight
    }
  }
)

// 发送消息
const sendMessage = (content: string) => {
  if (!content.trim()) return
  
  conversationStore.addUserMessage(content)
  websocketService.sendUserMessage({
    conversation_id: conversationStore.currentConversationId,
    content
  })
}
</script>