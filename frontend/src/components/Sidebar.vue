<template>
  <div class="sidebar" :class="{ 'sidebar-collapsed': !isExpanded }">
    <!-- 侧边栏内容 -->
    <div class="sidebar-content">
      <!-- 顶部功能按钮 -->
      <div class="sidebar-top">
        <button
          @click="toggleSidebar"
          class="sidebar-toggle-btn"
          :title="isExpanded ? '收起侧边栏' : '展开侧边栏'"
        >
          <span v-if="isExpanded">◀</span>
          <span v-else>▶</span>
        </button>

        <button
          @click="startNewChat"
          class="sidebar-btn"
          :title="isExpanded ? '新建对话' : '新建对话'"
        >
          <span class="btn-icon">💬</span>
          <span v-if="isExpanded" class="btn-text">新建对话</span>
        </button>

        <button
          @click="showSearch = true"
          class="sidebar-btn"
          :title="isExpanded ? '搜索聊天' : '搜索聊天'"
        >
          <span class="btn-icon">🔍</span>
          <span v-if="isExpanded" class="btn-text">搜索聊天</span>
        </button>

        <button
          @click="$router.push('/history')"
          class="sidebar-btn"
          :title="isExpanded ? '历史记录' : '历史记录'"
        >
          <span class="btn-icon">📚</span>
          <span v-if="isExpanded" class="btn-text">历史记录</span>
        </button>
      </div>

      <!-- 历史聊天列表 -->
      <div class="sidebar-chats" v-if="isExpanded">
        <div class="chats-header">
          <h3>最近对话</h3>
        </div>
        <div class="chats-list">
          <div
            v-for="session in chatStore.sessions"
            :key="session.id"
            class="chat-item"
            :class="{ 'chat-item-active': session.id === chatStore.currentSession?.id }"
            @click="selectSession(session)"
          >
            <div class="chat-item-content">
              <div class="chat-title">{{ session.title }}</div>
              <div class="chat-preview">{{ getSessionPreview(session) }}</div>
              <div class="chat-time">{{ formatTime(session.updatedAt) }}</div>
            </div>
            <button
              @click.stop="deleteSession(session.id)"
              class="chat-delete-btn"
              title="删除对话"
            >
              🗑️
            </button>
          </div>
        </div>
      </div>

      <!-- 底部用户中心 -->
      <div class="sidebar-bottom">
        <button
          @click="$router.push('/user')"
          class="user-center-btn"
          :title="isExpanded ? '用户中心' : '用户中心'"
        >
          <div class="user-avatar">
            {{ getUserInitial() }}
          </div>
          <div v-if="isExpanded" class="user-info">
            <div class="user-name">{{ authStore.user?.username || '用户' }}</div>
            <div class="user-email">{{ authStore.user?.email || '' }}</div>
          </div>
        </button>
      </div>
    </div>

    <!-- 搜索弹窗 -->
    <div v-if="showSearch" class="search-modal" @click="showSearch = false">
      <div class="search-content" @click.stop>
        <div class="search-header">
          <h3>搜索聊天</h3>
          <button @click="showSearch = false" class="close-btn">×</button>
        </div>
        <div class="search-body">
          <input
            v-model="searchQuery"
            type="text"
            placeholder="输入关键词搜索..."
            class="search-input"
            @input="performSearch"
          />
          <div class="search-results">
            <div
              v-for="result in searchResults"
              :key="result.sessionId"
              class="search-result-item"
              @click="selectSearchResult(result)"
            >
              <div class="result-title">{{ result.sessionTitle }}</div>
              <div class="result-preview">{{ result.messagePreview }}</div>
              <div class="result-time">{{ formatTime(result.timestamp) }}</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useChatStore } from '@/stores/chat'
import type { ChatSession } from '@/stores/chat'

const router = useRouter()
const authStore = useAuthStore()
const chatStore = useChatStore()

// 侧边栏状态
const isExpanded = ref(true)
const showSearch = ref(false)
const searchQuery = ref('')
const searchResults = ref<any[]>([])

// 切换侧边栏展开/收起
const toggleSidebar = () => {
  isExpanded.value = !isExpanded.value
  emit('toggle', isExpanded.value)
}

// 定义emit
const emit = defineEmits<{
  toggle: [expanded: boolean]
  newChat: []
  selectSession: [session: ChatSession]
  searchResultSelected: [result: any]
}>()

// 新建对话
const startNewChat = () => {
  chatStore.createNewSession()
  emit('newChat')
  router.push('/')
}

