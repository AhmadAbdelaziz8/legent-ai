import { ref, reactive, computed } from 'vue'
import { api, apiUtils } from '@/services/api.js'
export function useSessions() {
  const sessions = ref([])
  const currentSession = ref(null)
  const loading = ref(false)
  const error = ref(null)

  const createSession = async (initialPrompt, provider = 'bedrock') => {
    loading.value = true
    error.value = null

    try {
      const session = await api.sessions.create({
        initial_prompt: initialPrompt,
        provider: provider,
      })

      currentSession.value = session
      sessions.value.unshift(session) // Add to beginning of list

      return session
    } catch (err) {
      error.value = err.message
      throw err
    } finally {
      loading.value = false
    }
  }

  const fetchSessions = async (skip = 0, limit = 100) => {
    loading.value = true
    error.value = null

    try {
      const sessionList = await api.sessions.getAll(skip, limit)
      sessions.value = sessionList
      return sessionList
    } catch (err) {
      error.value = err.message
      throw err
    } finally {
      loading.value = false
    }
  }

  const fetchSession = async (sessionId) => {
    loading.value = true
    error.value = null

    try {
      const session = await api.sessions.getById(sessionId)
      currentSession.value = session
      return session
    } catch (err) {
      error.value = err.message
      throw err
    } finally {
      loading.value = false
    }
  }

  const createSessionWithStream = async (initialPrompt, provider = 'bedrock') => {
    loading.value = true
    error.value = null

    try {
      const result = await apiUtils.createSessionWithStream(initialPrompt, provider)
      currentSession.value = result.session
      sessions.value.unshift(result.session)

      return result
    } catch (err) {
      error.value = err.message
      throw err
    } finally {
      loading.value = false
    }
  }

  return {
    sessions: computed(() => sessions.value),
    currentSession: computed(() => currentSession.value),
    loading: computed(() => loading.value),
    error: computed(() => error.value),
    createSession,
    fetchSessions,
    fetchSession,
    createSessionWithStream,
  }
}

export function useMessages() {
  const messages = ref([])
  const loading = ref(false)
  const error = ref(null)

  const fetchMessages = async (sessionId) => {
    loading.value = true
    error.value = null

    try {
      const messageList = await api.messages.getBySessionId(sessionId)
      messages.value = messageList
      return messageList
    } catch (err) {
      error.value = err.message
      throw err
    } finally {
      loading.value = false
    }
  }

  const createMessage = async (messageData) => {
    loading.value = true
    error.value = null

    try {
      const message = await api.messages.create(messageData)
      messages.value.push(message)
      return message
    } catch (err) {
      error.value = err.message
      throw err
    } finally {
      loading.value = false
    }
  }

  const fetchSessionWithMessages = async (sessionId) => {
    loading.value = true
    error.value = null

    try {
      const result = await apiUtils.getSessionWithMessages(sessionId)
      messages.value = result.messages
      return result
    } catch (err) {
      error.value = err.message
      throw err
    } finally {
      loading.value = false
    }
  }

  const waitForCompletion = async (sessionId, maxWaitTime = 30000) => {
    loading.value = true
    error.value = null

    try {
      const result = await apiUtils.waitForSessionCompletion(sessionId, maxWaitTime)
      messages.value = result.messages
      return result
    } catch (err) {
      error.value = err.message
      throw err
    } finally {
      loading.value = false
    }
  }

  return {
    messages: computed(() => messages.value),
    loading: computed(() => loading.value),
    error: computed(() => error.value),
    fetchMessages,
    createMessage,
    fetchSessionWithMessages,
    waitForCompletion,
  }
}

export function useStreamingSession() {
  const session = ref(null)
  const messages = ref([])
  const eventSource = ref(null)
  const loading = ref(false)
  const error = ref(null)
  const isConnected = ref(false)

  const startStreaming = async (initialPrompt, provider = 'bedrock') => {
    loading.value = true
    error.value = null

    try {
      const result = await apiUtils.createSessionWithStream(initialPrompt, provider)
      session.value = result.session
      eventSource.value = result.eventSource

      // Set up event listeners
      setupEventListeners()

      return result
    } catch (err) {
      error.value = err.message
      throw err
    } finally {
      loading.value = false
    }
  }

  const setupEventListeners = () => {
    if (!eventSource.value) return

    eventSource.value.onopen = () => {
      isConnected.value = true
      console.log('Streaming connection opened')
    }

    eventSource.value.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data)
        console.log('Received streaming data:', data)

        if (data.type === 'assistant' || data.type === 'tool') {
          messages.value.push({
            id: Date.now(),
            session_id: session.value.id,
            role: data.type,
            content: data.content,
            created_at: new Date().toISOString(),
          })
        }
      } catch (err) {
        console.error('Error parsing streaming data:', err)
      }
    }

    eventSource.value.onerror = (event) => {
      console.error('Streaming connection error:', event)
      isConnected.value = false
      error.value = 'Streaming connection error'
    }
  }

  const stopStreaming = () => {
    if (eventSource.value) {
      eventSource.value.close()
      eventSource.value = null
      isConnected.value = false
    }
  }

  const cleanup = () => {
    stopStreaming()
    session.value = null
    messages.value = []
    loading.value = false
    error.value = null
  }

  return {
    session: computed(() => session.value),
    messages: computed(() => messages.value),
    eventSource: computed(() => eventSource.value),
    loading: computed(() => loading.value),
    error: computed(() => error.value),
    isConnected: computed(() => isConnected.value),
    startStreaming,
    stopStreaming,
    cleanup,
  }
}

export function useHealth() {
  const isHealthy = ref(false)
  const loading = ref(false)
  const error = ref(null)

  const checkHealth = async () => {
    loading.value = true
    error.value = null

    try {
      const result = await api.health.check()
      isHealthy.value = true
      return result
    } catch (err) {
      isHealthy.value = false
      error.value = err.message
      throw err
    } finally {
      loading.value = false
    }
  }

  return {
    isHealthy: computed(() => isHealthy.value),
    loading: computed(() => loading.value),
    error: computed(() => error.value),
    checkHealth,
  }
}
