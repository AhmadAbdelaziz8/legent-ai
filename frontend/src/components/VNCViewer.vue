<template>
  <div class="vnc-viewer-container">
    <!-- VNC Status Bar -->
    <div
      class="vnc-status-bar bg-slate-100 dark:bg-slate-800 border-b border-slate-200 dark:border-slate-700 p-3"
    >
      <div class="flex items-center justify-between">
        <div class="flex items-center gap-3">
          <div class="flex items-center gap-2">
            <div
              :class="[
                'w-3 h-3 rounded-full',
                vncStatus.connected
                  ? 'bg-green-500'
                  : vncStatus.connecting
                    ? 'bg-yellow-500 animate-pulse'
                    : 'bg-red-500',
              ]"
            ></div>
            <span class="text-sm font-medium text-slate-700 dark:text-slate-300">
              {{
                vncStatus.connected
                  ? 'VNC Connected'
                  : vncStatus.connecting
                    ? 'Connecting...'
                    : 'VNC Disconnected'
              }}
            </span>
          </div>

          <div v-if="vncStatus.error" class="text-xs text-red-600 dark:text-red-400">
            {{ vncStatus.error }}
          </div>
        </div>

        <div class="flex items-center gap-2">
          <button
            @click="takeScreenshot"
            :disabled="!vncStatus.connected"
            class="px-3 py-1.5 bg-blue-500 hover:bg-blue-600 disabled:bg-slate-400 text-white text-xs font-medium rounded-lg transition-colors duration-200 flex items-center gap-1"
          >
            <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
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
            Screenshot
          </button>

          <button
            @click="toggleVNC"
            :disabled="vncStatus.connecting"
            class="px-3 py-1.5 bg-green-500 hover:bg-green-600 disabled:bg-slate-400 text-white text-xs font-medium rounded-lg transition-colors duration-200"
          >
            {{ vncStatus.connected ? 'Disconnect' : 'Connect' }}
          </button>
        </div>
      </div>
    </div>

    <!-- VNC Content -->
    <div class="vnc-content flex-1 relative">
      <!-- VNC iframe or viewer -->
      <div v-if="vncStatus.connected" class="w-full h-full">
        <iframe
          :src="vncUrl"
          class="w-full h-full border-0"
          title="VNC Desktop"
          @load="onVNCLoad"
          @error="onVNCError"
        ></iframe>
      </div>

      <!-- Connection prompt -->
      <div v-else class="flex items-center justify-center h-full">
        <div class="text-center">
          <div
            class="w-16 h-16 bg-slate-200 dark:bg-slate-700 rounded-full flex items-center justify-center mx-auto mb-4"
          >
            <svg
              class="w-8 h-8 text-slate-500"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2-2v10a2 2 0 002 2z"
              ></path>
            </svg>
          </div>
          <h3 class="text-lg font-semibold text-slate-900 dark:text-slate-100 mb-2">VNC Desktop</h3>
          <p class="text-slate-500 dark:text-slate-400 text-sm mb-4">
            Connect to view and control the desktop environment
          </p>
          <button
            @click="connectVNC"
            :disabled="vncStatus.connecting"
            class="px-4 py-2 bg-green-500 hover:bg-green-600 disabled:bg-slate-400 text-white font-medium rounded-lg transition-colors duration-200"
          >
            {{ vncStatus.connecting ? 'Connecting...' : 'Connect VNC' }}
          </button>
        </div>
      </div>
    </div>

    <!-- Screenshot Modal -->
    <div
      v-if="showScreenshotModal"
      class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
    >
      <div class="bg-white dark:bg-slate-800 rounded-lg p-6 max-w-4xl max-h-[90vh] overflow-auto">
        <div class="flex items-center justify-between mb-4">
          <h3 class="text-lg font-semibold text-slate-900 dark:text-slate-100">Screenshot</h3>
          <button
            @click="closeScreenshotModal"
            class="text-slate-500 hover:text-slate-700 dark:text-slate-400 dark:hover:text-slate-200"
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

        <div v-if="currentScreenshot" class="text-center">
          <img
            :src="currentScreenshot"
            alt="Screenshot"
            class="max-w-full max-h-[70vh] rounded border border-slate-200 dark:border-slate-600"
          />
          <div class="mt-4 flex justify-center gap-2">
            <button
              @click="downloadScreenshot"
              class="px-4 py-2 bg-blue-500 hover:bg-blue-600 text-white font-medium rounded-lg transition-colors duration-200"
            >
              Download
            </button>
            <button
              @click="closeScreenshotModal"
              class="px-4 py-2 bg-slate-500 hover:bg-slate-600 text-white font-medium rounded-lg transition-colors duration-200"
            >
              Close
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { vncService } from '@/services/vncService.js'