// 选择会话
const selectSession = (session: ChatSession) => {
  chatStore.currentSession = session
  emit('selectSession', session)
  router.push('/')
}

// 删除会话
const deleteSession = async (sessionId: string) => {
  if (confirm('确定要删除这个对话吗？删除后无法恢复。')) {
    await chatStore.deleteSession(sessionId)
  }
}

// 获取会话预览
const getSessionPreview = (session: ChatSession): string => {
  if (session.messages.length === 0) return '空对话'

  const lastMessage = session.messages[session.messages.length - 1]
  if (lastMessage.imageUrl || lastMessage.imageFile) {
    return lastMessage.content || '[图片]'
  }
  return lastMessage.content || '空消息'
}

// 格式化时间
const formatTime = (timestamp: Date): string => {
  const now = new Date()
  const diff = now.getTime() - timestamp.getTime()

  if (diff < 60000) {
    return '刚刚'
  } else if (diff < 3600000) {
    return `${Math.floor(diff / 60000)}分钟前`
  } else if (diff < 86400000) {
    return `${Math.floor(diff / 3600000)}小时前`
  } else if (diff < 2592000000) {
    return `${Math.floor(diff / 86400000)}天前`
  } else {
    return timestamp.toLocaleDateString('zh-CN')
  }
}

// 获取用户头像初始字母
const getUserInitial = (): string => {
  const username = authStore.user?.username || 'U'
  return username.charAt(0).toUpperCase()
}

// 执行搜索
const performSearch = () => {
  if (!searchQuery.value.trim()) {
    searchResults.value = []
    return
  }

  const results: any[] = []
  const query = searchQuery.value.toLowerCase()

  chatStore.sessions.forEach((session) => {
    session.messages.forEach((message) => {
      if (message.content.toLowerCase().includes(query)) {
        results.push({
          sessionId: session.id,
          messageId: message.id,
          sessionTitle: session.title,
          messagePreview: message.content.substring(0, 50) + '...',
          timestamp: message.timestamp,
        })
      }
    })
  })

  searchResults.value = results.slice(0, 10) // 限制结果数量
}

// 选择搜索结果
const selectSearchResult = (result: any) => {
  const session = chatStore.sessions.find((s) => s.id === result.sessionId)
  if (session) {
    selectSession(session)
    emit('searchResultSelected', result)
    showSearch.value = false
  }
}

// 退出登录
const handleLogout = async () => {
  await authStore.logout()
  router.push('/login')
}
</script>

<style scoped>
.sidebar {
  position: fixed;
  left: 0;
  top: 0;
  height: 100vh;
  background: #f8f9fa;
  border-right: 1px solid #e0e0e0;
  transition: width 0.3s ease;
  width: 280px;
  z-index: 1000;
  display: flex;
  flex-direction: column;
}

.sidebar-collapsed {
  width: 60px;
}

/* 收起状态下的内容样式 */
.sidebar-collapsed .sidebar-content {
  padding: 16px 0;
}

.sidebar-content {
  display: flex;
  flex-direction: column;
  height: 100%;
  padding: 16px 0;
}

/* 顶部功能按钮 */
.sidebar-top {
  padding: 0 12px;
  margin-bottom: 20px;
}

.sidebar-toggle-btn {
  width: 100%;
  height: 40px;
  background: #007bff;
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 14px;
  margin-bottom: 8px;
  transition: background-color 0.2s;
}

.sidebar-toggle-btn:hover {
  background: #0056b3;
}

.sidebar-btn {
  width: 100%;
  height: 40px;
  background: transparent;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  cursor: pointer;
  margin-bottom: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0 12px;
  transition: all 0.2s;
}

.sidebar-btn:hover {
  background: #e9ecef;
  border-color: #007bff;
}

.btn-icon {
  font-size: 16px;
  margin-right: 8px;
  min-width: 20px;
}

/* 收起状态下的图标样式 */
.sidebar-collapsed .btn-icon {
  margin-right: 0;
  font-size: 18px;
}

/* 收起状态下的按钮样式 */
.sidebar-collapsed .sidebar-btn {
  justify-content: center;
  padding: 0;
}

.btn-text {
  font-size: 14px;
  color: #333;
}

/* 历史聊天列表 */
.sidebar-chats {
  flex: 1;
  overflow-y: auto;
  padding: 0 12px;
}

.chats-header {
  margin-bottom: 12px;
}

.chats-header h3 {
  font-size: 14px;
  color: #666;
  margin: 0;
  font-weight: 500;
}

.chats-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.chat-item {
  padding: 12px;
  border-radius: 8px;
  cursor: pointer;
  transition: background-color 0.2s;
  border: 1px solid transparent;
  position: relative;
}

