<template>
  <div class="max-w-4xl mx-auto p-6">
    <div class="card">
      <h1 class="text-2xl font-bold mb-6">系统设置</h1>
      
      <el-form :model="form" label-position="top">
        <h2 class="text-xl font-semibold mb-4">模型配置</h2>
        
        <el-form-item label="模型类型">
          <el-select v-model="form.model.type" class="w-full">
            <el-option label="OpenAI" value="openai" />
          </el-select>
        </el-form-item>
        
        <el-form-item label="API密钥">
          <el-input 
            v-model="form.model.api_key" 
            placeholder="请输入API密钥" 
            show-password 
          />
        </el-form-item>
        
        <el-form-item label="API端点">
          <el-input 
            v-model="form.model.endpoint" 
            placeholder="https://api.openai.com/v1" 
          />
        </el-form-item>
        
        <el-form-item label="模型名称">
          <el-input 
            v-model="form.model.model" 
            placeholder="gpt-4" 
          />
        </el-form-item>
      
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

const router = useRouter()
const loading = ref(false)

const form = reactive({
  model: {
    type: 'openai',
    api_key: '',
    endpoint: '',
    model: ''  // 新增模型名称字段
  }
})

onMounted(async () => {
  try {
    const status = await apiService.getSystemStatus()
    if (status.config?.model) {
      // 从配置中获取所有模型相关设置
      form.model.type = status.config.model.type || 'openai'
      form.model.endpoint = status.config.model.endpoint || 'https://api.openai.com/v1'
      form.model.model = status.config.model.model || 'gpt-4'
      form.model.api_key = status.config.model.api_key || ''
    }
  } catch (error) {
    console.error('Failed to get system status:', error)
    ElMessage.error('获取系统状态失败')
  }
})

const saveSettings = async () => {
  if (!form.model.api_key) {
    ElMessage.warning('请输入API密钥')
    return
  }
  
  loading.value = true
  try {
    await apiService.updateConfig(form)
    ElMessage.success('设置已保存')
    router.push('/')
  } catch (error) {
    console.error('Failed to update config:', error)
    ElMessage.error('保存设置失败')
  } finally {
    loading.value = false
  }
}
</script>