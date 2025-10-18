<template>
  <div class="session-manager p-6 max-w-4xl mx-auto">
    <h1 class="text-3xl font-bold mb-6">Legent AI Session Manager</h1>

    <!-- Health Status -->
    <div class="mb-6">
      <div class="flex items-center gap-2">
        <div :class="['w-3 h-3 rounded-full', isHealthy ? 'bg-green-500' : 'bg-red-500']"></div>
        <span class="text-sm"> API Status: {{ isHealthy ? 'Connected' : 'Disconnected' }} </span>
        <button
          @click="checkHealth"
          :disabled="healthLoading"
          class="ml-2 px-3 py-1 text-xs bg-blue-500 text-white rounded hover:bg-blue-600 disabled:opacity-50"
        >
          {{ healthLoading ? 'Checking...' : 'Refresh' }}
        </button>
      </div>
    </div>

    <!-- Create New Session -->
    <div class="mb-8 p-4 border rounded-lg">
      <h2 class="text-xl font-semibold mb-4">Create New Session</h2>
      <form @submit.prevent="createNewSession" class="flex flex-col gap-4">
        <div>
          <label for="prompt" class="block text-sm font-medium mb-2"> Initial Prompt </label>
          <textarea
            id="prompt"
            v-model="newSessionPrompt"
            rows="3"
            class="w-full p-3 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            placeholder="Enter your initial prompt here..."
            required
          ></textarea>
        </div>

        <div>
          <label for="provider" class="block text-sm font-medium mb-2"> Provider </label>
          <select
            id="provider"
            v-model="selectedProvider"
            class="w-full p-3 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          >
            <option value="bedrock">AWS Bedrock</option>
            <option value="anthropic">Anthropic</option>
            <option value="vertex">Vertex AI</option>
          </select>
        </div>

        <button
          type="submit"
          :disabled="sessionLoading"
          class="w-full px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {{ sessionLoading ? 'Creating Session...' : 'Create Session' }}
        </button>
      </form>
    </div>

    <!-- Current Session -->
    <div v-if="currentSession" class="mb-8 p-4 border rounded-lg">
      <h2 class="text-xl font-semibold mb-4">Current Session</h2>
      <div class="flex flex-col gap-2">
        <p><strong>ID:</strong> {{ currentSession.id }}</p>
        <p>
          <strong>Status:</strong>
          <span :class="getStatusClass(currentSession.status)">
            {{ currentSession.status }}
          </span>
        </p>
        <p><strong>Provider:</strong> {{ currentSession.provider }}</p>
        <p><strong>Created:</strong> {{ formatDate(currentSession.created_at) }}</p>
        <p><strong>Initial Prompt:</strong> {{ currentSession.initial_prompt }}</p>
      </div>

      <!-- Session Actions -->
      <div class="mt-4 flex gap-2">
        <button
          @click="fetchSessionMessages"
          :disabled="messageLoading"
          class="px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700 disabled:opacity-50"
        >
          {{ messageLoading ? 'Loading...' : 'Load Messages' }}
        </button>

        <button
          @click="startStreaming"
          :disabled="streamingLoading"
          class="px-4 py-2 bg-purple-600 text-white rounded hover:bg-purple-700 disabled:opacity-50"
        >
          {{ streamingLoading ? 'Starting...' : 'Start Streaming' }}
        </button>
      </div>
    </div>

    <!-- Messages -->
    <div v-if="messages.length > 0" class="mb-8">
      <h2 class="text-xl font-semibold mb-4">Messages</h2>
      <div class="flex flex-col gap-4">
        <div
          v-for="message in messages"
          :key="message.id"
          class="p-4 border rounded-lg"
          :class="getMessageClass(message.role)"
        >
          <div class="flex justify-between items-start mb-2">
            <span class="font-medium">{{ message.role }}</span>
            <span class="text-sm text-gray-500">{{ formatDate(message.created_at) }}</span>
          </div>
          <div class="prose max-w-none">
            <pre class="whitespace-pre-wrap">{{ formatMessageContent(message.content) }}</pre>
          </div>
        </div>
      </div>
    </div>

    <!-- Sessions List -->
    <div v-if="sessions.length > 0" class="mb-8">
      <h2 class="text-xl font-semibold mb-4">All Sessions</h2>
      <div class="flex flex-col gap-2">
        <div
          v-for="session in sessions"
          :key="session.id"
          class="p-3 border rounded-lg cursor-pointer hover:bg-gray-50"
          @click="selectSession(session.id)"
        >
          <div class="flex justify-between items-center">
            <div>
              <p class="font-medium">Session #{{ session.id }}</p>
              <p class="text-sm text-gray-600">{{ session.initial_prompt.substring(0, 100) }}...</p>
            </div>
            <div class="text-right">
              <span :class="getStatusClass(session.status)" class="text-sm">
                {{ session.status }}
              </span>
              <p class="text-xs text-gray-500">{{ formatDate(session.created_at) }}</p>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Error Display -->
    <div v-if="error" class="p-4 bg-red-50 border border-red-200 rounded-lg">
      <h3 class="text-red-800 font-medium">Error</h3>
      <p class="text-red-600">{{ error }}</p>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useSessions, useMessages, useStreamingSession, useHealth } from '@/composables/useApi.js'

