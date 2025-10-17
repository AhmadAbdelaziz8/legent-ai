<template>
  <div class="vnc-container relative w-full h-full bg-gray-900">
    <!-- Loading State -->
    <div
      v-if="isConnecting"
      class="absolute inset-0 flex items-center justify-center bg-gradient-to-br from-slate-900 to-slate-800"
    >
      <div class="text-center text-white flex flex-col items-center gap-6">
        <div class="relative">
          <div
            class="animate-spin rounded-full h-16 w-16 border-4 border-slate-600 border-t-blue-500"
          ></div>
          <div
            class="absolute inset-0 animate-ping rounded-full h-16 w-16 border-4 border-blue-500 opacity-20"
          ></div>
        </div>
        <div class="flex flex-col items-center gap-2">
          <p class="text-xl font-semibold">Connecting to VNC...</p>
          <p class="text-sm text-slate-400">{{ connectionStatus }}</p>
        </div>
      </div>
    </div>

    <!-- Error State -->
    <div
      v-else-if="error"
      class="absolute inset-0 flex items-center justify-center bg-gradient-to-br from-red-900 to-red-800"
    >
      <div class="text-center text-white flex flex-col items-center gap-6 max-w-md mx-auto p-6">
        <div class="relative">
          <div class="w-20 h-20 bg-red-500/20 rounded-full flex items-center justify-center">
            <svg
              class="h-10 w-10 text-red-400"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z"
              ></path>
            </svg>
          </div>
        </div>
        <div class="flex flex-col items-center gap-3">
          <h3 class="text-2xl font-bold">Connection Failed</h3>
          <p class="text-red-200 text-center">{{ error }}</p>
        </div>
        <button
          @click="reconnect"
          class="flex items-center gap-3 px-6 py-3 bg-gradient-to-r from-blue-600 to-blue-700 text-white rounded-xl hover:from-blue-700 hover:to-blue-800 transition-all duration-300 shadow-lg hover:shadow-xl transform hover:scale-105"
        >
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"
            ></path>
          </svg>
          Retry Connection
        </button>
      </div>
    </div>

    <!-- VNC Display -->
    <div v-else-if="isConnected" class="w-full h-full">
      <!-- VNC iframe for noVNC -->
      <iframe
        v-if="useNoVNC"
        ref="vncFrame"
        :src="vncUrl"
        class="w-full h-full border-0"
        @load="onVNCConnect"
        @error="onVNCError"
      ></iframe>

      <!-- Canvas for direct VNC connection (if needed) -->
      <canvas
        v-else
        ref="vncCanvas"
        class="w-full h-full"
        @mousedown="onMouseDown"
        @mouseup="onMouseUp"
        @mousemove="onMouseMove"
        @keydown="onKeyDown"
        @keyup="onKeyUp"
      ></canvas>
    </div>

    <!-- Disconnected State -->
    <div
      v-else
      class="absolute inset-0 flex items-center justify-center bg-gradient-to-br from-slate-900 to-slate-800"
    >
      <div class="text-center text-white flex flex-col items-center gap-8 max-w-lg mx-auto p-8">
        <div class="relative">
          <div
            class="w-24 h-24 bg-gradient-to-br from-blue-500/20 to-purple-500/20 rounded-full flex items-center justify-center"
          >
            <svg
              class="h-12 w-12 text-blue-400"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="1.5"
                d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"
              ></path>
            </svg>
          </div>
          <div
            class="absolute -top-2 -right-2 w-6 h-6 bg-green-500 rounded-full flex items-center justify-center"
          >
            <svg class="w-3 h-3 text-white" fill="currentColor" viewBox="0 0 20 20">
              <path
                fill-rule="evenodd"
                d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z"
                clip-rule="evenodd"
              ></path>
            </svg>
          </div>
        </div>
        <div class="flex flex-col items-center gap-4">
          <h3
            class="text-3xl font-bold bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent"
          >
            Workspace 1
          </h3>
          <p class="text-slate-300 text-lg">AI Agent Desktop Environment</p>
          <p class="text-slate-400 text-sm max-w-md text-center">
            Connect to your virtual desktop environment to start interacting with the AI agent
          </p>
        </div>
        <button
          @click="connect"
          class="flex items-center gap-3 px-8 py-4 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-xl hover:from-blue-700 hover:to-purple-700 transition-all duration-300 shadow-xl hover:shadow-2xl transform hover:scale-105 font-semibold text-lg"
        >
          <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M13 10V3L4 14h7v7l9-11h-7z"
            ></path>
          </svg>
          Connect to Desktop
        </button>
      </div>
    </div>

    <!-- VNC Controls -->
    <div v-if="isConnected" class="absolute top-6 right-6 flex gap-3">
      <button
        @click="toggleFullscreen"
        class="flex items-center gap-2 px-4 py-2 bg-black/60 backdrop-blur-sm text-white rounded-lg hover:bg-black/80 transition-all duration-300 shadow-lg hover:shadow-xl"
        :title="isFullscreen ? 'Exit Fullscreen' : 'Enter Fullscreen'"
      >
        <svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path
            v-if="!isFullscreen"
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="2"
            d="M4 8V4m0 0h4M4 4l5 5m11-1V4m0 0h-4m4 0l-5 5M4 16v4m0 0h4m-4 0l5-5m11 5l-5-5m5 5v-4m0 4h-4"
          ></path>
          <path
            v-else
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="2"
            d="M9 9V4.5M9 9H4.5M9 9L4 4m11 5V4.5M20 9h-4.5M20 9l-5-5m-5 5v4.5M9 20h4.5M9 20l-5-5m11 5l-5-5m5 5v-4.5m0 4.5h-4.5"
          ></path>
        </svg>
        <span class="text-sm font-medium">{{ isFullscreen ? 'Exit' : 'Fullscreen' }}</span>
      </button>

      <button
        @click="disconnect"
        class="flex items-center gap-2 px-4 py-2 bg-red-600/80 backdrop-blur-sm text-white rounded-lg hover:bg-red-600 transition-all duration-300 shadow-lg hover:shadow-xl"
        title="Disconnect"
      >
        <svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="2"
            d="M6 18L18 6M6 6l12 12"
          ></path>
        </svg>
        <span class="text-sm font-medium">Disconnect</span>
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, computed } from 'vue'

