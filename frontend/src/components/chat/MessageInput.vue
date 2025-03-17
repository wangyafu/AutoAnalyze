<template>
  <div class="flex gap-2 p-3 bg-white border-t border-gray-200">
    <el-input
      ref="inputRef"
      v-model="inputValue"
      :placeholder="placeholder"
      :disabled="disabled"
      type="textarea"
      :autosize="{ minRows: 1, maxRows: 4 }"
      @keydown.enter.prevent="handleEnter"
      resize="none"
    />
    <el-button
      type="primary"
      :disabled="disabled || !inputValue.trim()"
      @click="handleSubmit"
      class="self-end h-[40px] min-w-[80px]"
    >
      <template #icon>
        <el-icon><Right /></el-icon>
      </template>
      发送
    </el-button>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { Right } from '@element-plus/icons-vue';

// Props
const props = defineProps<{
  placeholder?: string;
  disabled?: boolean;
}>();

// Emits
const emit = defineEmits<{
  (e: 'submit', content: string): void;
}>();

// Refs
const inputRef = ref<HTMLTextAreaElement | null>(null);
const inputValue = ref('');

// Methods
const handleSubmit = () => {
  if (inputValue.value.trim() && !props.disabled) {
    emit('submit', inputValue.value);
    inputValue.value = '';
  }
};

const handleEnter = (e: KeyboardEvent) => {
  // Ctrl+Enter 或 Shift+Enter 换行
  if (e.ctrlKey || e.shiftKey) {
    return;
  }
  
  // 普通 Enter 发送
  handleSubmit();
};
</script>

