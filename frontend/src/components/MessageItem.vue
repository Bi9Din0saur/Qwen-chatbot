<template>
  <div :class="['message-item', message.type]" :data-message-id="message.id">
    <div class="message-avatar">
      <img
        v-if="message.type === 'bot'"
        src="/ai-avatar.svg"
        alt="AI助手"
        class="avatar-img"
        @error="handleAvatarError"
      />
      <span v-else-if="message.type === 'user'">👤</span>
      <span v-else>🤖</span>
    </div>

    <div class="message-content">
      <div class="message-header">
        <span class="message-author">
          {{ message.type === 'user' ? '你' : 'AI助手' }}
        </span>
        <span class="message-time">
          {{ formatTime(message.timestamp) }}
        </span>
      </div>

      <div class="message-body">
        <!-- 图片显示 -->
        <div v-if="message.imageUrl || message.imageFile" class="message-image">
          <img
            :src="getImageSrc()"
            :alt="message.content || '图片'"
            @load="handleImageLoad"
            @error="handleImageError"
            class="content-image"
          />
        </div>

        <!-- 文本内容 -->
        <div v-if="message.content" class="message-text">
          <div
            v-if="message.type === 'bot'"
            v-html="renderedContent"
            class="markdown-content"
          ></div>
          <div v-else>{{ message.content }}</div>
        </div>

        <!-- 流式输出指示器 -->
        <div v-if="isStreaming" class="streaming-indicator">
          <span class="dot"></span>
          <span class="dot"></span>
          <span class="dot"></span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import MarkdownIt from 'markdown-it'
import type { Message } from '@/stores/chat'

interface Props {
  message: Message
  isStreaming?: boolean
}

const props = defineProps<Props>()

// 创建markdown-it实例
const md = new MarkdownIt({
  html: true,
  linkify: true,
  typographer: true,
  breaks: true,
})

// 渲染Markdown内容
const renderedContent = computed(() => {
  if (!props.message.content) return ''
  return md.render(props.message.content)
})

const getImageSrc = (): string => {
  if (props.message.imageFile) {
    return URL.createObjectURL(props.message.imageFile)
  }
  const imageUrl = props.message.imageUrl || ''
  // 调试信息：检查图片URL
  if (imageUrl) {
    console.log(`MessageItem: 获取图片URL:`, imageUrl)
  }
  return imageUrl
}

const formatTime = (timestamp: Date): string => {
  const now = new Date()
  const diff = now.getTime() - timestamp.getTime()

  if (diff < 60000) {
    // 1分钟内
    return '刚刚'
  } else if (diff < 3600000) {
    // 1小时内
    return `${Math.floor(diff / 60000)}分钟前`
  } else if (diff < 86400000) {
    // 1天内
    return `${Math.floor(diff / 3600000)}小时前`
  } else {
    return timestamp.toLocaleDateString('zh-CN')
  }
}

const handleImageLoad = () => {
  // 图片加载成功
}

const handleImageError = () => {
  // 图片加载失败处理
  console.error('图片加载失败')
}

const handleAvatarError = (event: Event) => {
  // 头像加载失败时，隐藏图片，显示emoji
  const imgElement = event.target as HTMLImageElement
  if (imgElement) {
    imgElement.style.display = 'none'
    // 创建一个span元素显示emoji
    const spanElement = document.createElement('span')
    spanElement.textContent = '🤖'
    spanElement.style.fontSize = '18px'
    imgElement.parentNode?.appendChild(spanElement)
  }
}
</script>

<style scoped>
.message-item {
  display: flex;
  margin-bottom: 20px;
  gap: 12px;
}

.message-item.user {
  flex-direction: row-reverse;
}

.message-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
  flex-shrink: 0;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
  border: 2px solid white;
}

