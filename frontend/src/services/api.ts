import axios from 'axios'

const API_BASE_URL = 'http://127.0.0.1:8000'

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json'
  }
})

export const apiService = {
  /**
   * 获取系统状态
   */
  getSystemStatus: async () => {
    const response = await apiClient.get('/api/status')
    return response.data
  },
  
  /**
   * 更新系统配置
   */
  updateConfig: async (config: any) => {
    const response = await apiClient.put('/api/config', config)
    return response.data
  },
  
  /**
   * 设置工作目录
   */
  setWorkspace: async (path: string) => {
    console.log("setWorkspace",path)
    const response = await apiClient.post('/api/workspace', { path })
    return response.data
  },
  
  /**
   * 获取文件目录结构
   */
  getFiles: async (path?: string) => {
    const response = await apiClient.get('/api/files', {
      params: { path }
    })
    return response.data
  },
  
  /**
   * 获取文件内容预览
   */
  getFilePreview: async (path: string, maxSize?: number) => {
    const response = await apiClient.get('/api/files/preview', {
      params: { path, max_size: maxSize }
    })
    return response.data
  },
  
  /**
   * 创建新对话
   */
  createConversation: async (title?: string) => {
    console.log("createConversation",title)
    const response = await apiClient.post('/api/conversations', {"title":title })
    return response.data
  },
  
  async getWorkspace() {
    const response = await axios.get('/api/workspace')
    return response.data
  },
  

}