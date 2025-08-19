<template>
  <div class="history-container">
    <div class="history-header">
      <h1>对话历史</h1>
      <button @click="startNewChat" class="new-chat-button">+ 新对话</button>
    </div>

    <div v-if="chatStore.sessions.length === 0" class="empty-state">
      <div class="empty-icon">💬</div>
      <h3>还没有对话记录</h3>
      <p>开始你的第一次AI图像识别对话吧！</p>
      <button @click="startNewChat" class="start-chat-button">开始对话</button>
    </div>

    <div v-else class="sessions-list">
      <div
        v-for="session in chatStore.sessions"
        :key="session.id"
        class="session-item"
        @click="selectSession(session)"
      >
        <div class="session-info">
          <h3 class="session-title">{{ session.title }}</h3>
          <p class="session-preview">
            {{ getSessionPreview(session) }}
          </p>
          <div class="session-meta">
            <span class="session-time">
              {{ formatTime(session.updatedAt) }}
            </span>
            <span class="message-count"> {{ session.messages.length }} 条消息 </span>
          </div>
        </div>

        <div class="session-actions">
          <button @click.stop="deleteSession(session.id)" class="delete-button" title="删除对话">
            🗑️
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useChatStore } from '@/stores/chat'
import type { ChatSession } from '@/stores/chat'

const router = useRouter()
const chatStore = useChatStore()

const startNewChat = () => {
  // 创建新的对话会话
  chatStore.createNewSession()
  // 跳转到聊天页面
  router.push('/')
}

const selectSession = async (session: ChatSession) => {
  // 选择现有会话
  chatStore.currentSession = session
  // 等待路由跳转完成
  await router.push('/')
}

const deleteSession = async (sessionId: string) => {
  if (confirm('确定要删除这个对话吗？删除后无法恢复。')) {
    await chatStore.deleteSession(sessionId)
  }
}

const getSessionPreview = (session: ChatSession): string => {
  if (session.messages.length === 0) return '空对话'

  const lastMessage = session.messages[session.messages.length - 1]
  if (lastMessage.imageUrl || lastMessage.imageFile) {
    return lastMessage.content || '[图片]'
  }
  return lastMessage.content || '空消息'
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
  } else if (diff < 2592000000) {
    // 30天内
    return `${Math.floor(diff / 86400000)}天前`
  } else {
    return timestamp.toLocaleDateString('zh-CN')
  }
}

onMounted(() => {
  chatStore.loadSessions()
})
</script>

<style scoped>
.history-container {
  max-width: 800px;
  margin: 0 auto;
  padding: 20px;
}

.history-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 32px;
  padding-bottom: 16px;
  border-bottom: 2px solid #f0f0f0;
}

.history-header h1 {
  margin: 0;
  color: #333;
  font-size: 28px;
  font-weight: 600;
}

.new-chat-button {
  padding: 12px 24px;
  background: #007bff;
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 16px;
  cursor: pointer;
  transition: background-color 0.2s;
}

.new-chat-button:hover {
  background: #0056b3;
}

.empty-state {
  text-align: center;
  padding: 80px 20px;
  color: #666;
}

.empty-icon {
  font-size: 64px;
  margin-bottom: 24px;
}

.empty-state h3 {
  margin: 0 0 16px 0;
  color: #333;
  font-size: 24px;
}

.empty-state p {
  margin: 0 0 32px 0;
  font-size: 16px;
}

.start-chat-button {
  padding: 16px 32px;
  background: #007bff;
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 18px;
  cursor: pointer;
  transition: all 0.2s;
}

.start-chat-button:hover {
  background: #0056b3;
  transform: translateY(-2px);
}

.sessions-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.session-item {
  background: white;
  border: 1px solid #e0e0e0;
  border-radius: 12px;
  padding: 20px;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
}

.session-item:hover {
  border-color: #007bff;
  box-shadow: 0 4px 12px rgba(0, 123, 255, 0.1);
  transform: translateY(-2px);
}

.session-info {
  flex: 1;
}

.session-title {
  margin: 0 0 8px 0;
  color: #333;
  font-size: 18px;
  font-weight: 600;
}

.session-preview {
  margin: 0 0 12px 0;
  color: #666;
  font-size: 14px;
  line-height: 1.4;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.session-meta {
  display: flex;
  gap: 16px;
  font-size: 12px;
  color: #999;
}

.session-time,
.message-count {
  display: flex;
  align-items: center;
  gap: 4px;
}

.session-actions {
  display: flex;
  gap: 8px;
}

.delete-button {
  background: none;
  border: none;
  font-size: 18px;
  cursor: pointer;
  padding: 8px;
  border-radius: 6px;
  transition: background-color 0.2s;
  opacity: 0.6;
}

.delete-button:hover {
  background: #f8f9fa;
  opacity: 1;
}

@media (max-width: 768px) {
  .history-container {
    padding: 16px;
  }

  .history-header {
    flex-direction: column;
    gap: 16px;
    align-items: stretch;
  }

  .new-chat-button {
    width: 100%;
  }

  .session-item {
    padding: 16px;
  }

  .session-meta {
    flex-direction: column;
    gap: 8px;
  }
}
</style>
