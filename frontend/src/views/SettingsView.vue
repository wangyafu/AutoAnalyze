<template>
  <div class="max-w-4xl mx-auto p-6">
    <div class="card">
      <h1 class="text-2xl font-bold mb-6">系统设置</h1>
      
      <el-form :model="form" label-position="top">
        <!-- 添加服务器配置部分 -->
        <h2 class="text-xl font-semibold mb-4">服务器配置</h2>
        <el-form-item label="后端服务端口">
          <el-input-number 
            v-model="form.server.port" 
            :min="1" 
            :max="65535"
            placeholder="请输入端口号"
          />
        </el-form-item>
        
        <h2 class="text-xl font-semibold mb-4">主模型配置</h2>
        <ModelConfigForm v-model="form.model" />
        
        <h2 class="text-xl font-semibold mb-4 mt-8">用户代理模型配置</h2>
        <ModelConfigForm v-model="form.user_model" />
        
        <h2 class="text-xl font-semibold mb-4 mt-8">视觉模型配置</h2>
        <ModelConfigForm v-model="form.vision_model" />
      
        <div class="flex justify-end mt-6">
          <el-button @click="router.push('/')">取消</el-button>
          <el-button type="primary" @click="saveSettings" :loading="loading">保存设置</el-button>
        </div>
      </el-form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { apiService } from '../services/api'
import { configService } from '../services/config'
import ModelConfigForm from '../components/ModelConfigForm.vue'

const router = useRouter()
const loading = ref(false)

const form = reactive({
  model: {
    type: 'openai',
    api_key: '',
    endpoint: '',
    model: ''
  },
  user_model: {
    type: 'openai',
    api_key: '',
    endpoint: '',
    model: ''
  },
  vision_model: {
    type: 'openai',
    api_key: '',
    endpoint: '',
    model: ''
  },
  // 添加服务器配置
  server: {
    port: 8000
  }
})

onMounted(async () => {
  try {
    // 优先从本地存储加载用户设置
    const savedPort = localStorage.getItem('backendPort')
    if (savedPort) {
      form.server.port = Number(savedPort)
    }

    const status = await apiService.getSystemStatus()
    if (status.config) {
      // 只加载模型配置，不加载服务器端口
      if (status.config.model) {
        Object.assign(form.model, status.config.model)
      }
      if (status.config.user_model) {
        Object.assign(form.user_model, status.config.user_model)
      }
      if (status.config.vision_model) {
        Object.assign(form.vision_model, status.config.vision_model)
      }
    }
  } catch (error) {
    console.error('Failed to get system status:', error)
    ElMessage.error('获取系统状态失败')
  }
})

const checkModelConfig = (model: {
  type?: string,
  api_key?: string,
  endpoint?: string,
  model?: string
}): boolean => {
  return Boolean(
    model?.type && 
    model?.api_key?.trim() && 
    model?.endpoint?.trim() && 
    model?.model?.trim()
  )
}

const saveSettings = async () => {
  // 验证主模型配置（必填）
  if (!checkModelConfig(form.model)) {
    ElMessage.warning('请完整填写主模型配置，这是必需的')
  
  }
  
  // 检查用户代理模型配置
  if (!checkModelConfig(form.user_model)) {
    ElMessage.warning('用户代理模型配置不完整，系统将无法使用双智能体模式')
  }
  
  // 检查视觉模型配置
  if (!checkModelConfig(form.vision_model)) {
    ElMessage.warning('视觉模型配置不完整，AI将无法理解生成的图片')
  }
  
  loading.value = true
  try {
    const oldPort = configService.backendPort.value
    const newPort = form.server.port
    localStorage.setItem('backendPort', newPort.toString())
    configService.setBackendPort(newPort)
    await apiService.updateConfig(form)
    
    // 只在端口变化时更新存储并刷新
    if (oldPort !== newPort) {
      
      ElMessage.success('设置已保存，正在应用新端口...')
      setTimeout(() => {
        window.location.reload()
      }, 1000)
    } else {
      ElMessage.success('设置已保存')
      loading.value = false
    }
  } catch (error) {
    console.error('Failed to update config:', error)
    ElMessage.error('保存设置失败')
    loading.value = false
  }
}
</script>