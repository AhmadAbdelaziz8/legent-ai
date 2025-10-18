import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { api } from '@/services/api.js'
import { useSessionsStore } from './sessions.js'

export const useMessagesStore = defineStore('messages', () => {
  // State
  const messages = ref([])
  const loading = ref(false)
  const error = ref(null)
  const isStreaming = ref(false)
  const eventSource = ref(null)
  const streamingMessage = ref(null)

  // Getters
  const hasMessages = computed(() => messages.value.length > 0)
  const lastMessage = computed(() => messages.value[messages.value.length - 1])

  // Actions
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

  const sendMessage = async (content, sessionId) => {
    loading.value = true
    error.value = null

    try {
      const messageData = {
        session_id: sessionId,
        role: 'user',
        content: { text: content },
      }

      const newMessage = await api.messages.create(messageData)
      messages.value.push(newMessage)
      return newMessage
    } catch (err) {
      error.value = err.message
      throw err
    } finally {
      loading.value = false
    }
  }

  const createSessionAndSendMessage = async (content) => {
    const sessionsStore = useSessionsStore()

    try {
      // Create new session with the message as initial prompt
      const session = await sessionsStore.createSession(content, 'bedrock')

      // Add user message to local messages
      const userMessage = {
        id: Date.now(),
        session_id: session.id,
        role: 'user',
        content: { text: content },
        created_at: new Date().toISOString(),
      }
      messages.value.push(userMessage)

      // Start streaming
      await startStreaming(session.id)

      return session
    } catch (err) {
      error.value = err.message
      throw err
    }
  }

  const startStreaming = async (sessionId) => {
    // Prevent multiple calls to startStreaming
    if (isStreaming.value) {
      return
    }

    if (eventSource.value) {
      eventSource.value.close()
    }

    isStreaming.value = true
    streamingMessage.value = {
      id: Date.now(),
      session_id: sessionId,
      role: 'assistant',
      content: { text: '' },
      created_at: new Date().toISOString(),
      isStreaming: true,
    }

    // Streaming message will be added to display when content is received

    // Add a small delay to ensure backend stream is ready
    await new Promise((resolve) => setTimeout(resolve, 1000))

    // Create the EventSource
    eventSource.value = api.sessions.streamUpdates(sessionId)

    // Set up event handlers for the stream
    if (eventSource.value) {
      eventSource.value.onopen = () => {
        console.log('✅ [FRONTEND] Streaming connection opened for session:', sessionId)
      }

      eventSource.value.onmessage = (event) => {
        try {
          // Handle ping messages (keep-alive)
          if (event.data === 'ping' || event.data.includes('ping')) {
            return
          }

          console.log('📨 [FRONTEND] Received streaming data:', event.data)
          const data = JSON.parse(event.data)

          if (data.type === 'assistant' || data.type === 'tool') {
            // Update the streaming message content
            if (streamingMessage.value) {
              // Add streaming message to display on first content
              if (!messages.value.includes(streamingMessage.value)) {
                messages.value.push(streamingMessage.value)
                console.log('📝 [FRONTEND] Added streaming message to display')
              }
              
              // Handle the nested content structure from backend
              if (data.content && data.content.content && Array.isArray(data.content.content)) {
                // Extract text from the content array
                const textContent = data.content.content
                  .filter((item) => item.type === 'text')
                  .map((item) => item.text)
                  .join('')
                console.log('📝 [FRONTEND] Adding text content:', textContent)
                streamingMessage.value.content.text += textContent
              } else if (data.content && data.content.text) {
                console.log('📝 [FRONTEND] Adding text content (direct):', data.content.text)
                streamingMessage.value.content.text += data.content.text
              } else if (typeof data.content === 'string') {
                console.log('📝 [FRONTEND] Adding text content (string):', data.content)
                streamingMessage.value.content.text += data.content
              }
            }
          } else if (data.type === 'error') {
            console.error('Stream error:', data.message)
            stopStreaming()
          }
        } catch (err) {
          console.error('Error parsing streaming data:', err, 'Raw data:', event.data)
        }
      }

      eventSource.value.onerror = (event) => {
        console.error('Streaming connection error:', event)
        isStreaming.value = false
        if (streamingMessage.value) {
          streamingMessage.value.isStreaming = false
        }
        error.value = 'Streaming connection error'

        // Try to reconnect after a short delay
        setTimeout(() => {
          if (isStreaming.value) {
            startStreaming(sessionId)
          }
        }, 2000)
      }

      // Auto-close stream after 60 seconds to prevent hanging
      setTimeout(() => {
        if (isStreaming.value) {
          stopStreaming()
        }
      }, 60000)
    } else {
      console.error('Failed to create EventSource')
    }
  }

  const stopStreaming = () => {
    if (eventSource.value) {
      eventSource.value.close()
      eventSource.value = null
    }
    isStreaming.value = false
    if (streamingMessage.value) {
      streamingMessage.value.isStreaming = false
      console.log('📝 [FRONTEND] Streaming completed')
    }
    streamingMessage.value = null
  }

  const clearMessages = () => {
    messages.value = []
    stopStreaming()
    error.value = null
  }

  const clearError = () => {
    error.value = null
  }

  return {
    // State
    messages,
    loading,
    error,
    isStreaming,
    streamingMessage,

    // Getters
    hasMessages,
    lastMessage,

    // Actions
    fetchMessages,
    sendMessage,
    createSessionAndSendMessage,
    startStreaming,
    stopStreaming,
    clearMessages,
    clearError,
  }
})
