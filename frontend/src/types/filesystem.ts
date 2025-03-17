// 文件系统相关类型定义
import type { FileItem, FileDirectory, FilePreview } from './api';

// 文件系统变更事件类型
export type FileSystemEventType = 'created' | 'modified' | 'deleted';

// 文件系统变更事件
export interface FileSystemEvent {
  event: FileSystemEventType;
  path: string;
  item_type: 'file' | 'directory';
  timestamp: string;
}

// 工作区设置响应
export interface WorkspaceResponse {
  status: string;
  workspace: string;
  files_count: number;
}

// 导出API类型
export type { FileItem, FileDirectory, FilePreview };