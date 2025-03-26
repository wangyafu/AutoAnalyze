import axios from 'axios'
import { configService } from './config'

// 创建一个获取baseURL的函数
const getBaseURL = () => configService.getBackendBaseUrl()

const createApiClient = () => {
  return axios.create({
    baseURL: getBaseURL(),
    headers: {
      'Content-Type': 'application/json'
    }
  })
}

export const apiService = {
  // 获取当前的API客户端实例
  getClient() {
    return createApiClient()
  },

  /**
   * 获取系统状态
   */
  getSystemStatus: async () => {
    const response = await createApiClient().get('/api/status')
    return response.data
  },
  
  /**
   * 更新系统配置
   */
  updateConfig: async (config: any) => {
    const response = await createApiClient().put('/api/config', config)
    return response.data
  },
  
  /**
   * 设置工作目录
   */
  setWorkspace: async (path: string) => {
    console.log("setWorkspace",path)
    const response = await createApiClient().post('/api/workspace', { path })
    return response.data
  },
  
  /**
   * 获取文件目录结构
   */
  getFiles: async (path?: string) => {
    const response = await createApiClient().get('/api/files', {
      params: { path }
    })
    return response.data
  },
  
  /**
   * 获取文件内容预览
   */
  getFilePreview: async (path: string, maxSize?: number) => {
    const response = await createApiClient().get('/api/files/preview', {
      params: { path, max_size: maxSize }
    })
    return response.data
  },
  
  /**
   * 创建新对话
   */
  createConversation: async (title?: string) => {
    console.log("createConversation",title)
    const response = await createApiClient().post('/api/conversations', {"title":title })
    return response.data
  },
  
  async getWorkspace() {
    const response = await createApiClient().get('/api/workspace')
    return response.data
  },
  

}