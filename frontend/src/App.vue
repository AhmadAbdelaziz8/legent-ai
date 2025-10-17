<script setup>
import { onMounted } from 'vue'
import AppHeader from './components/AppHeader.vue'
import SessionsSidebar from './components/SessionsSidebar.vue'
import WorkspaceViewer from './components/WorkspaceViewer.vue'
import ChatPanel from './components/ChatPanel.vue'
import './global.css'

// Initialize stores on app mount
onMounted(() => {
  // Any global initialization can go here
})
</script>

<template>
  <div class="h-screen w-screen flex flex-col bg-gray-100">
    <!-- Header -->
    <AppHeader />

    <!-- Main Content -->
    <main class="flex-1 flex overflow-hidden">
      <!-- Left Sidebar: Sessions History -->
      <SessionsSidebar />

      <!-- Center: Workspace Viewer -->
      <WorkspaceViewer />

      <!-- Right Sidebar: Chat Panel -->
      <ChatPanel />
    </main>
  </div>
</template>