// State
const vncStatus = ref({
  connected: false,
  connecting: false,
  error: null,
})

const showScreenshotModal = ref(false)
const currentScreenshot = ref('')
const vncUrl = ref('http://localhost:8080/vnc.html?autoconnect=true&resize=scale&quality=6')

// Computed
const isVNCReady = computed(() => vncStatus.value.connected && !vncStatus.value.error)

// Methods
const connectVNC = async () => {
  try {
    vncStatus.value.connecting = true
    vncStatus.value.error = null

    const success = await vncService.connect()
    if (success) {
      vncStatus.value.connected = true
      vncStatus.value.connecting = false
      // VNC URL is already set with proper parameters
    } else {
      vncStatus.value.connected = false
      vncStatus.value.connecting = false
      vncStatus.value.error = 'Failed to connect to VNC'
    }
  } catch (err) {
    console.error('Failed to connect VNC:', err)
    vncStatus.value.connected = false
    vncStatus.value.connecting = false
    vncStatus.value.error = err.message || 'VNC connection failed'
  }
}

const toggleVNC = async () => {
  if (vncStatus.value.connected) {
    vncService.disconnect()
  } else {
    await connectVNC()
  }
}

const takeScreenshot = async () => {
  try {
    const screenshot = await vncService.takeScreenshot()
    currentScreenshot.value = screenshot
    showScreenshotModal.value = true
  } catch (err) {
    console.error('Failed to take screenshot:', err)
  }
}

const closeScreenshotModal = () => {
  showScreenshotModal.value = false
  currentScreenshot.value = ''
}

const downloadScreenshot = () => {
  if (currentScreenshot.value) {
    const link = document.createElement('a')
    link.href = currentScreenshot.value
    link.download = `screenshot-${Date.now()}.png`
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
  }
}

const onVNCLoad = () => {
  console.log('VNC iframe loaded')
}

const onVNCError = () => {
  console.error('VNC iframe error')
  vncStatus.value.error = 'Failed to load VNC interface'
}

// Event handlers
const handleVNCConnected = () => {
  vncStatus.value.connected = true
  vncStatus.value.connecting = false
  vncStatus.value.error = null
}

const handleVNCDisconnected = () => {
  vncStatus.value.connected = false
  vncStatus.value.connecting = false
}

const handleVNCConnecting = () => {
  vncStatus.value.connecting = true
  vncStatus.value.error = null
}

const handleVNCError = (error) => {
  vncStatus.value.error = error.message || 'VNC connection error'
  vncStatus.value.connected = false
  vncStatus.value.connecting = false
}

// Lifecycle
onMounted(() => {
  // Set up VNC event listeners
  vncService.on('connected', handleVNCConnected)
  vncService.on('disconnected', handleVNCDisconnected)
  vncService.on('connecting', handleVNCConnecting)
  vncService.on('error', handleVNCError)

  // Update status from service
  const status = vncService.getStatus()
  vncStatus.value = { ...status }
})

onUnmounted(() => {
  // Clean up event listeners
  vncService.off('connected', handleVNCConnected)
  vncService.off('disconnected', handleVNCDisconnected)
  vncService.off('connecting', handleVNCConnecting)
  vncService.off('error', handleVNCError)
})
</script>

<style scoped>
.vnc-viewer-container {
  @apply flex flex-col h-full;
}

.vnc-content {
  @apply flex-1;
}

.vnc-status-bar {
  @apply flex-shrink-0;
}
</style>
