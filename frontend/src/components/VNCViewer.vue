<template>
  <div class="vnc-container relative w-full h-full bg-gray-900">
    <!-- Loading State -->
    <div v-if="isConnecting" class="absolute inset-0 flex items-center justify-center bg-gray-900">
      <div class="text-center text-white">
        <div
          class="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto mb-4"
        ></div>
        <p class="text-lg">Connecting to VNC...</p>
        <p class="text-sm text-gray-400 mt-2">{{ connectionStatus }}</p>
      </div>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="absolute inset-0 flex items-center justify-center bg-gray-900">
      <div class="text-center text-white">
        <div class="text-red-500 mb-4">
          <svg class="h-16 w-16 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z"
            ></path>
          </svg>
        </div>
        <h3 class="text-xl font-semibold mb-2">Connection Failed</h3>
        <p class="text-gray-400 mb-4">{{ error }}</p>
        <button
          @click="reconnect"
          class="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 transition-colors"
        >
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
    <div v-else class="absolute inset-0 flex items-center justify-center bg-gray-900">
      <div class="text-center text-white">
        <div class="mb-4">
          <svg
            class="h-16 w-16 mx-auto text-gray-400"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="1"
              d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"
            ></path>
          </svg>
        </div>
        <h3 class="text-xl font-semibold mb-2">Workspace 1</h3>
        <p class="text-gray-400 mb-4">AI Agent Desktop Environment</p>
        <button
          @click="connect"
          class="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
        >
          Connect to Desktop
        </button>
      </div>
    </div>

    <!-- VNC Controls -->
    <div v-if="isConnected" class="absolute top-4 right-4 flex space-x-2">
      <button
        @click="toggleFullscreen"
        class="p-2 bg-black bg-opacity-50 text-white rounded hover:bg-opacity-70 transition-colors"
        :title="isFullscreen ? 'Exit Fullscreen' : 'Enter Fullscreen'"
      >
        <svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
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
      </button>

      <button
        @click="disconnect"
        class="p-2 bg-red-600 bg-opacity-50 text-white rounded hover:bg-opacity-70 transition-colors"
        title="Disconnect"
      >
        <svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
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
