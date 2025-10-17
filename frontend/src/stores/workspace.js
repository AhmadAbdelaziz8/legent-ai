import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useWorkspaceStore = defineStore('workspace', () => {
  // State
  const workspaces = ref([])
  const currentWorkspace = ref(null)
  const isRecording = ref(false)
  const recordingStatus = ref('idle')
  const loading = ref(false)
  const error = ref(null)

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

  return {
    // State
    workspaces,
    currentWorkspace,
    isRecording,
    recordingStatus,
    loading,
    error,

    // Getters
    workspaceCount,

    // Actions
    fetchWorkspaces,
    startRecording,
    stopRecording,
    setCurrentWorkspace,
    clearError,
  }
})
