import MarkdownIt from 'markdown-it'
import hljs from 'highlight.js'

// 创建markdown-it实例
const md = new MarkdownIt({
  html: false,
  linkify: true,
  typographer: true,
  highlight: function (str, lang) {
    if (lang && hljs.getLanguage(lang)) {
      try {
        return hljs.highlight(str, { language: lang }).value
      } catch (__) {}
    }
    return '' // 使用默认的转义
  }
})

/**
 * 渲染Markdown文本为HTML
 */
export function renderMarkdown(text: string): string {
  return md.render(text)
}

/**
 * 渲染文档预览
 * 为文档添加一些额外的样式和结构
 */
export function renderDocumentPreview(markdown: string, metadata?: any): string {
  let html = renderMarkdown(markdown)
  
  // 如果有元数据，添加文档信息头
  if (metadata) {
    const metaHtml = `
      <div class="document-meta">
        <h1>${metadata.title || '文档'}</h1>
        ${metadata.type === 'word' 
          ? `<div class="meta-item">Word文档 · ${metadata.pages || '未知'}页 · 约${metadata.word_count || '未知'}字</div>`
          : `<div class="meta-item">PowerPoint演示文稿 · ${metadata.slides || '未知'}张幻灯片</div>`
        }
        <hr>
      </div>
    `
    html = metaHtml + html
  }
  
  return html
}

/**
 * 简单的Markdown渲染，不使用外部库
 * 用于简单场景或作为备选方案
 */
