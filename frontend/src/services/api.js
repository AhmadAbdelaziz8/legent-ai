// Use environment variable for API URL, fallback to localhost for development
const API_BASE_URL = 'http://localhost:8000'
async function apiRequest(endpoint, options = {}) {
  const url = `${API_BASE_URL}${endpoint}`

  // Debug logging
  console.log(`Making API request to: ${url}`)
  console.log(`API_BASE_URL: ${API_BASE_URL}`)

  const defaultOptions = {
    headers: {
      'Content-Type': 'application/json',
    },
  }

  const config = {
    ...defaultOptions,
    ...options,
    headers: {
      ...defaultOptions.headers,
      ...options.headers,
    },
  }

  try {
    const response = await fetch(url, config)

    console.log(`Response status: ${response.status}`)

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}))
      throw new Error(
        `API Error: ${response.status} ${response.statusText} - ${errorData.detail || 'Unknown error'}`,
      )
    }

    return await response.json()
  } catch (error) {
    console.error(`API Request failed for ${endpoint}:`, error)
    console.error(`Full URL: ${url}`)
    throw error
  }
}

export const healthApi = {
  async check() {
    return apiRequest('/')
  },
}

export const sessionsApi = {
  async create(sessionData) {
    return apiRequest('/sessions/', {
      method: 'POST',
      body: JSON.stringify(sessionData),
    })
  },

  async getAll(skip = 0, limit = 100) {
    return apiRequest(`/sessions/?skip=${skip}&limit=${limit}`)
  },

  async getById(sessionId) {
    return apiRequest(`/sessions/${sessionId}`)
  },

  streamUpdates(sessionId) {
    return new EventSource(`${API_BASE_URL}/sessions/${sessionId}/stream`)
  },
}

export const messagesApi = {
  async create(messageData) {
    return apiRequest('/messages/', {
      method: 'POST',
      body: JSON.stringify(messageData),
    })
  },

  async getBySessionId(sessionId) {
    return apiRequest(`/messages/session/${sessionId}`)
  },
}

export const api = {
  health: healthApi,
  sessions: sessionsApi,
  messages: messagesApi,
}

export const apiUtils = {
  async createSessionWithStream(initialPrompt, provider = 'bedrock') {
    try {
      const session = await sessionsApi.create({
        initial_prompt: initialPrompt,
        provider: provider,
      })

      const eventSource = sessionsApi.streamUpdates(session.id)

      return {
        session,
        eventSource,
      }
    } catch (error) {
      console.error('Failed to create session with stream:', error)
      throw error
    }
  },

  async waitForSessionCompletion(sessionId, maxWaitTime = 30000) {
    const startTime = Date.now()

    while (Date.now() - startTime < maxWaitTime) {
      try {
        const session = await sessionsApi.getById(sessionId)

        if (session.status === 'completed' || session.status === 'error') {
          const messages = await messagesApi.getBySessionId(sessionId)
          return {
            session,
            messages,
          }
        }

        await new Promise((resolve) => setTimeout(resolve, 1000))
      } catch (error) {
        console.error('Error waiting for session completion:', error)
        throw error
      }
    }

    throw new Error(`Session ${sessionId} did not complete within ${maxWaitTime}ms`)
  },

  async getSessionWithMessages(sessionId) {
    try {
      const [session, messages] = await Promise.all([
        sessionsApi.getById(sessionId),
        messagesApi.getBySessionId(sessionId),
      ])

      return {
        session,
        messages,
      }
    } catch (error) {
      console.error('Failed to get session with messages:', error)
      throw error
    }
  },
}

export default api
