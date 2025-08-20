<template>
  <div class="user-center-container">
    <div class="user-center-header">
      <button @click="$router.go(-1)" class="back-btn">← 返回</button>
      <h1>用户中心</h1>
    </div>

    <div class="user-center-content">
      <!-- 用户信息卡片 -->
      <div class="user-card">
        <div class="user-avatar-large">
          {{ getUserInitial() }}
        </div>
        <div class="user-info">
          <h2>{{ authStore.user?.username }}</h2>
          <p class="user-email">{{ authStore.user?.email }}</p>
          <p class="user-id">用户ID: {{ authStore.user?.id }}</p>
        </div>
      </div>

      <!-- 功能区域 -->
      <div class="user-sections">
        <!-- 账户设置 -->
        <div class="section">
          <h3>账户设置</h3>
          <div class="section-content">
            <div class="setting-item">
              <label>用户名</label>
              <input v-model="editUsername" type="text" placeholder="输入新用户名" />
              <button @click="updateUsername" :disabled="!editUsername.trim()">更新</button>
            </div>
            <div class="setting-item">
              <label>邮箱</label>
              <input v-model="editEmail" type="email" placeholder="输入新邮箱" />
              <button @click="updateEmail" :disabled="!editEmail.trim()">更新</button>
            </div>
          </div>
        </div>

        <!-- 密码修改 -->
        <div class="section">
          <h3>密码修改</h3>
          <div class="section-content">
            <div class="setting-item">
              <label>当前密码</label>
              <input v-model="currentPassword" type="password" placeholder="输入当前密码" />
            </div>
            <div class="setting-item">
              <label>新密码</label>
              <input v-model="newPassword" type="password" placeholder="输入新密码" />
            </div>
            <div class="setting-item">
              <label>确认新密码</label>
              <input v-model="confirmPassword" type="password" placeholder="再次输入新密码" />
            </div>
            <button
              @click="updatePassword"
              :disabled="!canUpdatePassword"
              class="update-password-btn"
            >
              更新密码
            </button>
          </div>
        </div>

        <!-- 数据统计 -->
        <div class="section">
          <h3>使用统计</h3>
          <div class="stats-grid">
            <div class="stat-item">
              <div class="stat-number">{{ chatStore.sessions.length }}</div>
              <div class="stat-label">总对话数</div>
            </div>
            <div class="stat-item">
              <div class="stat-number">{{ totalMessages }}</div>
              <div class="stat-label">总消息数</div>
            </div>
            <div class="stat-item">
              <div class="stat-number">{{ imageMessages }}</div>
              <div class="stat-label">图片消息</div>
            </div>
          </div>
        </div>

        <!-- 账户操作 -->
        <div class="section">
          <h3>账户操作</h3>
          <div class="section-content">
            <button @click="handleLogout" class="logout-btn">退出登录</button>
            <button @click="deleteAccount" class="delete-account-btn">删除账户</button>
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

const router = useRouter()
const authStore = useAuthStore()
const chatStore = useChatStore()

// 编辑状态
const editUsername = ref(authStore.user?.username || '')
const editEmail = ref(authStore.user?.email || '')
const currentPassword = ref('')
const newPassword = ref('')
const confirmPassword = ref('')

// 获取用户头像初始字母
const getUserInitial = (): string => {
  const username = authStore.user?.username || 'U'
  return username.charAt(0).toUpperCase()
}

// 计算属性
const totalMessages = computed(() => {
  return chatStore.sessions.reduce((total, session) => {
    return total + session.messages.length
  }, 0)
})

const imageMessages = computed(() => {
  return chatStore.sessions.reduce((total, session) => {
    return total + session.messages.filter((msg) => msg.imageUrl || msg.imageFile).length
  }, 0)
})

const canUpdatePassword = computed(() => {
  return (
    currentPassword.value.trim() &&
    newPassword.value.trim() &&
    confirmPassword.value.trim() &&
    newPassword.value === confirmPassword.value
  )
})

// 更新用户名
const updateUsername = async () => {
  try {
    // TODO: 调用后端API更新用户名
    console.log('更新用户名:', editUsername.value)
    alert('用户名更新功能待实现')
  } catch (error) {
    console.error('更新用户名失败:', error)
    alert('更新失败')
  }
}

