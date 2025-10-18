import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { api } from '../services/api.js'

export const useSessionPollingStore = defineStore('sessionPolling', () => {
  // State
  const currentSession = ref(null)
  const messages = ref([])
  const sessionStatus = ref(null)
  const isPolling = ref(false)
  const pollingInterval = ref(null)
  const lastMessageCount = ref(0)
  const lastStatusUpdate = ref(null)

  // Computed
  const hasNewMessages = computed(() => {
    return messages.value.length > lastMessageCount.value
  })

  const isSessionActive = computed(() => {
    return sessionStatus.value?.status === 'running' || sessionStatus.value?.status === 'processing'
  })

  // Actions
  const startSession = async (initialPrompt, provider = 'bedrock', config = {}) => {
    try {
      console.log('🚀 [POLLING] Starting new session...')
      const result = await api.sessions.create({
        initial_prompt: initialPrompt,
        provider: provider,
        model: config.model,
        system_prompt_suffix: config.system_prompt_suffix,
        max_tokens: config.max_tokens,
        thinking_budget: config.thinking_budget,
        only_n_most_recent_images: config.only_n_most_recent_images,
        tool_version: config.tool_version,
      })

      currentSession.value = result
      messages.value = []
      sessionStatus.value = null
      lastMessageCount.value = 0

      console.log('✅ [POLLING] Session created:', result.id)

      // Start polling immediately
      startPolling(result.id)

      return result
    } catch (error) {
      console.error('❌ [POLLING] Failed to start session:', error)
      throw error
    }
  }

  const startPolling = (sessionId) => {
    if (isPolling.value) {
      console.log('⚠️ [POLLING] Already polling, stopping previous poll')
      stopPolling()
    }

    console.log('🔄 [POLLING] Starting polling for session:', sessionId)
    isPolling.value = true

    // Poll immediately
    pollSession(sessionId)

    // Set up interval polling (every 1 second)
    pollingInterval.value = setInterval(() => {
      pollSession(sessionId)
    }, 1000)
  }

  const pollSession = async (sessionId) => {
    try {
      // Poll for messages and status in parallel
      const [messagesResponse, statusResponse] = await Promise.all([
        api.sessions.getMessages(sessionId),
        api.sessions.getStatus(sessionId),
      ])

      // Update messages if there are new ones
      if (messagesResponse.length > lastMessageCount.value) {
        console.log(
          `📨 [POLLING] Found ${messagesResponse.length - lastMessageCount.value} new messages`,
        )
        messages.value = messagesResponse
        lastMessageCount.value = messagesResponse.length
      }

      // Update status
      sessionStatus.value = statusResponse

      // Check if session is completed
      if (statusResponse.status === 'completed' || statusResponse.status === 'error') {
        console.log('🏁 [POLLING] Session completed, stopping polling')
        stopPolling()
      }
    } catch (error) {
      console.error('❌ [POLLING] Error polling session:', error)
      // Don't stop polling on error, just log it
    }
  }

  const stopPolling = () => {
    if (pollingInterval.value) {
      clearInterval(pollingInterval.value)
      pollingInterval.value = null
    }
    isPolling.value = false
    console.log('🛑 [POLLING] Stopped polling')
  }

  const refreshSession = async (sessionId) => {
    try {
      console.log('🔄 [POLLING] Manual refresh for session:', sessionId)
      await pollSession(sessionId)
    } catch (error) {
      console.error('❌ [POLLING] Error refreshing session:', error)
      throw error
    }
  }

  const loadExistingSession = async (sessionId) => {
    try {
      console.log('📂 [POLLING] Loading existing session:', sessionId)

      const [session, sessionMessages, status] = await Promise.all([
        api.sessions.getById(sessionId),
        api.sessions.getMessages(sessionId),
        api.sessions.getStatus(sessionId),
      ])

      currentSession.value = session
      messages.value = sessionMessages
      sessionStatus.value = status
      lastMessageCount.value = sessionMessages.length

      // Start polling if session is still active
      if (status.status === 'running' || status.status === 'processing') {
        startPolling(sessionId)
      }

      return session
    } catch (error) {
      console.error('❌ [POLLING] Error loading existing session:', error)
      throw error
    }
  }

  const clearSession = () => {
    stopPolling()
    currentSession.value = null
    messages.value = []
    sessionStatus.value = null
    lastMessageCount.value = 0
    lastStatusUpdate.value = null
    console.log('🧹 [POLLING] Cleared session state')
  }

  // Cleanup on store destruction
  const cleanup = () => {
    stopPolling()
  }

  return {
    // State
    currentSession: computed(() => currentSession.value),
    messages: computed(() => messages.value),
    sessionStatus: computed(() => sessionStatus.value),
    isPolling: computed(() => isPolling.value),

    // Computed
    hasNewMessages,
    isSessionActive,

    // Actions
    startSession,
    startPolling,
    stopPolling,
    refreshSession,
    loadExistingSession,
    clearSession,
    cleanup,
  }
})