// Emits
const emit = defineEmits(['connected', 'disconnected', 'error'])

// Props
const props = defineProps({
  vncHost: {
    type: String,
    default: 'localhost',
  },
  vncPort: {
    type: Number,
    default: 8080, // Docker maps 6080 to 8080
  },
  autoConnect: {
    type: Boolean,
    default: false,
  },
})

// Reactive state
const isConnecting = ref(false)
const isConnected = ref(false)
const error = ref(null)
const connectionStatus = ref('')
const isFullscreen = ref(false)
const useNoVNC = ref(true) // Use noVNC by default

// Refs
const vncFrame = ref(null)
const vncCanvas = ref(null)

// Computed
const vncUrl = computed(() => {
  return `http://${props.vncHost}:${props.vncPort}/vnc.html?autoconnect=true&resize=scale&quality=6`
})

// Methods
const connect = async () => {
  if (isConnecting.value || isConnected.value) return

  isConnecting.value = true
  error.value = null
  connectionStatus.value = 'Initializing connection...'

  try {
    // Check if VNC server is available
    connectionStatus.value = 'Checking VNC server...'
    const response = await fetch(`http://${props.vncHost}:${props.vncPort}/`, {
      method: 'HEAD',
      mode: 'no-cors',
    })

    connectionStatus.value = 'Connecting to desktop...'
    isConnected.value = true
    connectionStatus.value = 'Connected successfully'

    // Emit connected event
    emit('connected', { host: props.vncHost, port: props.vncPort })

    // Small delay to show connection status
    setTimeout(() => {
      isConnecting.value = false
    }, 1000)
  } catch (err) {
    error.value = `Failed to connect to VNC server: ${err.message}`
    isConnecting.value = false
    connectionStatus.value = 'Connection failed'

    // Emit error event
    emit('error', error.value)
  }
}

const disconnect = () => {
  isConnected.value = false
  isConnecting.value = false
  error.value = null
  connectionStatus.value = ''

  // Emit disconnected event
  emit('disconnected')
}

const reconnect = () => {
  disconnect()
  setTimeout(() => {
    connect()
  }, 500)
}

const toggleFullscreen = () => {
  if (!document.fullscreenElement) {
    document.documentElement.requestFullscreen()
    isFullscreen.value = true
  } else {
    document.exitFullscreen()
    isFullscreen.value = false
  }
}

// Event handlers
const onVNCConnect = () => {
  console.log('VNC iframe loaded')
  isConnecting.value = false
}

const onVNCError = () => {
  error.value = 'Failed to load VNC interface'
  isConnecting.value = false
}

const onMouseDown = (event) => {
  // Handle mouse events for direct VNC connection
  console.log('Mouse down:', event)
}

const onMouseUp = (event) => {
  // Handle mouse events for direct VNC connection
  console.log('Mouse up:', event)
}

const onMouseMove = (event) => {
  // Handle mouse events for direct VNC connection
  console.log('Mouse move:', event)
}

const onKeyDown = (event) => {
  // Handle keyboard events for direct VNC connection
  console.log('Key down:', event)
}

const onKeyUp = (event) => {
  // Handle keyboard events for direct VNC connection
  console.log('Key up:', event)
}

// Lifecycle
onMounted(() => {
  if (props.autoConnect) {
    connect()
  }

  // Listen for fullscreen changes
  document.addEventListener('fullscreenchange', () => {
    isFullscreen.value = !!document.fullscreenElement
  })
})

onUnmounted(() => {
  disconnect()
})
</script>

<style scoped>
.vnc-container {
  min-height: 400px;
}

/* Ensure iframe takes full space */
iframe {
  width: 100%;
  height: 100%;
  border: none;
  background: #000;
}

/* Canvas styling for direct VNC */
canvas {
  cursor: crosshair;
  background: #000;
}

/* Fullscreen styles */
:fullscreen .vnc-container {
  background: #000;
}
</style>
