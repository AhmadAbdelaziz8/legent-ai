<template>
  <div class="flex flex-col h-full bg-white">
    <!-- Header -->
    <div class="flex items-center justify-between p-4 border-b border-slate-200">
      <h2 class="text-lg font-semibold text-slate-900">Claude Computer Use Demo</h2>
      <div class="flex items-center gap-2">
        <!-- Polling Status Indicator -->
        <div v-if="isPolling" class="flex items-center gap-1 text-xs text-green-600">
          <div class="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
          <span>Live</span>
        </div>
        <button
          @click="resetSession"
          class="px-3 py-1.5 bg-red-600 hover:bg-red-700 text-white text-xs font-medium rounded-lg transition-all duration-200 shadow-sm hover:shadow-md"
        >
          Reset
        </button>
      </div>
    </div>

    <!-- Configuration Panel -->
    <div v-if="!currentSession" class="p-4 border-b border-slate-200">
      <div class="space-y-4">
        <!-- Prompt Input -->
        <div>
          <label class="block text-sm font-medium text-slate-700 mb-2"> Your Prompt </label>
          <textarea
            v-model="userPrompt"
            placeholder="Type a message to send to Claude to control the computer..."
            class="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 bg-white text-slate-900"
            rows="3"
          ></textarea>
        </div>

        <!-- Configuration Options -->
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <!-- Provider Selection -->
          <div>
            <label class="block text-sm font-medium text-slate-700 text-slate-700 mb-2">
              API Provider
            </label>
            <select
              v-model="config.provider"
              class="w-full px-3 py-2 border border-slate-300 border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 bg-white text-slate-900"
            >
              <option value="anthropic">Anthropic</option>
              <option value="bedrock">Bedrock</option>
              <option value="vertex">Vertex</option>
            </select>
          </div>

          <!-- Model Selection -->
          <div>
            <label class="block text-sm font-medium text-slate-700 text-slate-700 mb-2">
              Model
            </label>
            <input
              v-model="config.model"
              placeholder="claude-sonnet-4-5-20250929"
              class="w-full px-3 py-2 border border-slate-300 border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 bg-white text-slate-900"
            />
          </div>

          <!-- Max Tokens -->
          <div>
            <label class="block text-sm font-medium text-slate-700 text-slate-700 mb-2">
              Max Output Tokens
            </label>
            <input
              v-model.number="config.max_tokens"
              type="number"
              min="1"
              step="1"
              class="w-full px-3 py-2 border border-slate-300 border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 bg-white text-slate-900"
            />
          </div>

          <!-- Only N Most Recent Images -->
          <div>
            <label class="block text-sm font-medium text-slate-700 text-slate-700 mb-2">
              Only send N most recent images
            </label>
            <input
              v-model.number="config.only_n_most_recent_images"
              type="number"
              min="0"
              step="1"
              class="w-full px-3 py-2 border border-slate-300 border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 bg-white text-slate-900"
            />
          </div>

          <!-- Thinking Budget -->
          <div>
            <label class="block text-sm font-medium text-slate-700 text-slate-700 mb-2">
              Thinking Budget
            </label>
            <input
              v-model.number="config.thinking_budget"
              type="number"
              min="0"
              step="1"
              :max="config.max_tokens"
              class="w-full px-3 py-2 border border-slate-300 border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 bg-white text-slate-900"
            />
          </div>

          <!-- Tool Version -->
          <div>
            <label class="block text-sm font-medium text-slate-700 text-slate-700 mb-2">
              Tool Version
            </label>
            <select
              v-model="config.tool_version"
              class="w-full px-3 py-2 border border-slate-300 border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 bg-white text-slate-900"
            >
              <option value="computer_use_20250124">computer_use_20250124</option>
              <option value="computer_use_20241022">computer_use_20241022</option>
              <option value="computer_use_20250429">computer_use_20250429</option>
            </select>
          </div>
        </div>

        <!-- System Prompt Suffix -->
        <div>
          <label class="block text-sm font-medium text-slate-700 text-slate-700 mb-2">
            Custom System Prompt Suffix
          </label>
          <textarea
            v-model="config.system_prompt_suffix"
            placeholder="Additional instructions to append to the system prompt..."
            class="w-full px-3 py-2 border border-slate-300 border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 bg-white text-slate-900"
            rows="2"
          ></textarea>
        </div>

        <!-- Start Session Button -->
        <div class="flex justify-center">
          <button
            @click="startNewSession"
            :disabled="loading || !userPrompt.trim()"
            class="px-6 py-3 bg-blue-600 hover:bg-blue-700 disabled:bg-slate-400 text-white font-medium rounded-lg transition-all duration-200 shadow-sm hover:shadow-md disabled:cursor-not-allowed flex items-center gap-2"
          >
            <svg
              v-if="loading"
              class="w-4 h-4 animate-spin"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"
              ></path>
            </svg>
            <span>{{ loading ? 'Starting...' : 'Start Session' }}</span>
          </button>
        </div>
      </div>
    </div>

    <!-- Chat Messages -->
    <div v-if="currentSession" class="flex-1 flex flex-col min-h-0">
      <!-- Messages area -->
      <div
        ref="messagesContainer"
        class="flex-1 overflow-y-auto p-4 flex flex-col gap-4 scroll-smooth"
      >
        <!-- Loading state -->
        <div v-if="loading" class="flex flex-col items-center justify-center h-full">
          <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-slate-600"></div>
          <p class="text-sm text-slate-600 text-slate-500 mt-2">Starting session...</p>
        </div>

        <!-- Error state -->
        <div
          v-if="error"
          class="bg-red-50 bg-red-50 border border-red-200 border-red-200 rounded-lg p-3"
        >
          <p class="text-sm text-red-600 text-red-600">{{ error }}</p>
          <button @click="clearError" class="text-xs text-red-500 hover:text-red-700 mt-1">
            Dismiss
          </button>
        </div>

        <!-- Messages -->
        <div v-for="message in messages" :key="message.id" class="flex flex-col gap-2">
          <!-- User Message -->
          <div v-if="message.role === 'user'" class="flex justify-end">
            <div class="max-w-[80%] bg-blue-600 text-white rounded-lg px-3 py-2 text-sm">
              <div v-if="typeof message.content === 'string'">
                {{ message.content }}
              </div>
              <div v-else-if="message.content.text">
                {{ message.content.text }}
              </div>
              <div v-else>
                {{ JSON.stringify(message.content) }}
              </div>
            </div>
          </div>

          <!-- Assistant Message -->
          <div v-else-if="message.role === 'assistant'" class="flex justify-start">
            <div
              class="max-w-[80%] bg-white bg-white border border-slate-200 border-slate-300 rounded-lg px-3 py-2 text-sm"
            >
              <div v-if="message.content.text" class="text-slate-900 text-slate-900">
                {{ message.content.text }}
              </div>
              <div
                v-else-if="typeof message.content === 'string'"
                class="text-slate-900 text-slate-900"
              >
                {{ message.content }}
              </div>
              <div v-else class="text-slate-900 text-slate-900">
                {{ JSON.stringify(message.content) }}
              </div>
            </div>
          </div>

          <!-- Tool Message -->
          <div v-else-if="message.role === 'tool'" class="flex justify-start">
            <div
              class="max-w-[80%] bg-blue-50 bg-blue-50 border border-blue-200 border-blue-200 rounded-lg px-3 py-2 text-sm"
            >
              <div class="flex items-center gap-2 mb-2">
                <svg
                  class="w-4 h-4 text-blue-600"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="2"
                    d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"
                  ></path>
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="2"
                    d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"
                  ></path>
                </svg>
                <span class="text-xs font-medium text-blue-600 text-blue-600">Tool Output</span>
              </div>
              <div v-if="message.content.output" class="text-slate-700 text-slate-700">
                {{ message.content.output }}
              </div>
              <div v-if="message.content.error" class="text-red-600 text-red-600">
                {{ message.content.error }}
              </div>
              <div v-if="message.content.system" class="text-slate-500 text-slate-500 text-xs">
                {{ message.content.system }}
              </div>
            </div>
          </div>

          <!-- Screenshot if present -->
          <div v-if="message.base64_image" class="flex justify-start">
            <div class="max-w-[80%] bg-slate-100 bg-white rounded-lg p-2">
              <img
                :src="`data:image/png;base64,${message.base64_image}`"
                alt="Screenshot"
                class="max-w-full h-auto rounded border border-slate-200 border-slate-300 cursor-pointer hover:opacity-90 transition-opacity"
                @click="openScreenshotModal(message.base64_image)"
              />
            </div>
          </div>
        </div>

        <!-- Session Status -->
        <div
          v-if="currentSession && sessionStatus"
          class="mt-4 p-2 bg-slate-50 bg-white rounded-lg"
        >
          <div class="flex items-center gap-2 text-xs">
            <div
              class="w-2 h-2 rounded-full"
              :class="{
                'bg-green-500': sessionStatus.status === 'completed',
                'bg-yellow-500':
                  sessionStatus.status === 'running' || sessionStatus.status === 'processing',
                'bg-red-500': sessionStatus.status === 'error',
              }"
            ></div>
            <span class="text-slate-600 text-slate-500"> Status: {{ sessionStatus.status }} </span>
          </div>
        </div>
      </div>
    </div>

    <!-- Screenshot Modal -->
    <div
      v-if="showScreenshotModal"
      class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
      @click="closeScreenshotModal"
    >
      <div class="bg-white bg-white rounded-lg p-4 max-w-4xl max-h-4xl">
        <div class="flex justify-between items-center mb-4">
          <h3 class="text-lg font-semibold text-slate-900 text-slate-900">Screenshot</h3>
          <button
            @click="closeScreenshotModal"
            class="text-slate-500 hover:text-slate-700 text-slate-500 dark:hover:text-slate-200"
          >
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M6 18L18 6M6 6l12 12"
              ></path>
            </svg>
          </button>
        </div>
        <img
          :src="`data:image/png;base64,${currentScreenshot}`"
          alt="Screenshot"
          class="max-w-full max-h-full object-contain"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, nextTick, watch } from 'vue'
