<template>
  <div class="model-config-form">
    <el-form-item label="模型类型">
      <el-select v-model="modelValue.type" class="w-full">
        <el-option label="OpenAI" value="openai" />
      </el-select>
    </el-form-item>
    
    <el-form-item label="API密钥">
      <el-input 
        v-model="modelValue.api_key" 
        placeholder="请输入API密钥" 
        show-password 
      />
    </el-form-item>
    
    <el-form-item label="API端点">
      <el-input 
        v-model="modelValue.endpoint" 
        placeholder="https://api.openai.com/v1" 
      />
    </el-form-item>
    
    <el-form-item label="模型名称">
      <el-input 
        v-model="modelValue.model" 
        placeholder="gpt-4" 
      />
    </el-form-item>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{
  modelValue: {
    type: string
    api_key: string
    endpoint: string
    model: string
  }
}>()

const emit = defineEmits(['update:modelValue'])

// 使用计算属性处理双向绑定
const modelValue = computed({
  get: () => props.modelValue,
  set: (value) => emit('update:modelValue', value)
})
</script>