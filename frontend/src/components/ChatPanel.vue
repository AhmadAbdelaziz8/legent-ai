<template>
  <div
    class="w-56 bg-gradient-to-b from-slate-50 to-white dark:from-slate-800 dark:to-slate-900 border-l border-slate-200 dark:border-slate-700 flex flex-col h-full shadow-lg"
  >
    <!-- Header -->
    <div
      class="p-3 border-b border-slate-200 dark:border-slate-700 bg-gradient-to-r from-slate-50 to-slate-100 dark:from-slate-800 dark:to-slate-900"
    >
      <div class="flex items-center justify-between">
        <div>
          <div class="flex items-center space-x-2">
            <div
              class="w-8 h-8 bg-gradient-to-br from-green-500 to-green-600 rounded-lg flex items-center justify-center"
            >
              <svg class="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2-2v10a2 2 0 002 2z"
                ></path>
              </svg>
            </div>
            <div>
              <h2 class="text-lg font-bold text-slate-900 dark:text-slate-100">AI Assistant</h2>
              <p class="text-xs text-slate-500 dark:text-slate-400 mt-1">Always here to help</p>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Content -->
    <div class="flex-1 p-3 flex flex-col">
      <!-- Messages area -->
      <div class="flex-1 overflow-y-auto">
        <!-- No session selected -->
        <div
          v-if="!currentSession"
          class="flex flex-col items-center justify-center h-full text-center gap-6"
        >
          <!-- AI Assistant Welcome Message -->
          <div class="mb-4">
            <div
              class="bg-gradient-to-r from-green-50 to-green-100 dark:from-green-900/20 dark:to-green-800/20 rounded-lg p-3 border border-green-200 dark:border-green-700"
            >
              <p class="text-sm text-slate-900 dark:text-slate-100">
                Hi! Let me know what task to accomplish
              </p>
            </div>
          </div>
          <div class="relative">
            <div
              class="w-20 h-20 bg-gradient-to-br from-slate-200 to-slate-300 dark:from-slate-700 dark:to-slate-600 rounded-full flex items-center justify-center"
            >
              <svg
                class="w-10 h-10 text-slate-500 dark:text-slate-400"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"
                ></path>
              </svg>
            </div>
          </div>
          <div class="flex flex-col items-center gap-3">
            <h3 class="text-xl font-semibold text-slate-900 dark:text-slate-100">
              No Session Selected
            </h3>
            <p class="text-slate-500 dark:text-slate-400 text-sm max-w-xs">
              Select a session from the sidebar to view its chat history
            </p>
          </div>
        </div>

        <!-- Session selected but no messages -->
        <div
          v-else-if="currentSession && messages.length === 0"
          class="flex flex-col items-center justify-center h-full text-center gap-6"
        >
          <div class="relative">
            <div
              class="w-20 h-20 bg-gradient-to-br from-blue-200 to-purple-200 dark:from-blue-800 dark:to-purple-800 rounded-full flex items-center justify-center"
            >
              <svg
                class="w-10 h-10 text-blue-500 dark:text-blue-400"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"
                ></path>
              </svg>
            </div>
          </div>
          <div class="flex flex-col items-center gap-3">
            <h3 class="text-xl font-semibold text-slate-900 dark:text-slate-100">
              No Messages Yet
            </h3>
            <p class="text-slate-500 dark:text-slate-400 text-sm">
              This session doesn't have any messages yet
            </p>
          </div>
        </div>

        <!-- Messages list -->
        <div v-else class="space-y-4">
          <div
            v-for="message in messages"
            :key="message.id"
            :class="[
              'p-4 rounded-xl shadow-sm border-2 transition-all duration-300',
              message.role === 'user'
                ? 'bg-gradient-to-r from-blue-50 to-blue-100 dark:from-blue-900/20 dark:to-blue-800/20 border-blue-200 dark:border-blue-700 ml-8'
                : 'bg-gradient-to-r from-slate-50 to-slate-100 dark:from-slate-700 dark:to-slate-600 border-slate-200 dark:border-slate-600 mr-8',
            ]"
          >
            <div class="flex items-start gap-3">
              <div class="flex-shrink-0">
                <div
                  :class="[
                    'w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold shadow-lg',
                    message.role === 'user'
                      ? 'bg-gradient-to-br from-blue-500 to-blue-600 text-white'
                      : 'bg-gradient-to-br from-slate-500 to-slate-600 text-white',
                  ]"
                >
                  {{ message.role === 'user' ? 'U' : 'AI' }}
                </div>
              </div>
              <div class="flex-1 min-w-0">
                <p class="text-sm text-slate-900 dark:text-slate-100 leading-relaxed">
                  {{ message.content }}
                </p>
                <p class="text-xs text-slate-500 dark:text-slate-400 mt-2 flex items-center gap-1">
                  <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path
                      stroke-linecap="round"
                      stroke-linejoin="round"
                      stroke-width="2"
                      d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"
                    ></path>
                  </svg>
                  {{ formatTime(message.created_at) }}
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- File Upload Zone -->
      <div
        class="p-3 border-t border-slate-200 dark:border-slate-700 bg-gradient-to-r from-slate-50 to-slate-100 dark:from-slate-800 dark:to-slate-900"
      >
        <div
          class="relative border-2 border-dashed border-slate-300 dark:border-slate-600 rounded-lg p-4 text-center hover:border-green-400 dark:hover:border-green-500 transition-colors cursor-pointer group"
        >
          <div class="flex flex-col items-center space-y-2">
            <div
              class="w-8 h-8 bg-gradient-to-br from-green-500 to-green-600 rounded-lg flex items-center justify-center group-hover:scale-110 transition-transform"
            >
              <svg class="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"
                ></path>
              </svg>
            </div>
            <p class="text-xs text-slate-600 dark:text-slate-400">
              Drag and drop a single file here or click to select a file
            </p>
            <button
              class="px-3 py-1 bg-slate-200 dark:bg-slate-600 text-slate-700 dark:text-slate-300 rounded text-xs font-medium hover:bg-slate-300 dark:hover:bg-slate-500 transition-colors"
            >
              Select File
            </button>
          </div>
          <button
            class="absolute top-2 right-2 w-4 h-4 text-slate-400 hover:text-slate-600 dark:hover:text-slate-300"
          >
            <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M6 18L18 6M6 6l12 12"
              ></path>
            </svg>
          </button>
        </div>
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
