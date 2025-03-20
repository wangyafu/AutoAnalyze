export interface FileItem {
    name: string
    path: string 
    type: 'file' | 'directory'
    size?: number
    modified?: string
    extension?: string
    expanded?: boolean
    children?: FileItem[] 
  }
  
  export interface FilePreview {
    name: string
    path: string
    type: string
    size: number
    content: string
    is_binary: boolean
    is_truncated: boolean
    encoding?: string
  }
  
  export interface OutputItem {
    type: string
    content: string
  }
  
  export interface ImageItem {
    type: string
    format: string
    data: string
  }
  
  export interface ExecutionStatus {
    status: 'running' | 'completed' | 'error'
    output: OutputItem[]
    images: ImageItem[]
    error?: string
  }
  