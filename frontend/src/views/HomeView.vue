<template>
  <div class="flex flex-col items-center justify-center min-h-screen p-6">
    <div class="card max-w-4xl w-full text-center">
      <h1 class="text-3xl font-bold mb-4">欢迎使用 AutoAnalyze</h1>
      <p class="text-lg mb-6">智能数据分析助手，帮助您更高效地理解和处理数据</p>
      
      <!-- 系统状态部分 -->
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
            <!-- 工作目录选择部分 -->
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
      <!-- 功能特色展示部分 -->
      <div class="mb-8 bg-gray-50 p-6 rounded-lg shadow-inner text-left">
        <h2 class="text-2xl font-semibold mb-4 text-center">功能亮点</h2>
        <div class="grid md:grid-cols-2 gap-6">
          <div class="feature-card">
            <div class="text-blue-600 mb-2">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-8 w-8" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 8h10M7 12h4m1 8l-4-4H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-3l-4 4z" />
              </svg>
            </div>
            <h3 class="text-lg font-medium mb-2">自然语言交互</h3>
            <p>通过自然语言描述需求，AI会自动编写Python代码并执行，无需编程知识</p>
          </div>
          
          <div class="feature-card">
            <div class="text-green-600 mb-2">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-8 w-8" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 17v-2m3 2v-4m3 4v-6m2 10H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
            </div>
            <h3 class="text-lg font-medium mb-2">数据可视化</h3>
            <p>支持显示图像输出，生成专业水准的图表和可视化效果</p>
          </div>
          
          <div class="feature-card">
            <div class="text-purple-600 mb-2">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-8 w-8" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
              </svg>
            </div>
            <h3 class="text-lg font-medium mb-2">实时工具调用</h3>
            <p>实时查看AI对工具的调用情况，透明化分析过程</p>
          </div>
          
          <div class="feature-card">
            <div class="text-yellow-600 mb-2">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-8 w-8" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
              </svg>
            </div>
            <h3 class="text-lg font-medium mb-2">自定义模型</h3>
            <p>支持配置不同的大模型，包括双智能体模式和视觉模型</p>
          </div>
        </div>
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
      ElMessage.warning('后端服务已重启')
      //说明服务经过重启了
      workspaceStore.tag=status.tag
      workspaceStore.clearWorkspace()
   
    }
  } catch (error) {
    systemStatus.backendConnected = false
    systemStatus.modelConnected = false
    console.error('Failed to get system status:', error)
    ElMessage.error('获取系统状态失败')
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
</script>

<style scoped>
.feature-card {
  background-color: white;
  padding: 1rem;
  border-radius: 0.5rem;
  box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
  border: 1px solid #f3f4f6;
  transition: box-shadow 0.3s ease;
}

.feature-card:hover {
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
}

</style>