<template>
  <div class="chat-container" :class="{ 'sidebar-collapsed': !sidebarExpanded }">
    <!-- 侧边栏 -->
    <Sidebar
      @toggle="handleSidebarToggle"
      @newChat="handleNewChat"
      @selectSession="handleSelectSession"
      @searchResultSelected="handleSearchResultSelected"
    />

    <!-- 主聊天区域 -->
    <div class="chat-content">
      <div class="messages-area" ref="messagesContainer">
        <div v-if="!chatStore.currentSession?.messages.length" class="welcome">
          <h2>欢迎使用AI图像识别助手！</h2>
          <p>上传图片或输入URL，我就能帮你分析图像内容</p>
        </div>

        <MessageItem
          v-for="message in chatStore.currentSession?.messages"
          :key="message.id"
          :message="message"
        />
        <div ref="bottomMarker" class="bottom-marker" style="height: 5px; margin-top: 5px"></div>
      </div>

      <div class="input-area" ref="inputAreaRef">
        <div class="text-input">
          <!-- 图片预览区域 -->
          <div v-if="selectedImage" class="image-preview-area">
            <div class="preview-container">
              <img
                :src="getImagePreviewSrc()"
                alt="预览图片"
                class="preview-image"
                @error="handlePreviewError"
              />
              <button @click="removeSelectedImage" class="remove-preview-btn" title="移除图片">
                ×
              </button>
            </div>
          </div>

          <textarea
            ref="messageInputRef"
            v-model="inputMessage"
            @keydown.enter.prevent="sendMessage"
            :placeholder="getPlaceholderText()"
            class="message-input"
          />
          <div class="input-actions">
            <button @click="showImageUpload = true" class="upload-btn" title="上传图片">📷</button>
            <button @click="sendMessage" :disabled="!canSend" class="send-btn">发送</button>
          </div>
        </div>

        <!-- 图片上传弹窗 -->
        <div v-if="showImageUpload" class="image-upload-modal" @click="showImageUpload = false">
          <div class="modal-content" @click.stop>
            <div class="modal-header">
              <h3>上传图片</h3>
              <button @click="showImageUpload = false" class="close-btn">×</button>
            </div>
            <div class="modal-body">
              <ImageUpload v-model="selectedImage" @image-selected="showImageUpload = false" />
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 返回最新按钮 -->
    <button
      v-if="showBackToLatest"
      @click="scrollToBottom"
      class="back-to-latest-btn visible"
      title="返回最新消息"
    >
      <span class="icon">⬇️</span>
      <span>返回最新</span>
    </button>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, nextTick, onMounted, onUnmounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useChatStore } from '@/stores/chat'
import ImageUpload from '@/components/ImageUpload.vue'
import MessageItem from '@/components/MessageItem.vue'
import Sidebar from '@/components/Sidebar.vue'

const router = useRouter()
const authStore = useAuthStore()
const chatStore = useChatStore()

const inputMessage = ref('')
const selectedImage = ref<File | string>()
const messagesContainer = ref<HTMLElement>()
const inputAreaRef = ref<HTMLElement>()
const bottomMarker = ref<HTMLElement>()
const messageInputRef = ref<HTMLTextAreaElement>()
const showImageUpload = ref(false)
const sidebarExpanded = ref(true)
const showBackToLatest = ref(false)

const canSend = computed(() => {
  return (inputMessage.value.trim() || selectedImage.value) && !chatStore.isLoading
})

// 获取图片预览源
const getImagePreviewSrc = (): string => {
  if (selectedImage.value instanceof File) {
    return URL.createObjectURL(selectedImage.value)
  }
  return (selectedImage.value as string) || ''
}

// 获取占位符文本
const getPlaceholderText = (): string => {
  if (selectedImage.value) {
    return '描述这张图片或询问相关问题...'
  }
  return '描述你的问题...'
}

// 移除选中的图片
const removeSelectedImage = () => {
  selectedImage.value = undefined
}

// 处理预览图片加载错误
const handlePreviewError = () => {
  console.error('图片预览加载失败')
  // 可以选择显示一个默认的占位符图片
}

