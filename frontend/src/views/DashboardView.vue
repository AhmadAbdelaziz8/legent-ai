<template>
  <div
    class="h-screen w-[100vw] flex flex-col bg-gradient-to-br from-slate-50 to-slate-100 dark:from-slate-900 dark:to-slate-800"
  >
    <!-- Header -->
    <AppHeader />

    <!-- Main Content -->
    <main class="flex-1 flex overflow-hidden bg-white dark:bg-slate-900 shadow-inner">
      <!-- Left Sidebar: Task History -->
      <SessionsSidebar />

      <!-- Center: Workspace Viewer -->
      <WorkspaceViewer />

      <!-- Right Sidebar: AI Assistant -->
      <ChatPanel />
    </main>
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import AppHeader from '../components/AppHeader.vue'
import SessionsSidebar from '../components/SessionsSidebar.vue'
import WorkspaceViewer from '../components/WorkspaceViewer.vue'
import ChatPanel from '../components/ChatPanel.vue'

// Initialize stores on app mount
onMounted(() => {
  // Any global initialization can go here
})
</script>
