<template>
  <div class="flex h-screen overflow-hidden">
    <!-- 左侧文件浏览器 -->
    <div class="w-1/4 bg-white border-r border-gray-200 overflow-y-auto">
      <div class="p-4 border-b border-gray-200">
        <h2 class="text-lg font-semibold">{{ $t('workspace.fileExplorer.title') }}</h2>
        <p class="text-sm text-gray-500 mt-1">{{ workspaceStore.currentWorkspace }}</p>
      </div>
      <FileExplorer @filePreview="handleFilePreview"/>
    </div>
    
    <!-- 右侧聊天区域 -->
    <div class="flex-1 flex flex-col overflow-hidden">
      <div class="p-4 border-b border-gray-200 flex justify-between items-center">
        <h2 class="text-lg font-semibold">{{ $t('workspace.chat.title') }}</h2>
        <div class="flex gap-2 items-center">
          <el-switch
            v-model="useDualAgent"
            :active-text="$t('workspace.chat.agent.dual')"
            :inactive-text="$t('workspace.chat.agent.single')"
            @change="handleAgentModeChange"
          />
          <el-button size="small" type="danger" @click="clearHistory">
            {{ $t('workspace.chat.buttons.clearHistory') }}
          </el-button>
          <el-button size="small" @click="router.push('/')">
            {{ $t('workspace.chat.buttons.returnHome') }}
          </el-button>
        </div>
      </div>
      
      <div class="flex-1 overflow-y-auto p-4" ref="chatContainer">
        <ChatHistory :messages="conversationStore.messages" />
      </div>
      
      <div class="border-t border-gray-200 p-4">
        <ChatInput 
          @send="sendMessage" 
        />
      </div>
    </div>
    
    <!-- 使用封装的文件预览组件 -->
    <FilePreviewDialog
      v-model="showPreview"
      :file="previewFile"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, nextTick, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'  // 添加这行
import { ElMessage, ElMessageBox } from 'element-plus'
import FileExplorer from '../components/file/FileExplorer.vue'
import ChatHistory from '../components/chat/ChatHistory.vue'
import ChatInput from '../components/chat/ChatInput.vue'
import FilePreviewDialog from '../components/file/FilePreviewDialog.vue'
import { useWorkspaceStore } from '../stores/workspace'
import { useConversationStore } from '../stores/conversation'
import { websocketService } from '../services/websocket'
import { filePreviewService } from '../services/filePreview'
import type { FilePreview } from '../types'

const router = useRouter()
const workspaceStore = useWorkspaceStore()
const conversationStore = useConversationStore()
const chatContainer = ref<HTMLElement | null>(null)

const showPreview = ref(false)
const previewFile = ref<FilePreview | null>(null)
// 添加智能体模式切换状态
const useDualAgent = ref(false)

// 如果没有设置工作目录，重定向到首页
onMounted(() => {
  if (!workspaceStore.currentWorkspace) {
    ElMessage.warning(t('workspace.messages.selectWorkspace'))
    router.push('/')
    return
  }
  
  // 初始化WebSocket连接
  websocketService.connect()
})

// 处理智能体模式切换
function handleAgentModeChange(value: boolean) {
  const mode = value ? t('workspace.chat.agent.dual') : t('workspace.chat.agent.single')
  ElMessage.info(t('workspace.chat.agent.switchMessage', { mode }))
}

async function handleFilePreview(path: string) {
  const data = await filePreviewService.getFilePreview(path)
  if (data) {
    previewFile.value = data
    showPreview.value = true
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
  const toSend={
    conversation_id: conversationStore.currentConversationId,
    content,
    use_dual_agent: useDualAgent.value // 添加智能体模式信息
  }
  console.log(toSend)
  websocketService.sendUserMessage(toSend)
}

// 清空会话历史
async function clearHistory() {
  try {
    await ElMessageBox.confirm(
      t('workspace.messages.clearConfirm'),
      t('workspace.messages.warning'),
      {
        confirmButtonText: t('workspace.messages.confirm'),
        cancelButtonText: t('workspace.messages.cancel'),
        type: 'warning',
      }
    )
    await conversationStore.createConversation()
    ElMessage.success(t('workspace.messages.clearSuccess'))
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error(t('workspace.messages.clearFailed'))
    }
  }
}
</script>

