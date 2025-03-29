<template>
  <div class="model-config-form">
    <el-form-item :label="$t('settings.modelConfig.type')">
      <el-select v-model="modelValue.type" class="w-full">
        <el-option label="OpenAI" value="openai" />
      </el-select>
    </el-form-item>
    
    <el-form-item :label="$t('settings.modelConfig.apiKey')">
      <el-input 
        v-model="modelValue.api_key" 
        :placeholder="$t('settings.modelConfig.apiKeyPlaceholder')" 
        show-password 
      />
    </el-form-item>
    
    <el-form-item :label="$t('settings.modelConfig.endpoint')">
      <el-input 
        v-model="modelValue.endpoint" 
        :placeholder="$t('settings.modelConfig.endpointPlaceholder')" 
      />
    </el-form-item>
    
    <el-form-item :label="$t('settings.modelConfig.modelName')">
      <el-input 
        v-model="modelValue.model" 
        :placeholder="$t('settings.modelConfig.modelNamePlaceholder')" 
      />
    </el-form-item>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'

const { t } = useI18n()

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