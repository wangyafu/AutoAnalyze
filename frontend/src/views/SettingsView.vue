<template>
  <div class="min-h-screen bg-gray-100 py-12 px-4 sm:px-6 lg:px-8">
    <div class="max-w-4xl mx-auto">
      <el-card class="w-full">
        <template #header>
          <div class="text-2xl font-bold text-gray-900">系统设置</div>
        </template>

        <el-form label-position="top">
          <div class="mb-8">
            <div class="text-xl font-semibold text-gray-800 mb-4">模型配置</div>
            <el-form-item label="模型类型">
              <el-select v-model="modelConfig.type" class="w-full">
                <el-option value="openai" label="OpenAI" />
                <el-option value="claude" label="Claude" />
                <el-option value="local" label="本地模型 (Ollama)" />
              </el-select>
            </el-form-item>

            <el-form-item label="API密钥">
              <el-input v-model="modelConfig.api_key" type="password" placeholder="输入API密钥" show-password />
            </el-form-item>

            <el-form-item label="API端点">
              <el-input v-model="modelConfig.endpoint" placeholder="输入API端点URL" />
            </el-form-item>
          </div>

          <div class="mb-8">
            <div class="text-xl font-semibold text-gray-800 mb-4">安全设置</div>
            <el-form-item label="最大执行时间 (秒)">
              <el-input-number v-model="securityConfig.max_execution_time" :min="1" :max="3600" class="w-full" />
            </el-form-item>

            <el-form-item label="最大内存使用 (MB)">
              <el-input-number v-model="securityConfig.max_memory" :min="128" :max="4096" class="w-full" />
            </el-form-item>
          </div>

          <div class="flex justify-end space-x-4">
            <el-button :loading="isSaving" type="primary" @click="saveConfig">保存配置</el-button>
            <el-button :loading="isTesting" @click="testConnection">测试连接</el-button>
          </div>

          <el-alert
            v-if="message"
            :title="message"
            :type="messageType"
            show-icon
            class="mt-4"
          />
        </el-form>
      </el-card>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue';
import { useConfigStore } from '../stores/config';
import type { SystemConfig } from '../types/api';

const configStore = useConfigStore();

// 模型配置
const modelConfig = reactive({
  type: 'openai',
  api_key: '',
  endpoint: 'https://api.openai.com/v1'
});

// 安全配置
const securityConfig = reactive({
  max_execution_time: 300,
  max_memory: 1024
});

// 状态
const isSaving = ref(false);
const isTesting = ref(false);
const message = ref('');
const messageType = ref('info');

// 加载配置
const loadConfig = async () => {
  const status = await configStore.loadStatus();
  
  if (configStore.config) {
    // 填充表单
    modelConfig.type = configStore.config.model.type;
    modelConfig.api_key = configStore.config.model.api_key;
    modelConfig.endpoint = configStore.config.model.endpoint;
    
    securityConfig.max_execution_time = configStore.config.security.max_execution_time;
    securityConfig.max_memory = configStore.config.security.max_memory;
  }
};

// 保存配置
const saveConfig = async () => {
  isSaving.value = true;
  message.value = '';
  
  try {
    const config: SystemConfig = {
      model: {
        type: modelConfig.type,
        api_key: modelConfig.api_key,
        endpoint: modelConfig.endpoint
      },
      security: {
        max_execution_time: securityConfig.max_execution_time,
        max_memory: securityConfig.max_memory
      }
    };
    
    const success = await configStore.updateConfig(config);
    
    if (success) {
      message.value = '配置已保存';
      messageType.value = 'success';
    } else {
      message.value = '保存配置失败';
      messageType.value = 'error';
    }
  } catch (error) {
    console.error('保存配置出错:', error);
    message.value = '保存配置时发生错误';
    messageType.value = 'error';
  } finally {
    isSaving.value = false;
  }
};

// 测试连接
const testConnection = async () => {
  isTesting.value = true;
  message.value = '正在测试连接...';
  messageType.value = 'info';
  
  try {
    const status = await configStore.loadStatus();
    
    if (status && status.status === 'running') {
      message.value = '连接成功';
      messageType.value = 'success';
    } else {
      message.value = '连接失败';
      messageType.value = 'error';
    }
  } catch (error) {
    console.error('测试连接出错:', error);
    message.value = '测试连接时发生错误';
    messageType.value = 'error';
  } finally {
    isTesting.value = false;
  }
};

onMounted(() => {
  loadConfig();
});
</script>

<style scoped>

</style>