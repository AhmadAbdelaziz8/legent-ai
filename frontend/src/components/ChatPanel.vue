<template>
  <div class="w-80 bg-white border-l border-gray-200 flex flex-col h-full">
    <!-- Header -->
    <div class="p-4 border-b border-gray-200 bg-gray-50">
      <h2 class="text-lg font-semibold text-gray-900">Chat</h2>
      <p class="text-sm text-gray-500 mt-1">
        {{ currentSession ? `Session #${currentSession.id}` : 'No session selected' }}
      </p>
    </div>

    <!-- Content -->
    <div class="flex-1 p-4">
      <!-- No session selected -->
      <div
        v-if="!currentSession"
        class="flex flex-col items-center justify-center h-full text-center"
      >
        <div class="text-gray-400 mb-4">
          <svg class="w-16 h-16 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"
            ></path>
          </svg>
        </div>
        <h3 class="text-lg font-medium text-gray-900 mb-2">No Session Selected</h3>
        <p class="text-gray-500 text-sm">
          Select a session from the sidebar to view its chat history
        </p>
      </div>

      <!-- Session selected but no messages -->
      <div
        v-else-if="currentSession && messages.length === 0"
        class="flex flex-col items-center justify-center h-full text-center"
      >
        <div class="text-gray-400 mb-4">
          <svg class="w-16 h-16 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"
            ></path>
          </svg>
        </div>
        <h3 class="text-lg font-medium text-gray-900 mb-2">No Messages Yet</h3>
        <p class="text-gray-500 text-sm">This session doesn't have any messages yet</p>
      </div>

      <!-- Messages list -->
      <div v-else class="space-y-4">
        <div
          v-for="message in messages"
          :key="message.id"
          :class="[
            'p-3 rounded-lg',
            message.role === 'user' ? 'bg-blue-50 ml-8' : 'bg-gray-50 mr-8',
          ]"
        >
          <div class="flex items-start space-x-2">
            <div class="flex-shrink-0">
              <div
                :class="[
                  'w-6 h-6 rounded-full flex items-center justify-center text-xs font-medium',
                  message.role === 'user' ? 'bg-blue-500 text-white' : 'bg-gray-500 text-white',
                ]"
              >
                {{ message.role === 'user' ? 'U' : 'A' }}
              </div>
            </div>
            <div class="flex-1 min-w-0">
              <p class="text-sm text-gray-900">{{ message.content }}</p>
              <p class="text-xs text-gray-500 mt-1">
                {{ formatTime(message.created_at) }}
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Footer -->
    <div v-if="currentSession" class="p-4 border-t border-gray-200 bg-gray-50">
      <div class="text-xs text-gray-500 text-center">
        Session status:
        <span :class="getStatusColor(currentSession.status)">
          {{ currentSession.status }}
        </span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useSessionsStore } from '@/stores/sessions.js'

const sessionsStore = useSessionsStore()

// For now, we'll use mock data since we don't have message fetching implemented yet
const messages = computed(() => {
  // This would be fetched from the messages store/API in a real implementation
  return []
})

const currentSession = computed(() => sessionsStore.currentSession)

const formatTime = (dateString) => {
  const date = new Date(dateString)
  return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
}

const getStatusColor = (status) => {
  switch (status) {
    case 'completed':
      return 'text-green-600'
    case 'error':
      return 'text-red-600'
    case 'processing':
      return 'text-yellow-600'
    case 'pending':
      return 'text-gray-600'
    default:
      return 'text-gray-600'
  }
}
</script>
