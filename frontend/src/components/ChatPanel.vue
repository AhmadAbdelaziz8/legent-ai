<template>
  <div class="w-56 bg-white border-l border-slate-200 flex flex-col h-full shadow-lg">
    <!-- Header -->
    <div class="flex items-center justify-between mx-auto">
      <button
        @click="startNewSession"
        :disabled="isStreaming"
        class="px-3 py-1.5 bg-slate-600 hover:bg-slate-700 disabled:bg-slate-400 text-white text-xs font-medium rounded-lg transition-all duration-200 shadow-sm hover:shadow-md disabled:cursor-not-allowed flex items-center gap-1"
      >
        <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="2"
            d="M12 4v16m8-8H4"
          ></path>
        </svg>
        <span>New Session</span>
      </button>
    </div>

    <!-- Content -->
    <div class="flex-1 flex flex-col min-h-0">
      <!-- Messages area -->
      <div
        ref="messagesContainer"
        class="flex-1 overflow-y-auto p-3 flex flex-col gap-4 scroll-smooth"
      >
        <!-- No session selected -->
        <div
          v-if="!currentSession && !isNewSessionPending"
          class="flex flex-col items-center justify-center h-full text-center gap-6"
        >
          <!-- AI Assistant Welcome Message -->
          <div class="mb-4">
            <div
              class="bg-gradient-to-r from-green-50 to-green-100 from-green-50 to-green-100 rounded-lg p-3 border border-green-200 border-green-200"
            >
              <p class="text-sm text-slate-900 text-slate-900">
                Hi! Click "New Session" to start a conversation
              </p>
            </div>
          </div>
          <div class="relative">
            <div
              class="w-20 h-20 bg-gradient-to-br from-slate-200 to-slate-300 from-slate-200 to-slate-300 rounded-full flex items-center justify-center"
            >
              <svg
                class="w-10 h-10 text-slate-500"
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
            <h3 class="text-xl font-semibold text-slate-900 text-slate-900">Ready to Chat</h3>
            <p class="text-slate-500 text-slate-500 text-sm max-w-xs">
              Start a new session to begin your conversation
            </p>
          </div>
        </div>

        <!-- New session pending - show empty state but allow input -->
        <div
          v-else-if="isNewSessionPending"
          class="flex flex-col items-center justify-center h-full text-center gap-6"
        >
          <div class="relative">
            <div
              class="w-20 h-20 bg-gradient-to-br from-blue-200 to-purple-200 from-blue-200 to-purple-200 rounded-full flex items-center justify-center"
            >
              <svg
                class="w-10 h-10 text-blue-500 text-blue-500"
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
            <h3 class="text-xl font-semibold text-slate-900 text-slate-900">New Session Ready</h3>
            <p class="text-slate-500 text-slate-500 text-sm">
              Type your message below to start the conversation
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
              class="w-20 h-20 bg-gradient-to-br from-blue-200 to-purple-200 from-blue-200 to-purple-200 rounded-full flex items-center justify-center"
            >
              <svg
                class="w-10 h-10 text-blue-500 text-blue-500"
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
            <h3 class="text-xl font-semibold text-slate-900 text-slate-900">No Messages Yet</h3>
            <p class="text-slate-500 text-slate-500 text-sm">
              This session doesn't have any messages yet
            </p>
          </div>
        </div>

        <!-- Messages list -->
        <div v-else class="flex flex-col gap-4">
          <div
            v-for="message in messages"
            :key="message.id"
            :class="[
              'p-4 rounded-xl shadow-sm border-2 transition-all duration-300',
              message.role === 'user'
                ? 'bg-blue-50 bg-blue-50 border-blue-200 border-blue-200 ml-8'
                : 'bg-slate-50 bg-slate-50 border-slate-200 border-slate-200 mr-8',
            ]"
          >
            <div class="flex items-start gap-3">
              <div class="flex-shrink-0">
                <div
                  :class="[
                    'w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold shadow-lg',
                    message.role === 'user' ? 'bg-blue-600 text-white' : 'bg-slate-600 text-white',
                  ]"
                >
                  {{ message.role === 'user' ? 'U' : 'AI' }}
                </div>
              </div>
              <div class="flex-1 min-w-0">
                <div class="flex items-start gap-2">
                  <div class="text-sm text-slate-900 text-slate-900 leading-relaxed">
                    <p class="whitespace-pre-wrap break-words">
                      {{ getMessageContent(message) }}
                    </p>
                    <!-- Screenshot display -->
                    <div v-if="getScreenshotUrl(message)" class="mt-3">
                      <img
                        :src="getScreenshotUrl(message)"
                        alt="Screenshot"
                        class="max-w-full h-auto rounded-lg border border-slate-200 border-slate-200 cursor-pointer hover:opacity-90 transition-opacity"
                        @click="openScreenshotModal(message)"
                      />
                    </div>
                  </div>
                  <!-- Typing indicator for streaming messages -->
                  <div v-if="message.isStreaming" class="flex gap-1">
                    <div class="w-1 h-1 bg-slate-400 rounded-full animate-bounce"></div>
                    <div
                      class="w-1 h-1 bg-slate-400 rounded-full animate-bounce"
                      style="animation-delay: 0.1s"
                    ></div>
                    <div
                      class="w-1 h-1 bg-slate-400 rounded-full animate-bounce"
                      style="animation-delay: 0.2s"
                    ></div>
                  </div>
                </div>

                <!-- Screenshot display for computer use messages -->
                <div v-if="hasScreenshot(message)" class="mt-3">
                  <div
                    class="bg-slate-100 bg-slate-100 rounded-lg p-2 border border-slate-200 border-slate-200"
                  >
                    <div class="flex items-center gap-2 mb-2">
                      <svg
                        class="w-4 h-4 text-slate-500"
                        fill="none"
                        stroke="currentColor"
                        viewBox="0 0 24 24"
                      >
                        <path
                          stroke-linecap="round"
                          stroke-linejoin="round"
                          stroke-width="2"
                          d="M3 9a2 2 0 012-2h.93a2 2 0 001.664-.89l.812-1.22A2 2 0 0110.07 4h3.86a2 2 0 011.664.89l.812 1.22A2 2 0 0018.07 7H19a2 2 0 012 2v9a2 2 0 01-2 2H5a2 2 0 01-2-2V9z"
                        ></path>
                        <path
                          stroke-linecap="round"
                          stroke-linejoin="round"
                          stroke-width="2"
                          d="M15 13a3 3 0 11-6 0 3 3 0 016 0z"
                        ></path>
                      </svg>
                      <span class="text-xs text-slate-500 text-slate-500">Screenshot</span>
                    </div>
                    <img
                      :src="getScreenshotUrl(message)"
                      :alt="'Screenshot from ' + message.role"
                      class="w-full max-w-md rounded border border-slate-200 border-slate-200 shadow-sm"
                      @click="openScreenshotModal(message)"
                    />
                  </div>
                </div>

                <p class="text-xs text-slate-500 text-slate-500 mt-2 flex items-center gap-1">
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

      <!-- Chat Input Bar -->
      <div
        v-if="currentSession || isNewSessionPending"
        class="p-3 border-t border-slate-200 border-slate-200 bg-gradient-to-r from-slate-50 to-slate-100 from-slate-50 to-slate-100 flex-shrink-0"
      >
        <div class="flex items-center gap-2">
          <div class="flex-1 relative">
            <input
              ref="messageInputRef"
              v-model="messageInput"
              @keydown.enter="sendMessage"
              :disabled="isStreaming"
              placeholder="Type your message..."
              class="w-full px-3 py-2 border border-slate-300 border-slate-200 rounded-lg bg-white bg-slate-50 text-slate-900 text-slate-900 placeholder-slate-500 dark:placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent disabled:opacity-50 disabled:cursor-not-allowed text-sm"
            />
          </div>
          <button
            @click="sendMessage"
            :disabled="!messageInput.trim() || isStreaming"
            class="px-3 py-2 bg-gradient-to-r from-green-500 to-green-600 hover:from-green-600 hover:to-green-700 disabled:from-slate-400 disabled:to-slate-500 text-white text-sm font-medium rounded-lg transition-all duration-200 shadow-sm hover:shadow-md disabled:cursor-not-allowed flex items-center gap-1"
          >
            <svg
              v-if="!isStreaming"
              class="w-4 h-4"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8"
              ></path>
            </svg>
            <div
              v-else
              class="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"
            ></div>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted, onUnmounted, nextTick } from 'vue'