import { useMessagesPollingStore } from '../stores/messagesPolling.js'

// Store
const messagesStore = useMessagesPollingStore()

// State
const messagesContainer = ref(null)
const showScreenshotModal = ref(false)
const currentScreenshot = ref(null)
const userPrompt = ref('')
const config = ref({
  provider: 'bedrock',
  model: 'claude-sonnet-4-5-20250929',
  system_prompt_suffix: '',
  max_tokens: 4096,
  thinking_budget: 2048,
  only_n_most_recent_images: 3,
  tool_version: 'computer_use_20250124',
})

// Computed
const messages = computed(() => messagesStore.messages)
const currentSession = computed(() => messagesStore.currentSession)
const sessionStatus = computed(() => messagesStore.sessionStatus)
const loading = computed(() => messagesStore.loading)
const error = computed(() => messagesStore.error)
const isPolling = computed(() => messagesStore.isPolling)

// Methods
const startNewSession = async () => {
  if (!userPrompt.value.trim()) return

  try {
    await messagesStore.startNewSession(userPrompt.value, config.value.provider, config.value)
    scrollToBottom()
  } catch (err) {
    console.error('Failed to start new session:', err)
  }
}

const resetSession = () => {
  messagesStore.clearSession()
  userPrompt.value = ''
  loadSavedConfig()
}

