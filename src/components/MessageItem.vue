<template>
  <div :class="['message-item', message.type]">
    <div class="message-avatar">
      {{ message.type === 'user' ? '👤' : '🤖' }}
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
          {{ message.content }}
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
import type { Message } from '@/stores/chat'

interface Props {
  message: Message
  isStreaming?: boolean
}

const props = defineProps<Props>()

const getImageSrc = (): string => {
  if (props.message.imageFile) {
    return URL.createObjectURL(props.message.imageFile)
  }
  return props.message.imageUrl || ''
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
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
  color: white;
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
}

.message-author {
  font-weight: 500;
  margin-right: 8px;
}

.message-time {
  opacity: 0.7;
}

.message-body {
  background: white;
  border-radius: 18px;
  padding: 12px 16px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  position: relative;
  display: inline-block;
  max-width: 100%;
  min-width: 60px;
  word-wrap: break-word;
}

.message-item.user .message-body {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  box-shadow: 0 2px 8px rgba(102, 126, 234, 0.3);
}

.message-item.bot .message-body {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
  color: white;
  box-shadow: 0 2px 8px rgba(240, 147, 251, 0.3);
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

.message-item.user .message-text {
  text-align: right;
}

.message-item.bot .message-text {
  text-align: left;
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
