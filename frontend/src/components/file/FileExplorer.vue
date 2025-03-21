<template>
  <div class="file-explorer text-sm">
    <div v-if="loading" class="flex justify-center p-4">
      <div class="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-500"></div>
    </div>
    
    <div v-else-if="error" class="text-red-500 p-4 text-center">
      <p>{{ error }}</p>
      <el-button size="small" type="primary" @click="fileStore.loadFiles()" class="mt-2">重试</el-button>
    </div>
    
    <div v-else-if="files.length === 0" class="text-gray-500 p-4 text-center">
      <p>当前目录为空</p>
    </div>
    
    <ul v-else class="file-list list-none p-0 max-h-[500px] overflow-y-auto scrollbar-thin scrollbar-thumb-gray-300 scrollbar-track-gray-100">
      <FileItem 
        v-for="item in files" 
        :key="item.path"
        :item="item"
        :depth="0"
        @file-preview="(path) => emit('filePreview', path)"
      />
    </ul>
  </div>
</template>

<script setup lang="ts">
import { onMounted, defineProps, watch, computed } from 'vue'
import FileItem from './FileItem.vue'
import {useWorkspaceStore} from "@/stores/workspace"
const emit = defineEmits(['filePreview'])
const fileStore=useWorkspaceStore()
const props = defineProps({
  basePath: {
    type: String,
    default: ''
  }
})

// 使用计算属性从store获取状态
const files = computed(() => fileStore.files)
const loading = computed(() => fileStore.loading)
const error = computed(() => fileStore.error)
// 监听basePath变化，重新加载文件
watch(() => props.basePath, () => {
  fileStore.loadFiles()
})

onMounted(() => {
  fileStore.loadFiles()
})


// 预览文件


</script>

<style scoped>
/* 添加自定义滚动条样式 */
.file-list::-webkit-scrollbar {
  width: 6px;
}

.file-list::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 3px;
}

.file-list::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 3px;
}

.file-list::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}

/* 兼容 Firefox */
.file-list {
  scrollbar-width: thin;
  scrollbar-color: #c1c1c1 #f1f1f1;
}
</style>