import { useSessionsStore } from '@/stores/sessions.js'
import { useMessagesStore } from '@/stores/messages.js'

const sessionsStore = useSessionsStore()
const messagesStore = useMessagesStore()

// State
const messageInput = ref('')
const isNewSessionPending = ref(false)
const messageInputRef = ref(null)
const messagesContainer = ref(null)

// Computed properties
const currentSession = computed(() => sessionsStore.currentSession)
const messages = computed(() => messagesStore.messages)
const isStreaming = computed(() => messagesStore.isStreaming)
const loading = computed(() => messagesStore.loading)
const error = computed(() => messagesStore.error)

// Methods
const startNewSession = () => {
  sessionsStore.clearCurrentSession()
  messagesStore.clearMessages()
  isNewSessionPending.value = true
  nextTick(() => {
    if (messageInputRef.value) {
      messageInputRef.value.focus()
    }
  })
}

const sendMessage = async () => {
  if (!messageInput.value.trim() || isStreaming.value) return

  const userMessage = messageInput.value.trim()
  messageInput.value = ''

  try {
    if (isNewSessionPending.value || !currentSession.value) {
      // Create new session with first message
      await messagesStore.createSessionAndSendMessage(userMessage)
      isNewSessionPending.value = false
    } else {
      // Send message in existing session
      await messagesStore.sendMessage(userMessage, currentSession.value.id)
      // Start streaming for the response
      await messagesStore.startStreaming(currentSession.value.id)
    }
  } catch (err) {
    console.error('Failed to send message:', err)
    // Optionally show error to user
  }
}

