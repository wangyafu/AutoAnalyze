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
 * 简单的Markdown渲染，不使用外部库
 * 用于简单场景或作为备选方案
 */
