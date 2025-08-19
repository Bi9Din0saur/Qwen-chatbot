import { defineStore } from 'pinia'
import { ref } from 'vue'

export interface Message {
  id: string
  content: string
  type: 'user' | 'bot'
  timestamp: Date
  imageUrl?: string
  imageFile?: File
}

export interface ChatSession {
  id: string
  title: string
  messages: Message[]
  createdAt: Date
  updatedAt: Date
}

export const useChatStore = defineStore('chat', () => {
  const currentSession = ref<ChatSession | null>(null)
  const sessions = ref<ChatSession[]>([])
  const isLoading = ref(false)

  const createNewSession = () => {
    const session: ChatSession = {
      id: '', // 让后端生成ID
      title: '新对话',
      messages: [],
      createdAt: new Date(),
      updatedAt: new Date(),
    }
    currentSession.value = session
    sessions.value.unshift(session)
    return session
  }

  const addMessage = (
    content: string,
    type: 'user' | 'bot',
    imageUrl?: string,
    imageFile?: File,
  ) => {
    if (!currentSession.value) {
      createNewSession()
    }

    const message: Message = {
      id: Date.now().toString(),
      content,
      type,
      timestamp: new Date(),
      imageUrl,
      imageFile,
    }

    currentSession.value!.messages.push(message)
    currentSession.value!.updatedAt = new Date()

    // 更新标题
    if (type === 'user' && currentSession.value!.title === '新对话') {
      currentSession.value!.title = content.slice(0, 20) + (content.length > 20 ? '...' : '')
    }

    return message
  }

  const addStreamingMessage = (
    content: string,
    type: 'user' | 'bot',
    imageUrl?: string,
    imageFile?: File,
  ) => {
    if (!currentSession.value) {
      createNewSession()
    }

    const message: Message = {
      id: Date.now().toString(),
      content,
      type,
      timestamp: new Date(),
      imageUrl,
      imageFile,
    }

    currentSession.value!.messages.push(message)
    currentSession.value!.updatedAt = new Date()

    // 更新标题
    if (type === 'user' && currentSession.value!.title === '新对话') {
      currentSession.value!.title = content.slice(0, 20) + (content.length > 20 ? '...' : '')
    }

    return message
  }

  const updateStreamingMessage = (content: string) => {
    if (!currentSession.value || currentSession.value.messages.length === 0) return

    const lastMessage = currentSession.value.messages[currentSession.value.messages.length - 1]
    if (lastMessage.type === 'bot') {
      lastMessage.content += content
    }
  }

  const updateLastMessage = (content: string) => {
    if (!currentSession.value || currentSession.value.messages.length === 0) return

    const lastMessage = currentSession.value.messages[currentSession.value.messages.length - 1]
    if (lastMessage.type === 'bot') {
      lastMessage.content = content
    }
  }

  const loadSessions = async () => {
    try {
      console.log('正在加载用户会话...')
      const response = await fetch('/api/chat/sessions', {
        headers: {
          Authorization: `Bearer ${localStorage.getItem('token')}`,
        },
      })

      if (response.ok) {
        const data = await response.json()
        console.log('加载到的会话数据:', data)

        // 后端直接返回会话数组，不是包装在sessions字段中
        sessions.value = data.map((session: any) => ({
          ...session,
          createdAt: new Date(session.created_at),
          updatedAt: new Date(session.updated_at),
          messages: session.messages.map((msg: any) => {
            const mappedMsg = {
              ...msg,
              timestamp: new Date(msg.timestamp),
              // 字段名映射：后端使用下划线，前端使用驼峰
              imageUrl: msg.image_url,
              imageFile: undefined, // 历史记录中没有File对象
            }
            // 调试信息：检查图片URL映射
            if (msg.image_url) {
              console.log(`消息 ${msg.id} 的图片URL映射:`, {
                original: msg.image_url,
                mapped: mappedMsg.imageUrl,
              })
            }
            return mappedMsg
          }),
        }))

        console.log('处理后的会话数据:', sessions.value)
      } else {
        console.error('加载会话失败:', response.status, response.statusText)
      }
    } catch (error) {
      console.error('加载会话失败:', error)
    }
  }

  const saveSession = async (session: ChatSession) => {
    try {
      // TODO: 保存会话到后端
      await fetch('/api/chat/sessions', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${localStorage.getItem('token')}`,
        },
        body: JSON.stringify(session),
      })
    } catch (error) {
      console.error('保存会话失败:', error)
    }
  }

  const deleteSession = async (sessionId: string) => {
    try {
      // TODO: 从后端删除会话
      await fetch(`/api/chat/sessions/${sessionId}`, {
        method: 'DELETE',
        headers: {
          Authorization: `Bearer ${localStorage.getItem('token')}`,
        },
      })

      sessions.value = sessions.value.filter((s) => s.id !== sessionId)
      if (currentSession.value?.id === sessionId) {
        currentSession.value = null
      }
    } catch (error) {
      console.error('删除会话失败:', error)
    }
  }

  const clearAllData = () => {
    currentSession.value = null
    sessions.value = []
    isLoading.value = false
  }

  return {
    currentSession,
    sessions,
    isLoading,
    createNewSession,
    addMessage,
    addStreamingMessage,
    updateStreamingMessage,
    updateLastMessage,
    loadSessions,
    saveSession,
    deleteSession,
    clearAllData,
  }
})
