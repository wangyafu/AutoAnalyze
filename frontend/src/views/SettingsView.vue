<template>
  <div class="max-w-4xl mx-auto p-6">
    <div class="card">
      <h1 class="text-2xl font-bold mb-6">{{ $t('settings.title') }}</h1>
      
      <el-form :model="form" label-position="top">
        <h2 class="text-xl font-semibold mb-4">{{ $t('settings.server.title') }}</h2>
        <el-form-item :label="$t('settings.server.port')">
          <el-input-number 
            v-model="form.server.port" 
            :min="1" 
            :max="65535"
            :placeholder="$t('settings.server.portPlaceholder')"
          />
        </el-form-item>
        
        <h2 class="text-xl font-semibold mb-4">{{ $t('settings.model.main') }}</h2>
        <ModelConfigForm v-model="form.model" />
        
        <h2 class="text-xl font-semibold mb-4 mt-8">{{ $t('settings.model.user') }}</h2>
        <ModelConfigForm v-model="form.user_model" />
        
        <h2 class="text-xl font-semibold mb-4 mt-8">{{ $t('settings.model.vision') }}</h2>
        <ModelConfigForm v-model="form.vision_model" />
      
        <div class="flex justify-end mt-6">
          <el-button @click="router.push('/')">{{ $t('settings.button.cancel') }}</el-button>
          <el-button type="primary" @click="saveSettings" :loading="loading">{{ $t('settings.button.save') }}</el-button>
        </div>
      </el-form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { ElMessage } from 'element-plus'
import { apiService } from '../services/api'
import { configService } from '../services/config'
import ModelConfigForm from '../components/ModelConfigForm.vue'

const { t } = useI18n()
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
  const loadingMessage = ElMessage({
    message: t('settings.message.loading'),
    type: 'info',
    duration: 0,
    icon: 'el-icon-loading'
  })
  
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
    
    ElMessage.success(t('settings.message.loadSuccess'))
  } catch (error) {
    console.error('Failed to get system status:', error)
    ElMessage.error(t('settings.message.loadFailed'))
  } finally {
    loadingMessage.close()
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
  if (!checkModelConfig(form.model)) {
    ElMessage.warning(t('settings.message.mainModelRequired'))
  }
  
  if (!checkModelConfig(form.user_model)) {
    ElMessage.warning(t('settings.message.userModelIncomplete'))
  }
  
  if (!checkModelConfig(form.vision_model)) {
    ElMessage.warning(t('settings.message.visionModelIncomplete'))
  }
  
  loading.value = true
  try {
    const oldPort = configService.backendPort.value
    const newPort = form.server.port
    localStorage.setItem('backendPort', newPort.toString())
    configService.setBackendPort(newPort)
    await apiService.updateConfig(form)
    
    if (oldPort !== newPort) {
      ElMessage.success(t('settings.message.portChanged'))
      setTimeout(() => {
        window.location.reload()
      }, 1000)
    } else {
      ElMessage.success(t('settings.message.saveSuccess'))
      loading.value = false
    }
  } catch (error) {
    console.error('Failed to update config:', error)
    ElMessage.error(t('settings.message.saveFailed'))
    loading.value = false
  }
}
</script>