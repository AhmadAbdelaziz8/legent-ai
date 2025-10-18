<template>
  <div class="h-screen w-[100vw] flex flex-col bg-white">
    <!-- Header -->
    <AppHeader />

    <!-- Main Content -->
    <main class="flex-1 flex overflow-hidden bg-white shadow-inner">
      <!-- Left Sidebar: Task History -->
      <SessionsSidebar />

      <!-- Center: Workspace Viewer -->
      <WorkspaceViewer />

      <!-- Right Sidebar: AI Assistant -->
      <ChatPanelPolling />
    </main>
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import AppHeader from '../components/AppHeader.vue'
import SessionsSidebar from '../components/SessionsSidebar.vue'
import WorkspaceViewer from '../components/WorkspaceViewer.vue'
import ChatPanelPolling from '../components/ChatPanelPolling.vue'

// Initialize stores on app mount
onMounted(() => {
  // Any global initialization can go here
})
</script>
