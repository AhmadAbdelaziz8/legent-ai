import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { api } from '@/services/api.js'

export const useSessionsStore = defineStore('sessions', () => {
  // State
  const sessions = ref([])
  const currentSession = ref(null)
  const loading = ref(false)
  const error = ref(null)

  // Getters
  const sortedSessions = computed(() => {
    return [...sessions.value].sort((a, b) => new Date(b.created_at) - new Date(a.created_at))
  })

  const sessionCount = computed(() => sessions.value.length)

  // Actions
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
      return session
    } catch (err) {
      error.value = err.message
      throw err
    } finally {
      loading.value = false
    }
  }

  const createSession = async (initialPrompt, provider = 'bedrock') => {
    loading.value = true
    error.value = null

    try {
      const session = await api.sessions.create({
        initial_prompt: initialPrompt,
        provider: provider,
      })

      // Add to sessions list at the beginning
      sessions.value.unshift(session)
      currentSession.value = session

      return session
    } catch (err) {
      error.value = err.message
      throw err
    } finally {
      loading.value = false
    }
  }

  const setCurrentSession = (session) => {
    currentSession.value = session
  }

  const refreshSessions = async () => {
    return await fetchSessions()
  }

  const clearError = () => {
    error.value = null
  }

  return {
    // State
    sessions,
    currentSession,
    loading,
    error,

    // Getters
    sortedSessions,
    sessionCount,

    // Actions
    fetchSessions,
    fetchSession,
    createSession,
    setCurrentSession,
    refreshSessions,
    clearError,
  }
})
