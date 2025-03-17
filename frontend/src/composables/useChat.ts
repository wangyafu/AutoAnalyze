// 对话管理与消息处理
import { useConversationStore } from '../stores/conversation';

export function useChat() {
  const conversationStore = useConversationStore();
  
  // 发送消息并获取回复
  const sendMessage = async (content: string) => {
    await conversationStore.sendMessage(content);
  };
  
  // 从消息内容中解析代码块
  const parseCodeBlocks = (content: string) => {
    return conversationStore.extractCodeBlocks(content);
  };
  
  // 从代码块中提取语言标识
  const extractLanguage = (codeBlock: string) => {
    const match = codeBlock.match(/^```(\w*)\n/);
    return match ? match[1] || 'text' : 'text';
  };
  
  return {
    sendMessage,
    parseCodeBlocks,
    extractLanguage
  };
}