<template>
  <div
    class="flex-1 flex flex-col bg-gradient-to-br from-slate-50 to-slate-100 dark:from-slate-900 dark:to-slate-800"
  >
   

    <!-- Main Workspace Area -->
    <div class="flex-1 relative bg-slate-900 dark:bg-slate-950">
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

// VNC State from store
const vncConnected = computed(() => workspaceStore.vncConnected)
const vncConnecting = computed(() => workspaceStore.vncConnecting)
const vncError = computed(() => workspaceStore.vncError)

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
