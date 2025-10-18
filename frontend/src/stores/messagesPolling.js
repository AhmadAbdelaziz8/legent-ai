import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { useSessionPollingStore } from './sessionPolling.js'

export const useMessagesPollingStore = defineStore('messagesPolling', () => {
  // State
  const loading = ref(false)
  const error = ref(null)

  // Get polling store
  const sessionPolling = useSessionPollingStore()

  // Computed - delegate to polling store
  const messages = computed(() => sessionPolling.messages)
  const currentSession = computed(() => sessionPolling.currentSession)
  const sessionStatus = computed(() => sessionPolling.sessionStatus)
  const isPolling = computed(() => sessionPolling.isPolling)
  const hasNewMessages = computed(() => sessionPolling.hasNewMessages)
  const isSessionActive = computed(() => sessionPolling.isSessionActive)

  // Getters
  const hasMessages = computed(() => messages.value.length > 0)
  const lastMessage = computed(() => messages.value[messages.value.length - 1])

  // Actions
  const startNewSession = async (initialPrompt, provider = 'bedrock', config = {}) => {
    loading.value = true
    error.value = null

    try {
      console.log('🚀 [MESSAGES] Starting new session with polling...')
      const session = await sessionPolling.startSession(initialPrompt, provider, config)
      console.log('✅ [MESSAGES] Session started:', session.id)
      return session
    } catch (err) {
      console.error('❌ [MESSAGES] Failed to start session:', err)
      error.value = err.message
      throw err
    } finally {
      loading.value = false
    }
  }

  const loadExistingSession = async (sessionId) => {
    loading.value = true
    error.value = null

    try {
      console.log('📂 [MESSAGES] Loading existing session:', sessionId)
      const session = await sessionPolling.loadExistingSession(sessionId)
      console.log('✅ [MESSAGES] Session loaded:', session.id)
      return session
    } catch (err) {
      console.error('❌ [MESSAGES] Failed to load session:', err)
      error.value = err.message
      throw err
    } finally {
      loading.value = false
    }
  }

  const refreshMessages = async () => {
    if (!currentSession.value) {
      console.warn('⚠️ [MESSAGES] No current session to refresh')
      return
    }

    try {
      console.log('🔄 [MESSAGES] Refreshing messages...')
      await sessionPolling.refreshSession(currentSession.value.id)
    } catch (err) {
      console.error('❌ [MESSAGES] Failed to refresh messages:', err)
      error.value = err.message
    }
  }

  const clearSession = () => {
    console.log('🧹 [MESSAGES] Clearing session and messages')
    sessionPolling.clearSession()
    error.value = null
  }

  const stopPolling = () => {
    console.log('🛑 [MESSAGES] Stopping polling')
    sessionPolling.stopPolling()
  }

  // Get messages by role
  const getMessagesByRole = (role) => {
    return messages.value.filter((msg) => msg.role === role)
  }

  // Get assistant messages
  const assistantMessages = computed(() => getMessagesByRole('assistant'))

  // Get user messages
  const userMessages = computed(() => getMessagesByRole('user'))

  // Get tool messages
  const toolMessages = computed(() => getMessagesByRole('tool'))

  // Check if session has screenshots
  const hasScreenshots = computed(() => {
    return messages.value.some((msg) => msg.base64_image)
  })

  // Get latest screenshot
  const latestScreenshot = computed(() => {
    const messagesWithImages = messages.value.filter((msg) => msg.base64_image)
    return messagesWithImages.length > 0 ? messagesWithImages[messagesWithImages.length - 1] : null
  })

  return {
    // State
    loading: computed(() => loading.value),
    error: computed(() => error.value),

    // Computed
    messages,
    currentSession,
    sessionStatus,
    isPolling,
    hasNewMessages,
    isSessionActive,
    hasMessages,
    lastMessage,
    assistantMessages,
    userMessages,
    toolMessages,
    hasScreenshots,
    latestScreenshot,

    // Actions
    startNewSession,
    loadExistingSession,
    refreshMessages,
    clearSession,
    stopPolling,
    getMessagesByRole,
  }
})
