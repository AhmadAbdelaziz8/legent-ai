<template>
  <div
    class="w-56 bg-white dark:bg-slate-800 border-r border-slate-200 dark:border-slate-700 flex flex-col h-full shadow-lg"
  >
    <!-- Header with Logo -->
    <div class="p-4 border-b border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800">
      <div class="flex items-center gap-3 mb-4">
        <div class="w-8 h-8 bg-slate-600 rounded-lg flex items-center justify-center">
          <svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M13 10V3L4 14h7v7l9-11h-7z"
            ></path>
          </svg>
        </div>
        <div>
          <h1 class="text-lg font-bold text-slate-900 dark:text-slate-100">Legent AI</h1>
          <p class="text-xs text-slate-500 dark:text-slate-400">AI Assistant Platform</p>
        </div>
      </div>

      <!-- Search Bar -->
      <div class="relative">
        <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
          <svg class="h-4 w-4 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
            ></path>
          </svg>
        </div>
        <input
          type="text"
          placeholder="Q Search"
          class="w-full pl-10 pr-3 py-2 border border-slate-300 dark:border-slate-600 rounded-lg bg-white dark:bg-slate-700 text-slate-900 dark:text-slate-100 placeholder-slate-500 dark:placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent"
        />
      </div>
    </div>

    <!-- Task History Section -->
    <div class="flex-1 overflow-y-auto">
      <div class="p-3">
        <!-- Library Section -->
        <div class="mb-4">
          <button
            @click="toggleLibrary"
            class="flex items-center justify-between w-full text-left text-sm font-medium text-slate-700 dark:text-slate-300 hover:text-slate-900 dark:hover:text-slate-100"
          >
            <div class="flex items-center gap-2">
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10"
                ></path>
              </svg>
              <span>Sessions</span>
            </div>
            <svg
              :class="[
                'w-4 h-4 transition-transform duration-200',
                libraryExpanded ? 'rotate-180' : '',
              ]"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M19 9l-7 7-7-7"
              ></path>
            </svg>
          </button>

          <!-- Library Items -->
          <div v-if="libraryExpanded" class="mt-2 flex flex-col gap-2">
            <div
              v-for="session in sortedSessions"
              :key="session.id"
              @click="selectSession(session)"
              :class="[
                'group p-2 rounded-lg cursor-pointer transition-all duration-300 border',
                currentSession?.id === session.id
                  ? 'bg-green-50 dark:bg-green-900/20 border-green-300 dark:border-green-600'
                  : 'hover:bg-slate-50 dark:hover:bg-slate-700 border-slate-200 dark:border-slate-600 hover:border-slate-300 dark:hover:border-slate-500',
              ]"
            >
              <p class="text-xs font-medium text-slate-900 dark:text-slate-100 truncate">
                {{ truncateText(session.initial_prompt, 30) }}
              </p>
              <p class="text-xs text-slate-500 dark:text-slate-400 mt-1">
                {{ formatRelativeTime(session.created_at) }}
              </p>
            </div>
          </div>
        </div>

        <!-- Prompt Gallery Section -->
        <div
          class="flex items-center gap-2 text-sm font-medium text-slate-700 dark:text-slate-300 hover:text-slate-900 dark:hover:text-slate-100 cursor-pointer"
        >
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.746 0 3.332.477 4.5 1.253v13C19.832 18.477 18.246 18 16.5 18c-1.746 0-3.332.477-4.5 1.253"
            ></path>
          </svg>
          <span>Prompt Gallery</span>
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
import { onMounted, computed, ref } from 'vue'
import { useSessionsStore } from '@/stores/sessions.js'
import StatusBadge from './StatusBadge.vue'

const sessionsStore = useSessionsStore()

// State
const libraryExpanded = ref(true)

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

const toggleLibrary = () => {
  libraryExpanded.value = !libraryExpanded.value
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
