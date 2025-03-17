<template>
  <div class="flex items-start gap-3 mb-4" :class="messageClass">
    <el-avatar :size="40" class="flex-shrink-0">
      {{ message.role === 'user' ? '👤' : '🤖' }}
    </el-avatar>
    <div class="flex-1 min-w-0">
      <div class="flex justify-between items-center mb-1 text-sm">
        <el-tag size="small" :type="message.role === 'user' ? 'primary' : 'success'">{{ roleLabel }}</el-tag>
        <span class="text-gray-500 text-xs">{{ formatTime(message.timestamp) }}</span>
      </div>
      
      <div class="message-body">
        <!-- 处理普通文本和代码块 -->
        <template v-if="message.code_blocks && message.code_blocks.length > 0">
          <!-- 分割消息内容，在代码块位置插入代码组件 -->
          <template v-for="(part, index) in messageParts" :key="index">
            <div v-if="part.type === 'text'" class="text-content" v-html="formatText(part.content)"></div>
            <CodeBlockComponent
              v-else-if="part.type === 'code'"
              :code="part.content"
              :language="part.language!"
              :id="part.id!"
              @execute="handleExecuteCode"
              @copy="handleCopyCode"
            />
          </template>
        </template>
        
        <!-- 没有代码块的情况 -->
        <div v-else class="text-content" v-html="formatText(message.content)"></div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import type { Message, CodeBlock } from '../../types/conversation';
import CodeBlockComponent from './CodeBlock.vue';

// Props
const props = defineProps<{
  message: Message;
}>();

// Emits
const emit = defineEmits<{
  (e: 'execute-code', params: { code: string, codeBlockId: string }): void;
}>();

// Computed
const messageClass = computed(() => {
  return {
    'user-message': props.message.role === 'user',
    'assistant-message': props.message.role === 'assistant',
    'system-message': props.message.role === 'system'
  };
});

const roleLabel = computed(() => {
  switch (props.message.role) {
    case 'user': return '用户';
    case 'assistant': return '助手';
    case 'system': return '系统';
    default: return props.message.role;
  }
});

const messageParts = computed(() => {
  if (!props.message.code_blocks || props.message.code_blocks.length === 0) {
    return [{ type: 'text', content: props.message.content }];
  }
  
  // 将消息内容分割成文本和代码块
  const parts = [];
  let lastIndex = 0;
  
  // 假设代码块在消息内容中的格式为 ```language\ncode\n```
  const codeBlockRegex = /```(\w*)\n([\s\S]*?)```/g;
  let match;
  
  while ((match = codeBlockRegex.exec(props.message.content)) !== null) {
    // 添加代码块前的文本
    if (match.index > lastIndex) {
      parts.push({
        type: 'text',
        content: props.message.content.substring(lastIndex, match.index)
      });
    }
    
    // 查找对应的代码块对象
    const codeBlock = props.message.code_blocks.find(block => 
      block.code === match[2] && block.language === match[1]
    );
    
    // 添加代码块
    parts.push({
      type: 'code',
      content: match[2],
      language: match[1] || 'plaintext',
      id: codeBlock?.id || `code-${Date.now()}`
    });
    
    lastIndex = match.index + match[0].length;
  }
  
  // 添加剩余的文本
  if (lastIndex < props.message.content.length) {
    parts.push({
      type: 'text',
      content: props.message.content.substring(lastIndex)
    });
  }
  
  return parts;
});

// Methods
const formatTime = (timestamp: string) => {
  const date = new Date(timestamp);
  return date.toLocaleTimeString();
};

const formatText = (text: string) => {
  // 简单的文本格式化，将换行符转换为<br>
  return text.replace(/\n/g, '<br>');
};

const handleExecuteCode = (code: string, codeBlockId: string) => {
  emit('execute-code', { code, codeBlockId });
};

const handleCopyCode = (code: string) => {
  navigator.clipboard.writeText(code)
    .then(() => console.log('代码已复制'))
    .catch(err => console.error('复制失败:', err));
};
</script>

