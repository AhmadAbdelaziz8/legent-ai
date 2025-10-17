<template>
  <div class="flex-1 flex flex-col bg-gray-100">
    <!-- Control Buttons -->
    <div class="p-4 border-b border-gray-200 bg-white">
      <div class="flex items-center space-x-4">
        <button
          @click="toggleRecording"
          :class="[
            'flex items-center px-4 py-2 rounded-lg font-medium transition-colors',
            isRecording
              ? 'bg-red-100 text-red-700 hover:bg-red-200'
              : 'bg-green-100 text-green-700 hover:bg-green-200',
          ]"
        >
          <svg class="h-5 w-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z"
            ></path>
          </svg>
          {{ isRecording ? 'Stop' : 'Record' }}
        </button>

        <div class="flex items-center text-sm text-gray-500">
          <span class="mr-2">Status:</span>
          <span
            :class="[
              'px-2 py-1 rounded text-xs font-medium',
              recordingStatus === 'recording'
                ? 'bg-red-100 text-red-700'
                : 'bg-gray-100 text-gray-700',
            ]"
          >
            {{ recordingStatus }}
          </span>
        </div>
      </div>
    </div>

    <!-- Main Workspace Area -->
    <div class="flex-1 relative">
      <!-- VNC Viewer Component -->
      <VNCViewer
        :vnc-host="vncHost"
        :vnc-port="vncPort"
        :auto-connect="autoConnect"
        @connected="onVNCConnected"
        @disconnected="onVNCDisconnected"
        @error="onVNCError"
      />
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useWorkspaceStore } from '../stores/workspace.js'
import VNCViewer from './VNCViewer.vue'

const workspaceStore = useWorkspaceStore()

// VNC Configuration
const vncHost = ref('localhost')
const vncPort = ref(8080) // Docker maps 6080 to 8080
const autoConnect = ref(false) // Set to true for automatic connection

const isRecording = computed(() => workspaceStore.isRecording)
const recordingStatus = computed(() => workspaceStore.recordingStatus)

// VNC State from store
const vncConnected = computed(() => workspaceStore.vncConnected)
const vncConnecting = computed(() => workspaceStore.vncConnecting)
const vncError = computed(() => workspaceStore.vncError)

const toggleRecording = async () => {
  try {
    if (isRecording.value) {
      await workspaceStore.stopRecording()
    } else {
      await workspaceStore.startRecording()
    }
  } catch (error) {
    console.error('Failed to toggle recording:', error)
  }
}

// VNC Event Handlers
const onVNCConnected = () => {
  console.log('VNC Connected')
  // Update workspace status or perform any actions when VNC connects
}

const onVNCDisconnected = () => {
  console.log('VNC Disconnected')
  // Handle VNC disconnection
}

const onVNCError = (error) => {
  console.error('VNC Error:', error)
  // Handle VNC errors
}

// VNC Actions
const connectVNC = async () => {
  try {
    await workspaceStore.connectVNC(vncHost.value, vncPort.value)
  } catch (error) {
    console.error('Failed to connect to VNC:', error)
  }
}

const disconnectVNC = () => {
  workspaceStore.disconnectVNC()
}

onMounted(() => {
  workspaceStore.fetchWorkspaces()
})
</script>
