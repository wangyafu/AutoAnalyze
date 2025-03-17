// 格式化工具

// 格式化日期
export const formatDate = (date: string | Date): string => {
  const d = typeof date === 'string' ? new Date(date) : date;
  return d.toLocaleString();
};

// 格式化文件大小
export const formatFileSize = (size: number): string => {
  if (size < 1024) {
    return `${size} B`;
  } else if (size < 1024 * 1024) {
    return `${(size / 1024).toFixed(2)} KB`;
  } else if (size < 1024 * 1024 * 1024) {
    return `${(size / (1024 * 1024)).toFixed(2)} MB`;
  } else {
    return `${(size / (1024 * 1024 * 1024)).toFixed(2)} GB`;
  }
};

// 格式化代码语言
export const formatCodeLanguage = (language: string): string => {
  const languageMap: Record<string, string> = {
    'py': 'python',
    'js': 'javascript',
    'ts': 'typescript',
    'md': 'markdown',
    'json': 'json',
    'html': 'html',
    'css': 'css',
    'sql': 'sql',
    'sh': 'shell',
    'bash': 'bash',
    'txt': 'text'
  };
  
  return languageMap[language.toLowerCase()] || language || 'text';
};

// 根据文件名判断文件类型
export const getFileType = (fileName: string): string => {
  const extension = fileName.split('.').pop()?.toLowerCase() || '';
  
  const imageExtensions = ['jpg', 'jpeg', 'png', 'gif', 'svg', 'bmp', 'webp'];
  const textExtensions = ['txt', 'md', 'json', 'csv', 'xml', 'html', 'css', 'js', 'ts', 'py', 'r', 'sql'];
  
  if (imageExtensions.includes(extension)) {
    return 'image';
  } else if (textExtensions.includes(extension)) {
    return 'text';
  } else {
    return 'binary';
  }
};

// 判断是否为文本文件
export const isTextFile = (fileName: string): boolean => {
  return getFileType(fileName) === 'text';
};

// 根据扩展名获取语言
export const getLanguageByExtension = (extension: string): string => {
  const extensionMap: Record<string, string> = {
    'py': 'python',
    'js': 'javascript',
    'ts': 'typescript',
    'jsx': 'jsx',
    'tsx': 'tsx',
    'vue': 'vue',
    'html': 'html',
    'css': 'css',
    'scss': 'scss',
    'less': 'less',
    'json': 'json',
    'md': 'markdown',
    'sql': 'sql',
    'sh': 'shell',
    'bash': 'bash',
    'r': 'r',
    'csv': 'csv',
    'txt': 'text'
  };
  
  return extensionMap[extension.toLowerCase()] || 'text';
};