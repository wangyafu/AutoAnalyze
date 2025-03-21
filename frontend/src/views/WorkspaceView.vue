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
        <div class="flex gap-2">
          <el-button size="small" type="danger" @click="clearHistory">清空会话</el-button>
          <el-button size="small" @click="router.push('/')">返回首页</el-button>
        </div>
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
      <!-- 文本文件预览 -->
      <pre v-if="previewFile?.preview_type === 'text'" class="whitespace-pre-wrap break-words">{{ previewFile?.content }}</pre>
      
      <!-- 图片预览 -->
      <div v-else-if="previewFile?.preview_type === 'image'" class="text-center">
        <img v-if="previewFile?.base64_data" :src="`data:image/${getImageType(previewFile.name)};base64,${previewFile.base64_data}`" class="max-w-full max-h-[70vh]" />
        <p v-else class="text-gray-500">无法预览图片</p>
      </div>
      
      <!-- Excel/CSV预览 -->
      <div v-else-if="['excel', 'csv'].includes(previewFile?.preview_type || '')" class="overflow-x-auto">
        <table v-if="previewFile?.structured_data" class="min-w-full border-collapse border border-gray-300">
          <thead>
            <tr>
              <th v-for="(column, index) in previewFile.structured_data.columns" :key="index" class="border border-gray-300 px-4 py-2 bg-gray-100">
                {{ column }}
              </th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(row, rowIndex) in previewFile.structured_data.data" :key="rowIndex">
              <td v-for="(cell, cellIndex) in row" :key="cellIndex" class="border border-gray-300 px-4 py-2">
                {{ cell }}
              </td>
            </tr>
          </tbody>
        </table>
        <p v-else class="text-gray-500">无法预览表格数据</p>
      </div>
      
      <!-- Word/PPT文档预览 -->
      <div v-else-if="previewFile?.preview_type === 'markdown'" class="document-preview">
        <div v-if="previewFile?.markdown_content" v-html="renderDocumentContent(previewFile)" class="markdown-body"></div>
        <p v-else class="text-gray-500">无法预览文档内容</p>
        <div v-if="previewFile?.is_truncated" class="text-gray-500 mt-4 text-center">
          [文档内容过长，仅显示部分内容]
        </div>
      </div>
      
      <!-- 其他文件类型 -->
      <div v-else class="text-center text-gray-500">
        <p>{{ previewFile?.content || '无法预览此类型文件' }}</p>
      </div>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, nextTick, watch } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage,ElMessageBox } from 'element-plus'
import FileExplorer from '../components/file/FileExplorer.vue'
import ChatHistory from '../components/chat/ChatHistory.vue'
import ChatInput from '../components/chat/ChatInput.vue'
import { useWorkspaceStore } from '../stores/workspace'
import { useConversationStore } from '../stores/conversation'
import { websocketService } from '../services/websocket'
import { apiService } from '../services/api'
import type { FilePreview } from '../types'
import { renderMarkdown, renderDocumentPreview } from '../utils/markdown'

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
      if (data.is_binary && !data.preview_type) {
        ElMessage.warning('二进制文件无法预览')
        return
      }
      previewFile.value = data
      showPreview.value = true
    
  } catch (error) {
    ElMessage.error('文件预览失败')
  }
}

// 根据文件名获取图片类型
function getImageType(filename: string): string {
  if (!filename) return 'png'
  const extension = filename.split('.').pop()?.toLowerCase() || ''
  
  switch (extension) {
    case 'jpg':
    case 'jpeg':
      return 'jpeg'
    case 'png':
      return 'png'
    case 'gif':
      return 'gif'
    case 'svg':
      return 'svg+xml'
    case 'webp':
      return 'webp'
    default:
      return 'png'
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

// 渲染文档内容
function renderDocumentContent(file: FilePreview): string {
  if (!file.markdown_content) return ''
  
  return renderDocumentPreview(file.markdown_content, file.document_metadata)
}

// 清空会话历史
async function clearHistory() {
  try {
    await ElMessageBox.confirm(
      '确定要清空当前会话历史吗？此操作不可恢复。',
      '警告',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning',
      }
    )
    await conversationStore.createConversation()
    ElMessage.success('会话已清空')
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('清空会话失败')
    }
  }
}
</script>

<style>
/* 添加文档预览样式 */
.document-preview {
  max-height: 70vh;
  overflow-y: auto;
  padding: 1rem;
}

.markdown-body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif;
  line-height: 1.6;
}

.document-meta {
  margin-bottom: 2rem;
}

.document-meta h1 {
  font-size: 1.8rem;
  margin-bottom: 0.5rem;
}

.meta-item {
  color: #666;
  font-size: 0.9rem;
}

.document-meta hr {
  margin: 1rem 0;
  border: 0;
  border-top: 1px solid #eee;
}


</style>

