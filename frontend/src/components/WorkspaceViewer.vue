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
    <div class="flex-1 relative bg-blue-900">
      <!-- Desktop-like background -->
      <div class="absolute inset-0 bg-gradient-to-br from-blue-800 to-blue-900">
        <!-- Workspace content placeholder -->
        <div class="absolute inset-0 flex items-center justify-center">
          <div class="text-center text-white">
            <div class="mb-4">
              <svg
                class="h-16 w-16 mx-auto text-blue-300"
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
            <p class="text-blue-200">AI Agent Desktop Environment</p>
          </div>
        </div>

        <!-- Taskbar-like element at bottom -->
        <div class="absolute bottom-0 left-0 right-0 bg-black bg-opacity-50 p-2">
          <div class="flex items-center space-x-2">
            <!-- App icons placeholder -->
            <div class="w-8 h-8 bg-green-500 rounded flex items-center justify-center">
              <svg class="h-4 w-4 text-white" fill="currentColor" viewBox="0 0 20 20"></svg>
            </div>
            <div class="w-8 h-8 bg-gray-600 rounded flex items-center justify-center">
              <svg class="h-4 w-4 text-white" fill="currentColor" viewBox="0 0 20 20">
                <path
                  fill-rule="evenodd"
                  d="M3 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm0 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm0 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1z"
                  clip-rule="evenodd"
                ></path>
              </svg>
            </div>
            <div class="w-8 h-8 bg-yellow-500 rounded flex items-center justify-center">
              <svg class="h-4 w-4 text-white" fill="currentColor" viewBox="0 0 20 20">
                <path
                  d="M3 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm0 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm0 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1z"
                ></path>
              </svg>
            </div>
            <div class="w-8 h-8 bg-red-500 rounded flex items-center justify-center">
              <svg class="h-4 w-4 text-white" fill="currentColor" viewBox="0 0 20 20">
                <path
                  fill-rule="evenodd"
                  d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z"
                  clip-rule="evenodd"
                ></path>
              </svg>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted } from 'vue'
import { useWorkspaceStore } from '../stores/workspace.js'

const workspaceStore = useWorkspaceStore()

const isRecording = computed(() => workspaceStore.isRecording)
const recordingStatus = computed(() => workspaceStore.recordingStatus)

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

onMounted(() => {
  workspaceStore.fetchWorkspaces()
})
</script>