const sendMessage = async () => {
  if (!canSend.value) return

  const content = inputMessage.value.trim()
  const hasImage = selectedImage.value

  if (!content && !hasImage) return

  let imageUrl: string | undefined = undefined

  // 如果有图片文件，先上传获取URL
  if (selectedImage.value instanceof File) {
    try {
      const formData = new FormData()
      formData.append('file', selectedImage.value)

      const uploadResponse = await fetch('/api/upload/image', {
        method: 'POST',
        headers: {
          Authorization: `Bearer ${localStorage.getItem('token')}`,
        },
        body: formData,
      })

      if (uploadResponse.ok) {
        const uploadData = await uploadResponse.json()
        imageUrl = uploadData.image_url
      } else {
        chatStore.addMessage('图片上传失败，请重试。', 'bot')
        return
      }
    } catch (error) {
      console.error('图片上传失败:', error)
      chatStore.addMessage('图片上传出现问题，请重试。', 'bot')
      return
    }
  } else if (typeof selectedImage.value === 'string') {
    imageUrl = selectedImage.value
  }

  // 添加用户消息
  chatStore.addMessage(
    content || '[图片]',
    'user',
    imageUrl,
    selectedImage.value instanceof File ? selectedImage.value : undefined,
  )

  // 清空输入
  inputMessage.value = ''
  selectedImage.value = undefined

  // 滚动到底部
  await nextTick()
  scrollToBottom()

  // 调用后端AI聊天API（流式输出）
  try {
    const token = localStorage.getItem('token')
    console.log('发送流式聊天请求:', { message: content, token: token ? 'exists' : 'missing' })

    // 添加一个空的AI消息用于流式更新
    chatStore.addStreamingMessage('', 'bot')

    // 再次滚动到底部，确保看到新的AI消息
    await nextTick()
    scrollToBottom()

    const response = await fetch('/api/chat/chat/stream', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify({
        message: content || '[图片]',
        session_id: chatStore.currentSession?.id,
        image_url: imageUrl,
      }),
    })

    console.log('流式聊天API响应状态:', response.status)

    if (response.ok) {
      const reader = response.body?.getReader()
      const decoder = new TextDecoder()

      if (reader) {
        let buffer = ''

        while (true) {
          const { done, value } = await reader.read()
          if (done) break

          buffer += decoder.decode(value, { stream: true })
          const lines = buffer.split('\n')
          buffer = lines.pop() || ''

          for (const line of lines) {
            if (line.startsWith('data: ')) {
              try {
                const data = JSON.parse(line.slice(6))

                if (data.session_id) {
                  // 更新会话ID（如果是新会话）
                  if (
                    chatStore.currentSession &&
                    (!chatStore.currentSession.id || chatStore.currentSession.id === '')
                  ) {
                    chatStore.currentSession.id = data.session_id
                  }
                } else if (data.content && data.type === 'chunk') {
                  // 更新流式内容
                  if (data.content) {
                    chatStore.updateStreamingMessage(data.content)
                    // 每次内容更新后滚动到底部
                    nextTick(() => scrollToBottom())
                  }
                } else if (data.type === 'done') {
                  // 流式输出完成
                  console.log('流式输出完成')
                  // 完成后再次滚动确保看到完整内容
                  nextTick(() => scrollToBottom())
                } else if (data.type === 'error') {
                  // 错误处理
                  chatStore.updateStreamingMessage(data.content)
                  // 错误时也滚动到底部
                  nextTick(() => scrollToBottom())
                }
              } catch (parseError) {
                console.error('解析流式数据失败:', parseError)
              }
            }
          }
        }
      }
    } else {
      // 获取详细错误信息
      try {
        const errorData = await response.json()
        console.error('流式聊天API错误:', response.status, errorData)
        chatStore.updateStreamingMessage(
          `AI服务错误 (${response.status}): ${errorData.detail || '未知错误'}`,
        )
      } catch (parseError) {
        console.error('解析错误响应失败:', parseError)
        chatStore.updateStreamingMessage(`AI服务错误 (${response.status}): ${response.statusText}`)
      }
    }
  } catch (error: any) {
    console.error('AI流式聊天失败:', error)
    chatStore.updateStreamingMessage(`网络连接出现问题: ${error?.message || '未知错误'}`)
  }

  nextTick(() => scrollToBottom())
}

