<template>
  <div class="flex flex-col items-center justify-center min-h-screen p-6">
    <div class="card max-w-2xl w-full text-center">
      <h1 class="text-3xl font-bold mb-4">欢迎使用 AutoAnalyze</h1>
      <p class="text-lg mb-6">智能数据分析助手，帮助您更高效地理解和处理数据</p>
      
      <div class="mb-8">
        <div v-if="systemStatus.loading" class="flex justify-center">
          <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
        </div>
        <div v-else>
          <!-- 后端服务状态 -->
          <div :class="systemStatus.backendConnected ? 'text-green-500' : 'text-red-500'" class="mb-2">
            <div class="flex items-center justify-center">
              <svg v-if="systemStatus.backendConnected" xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
              </svg>
              <svg v-else xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
              </svg>
              <span>后端服务: {{ systemStatus.backendConnected ? '已连接' : '连接失败' }}</span>
            </div>
          </div>
          
          <div v-if="systemStatus.backendConnected">
            <!-- 模型状态 -->
          <div :class="systemStatus.modelConnected ? 'text-green-500' : 'text-red-500'" class="mb-4">
            <div class="flex items-center justify-center">
              <svg v-if="systemStatus.modelConnected" xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
              </svg>
              <svg v-else xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
              </svg>
              <span>模型状态: {{ systemStatus.modelConnected ? '正常' : '异常' }}</span>
              <span v-if="systemStatus.modelError" class="ml-2 text-xs">({{ systemStatus.modelError }})</span>
            </div>
          </div>
          </div>
          
          <el-button type="primary" class="mt-2" @click="router.push('/settings')">
            {{ (!systemStatus.backendConnected || !systemStatus.modelConnected) ? '前往设置' : '修改配置' }}
          </el-button>
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
import { onMounted, reactive, ref } from 'vue'
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
  backendConnected: false,
  modelConnected: false,
  modelError: ''
})

onMounted(async () => {
  try {
    // 获取系统状态
    const status = await apiService.getSystemStatus()
    systemStatus.backendConnected = !!(status.status)
    systemStatus.modelConnected = status.model.status === 'connected'
    systemStatus.modelError = status.model.error || ''

    // 检查后端服务一致性
    if(workspaceStore.tag!=status.tag){
      //说明服务经过重启了
      workspaceStore.tag=status.tag
      workspaceStore.clearWorkspace()
   
    }
  } catch (error) {
    systemStatus.backendConnected = false
    systemStatus.modelConnected = false
    console.error('Failed to get system status:', error)
  } finally {
    systemStatus.loading = false
  }
})

const directoryPath = ref('')

// 处理路径的辅助函数
const sanitizePath = (path: string): string => {
  const trimmedPath = path.trim()
  if ((trimmedPath.startsWith('"') && trimmedPath.endsWith('"')) || 
      (trimmedPath.startsWith("'") && trimmedPath.endsWith("'"))) {
    ElMessage.warning('路径两端的引号已被自动移除')
    return trimmedPath.slice(1, -1)
  }
  return trimmedPath
}

const handleDirectoryInput = async () => {
  if (!directoryPath.value) {
    ElMessage.warning('请输入目录路径')
    return
  }
  
  const sanitizedPath = sanitizePath(directoryPath.value)
  directoryPath.value = sanitizedPath
  
  try {
    const response = await apiService.setWorkspace(sanitizedPath)
    console.log(response)
    workspaceStore.setWorkspace(response.workspace)
    
    // 创建新对话，不需要手动设置标题
    await conversationStore.createConversation()
    
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