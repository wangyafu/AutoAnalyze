<template>
  <div class="file-explorer text-sm">
    <div v-if="loading" class="flex justify-center p-4">
      <div class="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-500"></div>
    </div>
    
    <div v-else-if="error" class="text-red-500 p-4 text-center">
      <p>{{ error }}</p>
      <el-button size="small" type="primary" @click="loadFiles()" class="mt-2">重试</el-button>
    </div>
    
    <div v-else-if="files.length === 0" class="text-gray-500 p-4 text-center">
      <p>当前目录为空</p>
    </div>
    
    <ul v-else class="file-list list-none p-0 max-h-[500px] overflow-y-auto scrollbar-thin scrollbar-thumb-gray-300 scrollbar-track-gray-100">
      <li v-for="item in files" :key="item.name" class="file-item border-b border-gray-100;">
        <div 
          class="flex items-center p-2 hover:bg-gray-100 cursor-pointer"
          @click="handleItemClick(item)"
        >
          <!-- 使用图片替代内联SVG -->
          <img v-if="item.type === 'directory'" :src="folderIcon" class="h-5 w-5 mr-2" alt="文件夹" />
          <img v-else-if="isCodeFile(item)" :src="codeIcon" class="h-5 w-5 mr-2" alt="代码文件" />
          <img v-else-if="isImageFile(item)" :src="imageIcon" class="h-5 w-5 mr-2" alt="图片文件" />
          <img v-else-if="isDocumentFile(item)" :src="documentIcon" class="h-5 w-5 mr-2" alt="文档文件" />
          <img v-else-if="isArchiveFile(item)" :src="archiveIcon" class="h-5 w-5 mr-2" alt="压缩文件" />
          <img v-else :src="fileIcon" class="h-5 w-5 mr-2" alt="文件" />
          
          <span>{{ item.name }}</span>
        </div>
        
        <!-- 递归显示子目录 -->
        <div v-if="item.type === 'directory' && item.expanded" class="pl-4">
          <FileExplorer 
            :base-path="getItemPath(item)" 
            :depth="depth + 1" 
          />
        </div>
      </li>
    </ul>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, defineProps, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { apiService } from '../../services/api'

// 导入图标
import folderIcon from '@/assets/icons/folder.svg'
import codeIcon from '@/assets/icons/code.svg'
import imageIcon from '@/assets/icons/image.svg'
import documentIcon from '@/assets/icons/document.svg'
import archiveIcon from '@/assets/icons/archive.svg'
import fileIcon from '@/assets/icons/file.svg'

const emit = defineEmits(['filePreview'])
interface FileItem {
  name: string
  path: string 
  type: 'file' | 'directory'
  size?: number
  modified?: string
  extension?: string
  expanded?: boolean
  children?: FileItem[] 
}

interface FilePreview {
  name: string
  path: string
  type: string
  size: number
  content: string
  is_binary: boolean
  is_truncated: boolean
  encoding?: string
}

const props = defineProps({
  basePath: {
    type: String,
    default: ''
  },
  depth: {
    type: Number,
    default: 0
  }
})

const files = ref<FileItem[]>([])
const loading = ref(false)
const error = ref('')

// 监听basePath变化，重新加载文件
watch(() => props.basePath, () => {
  loadFiles()
})

onMounted(() => {
  loadFiles()
})

// 加载文件列表
async function loadFiles() {
  loading.value = true
  error.value = ''
  
  try {
    const response = await apiService.getFiles(props.basePath)
    console.log('Files:', response)
    // 将后端返回的数据结构转换为前端需要的格式
    files.value = response.map((item: any) => ({
      name: item.name,
      path: item.path,
      type: item.type,
      size: item.size,
      modified: item.modified,
      extension: item.extension,
      expanded: false,
      children: item.children
    }))
  } catch (err) {
    console.error('Failed to load files:', err)
    error.value = '加载文件失败'
    ElMessage.error('加载文件失败')
  } finally {
    loading.value = false
  }
}

// 处理文件/文件夹点击
function handleItemClick(item: FileItem) {
  if (item.type === 'directory') {
    // 切换展开/折叠状态
    item.expanded = !item.expanded
  } else {
    // 预览文件
    previewFile(item)
  }
}

// 获取完整路径
function getItemPath(item: FileItem): string {
  return props.basePath ? `${props.basePath}/${item.name}` : item.name
}

// 预览文件
async function previewFile(item: FileItem) {
  try {
    const preview = await apiService.getFilePreview(item.path)
    // 这里可以触发一个事件，通知父组件显示文件预览
    // 或者使用全局状态管理来处理
    console.log('File preview:', preview)
    
    // 添加事件触发
    emit('filePreview', preview)
  } catch (err) {
    console.error('Failed to preview file:', err)
    ElMessage.error('预览文件失败')
  }
}

// 判断文件类型的函数
function getFileExtension(item: FileItem): string {
  if (item.extension) return item.extension.toLowerCase()
  const parts = item.name.split('.')
  return parts.length > 1 ? parts[parts.length - 1].toLowerCase() : ''
}

function isCodeFile(item: FileItem): boolean {
  if (item.type !== 'file') return false
  const codeExtensions = ['js', 'ts', 'jsx', 'tsx', 'vue', 'py', 'java', 'c', 'cpp', 'cs', 'go', 'rb', 'php', 'html', 'css', 'scss', 'less', 'json', 'xml', 'yaml', 'yml']
  return codeExtensions.includes(getFileExtension(item))
}

function isImageFile(item: FileItem): boolean {
  if (item.type !== 'file') return false
  const imageExtensions = ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'svg', 'webp', 'ico']
  return imageExtensions.includes(getFileExtension(item))
}

function isDocumentFile(item: FileItem): boolean {
  if (item.type !== 'file') return false
  const docExtensions = ['pdf', 'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx', 'txt', 'rtf', 'md', 'csv']
  return docExtensions.includes(getFileExtension(item))
}

function isArchiveFile(item: FileItem): boolean {
  if (item.type !== 'file') return false
  const archiveExtensions = ['zip', 'rar', 'tar', 'gz', '7z', 'iso']
  return archiveExtensions.includes(getFileExtension(item))
}
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