.chat-item:hover {
  background: #e9ecef;
}

.chat-item-active {
  background: #e3f2fd;
  border-color: #007bff;
}

.chat-item-content {
  flex: 1;
}

.chat-title {
  font-size: 14px;
  font-weight: 500;
  color: #333;
  margin-bottom: 4px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.chat-preview {
  font-size: 12px;
  color: #666;
  margin-bottom: 4px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.chat-time {
  font-size: 11px;
  color: #999;
}

.chat-delete-btn {
  position: absolute;
  top: 8px;
  right: 8px;
  background: none;
  border: none;
  cursor: pointer;
  font-size: 12px;
  opacity: 0;
  transition: opacity 0.2s;
}

.chat-item:hover .chat-delete-btn {
  opacity: 1;
}

/* 底部用户中心 */
.sidebar-bottom {
  padding: 0 20px 12px 20px;
  border-top: 1px solid #e0e0e0;
  margin-top: auto;
  margin-right: 0;
  box-sizing: border-box;
}

/* 收起状态下的底部样式 */
.sidebar-collapsed .sidebar-bottom {
  padding: 12px 0;
  border-top: none;
}

.user-center-btn {
  width: 100%;
  background: transparent;
  border: none;
  cursor: pointer;
  display: flex;
  align-items: center;
  padding: 12px 8px;
  border-radius: 8px;
  transition: background-color 0.2s;
}

.user-center-btn:hover {
  background: #e9ecef;
}

.user-avatar {
  width: 32px;
  height: 32px;
  background: #007bff;
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  font-weight: 500;
  margin-right: 8px;
  flex-shrink: 0;
}

/* 收起状态下的用户头像样式 */
.sidebar-collapsed .user-avatar {
  margin-right: 0;
  width: 28px;
  height: 28px;
  font-size: 12px;
}

/* 收起状态下的用户中心按钮样式 */
.sidebar-collapsed .user-center-btn {
  justify-content: center;
  padding: 10px 0;
}

.user-info {
  flex: 1;
  text-align: left;
}

.user-name {
  font-size: 14px;
  font-weight: 500;
  color: #333;
}

.user-email {
  font-size: 12px;
  color: #666;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

/* 弹窗样式 */
.search-modal,
.user-modal {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 2000;
}

.search-content,
.user-content {
  background: white;
  border-radius: 12px;
  width: 90%;
  max-width: 500px;
  max-height: 80vh;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.search-header,
.user-header {
  padding: 20px;
  border-bottom: 1px solid #e0e0e0;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.search-header h3,
.user-header h3 {
  margin: 0;
  font-size: 18px;
  color: #333;
}

.close-btn {
  background: none;
  border: none;
  font-size: 24px;
  cursor: pointer;
  color: #666;
  padding: 0;
  width: 30px;
  height: 30px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.search-body,
.user-body {
  padding: 20px;
  flex: 1;
  overflow-y: auto;
}

.search-input {
  width: 100%;
  padding: 12px;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  font-size: 14px;
  margin-bottom: 16px;
}

.search-results {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.search-result-item {
  padding: 12px;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  cursor: pointer;
  transition: background-color 0.2s;
}

.search-result-item:hover {
  background: #f8f9fa;
}

.result-title {
  font-size: 14px;
  font-weight: 500;
  color: #333;
  margin-bottom: 4px;
}

.result-preview {
  font-size: 12px;
  color: #666;
  margin-bottom: 4px;
}

.result-time {
  font-size: 11px;
  color: #999;
}

/* 用户中心样式 */
.user-profile {
  display: flex;
  align-items: center;
  margin-bottom: 20px;
}

.profile-avatar {
  width: 60px;
  height: 60px;
  background: #007bff;
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  font-weight: 500;
  margin-right: 16px;
}

.profile-info {
  flex: 1;
}

.profile-name {
  font-size: 18px;
  font-weight: 500;
  color: #333;
  margin-bottom: 4px;
}

.profile-email {
  font-size: 14px;
  color: #666;
}

.user-actions {
  display: flex;
  gap: 12px;
  align-items: stretch;
}

.logout-btn {
  padding: 12px 24px;
  background: #dc3545;
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 14px;
  transition: background-color 0.2s;
  flex: 1;
  min-width: 120px;
}

.logout-btn:hover {
  background: #c82333;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .sidebar {
    width: 100%;
    transform: translateX(-100%);
  }

  .sidebar-collapsed {
    transform: translateX(0);
  }
}
</style>
