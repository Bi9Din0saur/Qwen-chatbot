import { defineStore } from 'pinia'
import { ref } from 'vue'

export interface User {
  id: number
  username: string
  email: string
}

export const useAuthStore = defineStore('auth', () => {
  const user = ref<User | null>(null)
  const token = ref<string | null>(localStorage.getItem('token'))
  const isAuthenticated = ref<boolean>(!!token.value)

  const login = async (username: string, password: string) => {
    try {
      // 调用后端登录API - 使用正确的表单格式
      const formData = new URLSearchParams()
      formData.append('username', username)
      formData.append('password', password)

      const response = await fetch('/api/auth/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: formData,
      })

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.detail || '登录失败')
      }

      const data = await response.json()
      token.value = data.access_token
      user.value = data.user
      isAuthenticated.value = true
      localStorage.setItem('token', data.access_token)

      // 登录成功后加载用户专属数据
      const { useChatStore } = await import('@/stores/chat')
      const chatStore = useChatStore()
      await chatStore.loadSessions()

      return { success: true }
    } catch (error) {
      return { success: false, error: error instanceof Error ? error.message : '登录失败' }
    }
  }

  const logout = async () => {
    // 清理当前用户的内存数据（但不删除数据库数据）
    const { useChatStore } = await import('@/stores/chat')
    const chatStore = useChatStore()
    chatStore.clearAllData()

    user.value = null
    token.value = null
    isAuthenticated.value = false
    localStorage.removeItem('token')
  }

  const checkAuth = async () => {
    if (!token.value) return false

    try {
      // TODO: 调用后端验证token API
      const response = await fetch('/api/auth/verify', {
        headers: {
          Authorization: `Bearer ${token.value}`,
        },
      })

      if (!response.ok) {
        logout()
        return false
      }

      const data = await response.json()
      user.value = data.user
      return true
    } catch (error) {
      logout()
      return false
    }
  }

  const mockLogin = (username: string) => {
    // 模拟登录，用于开发测试
    const mockUser: User = {
      id: 1,
      username: username,
      email: username + '@example.com',
    }

    const mockToken = 'mock-token-' + Date.now()

    user.value = mockUser
    token.value = mockToken
    isAuthenticated.value = true
    localStorage.setItem('token', mockToken)

    return { success: true }
  }

  return {
    user,
    token,
    isAuthenticated,
    login,
    logout,
    checkAuth,
    mockLogin,
  }
})
