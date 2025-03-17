// API相关类型定义

// 系统状态类型
export interface SystemStatus {
  status: string;
  model: {
    type: string;
    status: string;
  };
  version: string;
}

// 系统配置类型
export interface SystemConfig {
  model: {
    type: string;
    api_key: string;
    endpoint: string;
  };
  security: {
    max_execution_time: number;
    max_memory: number;
  };
}

// 文件项类型
export interface FileItem {
  name: string;
  type: 'file' | 'directory';
  size?: number;
  last_modified?: string;
  extension?: string;
  items_count?: number;
  children?: FileItem[];
}

// 文件目录结构类型
export interface FileDirectory {
  path: string;
  items: FileItem[];
}

// 文件预览类型
export interface FilePreview {
  name: string;
  type: string;
  size: number;
  preview: string;
  truncated: boolean;
}

// 执行状态类型
export type ExecutionStatus = 'pending' | 'running' | 'completed' | 'error' | 'cancelled';

// 执行输出类型
export type OutputType = 'stdout' | 'stderr' | 'result' | 'error' | 'figure';

// 图表类型
export interface Figure {
  figure_id: string;
  title: string;
  format: string;
  data: string; // base64编码的图片数据
}

// 错误类型
export interface ApiError {
  code: string;
  message: string;
  details?: string;
  timestamp: string;
}