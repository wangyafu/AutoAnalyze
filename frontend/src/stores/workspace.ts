import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { FileItem} from '../types'
import { ElMessage } from 'element-plus'
import { apiService } from '../services/api'
export const useWorkspaceStore = defineStore('workspace', () => {
  const currentWorkspace = ref<string | null>(null)
  const files = ref<FileItem[]>([])
  const loading = ref(false)
  const error = ref('')
  function setWorkspace(path: string) {
    currentWorkspace.value = path
  }
  
  function clearWorkspace() {
    currentWorkspace.value = null
  }
  async function loadFiles() {
    loading.value = true
    error.value = ''

    try {
      const response = await apiService.getFiles(currentWorkspace.value!)
      // 将后端返回的数据结构转换为前端需要的格式，并保留已存在项目的expanded属性
      const newFiles = response.map((item: any) => {
        // 查找是否已存在相同path和name的文件项
        const existingItem = files.value.find(
          existing => existing.path === item.path && existing.name === item.name
        )
        
        return {
          name: item.name,
          path: item.path,
          type: item.type,
          size: item.size,
          modified: item.modified,
          extension: item.extension,
          // 如果已存在相同项目，保留其expanded状态，否则设为false
          expanded: existingItem ? existingItem.expanded : false,
          children: item.children
        }
      })
      
      files.value = newFiles
      console.log(newFiles)
    } catch (err) {
      console.error('Failed to load files:', err)
      error.value = '加载文件失败'
      ElMessage.error('加载文件失败')
    } finally {
      loading.value = false
    }
  }
  return {
    currentWorkspace,
    setWorkspace,
    clearWorkspace,
    loadFiles,
    files,
    loading,
    error
  }
})