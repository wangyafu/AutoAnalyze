<template>
  <li class="file-item border-b border-gray-100">
    <div 
      class="flex items-center p-2 hover:bg-gray-100 cursor-pointer"
      :style="{ paddingLeft: `${depth * 1.5}rem` }"
      @click="handleItemClick"
    >
      <img v-if="item.type === 'directory'" :src="folderIcon" class="h-5 w-5 mr-2" alt="文件夹" />
      <img v-else-if="isCodeFile(item)" :src="codeIcon" class="h-5 w-5 mr-2" alt="代码文件" />
      <img v-else-if="isImageFile(item)" :src="imageIcon" class="h-5 w-5 mr-2" alt="图片文件" />
      <img v-else-if="isDocumentFile(item)" :src="documentIcon" class="h-5 w-5 mr-2" alt="文档文件" />
      <img v-else-if="isArchiveFile(item)" :src="archiveIcon" class="h-5 w-5 mr-2" alt="压缩文件" />
      <img v-else :src="fileIcon" class="h-5 w-5 mr-2" alt="文件" />
      
      <span>{{ item.name }}</span>
    </div>
    
    <ul v-if="item.type === 'directory' && item.expanded && item.children" class="list-none">
      <FileItem
        v-for="child in item.children"
        :key="child.path"
        :item="child"
        :depth="depth + 1"
        @file-preview="handleFilePreview"
      />
    </ul>
  </li>
</template>

<script setup lang="ts">
import { defineProps, defineEmits } from 'vue'
import type { FileItem } from '@/types'
import folderIcon from '@/assets/icons/folder.svg'
import codeIcon from '@/assets/icons/code.svg'
import imageIcon from '@/assets/icons/image.svg'
import documentIcon from '@/assets/icons/document.svg'
import archiveIcon from '@/assets/icons/archive.svg'
import fileIcon from '@/assets/icons/file.svg'

const props = defineProps<{
  item: FileItem
  depth: number
}>()

const emit = defineEmits<{
  (e: 'file-preview', path: string): void
}>()

const handleItemClick = () => {
  if (props.item.type === 'directory') {
    props.item.expanded = !props.item.expanded
  } else {
    handleFilePreview(props.item.path)
  }
}

const handleFilePreview = (path: string) => {
  emit('file-preview', path)
}

// 复用原来的文件类型判断函数
function getFileExtension(item: FileItem): string {
  if (item.extension) return item.extension.toLowerCase()
  const parts = item.name.split('.')
  return parts.length > 1 ? parts[parts.length - 1].toLowerCase() : ''
}

function isCodeFile(item: FileItem): boolean {
  if (item.type !== 'file') return false
  const codeExtensions = ['js', 'ts', 'jsx', 'tsx', 'vue', 'py', 'java', 'c', 'cpp', 'cs', 'go', 'rb', 'php', 'html', 'css', 'scss', 'less', 'json', 'xml', 'yaml', 'yml']
  return codeExtensions.includes(getFileExtension(item))
}

function isImageFile(item: FileItem): boolean {
  if (item.type !== 'file') return false
  const imageExtensions = ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'svg', 'webp', 'ico']
  return imageExtensions.includes(getFileExtension(item))
}

function isDocumentFile(item: FileItem): boolean {
  if (item.type !== 'file') return false
  const docExtensions = ['pdf', 'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx', 'txt', 'rtf', 'md', 'csv']
  return docExtensions.includes(getFileExtension(item))
}

function isArchiveFile(item: FileItem): boolean {
  if (item.type !== 'file') return false
  const archiveExtensions = ['zip', 'rar', 'tar', 'gz', '7z', 'iso']
  return archiveExtensions.includes(getFileExtension(item))
}




</script>