const getMessageContent = (message) => {
  console.log('🔍 [CHAT] getMessageContent called with message:', message)
  console.log('🔍 [CHAT] message.content:', message.content)

  if (typeof message.content === 'string') {
    console.log('🔍 [CHAT] String content:', message.content)
    return message.content
  } else if (message.content && message.content.text) {
    console.log('🔍 [CHAT] Text content:', message.content.text)
    return message.content.text
  } else if (message.content && message.content.content && Array.isArray(message.content.content)) {
    // Handle the nested content structure from streaming
    console.log('🔍 [CHAT] Nested content array:', message.content.content)
    const textContent = message.content.content
      .filter((item) => item.type === 'text')
      .map((item) => item.text)
      .join('')
    console.log('🔍 [CHAT] Extracted text:', textContent)
    return textContent
  }
  console.log('🔍 [CHAT] No content found, returning "No content"')
  return 'No content'
}

const formatTime = (dateString) => {
  const date = new Date(dateString)
  return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
}

// Screenshot handling methods
const hasScreenshot = (message) => {
  if (!message.content) return false

  // Check for base64_image in tool results
  if (message.content.base64_image) return true

  // Check for screenshot in nested content structure
  if (message.content.content && Array.isArray(message.content.content)) {
    return message.content.content.some(
      (item) =>
        item.base64_image ||
        (item.type === 'tool_result' && item.content && item.content.base64_image),
    )
  }

  return false
}

const getScreenshotUrl = (message) => {
  if (!message.content) return ''

  // Direct base64_image in message
  if (message.base64_image) {
    return `data:image/png;base64,${message.base64_image}`
  }

  // Direct base64_image in content
  if (message.content.base64_image) {
    return `data:image/png;base64,${message.content.base64_image}`
  }

  // Check nested content structure
  if (message.content.content && Array.isArray(message.content.content)) {
    for (const item of message.content.content) {
      if (item.base64_image) {
        return `data:image/png;base64,${item.base64_image}`
      }
      if (item.type === 'tool_result' && item.content && item.content.base64_image) {
        return `data:image/png;base64,${item.content.base64_image}`
      }
      // Check for image blocks in content
      if (item.type === 'image' && item.source && item.source.data) {
        return `data:image/png;base64,${item.source.data}`
      }
    }
  }

  return ''
}

const openScreenshotModal = (message) => {
  // TODO: Implement screenshot modal
  console.log('Opening screenshot modal for message:', message)
}

// Auto-scroll to bottom when new messages arrive
const scrollToBottom = () => {
  nextTick(() => {
    if (messagesContainer.value) {
      messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
    }
  })
}

// Watch for session changes to load messages
watch(
  currentSession,
  async (newSession) => {
    if (newSession) {
      try {
        await messagesStore.fetchMessages(newSession.id)
      } catch (err) {
        console.error('Failed to fetch messages:', err)
      }
    } else {
      messagesStore.clearMessages()
    }
  },
  { immediate: true },
)

// Auto-focus input when new session is pending
watch(isNewSessionPending, (isPending) => {
  if (isPending) {
    nextTick(() => {
      if (messageInputRef.value) {
        messageInputRef.value.focus()
      }
    })
  }
})

// Auto-scroll when messages change
watch(
  messages,
  () => {
    scrollToBottom()
  },
  { deep: true },
)

// Auto-scroll when streaming status changes
watch(isStreaming, (newValue, oldValue) => {
  if (newValue !== oldValue) {
    scrollToBottom()
  }
})

// Initial scroll to bottom on mount
onMounted(() => {
  scrollToBottom()
})

// Cleanup on unmount
onUnmounted(() => {
  messagesStore.stopStreaming()
})
</script>
