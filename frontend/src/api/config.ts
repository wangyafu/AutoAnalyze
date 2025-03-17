// 系统配置相关API
import { httpClient } from './http';

// 获取系统状态
const getStatus = async () => {
  const response = await httpClient.get('/api/status');
  return response.data;
};

// 更新系统配置
const updateConfig = async (config: any) => {
  const response = await httpClient.put('/api/config', config);
  return response.data;
};

export {
  getStatus,
  updateConfig
};