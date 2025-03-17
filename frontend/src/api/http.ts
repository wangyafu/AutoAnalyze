// 提供配置好的axios实例
import axios from 'axios';
import type{ AxiosInstance } from 'axios';

// 创建axios实例
const httpClient: AxiosInstance = axios.create({
  baseURL: 'http://127.0.0.1:8000',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json'
  }
});

// 请求拦截器
httpClient.interceptors.request.use(
  config => {
    // 可以在这里添加认证信息等
    return config;
  },
  error => {
    return Promise.reject(error);
  }
);

// 响应拦截器
httpClient.interceptors.response.use(
  response => {
    return response;
  },
  error => {
    // 统一处理错误
    console.error('API请求错误:', error);
    return Promise.reject(error);
  }
);

// 设置基础URL
const setBaseURL = (url: string): void => {
  httpClient.defaults.baseURL = url;
};

export {
  httpClient,
  setBaseURL
};