const scrollToBottom = () => {
  console.log('执行滚动到底部操作')

  // 使用锚点元素滚动，兼容性更好
  if (bottomMarker.value) {
    console.log('使用bottomMarker滚动')
    // 双层保障：在下一帧再触发，避免布局尚未完成
    requestAnimationFrame(() => {
      bottomMarker.value?.scrollIntoView({
        behavior: 'smooth',
        block: 'start',
        inline: 'nearest',
      })
      // 滚动完成后隐藏按钮
      setTimeout(() => {
        showBackToLatest.value = false
      }, 500)
    })
  } else if (messagesContainer.value) {
    console.log('使用messagesContainer滚动')
    messagesContainer.value.scrollTo({
      top: messagesContainer.value.scrollHeight,
      behavior: 'smooth',
    })
    // 滚动完成后隐藏按钮
    setTimeout(() => {
      showBackToLatest.value = false
    }, 500)
  } else {
    console.warn('滚动元素未找到')
  }
}

// 滚动到指定消息
const scrollToMessage = (messageId: string) => {
  console.log('滚动到消息:', messageId)

  // 查找消息元素
  const messageElement = document.querySelector(`[data-message-id="${messageId}"]`)
  if (messageElement) {
    messageElement.scrollIntoView({
      behavior: 'smooth',
      block: 'center',
      inline: 'nearest',
    })

    // 高亮显示该消息
    messageElement.classList.add('highlight-message')
    setTimeout(() => {
      messageElement.classList.remove('highlight-message')
    }, 2000)
  } else {
    console.warn('未找到消息元素:', messageId)
  }
}

const handleLogout = async () => {
  await authStore.logout()
  router.push('/login')
}

const handleSidebarToggle = (expanded: boolean) => {
  sidebarExpanded.value = expanded
}

// 自动聚焦到输入框的通用函数
const autoFocusInput = () => {
  nextTick(() => {
    // 检查当前会话是否为空，如果是空会话则自动聚焦
    if (chatStore.currentSession && chatStore.currentSession.messages.length === 0) {
      messageInputRef.value?.focus()
    }
  })
}

const handleNewChat = () => {
  autoFocusInput()
}

const handleSelectSession = (session: any) => {
  // 当选择会话时，如果是空会话则自动聚焦
  autoFocusInput()
}

const handleSearchResultSelected = (result: any) => {
  // 当选择搜索结果时，自动聚焦并滚动到相关消息
  autoFocusInput()
  // 延迟滚动到相关消息，确保DOM已渲染
  nextTick(() => {
    setTimeout(() => {
      scrollToMessage(result.messageId)
    }, 200)
  })
}

const startNewChat = () => {
  chatStore.createNewSession()
  inputMessage.value = ''
  selectedImage.value = undefined
  nextTick(() => {
    scrollToBottom()
    autoFocusInput()
  })
}

onMounted(() => {
  if (!chatStore.currentSession) {
    chatStore.createNewSession()
  }

  // 页面加载完成后，如果是空会话则自动聚焦
  autoFocusInput()

  // 计算并同步输入栏高度到CSS变量，供消息区域留白使用
  const updateInputAreaHeight = () => {
    const h = inputAreaRef.value?.offsetHeight ?? 80
    document.documentElement.style.setProperty('--input-area-height', `${h}px`)
  }

  updateInputAreaHeight()

  // 监听输入栏尺寸变化
  if (window.ResizeObserver && inputAreaRef.value) {
    const ro = new ResizeObserver(() => updateInputAreaHeight())
    ro.observe(inputAreaRef.value)
    ;(inputAreaRef as any)._ro = ro
  } else {
    // 兜底：窗口尺寸变化时也更新
    window.addEventListener('resize', updateInputAreaHeight)
    ;(inputAreaRef as any)._cleanupResize = () =>
      window.removeEventListener('resize', updateInputAreaHeight)
  }

  // 监听消息区域的滚动事件
  if (messagesContainer.value) {
    const handleScroll = () => {
      if (messagesContainer.value) {
        const { scrollTop, scrollHeight, clientHeight } = messagesContainer.value
        const isAtBottom = scrollTop + clientHeight >= scrollHeight - 10 // 10px的容差
        showBackToLatest.value = !isAtBottom
      }
    }

    messagesContainer.value.addEventListener('scroll', handleScroll)
    ;(messagesContainer as any)._scrollHandler = handleScroll
  }
})

