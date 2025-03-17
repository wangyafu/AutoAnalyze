// 执行相关类型定义
import type { ExecutionStatus, OutputType, Figure } from './api';

// 执行记录类型
export interface Execution {
  id: string;
  conversation_id: string;
  code: string;
  status: ExecutionStatus;
  created_at: string;
  updated_at: string;
  duration?: number;
  outputs: ExecutionOutput[];
}

// 执行输出类型
export interface ExecutionOutput {
  id: string;
  execution_id: string;
  type: OutputType;
  content: string | Figure;
  timestamp: string;
}

// 执行状态更新类型
export interface ExecutionUpdate {
  execution_id: string;
  status: ExecutionStatus;
  timestamp: string;
}

// 执行完成类型
export interface ExecutionComplete {
  execution_id: string;
  status: ExecutionStatus;
  duration: number;
  timestamp: string;
}