// Composables
const {
  sessions,
  currentSession,
  loading: sessionLoading,
  error: sessionError,
  createSession,
  fetchSessions,
} = useSessions()

const { messages, loading: messageLoading, error: messageError, fetchMessages } = useMessages()

const {
  loading: streamingLoading,
  error: streamingError,
  startStreaming: startStreamingSession,
} = useStreamingSession()

const { isHealthy, loading: healthLoading, error: healthError, checkHealth } = useHealth()

// Local state
const newSessionPrompt = ref('')
const selectedProvider = ref('bedrock')
const error = ref('')

// Computed
const allErrors = computed(() => {
  return [sessionError.value, messageError.value, streamingError.value, healthError.value]
    .filter(Boolean)
    .join('; ')
})

// Methods
const createNewSession = async () => {
  try {
    error.value = ''
    await createSession(newSessionPrompt.value, selectedProvider.value)
    newSessionPrompt.value = ''
  } catch (err) {
    error.value = err.message
  }
}

const fetchSessionMessages = async () => {
  if (!currentSession.value) return

  try {
    error.value = ''
    await fetchMessages(currentSession.value.id)
  } catch (err) {
    error.value = err.message
  }
}

const startStreaming = async () => {
  if (!currentSession.value) return

  try {
    error.value = ''
    await startStreamingSession(currentSession.value.initial_prompt, currentSession.value.provider)
  } catch (err) {
    error.value = err.message
  }
}

const selectSession = async (sessionId) => {
  try {
    error.value = ''
    await fetchSession(sessionId)
  } catch (err) {
    error.value = err.message
  }
}

const getStatusClass = (status) => {
  const classes = {
    queued: 'text-yellow-600 bg-yellow-100',
    running: 'text-blue-600 bg-blue-100',
    completed: 'text-green-600 bg-green-100',
    error: 'text-red-600 bg-red-100',
  }
  return classes[status] || 'text-gray-600 bg-gray-100'
}

const getMessageClass = (role) => {
  const classes = {
    user: 'bg-blue-50 border-blue-200',
    assistant: 'bg-green-50 border-green-200',
    tool: 'bg-purple-50 border-purple-200',
  }
  return classes[role] || 'bg-gray-50 border-gray-200'
}

const formatMessageContent = (content) => {
  if (typeof content === 'string') return content
  if (content && content.content) {
    return content.content.map((block) => block.text || JSON.stringify(block)).join('\n')
  }
  return JSON.stringify(content, null, 2)
}

const formatDate = (dateString) => {
  return new Date(dateString).toLocaleString()
}

// Lifecycle
onMounted(async () => {
  try {
    await checkHealth()
    await fetchSessions()
  } catch (err) {
    error.value = err.message
  }
})
</script>

<style scoped>
.session-manager {
  font-family:
    system-ui,
    -apple-system,
    sans-serif;
}
</style>