onUnmounted(() => {
  const ro = (inputAreaRef as any)._ro as ResizeObserver | undefined
  if (ro && inputAreaRef.value) ro.unobserve(inputAreaRef.value)
  const cleanup = (inputAreaRef as any)._cleanupResize as (() => void) | undefined
  if (cleanup) cleanup()

  // 清理滚动事件监听器
  const scrollHandler = (messagesContainer as any)._scrollHandler as (() => void) | undefined
  if (scrollHandler && messagesContainer.value) {
    messagesContainer.value.removeEventListener('scroll', scrollHandler)
  }
})

// 监听消息变化，自动滚动到底部
watch(
  () => chatStore.currentSession?.messages,
  () => {
    nextTick(() => scrollToBottom())
  },
  { deep: true },
)

// 进入任意会话时（或切换会话）自动滚动到底部并聚焦
watch(
  () => chatStore.currentSession?.id,
  () => {
    // 增加延迟确保DOM完全渲染
    nextTick(() => {
      setTimeout(() => {
        scrollToBottom()
        autoFocusInput()
      }, 100)
    })
  },
  { immediate: true },
)
</script>

<style scoped>
.chat-container {
  height: 100vh;
  display: flex;
  background: #f8f9fa;
  position: relative;
}

.chat-content {
  flex: 1;
  margin-left: 280px; /* 为侧边栏留出空间 */
  display: flex;
  flex-direction: column;
  transition: margin-left 0.3s ease;
  position: relative;
  z-index: 5;
  background: #f8f9fa;
}

/* 当侧边栏收起时的样式 */
.chat-container.sidebar-collapsed .chat-content {
  margin-left: 60px;
}

.messages-area {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
  /* 为固定的输入框留出空间 */
  padding-bottom: 100px;
  position: relative;
  background: #f8f9fa;
}

.welcome {
  text-align: center;
  padding: 120px 20px;
  color: #666;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 60vh;
}

.welcome h2 {
  margin: 0 0 20px 0;
  color: #333;
  font-size: 28px;
  font-weight: 600;
}

.welcome p {
  font-size: 18px;
  line-height: 1.6;
  max-width: 500px;
}

.input-area {
  background: #f8f9fa;
  border-top: 1px solid #e0e0e0;
  padding: 12px 20px;
  box-shadow: 0 -2px 8px rgba(0, 0, 0, 0.1);
  position: fixed;
  bottom: 0;
  left: 280px; /* 为侧边栏留出空间 */
  right: 0;
  z-index: 10;
  min-height: 80px;
  max-height: 200px;
  overflow-y: auto;
  transition: left 0.3s ease;
  box-sizing: border-box;
}

/* 当侧边栏收起时的输入框样式 */
.chat-container.sidebar-collapsed .input-area {
  left: 60px;
}

.text-input {
  display: flex;
  gap: 12px;
  align-items: flex-end;
  flex-wrap: wrap;
}

.image-preview-area {
  width: 100%;
  margin-bottom: 4px;
  display: flex;
  justify-content: flex-start;
}

.preview-container {
  position: relative;
  display: inline-block;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  background: #f8f9fa;
}

.preview-image {
  width: 64px;
  height: 48px;
  object-fit: cover;
  display: block;
}

.remove-preview-btn {
  position: absolute;
  top: -6px;
  right: -6px;
  width: 20px;
  height: 20px;
  background: #dc3545;
  color: white;
  border: none;
  border-radius: 50%;
  cursor: pointer;
  font-size: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
  transition: all 0.2s ease;
}

