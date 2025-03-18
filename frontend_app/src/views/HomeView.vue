<template>
  <div class="flex flex-col items-center justify-center min-h-screen p-6">
    <div class="card max-w-2xl w-full text-center">
      <h1 class="text-3xl font-bold mb-4">欢迎使用 DeepAnalyze</h1>
      <p class="text-lg mb-6">智能数据分析助手，帮助您更高效地理解和处理数据</p>
      
      <div class="mb-8">
        <div v-if="systemStatus.loading" class="flex justify-center">
          <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
        </div>
        <div v-else-if="systemStatus.connected" class="text-green-500 mb-4">
          <div class="flex items-center justify-center">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
            </svg>
            <span>系统已连接，模型状态正常</span>
          </div>
        </div>
        <div v-else class="text-red-500 mb-4">
          <div class="flex items-center justify-center">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
            </svg>
            <span>系统连接异常，请前往设置页面配置</span>
          </div>
          <el-button type="primary" class="mt-2" @click="router.push('/settings')">前往设置</el-button>
        </div>
      </div>
      
      <div class="mb-6">
        <h2 class="text-xl font-semibold mb-3">选择工作目录</h2>
        <p class="mb-4">请输入要分析的项目目录完整路径：</p>
        <div class="flex justify-center space-x-2">
          <el-input
            v-model="directoryPath"
            placeholder="例如：D:\project\data"
            class="max-w-md"
          />
          <el-button type="primary" @click="handleDirectoryInput">确认</el-button>
        </div>
      </div>
      
      <div v-if="workspaceStore.currentWorkspace" class="mt-4">
        <p>当前工作目录: <span class="font-medium">{{ workspaceStore.currentWorkspace }}</span></p>
        <el-button type="success" class="mt-4" @click="router.push('/workspace')">进入工作区</el-button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, reactive,ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useWorkspaceStore} from '../stores/workspace'
import { useConversationStore} from '../stores/conversation'
import { apiService } from '../services/api'

const router = useRouter()
const workspaceStore = useWorkspaceStore()
const conversationStore=useConversationStore()
const systemStatus = reactive({
  loading: true,
  connected: false
})

onMounted(async () => {
  try {
    const status = await apiService.getSystemStatus()
    systemStatus.connected = status.model.status === 'connected'
  } catch (error) {
    systemStatus.connected = false
    console.error('Failed to get system status:', error)
  } finally {
    systemStatus.loading = false
  }
})

const directoryPath = ref('')

const handleDirectoryInput = async () => {
  if (!directoryPath.value) {
    ElMessage.warning('请输入目录路径')
    return
  }
  
  try {
    const response = await apiService.setWorkspace(directoryPath.value)
    workspaceStore.setWorkspace(response.workspace)
    
    // 创建新对话，使用当前时间作为标题
    const now = new Date()
    const title = now.toLocaleString('zh-CN', { 
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit'
    })
    await conversationStore.createConversation(title)
    
    ElMessage.success('工作目录设置成功')
    router.push('/workspace')
  } catch (error) {
    console.error('Failed to set workspace:', error)
    ElMessage.error('设置工作目录失败')
  }
}

// 删除不再需要的代码
// const dirInput = ref<HTMLInputElement | null>(null)
// const triggerDirectorySelect = () => { ... }
// const handleDirectorySelect = async (event: Event) => { ... }
</script>