// 更新邮箱
const updateEmail = async () => {
  try {
    // TODO: 调用后端API更新邮箱
    console.log('更新邮箱:', editEmail.value)
    alert('邮箱更新功能待实现')
  } catch (error) {
    console.error('更新邮箱失败:', error)
    alert('更新失败')
  }
}

// 更新密码
const updatePassword = async () => {
  try {
    // TODO: 调用后端API更新密码
    console.log('更新密码')
    alert('密码更新功能待实现')

    // 清空密码字段
    currentPassword.value = ''
    newPassword.value = ''
    confirmPassword.value = ''
  } catch (error) {
    console.error('更新密码失败:', error)
    alert('更新失败')
  }
}

// 退出登录
const handleLogout = async () => {
  await authStore.logout()
  router.push('/login')
}

// 删除账户
const deleteAccount = () => {
  if (confirm('确定要删除账户吗？此操作不可恢复！')) {
    // TODO: 调用后端API删除账户
    console.log('删除账户')
    alert('删除账户功能待实现')
  }
}
</script>

<style scoped>
.user-center-container {
  max-width: 800px;
  margin: 0 auto;
  padding: 20px;
  background: white;
  min-height: 100vh;
}

.user-center-header {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 32px;
  padding-bottom: 16px;
  border-bottom: 2px solid #f0f0f0;
}

.back-btn {
  padding: 8px 16px;
  background: #f8f9fa;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.2s;
}

.back-btn:hover {
  background: #e9ecef;
}

.user-center-header h1 {
  margin: 0;
  color: #333;
  font-size: 24px;
}

.user-card {
  display: flex;
  align-items: center;
  padding: 24px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 12px;
  color: white;
  margin-bottom: 32px;
}

.user-avatar-large {
  width: 80px;
  height: 80px;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 32px;
  font-weight: 500;
  margin-right: 24px;
}

.user-info h2 {
  margin: 0 0 8px 0;
  font-size: 24px;
}

.user-email {
  margin: 0 0 4px 0;
  opacity: 0.9;
}

.user-id {
  margin: 0;
  opacity: 0.7;
  font-size: 14px;
}

.user-sections {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.section {
  background: #f8f9fa;
  border-radius: 12px;
  padding: 24px;
}

.section h3 {
  margin: 0 0 16px 0;
  color: #333;
  font-size: 18px;
}

.section-content {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

/* 账户操作按钮容器 */
.section-content:has(.logout-btn) {
  flex-direction: row;
  align-items: stretch;
}

.setting-item {
  display: flex;
  align-items: center;
  gap: 12px;
}

.setting-item label {
  min-width: 100px;
  font-weight: 500;
  color: #333;
}

.setting-item input {
  flex: 1;
  padding: 8px 12px;
  border: 1px solid #e0e0e0;
  border-radius: 6px;
  font-size: 14px;
}

.setting-item button {
  padding: 8px 16px;
  background: #007bff;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  transition: background-color 0.2s;
}

.setting-item button:hover:not(:disabled) {
  background: #0056b3;
}

.setting-item button:disabled {
  background: #ccc;
  cursor: not-allowed;
}

.update-password-btn {
  padding: 12px 24px;
  background: #28a745;
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 14px;
  transition: background-color 0.2s;
  align-self: flex-start;
}

.update-password-btn:hover:not(:disabled) {
  background: #218838;
}

.update-password-btn:disabled {
  background: #ccc;
  cursor: not-allowed;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 16px;
}

.stat-item {
  text-align: center;
  padding: 20px;
  background: white;
  border-radius: 8px;
  border: 1px solid #e0e0e0;
}

.stat-number {
  font-size: 32px;
  font-weight: bold;
  color: #007bff;
  margin-bottom: 8px;
}

.stat-label {
  font-size: 14px;
  color: #666;
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

.delete-account-btn {
  padding: 12px 24px;
  background: #6c757d;
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 14px;
  transition: background-color 0.2s;
  flex: 1;
  min-width: 120px;
}

.delete-account-btn:hover {
  background: #5a6268;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .user-center-container {
    padding: 16px;
  }

  .user-card {
    flex-direction: column;
    text-align: center;
  }

  .user-avatar-large {
    margin-right: 0;
    margin-bottom: 16px;
  }

  .setting-item {
    flex-direction: column;
    align-items: stretch;
  }

  .setting-item label {
    min-width: auto;
  }

  .stats-grid {
    grid-template-columns: 1fr;
  }
}
</style>
