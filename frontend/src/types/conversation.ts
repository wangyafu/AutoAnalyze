// 对话相关类型定义

// 消息角色类型
export type MessageRole = 'user' | 'assistant' | 'system';

// 消息类型
export interface Message {
  id: string;
  role: MessageRole;
  content: string;
  timestamp: string;
  code_blocks?: CodeBlock[];
}

// 代码块类型
export interface CodeBlock {
  id: string;
  language: string;
  code: string;
  execution_id?: string;
}

// 对话类型
export interface Conversation {
  id: string;
  title: string;
  created_at: string;
  messages: Message[];
  message_count?: number;
}

// 对话列表响应类型
export interface ConversationsResponse {
  total: number;
  conversations: Conversation[];
}