.remove-preview-btn:hover {
  background: #c82333;
  transform: scale(1.1);
}

.input-actions {
  display: flex;
  gap: 8px;
  align-items: flex-end;
}

.message-input {
  flex: 1;
  padding: 12px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-radius: 12px;
  resize: vertical;
  min-height: 40px;
  max-height: 120px;
  font-family: inherit;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  transition: all 0.3s ease;
  font-size: 14px;
}

.message-input:focus {
  outline: none;
  border-color: rgba(102, 126, 234, 0.5);
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
  background: rgba(255, 255, 255, 0.95);
}

.send-btn {
  padding: 8px 16px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 12px;
  cursor: pointer;
  height: 40px;
  font-weight: 600;
  transition: all 0.3s ease;
  box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
  font-size: 14px;
}

.send-btn:hover:not(:disabled) {
  background: linear-gradient(135deg, #5a6fd8 0%, #6a4190 100%);
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
}

.send-btn:disabled {
  background: linear-gradient(135deg, #ccc 0%, #999 100%);
  cursor: not-allowed;
  transform: none;
  box-shadow: none;
}

.upload-btn {
  padding: 8px;
  background: white;
  border: 2px solid #ddd;
  border-radius: 10px;
  cursor: pointer;
  font-size: 16px;
  transition: all 0.3s ease;
  height: 40px;
  width: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.upload-btn:hover {
  background: #f8f9fa;
  border-color: #007bff;
  transform: translateY(-2px);
  box-shadow: 0 4px 15px rgba(0, 123, 255, 0.3);
}

/* 图片上传弹窗样式 */
.image-upload-modal {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  backdrop-filter: blur(5px);
  padding: 20px;
}

.modal-content {
  background: white;
  border-radius: 16px;
  padding: 0;
  max-width: 500px;
  width: 90%;
  max-height: calc(100vh - 40px);
  overflow: auto;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
  animation: modalSlideIn 0.3s ease;
}

@keyframes modalSlideIn {
  from {
    opacity: 0;
    transform: translateY(-20px) scale(0.95);
  }
  to {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  border-bottom: 1px solid #eee;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.modal-header h3 {
  margin: 0;
  font-size: 18px;
}

.close-btn {
  background: none;
  border: none;
  color: white;
  font-size: 24px;
  cursor: pointer;
  padding: 0;
  width: 30px;
  height: 30px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  transition: background-color 0.3s ease;
}

.close-btn:hover {
  background: rgba(255, 255, 255, 0.2);
}

.modal-body {
  padding: 20px;
}

/* 高亮消息样式 */
.highlight-message {
  animation: highlightPulse 2s ease-in-out;
  border: 2px solid #007bff !important;
  border-radius: 8px;
  box-shadow: 0 0 10px rgba(0, 123, 255, 0.3);
}

@keyframes highlightPulse {
  0%,
  100% {
    border-color: #007bff;
    box-shadow: 0 0 10px rgba(0, 123, 255, 0.3);
  }
  50% {
    border-color: #0056b3;
    box-shadow: 0 0 20px rgba(0, 123, 255, 0.5);
  }
}

/* 返回最新按钮样式 */
.back-to-latest-btn {
  position: fixed;
  bottom: 100px;
  left: 50%;
  transform: translateX(-50%) translateY(20px);
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 50px;
  padding: 12px 20px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 600;
  box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
  transition: all 0.3s ease;
  z-index: 100;
  display: flex;
  align-items: center;
  gap: 8px;
  opacity: 0;
  pointer-events: none;
}

.back-to-latest-btn.visible {
  opacity: 1;
  transform: translateX(-50%) translateY(0);
  pointer-events: auto;
}

.back-to-latest-btn:hover {
  background: linear-gradient(135deg, #5a6fd8 0%, #6a4190 100%);
  transform: translateX(-50%) translateY(-2px);
  box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
}

.back-to-latest-btn .icon {
  font-size: 16px;
}
</style>
