<template>
  <div class="flex flex-col items-center justify-center min-h-screen p-6">
    <div class="card max-w-4xl w-full text-center">
      <!-- 添加语言切换按钮 -->
      <div class="absolute top-4 right-4">
        <el-button type="text" @click="toggleLanguage">
          {{ currentLocale === 'zh-CN' ? 'English' : '中文' }}
        </el-button>
      </div>

      <h1 class="text-3xl font-bold mb-4">{{ $t('home.title') }}</h1>
      <p class="text-lg mb-6">{{ $t('home.subtitle') }}</p>
      
      <!-- 系统状态部分 -->
      <div class="mb-8">
        <div v-if="systemStatus.loading" class="flex justify-center">
          <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
        </div>
        <div v-else>
          <!-- 后端服务状态 -->
          <div :class="systemStatus.backendConnected ? 'text-green-500' : 'text-red-500'" class="mb-2">
            <div class="flex items-center justify-center">
              <!-- SVG 图标保持不变 -->
              <span>{{ $t('home.systemStatus.backendService') }}: {{ systemStatus.backendConnected ? $t('home.systemStatus.connected') : $t('home.systemStatus.connectionFailed') }}</span>
            </div>
          </div>
          
          <div v-if="systemStatus.backendConnected">
            <!-- 模型状态 -->
            <div :class="systemStatus.modelConnected ? 'text-green-500' : 'text-red-500'" class="mb-4">
              <div class="flex items-center justify-center">
                <!-- SVG 图标保持不变 -->
                <span>{{ $t('home.systemStatus.modelStatus') }}: {{ systemStatus.modelConnected ? $t('home.systemStatus.normal') : $t('home.systemStatus.abnormal') }}</span>
                <span v-if="systemStatus.modelError" class="ml-2 text-xs">({{ systemStatus.modelError }})</span>
              </div>
            </div>
          </div>
          
          <el-button type="primary" class="mt-2" @click="router.push('/settings')">
            {{ (!systemStatus.backendConnected || !systemStatus.modelConnected) ? $t('home.systemStatus.goToSettings') : $t('home.systemStatus.modifyConfig') }}
          </el-button>
        </div>
      </div>

      <!-- 工作目录选择部分 -->
      <div class="mb-6">
        <h2 class="text-xl font-semibold mb-3">{{ $t('home.workspace.title') }}</h2>
        <p class="mb-4">{{ $t('home.workspace.description') }}</p>
        <div class="flex justify-center space-x-2">
          <el-input
            v-model="directoryPath"
            :placeholder="$t('home.workspace.placeholder')"
            class="max-w-md"
          />
          <el-button type="primary" @click="handleDirectoryInput">{{ $t('home.workspace.confirm') }}</el-button>
        </div>
      </div>
      <div v-if="workspaceStore.currentWorkspace" class="mt-4">
        <p>{{ $t('home.workspace.current') }}: <span class="font-medium">{{ workspaceStore.currentWorkspace }}</span></p>
        <el-button type="success" class="mt-4" @click="router.push('/workspace')">{{ $t('home.workspace.enterWorkspace') }}</el-button>
      </div>

      <!-- 功能特色展示部分 -->
      <div class="mb-8 bg-gray-50 p-6 rounded-lg shadow-inner text-left">
        <h2 class="text-2xl font-semibold mb-4 text-center">{{ $t('home.features.title') }}</h2>
        <div class="grid md:grid-cols-2 gap-6">
          <div class="feature-card">
            <div class="text-blue-600 mb-2">
              <!-- SVG 图标保持不变 -->
            </div>
            <h3 class="text-lg font-medium mb-2">{{ $t('home.features.naturalLanguage.title') }}</h3>
            <p>{{ $t('home.features.naturalLanguage.description') }}</p>
          </div>
          
          <div class="feature-card">
            <div class="text-green-600 mb-2">
              <!-- SVG 图标保持不变 -->
            </div>
            <h3 class="text-lg font-medium mb-2">{{ $t('home.features.dataVisualization.title') }}</h3>
            <p>{{ $t('home.features.dataVisualization.description') }}</p>
          </div>
          
          <div class="feature-card">
            <div class="text-purple-600 mb-2">
              <!-- SVG 图标保持不变 -->
            </div>
            <h3 class="text-lg font-medium mb-2">{{ $t('home.features.toolCalls.title') }}</h3>
            <p>{{ $t('home.features.toolCalls.description') }}</p>
          </div>
          
          <div class="feature-card">
            <div class="text-yellow-600 mb-2">
              <!-- SVG 图标保持不变 -->
            </div>
            <h3 class="text-lg font-medium mb-2">{{ $t('home.features.customModel.title') }}</h3>
            <p>{{ $t('home.features.customModel.description') }}</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, reactive, ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { ElMessage } from 'element-plus'
import { useWorkspaceStore } from '../stores/workspace'
import { useConversationStore } from '../stores/conversation'
import { apiService } from '../services/api'

const { t, locale } = useI18n()  // 修改这行，添加 locale

// 添加当前语言计算属性
const currentLocale = computed(() => locale.value)

// 添加语言切换函数
const toggleLanguage = () => {
  locale.value = locale.value === 'zh-CN' ? 'en-US' : 'zh-CN'
}

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
    ElMessage.warning(t('home.workspace.quoteRemoved'))
    return trimmedPath.slice(1, -1)
  }
  return trimmedPath
}

// 在错误消息中也使用 i18n
const handleDirectoryInput = async () => {
  if (!directoryPath.value) {
    ElMessage.warning(t('message.error'))
    return
  }
  
  const sanitizedPath = sanitizePath(directoryPath.value)
  directoryPath.value = sanitizedPath
  
  try {
    const response = await apiService.setWorkspace(sanitizedPath)
    console.log(response)
    workspaceStore.setWorkspace(response.workspace)
    await conversationStore.createConversation()
    ElMessage.success(t('message.success'))
    router.push('/workspace')
  } catch (error) {
    console.error('Failed to set workspace:', error)
    ElMessage.error(t('message.error'))
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