.message-item.user .message-avatar {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.message-item.bot .message-avatar {
  background: linear-gradient(135deg, #6b7280 0%, #4b5563 100%);
  color: white;
  overflow: hidden;
}

.avatar-img {
  width: 100%;
  height: 100%;
  border-radius: 50%;
  object-fit: cover;
  display: block;
}

.message-content {
  flex: 1;
  max-width: 70%;
  display: flex;
  flex-direction: column;
}

.message-item.user .message-content {
  align-items: flex-end;
}

.message-item.bot .message-content {
  align-items: flex-start;
}

.message-header {
  margin-bottom: 8px;
  font-size: 12px;
  color: #666;
  display: flex;
  align-items: center;
  min-height: 40px; /* 与头像高度一致 */
}

.message-author {
  font-weight: 500;
  margin-right: 8px;
}

.message-time {
  opacity: 0.7;
}

.message-body {
  background: #f8f9fa;
  border-radius: 18px;
  padding: 12px 16px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  position: relative;
  display: inline-block;
  max-width: 100%;
  min-width: 60px;
  word-wrap: break-word;
}

.message-item.bot .message-body {
  padding: 16px 0;
  border-radius: 0;
}

.message-item.user .message-body {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  box-shadow: 0 2px 8px rgba(102, 126, 234, 0.3);
}

.message-item.bot .message-body {
  background: #f8f9fa;
  color: #333333;
  box-shadow: none;
  border: none;
}

.message-image {
  margin-bottom: 12px;
}

.content-image {
  max-width: 100%;
  max-height: 300px;
  border-radius: 8px;
  display: block;
}

.message-text {
  line-height: 1.6;
  word-wrap: break-word;
  font-size: 14px;
  letter-spacing: 0.2px;
}

/* Markdown内容样式 */
.markdown-content {
  line-height: 1.6;
}

.markdown-content h1,
.markdown-content h2,
.markdown-content h3,
.markdown-content h4,
.markdown-content h5,
.markdown-content h6 {
  margin: 12px 0 6px 0;
  font-weight: 600;
  line-height: 1.4;
}

.markdown-content h1:first-child,
.markdown-content h2:first-child,
.markdown-content h3:first-child,
.markdown-content h4:first-child,
.markdown-content h5:first-child,
.markdown-content h6:first-child {
  margin-top: 0;
}

.markdown-content h1 {
  font-size: 20px;
}
.markdown-content h2 {
  font-size: 18px;
}
.markdown-content h3 {
  font-size: 16px;
}
.markdown-content h4 {
  font-size: 15px;
}
.markdown-content h5 {
  font-size: 14px;
}
.markdown-content h6 {
  font-size: 13px;
}

.markdown-content p {
  margin: 6px 0;
  line-height: 1.5;
}

.markdown-content ul,
.markdown-content ol {
  margin: 6px 0;
  padding-left: 20px;
}

.markdown-content li {
  margin: 3px 0;
  line-height: 1.4;
}

.markdown-content blockquote {
  margin: 12px 0;
  padding: 8px 16px;
  border-left: 4px solid #ddd;
  background: rgba(0, 0, 0, 0.05);
  border-radius: 4px;
}

.markdown-content code {
  background: rgba(0, 0, 0, 0.1);
  padding: 2px 6px;
  border-radius: 4px;
  font-family: 'Courier New', monospace;
  font-size: 13px;
}

.markdown-content pre {
  background: rgba(0, 0, 0, 0.1);
  padding: 12px;
  border-radius: 8px;
  overflow-x: auto;
  margin: 12px 0;
}

.markdown-content pre code {
  background: none;
  padding: 0;
}

.markdown-content strong {
  font-weight: 600;
}

.markdown-content em {
  font-style: italic;
}

.markdown-content a {
  color: #007bff;
  text-decoration: none;
}

.markdown-content a:hover {
  text-decoration: underline;
}

.markdown-content table {
  border-collapse: collapse;
  width: 100%;
  margin: 12px 0;
}

.markdown-content th,
.markdown-content td {
  border: 1px solid #ddd;
  padding: 8px 12px;
  text-align: left;
}

.markdown-content th {
  background: rgba(0, 0, 0, 0.05);
  font-weight: 600;
}

.markdown-content img {
  max-width: 100%;
  height: auto;
  border-radius: 8px;
  margin: 8px 0;
}

.message-item.user .message-text {
  text-align: right;
}

.message-item.bot .message-text {
  text-align: left;
}

/* AI消息中的Markdown样式调整 */
.message-item.bot .markdown-content {
  color: #333333;
  padding-left: 0;
}

.message-item.bot .markdown-content h1,
.message-item.bot .markdown-content h2,
.message-item.bot .markdown-content h3,
.message-item.bot .markdown-content h4,
.message-item.bot .markdown-content h5,
.message-item.bot .markdown-content h6 {
  color: #1f2937;
  margin: 16px 0 8px 0;
  font-weight: 600;
}

.message-item.bot .markdown-content h1:first-child,
.message-item.bot .markdown-content h2:first-child,
.message-item.bot .markdown-content h3:first-child,
.message-item.bot .markdown-content h4:first-child,
.message-item.bot .markdown-content h5:first-child,
.message-item.bot .markdown-content h6:first-child {
  margin-top: 0;
  color: #111827;
}

.message-item.bot .markdown-content p {
  margin: 8px 0;
  line-height: 1.6;
  color: #374151;
}

.message-item.bot .markdown-content ul,
.message-item.bot .markdown-content ol {
  margin: 8px 0;
  padding-left: 20px;
}

.message-item.bot .markdown-content li {
  margin: 4px 0;
  line-height: 1.5;
  color: #374151;
}

.message-item.bot .markdown-content blockquote {
  background: #ffffff;
  border-left: 4px solid #d1d5db;
  margin: 12px 0;
  padding: 12px 16px;
  border-radius: 0 4px 4px 0;
  color: #6b7280;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.message-item.bot .markdown-content code {
  background: #ffffff;
  color: #dc2626;
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 13px;
  font-family: 'Courier New', monospace;
  border: 1px solid #e5e7eb;
}

.message-item.bot .markdown-content pre {
  background: #ffffff;
  padding: 16px;
  border-radius: 8px;
  margin: 12px 0;
  border: 1px solid #e5e7eb;
  overflow-x: auto;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.message-item.bot .markdown-content pre code {
  color: #374151;
  background: none;
  padding: 0;
  font-size: 14px;
}

.message-item.bot .markdown-content strong {
  color: #111827;
  font-weight: 600;
}

.message-item.bot .markdown-content em {
  color: #6b7280;
  font-style: italic;
}

.message-item.bot .markdown-content a {
  color: #2563eb;
  text-decoration: none;
}

.message-item.bot .markdown-content a:hover {
  color: #1d4ed8;
  text-decoration: underline;
}

.message-item.bot .markdown-content table {
  margin: 12px 0;
  border-radius: 8px;
  overflow: hidden;
  border: 1px solid #e5e7eb;
  width: 100%;
}

.message-item.bot .markdown-content table th {
  background: #ffffff;
  color: #374151;
  font-weight: 600;
  border-color: #e5e7eb;
  padding: 12px 16px;
}

.message-item.bot .markdown-content table td {
  border-color: #e5e7eb;
  color: #374151;
  padding: 12px 16px;
}

.streaming-indicator {
  display: flex;
  gap: 4px;
  align-items: center;
  margin-top: 8px;
  padding: 4px 8px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  backdrop-filter: blur(10px);
}

.dot {
  width: 8px;
  height: 8px;
  background: currentColor;
  border-radius: 50%;
  animation: pulse 1.4s ease-in-out infinite both;
  box-shadow: 0 0 8px currentColor;
}

.dot:nth-child(1) {
  animation-delay: -0.32s;
}

.dot:nth-child(2) {
  animation-delay: -0.16s;
}

@keyframes pulse {
  0%,
  80%,
  100% {
    transform: scale(0.8);
    opacity: 0.5;
  }
  40% {
    transform: scale(1.2);
    opacity: 1;
  }
}

/* 响应式设计 */
@media (max-width: 768px) {
  .message-content {
    max-width: 85%;
  }

  .message-avatar {
    width: 32px;
    height: 32px;
    font-size: 16px;
  }
}
</style>
