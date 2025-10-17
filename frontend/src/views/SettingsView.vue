<template>
  <div
    class="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 dark:from-slate-900 dark:to-slate-800"
  >
    <!-- Header -->
    <header
      class="bg-gradient-to-r from-slate-800 to-slate-900 text-white shadow-xl border-b border-slate-700"
    >
      <div class="px-6 py-4">
        <div class="flex items-center justify-between">
          <div class="flex items-center space-x-4">
            <router-link to="/" class="flex items-center space-x-3">
              <div
                class="w-10 h-10 bg-gradient-to-br from-green-500 to-green-600 rounded-lg flex items-center justify-center shadow-lg"
              >
                <svg
                  class="w-6 h-6 text-white"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="2"
                    d="M13 10V3L4 14h7v7l9-11h-7z"
                  ></path>
                </svg>
              </div>
              <div>
                <h1 class="text-xl font-bold">Legent AI</h1>
                <span class="text-sm text-slate-300">Settings</span>
              </div>
            </router-link>
          </div>
          <div class="flex items-center space-x-4">
            <router-link to="/dashboard" class="text-slate-300 hover:text-white transition-colors">
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2-2v10a2 2 0 002 2z"
                ></path>
              </svg>
            </router-link>
          </div>
        </div>
      </div>
    </header>

    <!-- Main Content -->
    <main class="container mx-auto px-6 py-8">
      <div class="max-w-4xl mx-auto">
        <h2 class="text-2xl font-bold text-slate-900 dark:text-slate-100 mb-8">Settings</h2>

        <div class="grid gap-6">
          <!-- General Settings -->
          <div class="bg-white dark:bg-slate-800 rounded-lg shadow-lg p-6">
            <h3 class="text-lg font-semibold text-slate-900 dark:text-slate-100 mb-4">General</h3>
            <div class="space-y-4">
              <div>
                <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2"
                  >Theme</label
                >
                <select
                  class="w-full px-3 py-2 border border-slate-300 dark:border-slate-600 rounded-lg bg-white dark:bg-slate-700 text-slate-900 dark:text-slate-100"
                >
                  <option>Light</option>
                  <option>Dark</option>
                  <option>System</option>
                </select>
              </div>
              <div>
                <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2"
                  >Language</label
                >
                <select
                  class="w-full px-3 py-2 border border-slate-300 dark:border-slate-600 rounded-lg bg-white dark:bg-slate-700 text-slate-900 dark:text-slate-100"
                >
                  <option>English</option>
                  <option>Spanish</option>
                  <option>French</option>
                </select>
              </div>
            </div>
          </div>

          <!-- AI Settings -->
          <div class="bg-white dark:bg-slate-800 rounded-lg shadow-lg p-6">
            <h3 class="text-lg font-semibold text-slate-900 dark:text-slate-100 mb-4">
              AI Assistant
            </h3>
            <div class="space-y-4">
              <div>
                <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2"
                  >Default Model</label
                >
                <select
                  class="w-full px-3 py-2 border border-slate-300 dark:border-slate-600 rounded-lg bg-white dark:bg-slate-700 text-slate-900 dark:text-slate-100"
                >
                  <option>GPT-4</option>
                  <option>GPT-3.5</option>
                  <option>Claude</option>
                </select>
              </div>
              <div>
                <label class="flex items-center">
                  <input
                    type="checkbox"
                    class="rounded border-slate-300 text-green-600 focus:ring-green-500"
                  />
                  <span class="ml-2 text-sm text-slate-700 dark:text-slate-300"
                    >Enable voice commands</span
                  >
                </label>
              </div>
            </div>
          </div>

          <!-- Workspace Settings -->
          <div class="bg-white dark:bg-slate-800 rounded-lg shadow-lg p-6">
            <h3 class="text-lg font-semibold text-slate-900 dark:text-slate-100 mb-4">Workspace</h3>
            <div class="space-y-4">
              <div>
                <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2"
                  >VNC Server</label
                >
                <input
                  type="text"
                  placeholder="localhost:8080"
                  class="w-full px-3 py-2 border border-slate-300 dark:border-slate-600 rounded-lg bg-white dark:bg-slate-700 text-slate-900 dark:text-slate-100"
                />
              </div>
              <div>
                <label class="flex items-center">
                  <input
                    type="checkbox"
                    class="rounded border-slate-300 text-green-600 focus:ring-green-500"
                  />
                  <span class="ml-2 text-sm text-slate-700 dark:text-slate-300"
                    >Auto-connect to VNC</span
                  >
                </label>
              </div>
            </div>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup>
// SettingsView - Application settings
</script>