const scrollToBottom = () => {
  nextTick(() => {
    if (messagesContainer.value) {
      messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
    }
  })
}

const openScreenshotModal = (base64Image) => {
  currentScreenshot.value = base64Image
  showScreenshotModal.value = true
}

const closeScreenshotModal = () => {
  showScreenshotModal.value = false
  currentScreenshot.value = null
}

const clearError = () => {
  messagesStore.clearSession()
}

const saveConfig = () => {
  localStorage.setItem('chatConfig', JSON.stringify(config.value))
}

const loadSavedConfig = () => {
  const saved = localStorage.getItem('chatConfig')
  if (saved) {
    try {
      const savedConfig = JSON.parse(saved)
      config.value = { ...config.value, ...savedConfig }
    } catch (e) {
      console.warn('Failed to load saved config:', e)
    }
  }
}

// Auto-scroll when new messages arrive
const previousMessageCount = ref(0)
watch(
  () => messagesStore.messages.length,
  (newCount) => {
    if (newCount > previousMessageCount.value) {
      scrollToBottom()
      previousMessageCount.value = newCount
    }
  },
)

// Save config when it changes
watch(config, saveConfig, { deep: true })

// Load saved config on mount
onMounted(() => {
  loadSavedConfig()
})

// Cleanup on unmount
onUnmounted(() => {
  messagesStore.stopPolling()
})
</script>
