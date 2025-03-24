import { apiService } from './api'
import { ElMessage } from 'element-plus'
import type { FilePreview } from '../types'

export const filePreviewService = {
  /**
   * 获取文件预览数据
   * @param path 文件路径
   * @returns 文件预览数据或null
   */
  async getFilePreview(path: string): Promise<FilePreview | null> {
    try {
      const response = await apiService.getFilePreview(path)
      const data = response as FilePreview
      
      console.log('File preview:', data)
      
      if (data.is_binary && !data.preview_type) {
        ElMessage.warning('二进制文件无法预览')
        return null
      }
      
      return data
    } catch (error) {
      ElMessage.error('文件预览失败')
      return null
    }
  },
  
  /**
   * 根据文件名获取图片MIME类型
   * @param filename 文件名
   * @returns 图片MIME类型
   */
  getImageType(filename: string): string {
    if (!filename) return 'png'
    const extension = filename.split('.').pop()?.toLowerCase() || ''
    
    switch (extension) {
      case 'jpg':
      case 'jpeg':
        return 'jpeg'
      case 'png':
        return 'png'
      case 'gif':
        return 'gif'
      case 'svg':
        return 'svg+xml'
      case 'webp':
        return 'webp'
      default:
        return 'png'
    }
  }
}