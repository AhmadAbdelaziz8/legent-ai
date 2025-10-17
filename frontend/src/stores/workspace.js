import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import vncService from '../services/vncService.js'

export const useWorkspaceStore = defineStore('workspace', () => {
  // State
  const workspaces = ref([])
  const currentWorkspace = ref(null)
  const isRecording = ref(false)
  const recordingStatus = ref('idle')
  const loading = ref(false)
  const error = ref(null)

  // VNC State
  const vncConnected = ref(false)
  const vncConnecting = ref(false)
  const vncError = ref(null)

  // Getters
  const workspaceCount = computed(() => workspaces.value.length)

  // Actions
  const fetchWorkspaces = async () => {
    loading.value = true
    error.value = null

    try {
      // Mock data for now - in a real app this would fetch from API
      workspaces.value = [
        {
          id: 1,
          name: 'Workspace 1',
          status: 'active',
          created_at: new Date().toISOString(),
        },
      ]
    } catch (err) {
      error.value = err.message
      throw err
    } finally {
      loading.value = false
    }
  }

  const startRecording = async () => {
    try {
      isRecording.value = true
      recordingStatus.value = 'recording'
      // In a real app, this would start screen recording
      console.log('Recording started')
    } catch (err) {
      error.value = err.message
      throw err
    }
  }

  const stopRecording = async () => {
    try {
      isRecording.value = false
      recordingStatus.value = 'idle'
      // In a real app, this would stop screen recording
      console.log('Recording stopped')
    } catch (err) {
      error.value = err.message
      throw err
    }
  }

  const setCurrentWorkspace = (workspace) => {
    currentWorkspace.value = workspace
  }

  const clearError = () => {
    error.value = null
  }

  // VNC Actions
  const connectVNC = async (host = 'localhost', port = 6080) => {
    try {
      vncConnecting.value = true
      vncError.value = null

      const success = await vncService.connect(host, port)
      vncConnected.value = success

      if (!success) {
        vncError.value = vncService.error
      }

      return success
    } catch (err) {
      vncError.value = err.message
      vncConnected.value = false
      return false
    } finally {
      vncConnecting.value = false
    }
  }

  const disconnectVNC = () => {
    vncService.disconnect()
    vncConnected.value = false
    vncError.value = null
  }

  const getVNCUrl = (options = {}) => {
    return vncService.getVNCUrl(options)
  }

  const takeVNCScreenshot = async () => {
    if (!vncConnected.value) {
      throw new Error('VNC not connected')
    }
    return await vncService.takeScreenshot()
  }

  // Setup VNC event listeners
  vncService.on('connected', () => {
    vncConnected.value = true
    vncError.value = null
  })

  vncService.on('disconnected', () => {
    vncConnected.value = false
  })

  vncService.on('error', (error) => {
    vncError.value = error
    vncConnected.value = false
  })

  return {
    // State
    workspaces,
    currentWorkspace,
    isRecording,
    recordingStatus,
    loading,
    error,

    // VNC State
    vncConnected,
    vncConnecting,
    vncError,

    // Getters
    workspaceCount,

    // Actions
    fetchWorkspaces,
    startRecording,
    stopRecording,
    setCurrentWorkspace,
    clearError,

    // VNC Actions
    connectVNC,
    disconnectVNC,
    getVNCUrl,
    takeVNCScreenshot,
  }
})
