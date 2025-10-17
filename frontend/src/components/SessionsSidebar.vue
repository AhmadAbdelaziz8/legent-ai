<template>
  <div class="w-80 bg-white border-r border-gray-200 flex flex-col h-full">
    <!-- Header -->
    <div class="p-4 border-b border-gray-200 bg-gray-50">
      <h2 class="text-lg font-semibold text-gray-900">Sessions</h2>
      <p class="text-sm text-gray-500 mt-1">{{ sessionCount }} sessions</p>
    </div>

    <!-- New Session Button -->
    <div class="p-4 border-b border-gray-200">
      <button
        @click="handleNewSession"
        :disabled="loading"
        class="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white font-medium py-2 px-4 rounded-lg transition-colors duration-200 flex items-center justify-center gap-2"
      >
        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="2"
            d="M12 4v16m8-8H4"
          ></path>
        </svg>
        New Session
      </button>
    </div>

    <!-- Sessions List -->
    <div class="flex-1 overflow-y-auto">
      <!-- Loading State -->
      <div v-if="loading && sessions.length === 0" class="p-4 space-y-3">
        <div v-for="i in 3" :key="i" class="animate-pulse">
          <div class="h-16 bg-gray-200 rounded-lg"></div>
        </div>
      </div>

      <!-- Empty State -->
      <div v-else-if="!loading && sessions.length === 0" class="p-4 text-center">
        <div class="text-gray-400 mb-2">
          <svg class="w-12 h-12 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
            ></path>
          </svg>
        </div>
        <p class="text-gray-500 text-sm">No sessions yet</p>
        <p class="text-gray-400 text-xs mt-1">Create your first session to get started</p>
      </div>

      <!-- Sessions List -->
      <div v-else class="p-2">
        <div
          v-for="session in sortedSessions"
          :key="session.id"
          @click="selectSession(session)"
          :class="[
            'p-3 rounded-lg cursor-pointer transition-all duration-200 mb-2',
            currentSession?.id === session.id
              ? 'bg-blue-50 border border-blue-200'
              : 'hover:bg-gray-50 border border-transparent',
          ]"
        >
          <!-- Session Header -->
          <div class="flex items-start justify-between mb-2">
            <div class="flex-1 min-w-0">
              <p class="text-sm font-medium text-gray-900 truncate">
                {{ truncateText(session.initial_prompt, 50) }}
              </p>
              <p class="text-xs text-gray-500 mt-1">
                {{ formatRelativeTime(session.created_at) }}
              </p>
            </div>
            <StatusBadge :status="session.status" />
          </div>

          <!-- Session Footer -->
          <div class="flex items-center justify-between text-xs text-gray-500">
            <span>ID: {{ session.id }}</span>
            <span v-if="session.message_count !== undefined">
              {{ session.message_count }} messages
            </span>
          </div>
        </div>
      </div>
    </div>

    <!-- Error State -->
    <div v-if="error" class="p-4 bg-red-50 border-t border-red-200">
      <div class="flex items-center gap-2 text-red-600 text-sm">
        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="2"
            d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
          ></path>
        </svg>
        {{ error }}
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted, computed } from 'vue'
import { useSessionsStore } from '@/stores/sessions.js'
import StatusBadge from './StatusBadge.vue'

const sessionsStore = useSessionsStore()

// Computed properties
const sessions = computed(() => sessionsStore.sessions)
const currentSession = computed(() => sessionsStore.currentSession)
const loading = computed(() => sessionsStore.loading)
const error = computed(() => sessionsStore.error)
const sessionCount = computed(() => sessionsStore.sessionCount)
const sortedSessions = computed(() => sessionsStore.sortedSessions)

// Methods
const selectSession = (session) => {
  sessionsStore.setCurrentSession(session)
}

const handleNewSession = () => {
  // For now, just show an alert. In a real app, this would open a modal or navigate to a form
  const prompt = prompt('Enter initial prompt for new session:')
  if (prompt) {
    sessionsStore.createSession(prompt)
  }
}

const truncateText = (text, maxLength) => {
  if (!text) return 'No prompt'
  return text.length > maxLength ? text.substring(0, maxLength) + '...' : text
}

const formatRelativeTime = (dateString) => {
  const date = new Date(dateString)
  const now = new Date()
  const diffInSeconds = Math.floor((now - date) / 1000)

  if (diffInSeconds < 60) return 'Just now'
  if (diffInSeconds < 3600) return `${Math.floor(diffInSeconds / 60)}m ago`
  if (diffInSeconds < 86400) return `${Math.floor(diffInSeconds / 3600)}h ago`
  return `${Math.floor(diffInSeconds / 86400)}d ago`
}

// Lifecycle
onMounted(async () => {
  try {
    await sessionsStore.fetchSessions()
  } catch (err) {
    console.error('Failed to fetch sessions:', err)
  }
})
</script>
