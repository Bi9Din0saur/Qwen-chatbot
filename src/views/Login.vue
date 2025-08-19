<template>
  <div class="login-container">
    <div class="login-card">
      <!-- 登录表单 -->
      <div v-if="!showRegister" class="auth-form">
        <div class="auth-header">
          <h1>登录聊天机器人</h1>
          <p>请登录以开始使用AI图像识别功能</p>
        </div>

        <form @submit.prevent="handleLogin" class="auth-form-content">
          <div class="form-group">
            <label for="username">用户名</label>
            <input
              id="username"
              v-model="username"
              type="text"
              required
              placeholder="请输入用户名"
              class="form-input"
            />
          </div>

          <div class="form-group">
            <label for="password">密码</label>
            <input
              id="password"
              v-model="password"
              type="password"
              required
              placeholder="请输入密码"
              class="form-input"
            />
          </div>

          <div v-if="error" class="error-message">
            {{ error }}
          </div>

          <button type="submit" :disabled="isLoading" class="auth-button">
            {{ isLoading ? '登录中...' : '登录' }}
          </button>
        </form>

        <div class="auth-footer">
          <p>还没有账号？ <a href="#" @click.prevent="showRegister = true">立即注册</a></p>
        </div>
      </div>

      <!-- 注册表单 -->
      <div v-else class="auth-form">
        <div class="auth-header">
          <h1>注册新账号</h1>
          <p>创建账号以使用AI图像识别功能</p>
        </div>

        <form @submit.prevent="handleRegister" class="auth-form-content">
          <div class="form-group">
            <label for="reg-username">用户名</label>
            <input
              id="reg-username"
              v-model="regUsername"
              type="text"
              required
              placeholder="请输入用户名"
              class="form-input"
            />
          </div>

          <div class="form-group">
            <label for="reg-email">邮箱</label>
            <input
              id="reg-email"
              v-model="regEmail"
              type="email"
              required
              placeholder="请输入邮箱"
              class="form-input"
            />
          </div>

          <div class="form-group">
            <label for="reg-password">密码</label>
            <input
              id="reg-password"
              v-model="regPassword"
              type="password"
              required
              placeholder="请输入密码"
              class="form-input"
            />
          </div>

          <div class="form-group">
            <label for="reg-confirm-password">确认密码</label>
            <input
              id="reg-confirm-password"
              v-model="regConfirmPassword"
              type="password"
              required
              placeholder="请再次输入密码"
              class="form-input"
            />
          </div>

          <div v-if="error" class="error-message">
            {{ error }}
          </div>

          <button type="submit" :disabled="isLoading" class="auth-button">
            {{ isLoading ? '注册中...' : '注册' }}
          </button>
        </form>

        <div class="auth-footer">
          <p>已有账号？ <a href="#" @click.prevent="showRegister = false">立即登录</a></p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()

// 登录相关
const username = ref('')
const password = ref('')

// 注册相关
const regUsername = ref('')
const regEmail = ref('')
const regPassword = ref('')
const regConfirmPassword = ref('')

// 通用状态
const error = ref('')
const isLoading = ref(false)
const showRegister = ref(false)

const handleLogin = async () => {
  if (!username.value.trim() || !password.value.trim()) {
    error.value = '请填写完整的登录信息'
    return
  }

  isLoading.value = true
  error.value = ''

  try {
    // 真实的后端API调用
    console.log('尝试登录用户:', {
      username: username.value,
      password: password.value.length + '位密码',
    })

    const result = await authStore.login(username.value, password.value)

    if (result.success) {
      router.push('/')
    } else {
      error.value = result.error || '登录失败'
    }
  } catch (err) {
    console.error('Login error:', err)
    error.value = `登录过程中发生错误: ${err instanceof Error ? err.message : String(err)}`
  } finally {
    isLoading.value = false
  }
}

const handleRegister = async () => {
  // 验证输入
  if (
    !regUsername.value.trim() ||
    !regEmail.value.trim() ||
    !regPassword.value ||
    !regConfirmPassword.value
  ) {
    error.value = '请填写完整的注册信息'
    return
  }

  if (regPassword.value !== regConfirmPassword.value) {
    error.value = '两次输入的密码不一致'
    return
  }

  if (regPassword.value.length < 6) {
    error.value = '密码长度不能少于6位'
    return
  }

  isLoading.value = true
  error.value = ''

  try {
    // 真实的后端API调用
    console.log('尝试注册用户:', {
      username: regUsername.value,
      email: regEmail.value,
      password: regPassword.value.length + '位密码',
    })

    const response = await fetch('/api/auth/register', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        username: regUsername.value,
        email: regEmail.value,
        password: regPassword.value,
      }),
    })

    if (response.ok) {
      // 注册成功，切换到登录页面
      showRegister.value = false
      error.value = ''

      // 清空注册表单
      regUsername.value = ''
      regEmail.value = ''
      regPassword.value = ''
      regConfirmPassword.value = ''

      // 显示成功消息
      alert('🎉 注册成功！请使用新账号登录。')
    } else {
      const data = await response.json()
      error.value = data.detail || `注册失败 (${response.status})`
    }
  } catch (err) {
    console.error('Registration error:', err)
    error.value = `注册过程中发生错误: ${err instanceof Error ? err.message : String(err)}`
  } finally {
    isLoading.value = false
  }
}

// 切换表单时清空错误信息
const clearError = () => {
  error.value = ''
}

// 监听showRegister变化，清空错误信息
watch(showRegister, clearError)
</script>

<style scoped>
.login-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px;
}

.login-card {
  background: white;
  border-radius: 16px;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
  padding: 40px;
  width: 100%;
  max-width: 400px;
}

.auth-header {
  text-align: center;
  margin-bottom: 32px;
}

.auth-header h1 {
  color: #333;
  margin-bottom: 8px;
  font-size: 28px;
  font-weight: 600;
}

.auth-header p {
  color: #666;
  font-size: 16px;
}

.auth-form-content {
  margin-bottom: 24px;
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  color: #333;
  font-weight: 500;
  font-size: 14px;
}

.form-input {
  width: 100%;
  padding: 12px 16px;
  border: 2px solid #e1e5e9;
  border-radius: 8px;
  font-size: 16px;
  transition: border-color 0.2s;
  outline: none;
}

.form-input:focus {
  border-color: #667eea;
}

.error-message {
  background: #fef2f2;
  color: #dc2626;
  padding: 16px;
  border-radius: 8px;
  margin-bottom: 20px;
  font-size: 14px;
  border: 1px solid #fecaca;
  line-height: 1.5;
  white-space: pre-line;
}

.error-message::before {
  content: '⚠️ ';
  margin-right: 8px;
}

.auth-button {
  width: 100%;
  padding: 14px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: transform 0.2s;
}

.auth-button:hover:not(:disabled) {
  transform: translateY(-2px);
}

.auth-button:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.auth-footer {
  text-align: center;
  color: #666;
  font-size: 14px;
}

.auth-footer a {
  color: #667eea;
  text-decoration: none;
  font-weight: 500;
}

.auth-footer a:hover {
  text-decoration: underline;
}

@media (max-width: 480px) {
  .login-card {
    padding: 24px;
  }

  .auth-header h1 {
    font-size: 24px;
  }
}
</style>
