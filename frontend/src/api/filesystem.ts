// 文件系统相关API
import { httpClient } from './http';

// 设置工作目录
const setWorkspace = async (path: string) => {
  const response = await httpClient.post('/api/workspace', { path });
  return response.data;
};

// 获取文件目录结构
const getFiles = async (path?: string) => {
  const params: Record<string, string> = {};
  if (path) params.path = path;
  
  const response = await httpClient.get('/api/files', { params });
  return response.data;
};

// 获取文件内容预览
const getFilePreview = async (path: string, maxSize?: number) => {
  const params: Record<string, any> = { path };
  if (maxSize !== undefined) params.max_size = maxSize;
  
  const response = await httpClient.get('/api/files/preview', { params });
  return response.data;
};

// 获取文本文件完整内容
const getTextFileContent = async (path: string) => {
  const response = await httpClient.get('/api/files/content', { params: { path } });
  return response.data;
};

export {
  setWorkspace,
  getFiles,
  getFilePreview,
  getTextFileContent
};