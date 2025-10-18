<template>
  <div class="min-h-screen bg-white dark:bg-slate-900">
    <!-- Header -->
    <header class="bg-white text-slate-900 shadow-xl border-b border-slate-200">
      <div class="px-6 py-4">
        <div class="flex items-center justify-between">
          <div class="flex items-center gap-4">
            <router-link to="/" class="flex items-center gap-3">
              <div
                class="w-10 h-10 bg-slate-600 rounded-lg flex items-center justify-center shadow-lg"
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
                <h1 class="text-xl font-bold text-slate-900">Legent AI</h1>
                <span class="text-sm text-slate-600">Profile</span>
              </div>
            </router-link>
          </div>
          <div class="flex items-center gap-4">
            <router-link
              to="/dashboard"
              class="text-slate-600 hover:text-slate-900 transition-colors"
            >
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
        <h2 class="text-2xl font-bold text-slate-900 dark:text-slate-100 mb-8">User Profile</h2>

        <div class="grid gap-6">
          <!-- Profile Information -->
          <div class="bg-white dark:bg-slate-800 rounded-lg shadow-lg p-6">
            <h3 class="text-lg font-semibold text-slate-900 dark:text-slate-100 mb-4">
              Profile Information
            </h3>
            <div class="flex items-center gap-6 mb-6">
              <div class="w-20 h-20 bg-slate-600 rounded-full flex items-center justify-center">
                <svg class="w-10 h-10 text-white" fill="currentColor" viewBox="0 0 20 20">
                  <path
                    fill-rule="evenodd"
                    d="M10 9a3 3 0 100-6 3 3 0 000 6zm-7 9a7 7 0 1114 0H3z"
                    clip-rule="evenodd"
                  ></path>
                </svg>
              </div>
              <div>
                <h4 class="text-xl font-semibold text-slate-900 dark:text-slate-100">John Doe</h4>
                <p class="text-slate-600 dark:text-slate-400">john.doe@example.com</p>
                <p class="text-sm text-slate-500 dark:text-slate-500">Member since January 2024</p>
              </div>
            </div>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2"
                  >First Name</label
                >
                <input
                  type="text"
                  value="John"
                  class="w-full px-3 py-2 border border-slate-300 dark:border-slate-600 rounded-lg bg-white dark:bg-slate-700 text-slate-900 dark:text-slate-100"
                />
              </div>
              <div>
                <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2"
                  >Last Name</label
                >
                <input
                  type="text"
                  value="Doe"
                  class="w-full px-3 py-2 border border-slate-300 dark:border-slate-600 rounded-lg bg-white dark:bg-slate-700 text-slate-900 dark:text-slate-100"
                />
              </div>
              <div>
                <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2"
                  >Email</label
                >
                <input
                  type="email"
                  value="john.doe@example.com"
                  class="w-full px-3 py-2 border border-slate-300 dark:border-slate-600 rounded-lg bg-white dark:bg-slate-700 text-slate-900 dark:text-slate-100"
                />
              </div>
              <div>
                <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2"
                  >Phone</label
                >
                <input
                  type="tel"
                  value="+1 (555) 123-4567"
                  class="w-full px-3 py-2 border border-slate-300 dark:border-slate-600 rounded-lg bg-white dark:bg-slate-700 text-slate-900 dark:text-slate-100"
                />
              </div>
            </div>
          </div>

          <!-- Activity Stats -->
          <div class="bg-white dark:bg-slate-800 rounded-lg shadow-lg p-6">
            <h3 class="text-lg font-semibold text-slate-900 dark:text-slate-100 mb-4">
              Activity Statistics
            </h3>
            <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div class="text-center p-4 bg-green-50 dark:bg-green-900/20 rounded-lg">
                <div class="text-2xl font-bold text-green-600 dark:text-green-400">127</div>
                <div class="text-sm text-slate-600 dark:text-slate-400">Sessions Created</div>
              </div>
              <div class="text-center p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
                <div class="text-2xl font-bold text-blue-600 dark:text-blue-400">2,847</div>
                <div class="text-sm text-slate-600 dark:text-slate-400">Messages Exchanged</div>
              </div>
              <div class="text-center p-4 bg-purple-50 dark:bg-purple-900/20 rounded-lg">
                <div class="text-2xl font-bold text-purple-600 dark:text-purple-400">45h</div>
                <div class="text-sm text-slate-600 dark:text-slate-400">Total Usage Time</div>
              </div>
            </div>
          </div>

          <!-- Recent Sessions -->
          <div class="bg-white dark:bg-slate-800 rounded-lg shadow-lg p-6">
            <h3 class="text-lg font-semibold text-slate-900 dark:text-slate-100 mb-4">
              Recent Sessions
            </h3>
            <div class="flex flex-col gap-3">
              <div
                class="flex items-center justify-between p-3 bg-slate-50 dark:bg-slate-700 rounded-lg"
              >
                <div>
                  <p class="font-medium text-slate-900 dark:text-slate-100">
                    Data Analysis Project
                  </p>
                  <p class="text-sm text-slate-500 dark:text-slate-400">2 hours ago</p>
                </div>
                <span
                  class="px-2 py-1 bg-green-100 text-green-800 dark:bg-green-900/20 dark:text-green-400 rounded text-xs"
                  >Completed</span
                >
              </div>
              <div
                class="flex items-center justify-between p-3 bg-slate-50 dark:bg-slate-700 rounded-lg"
              >
                <div>
                  <p class="font-medium text-slate-900 dark:text-slate-100">Code Review Session</p>
                  <p class="text-sm text-slate-500 dark:text-slate-400">1 day ago</p>
                </div>
                <span
                  class="px-2 py-1 bg-blue-100 text-blue-800 dark:bg-blue-900/20 dark:text-blue-400 rounded text-xs"
                  >Active</span
                >
              </div>
              <div
                class="flex items-center justify-between p-3 bg-slate-50 dark:bg-slate-700 rounded-lg"
              >
                <div>
                  <p class="font-medium text-slate-900 dark:text-slate-100">Documentation Task</p>
                  <p class="text-sm text-slate-500 dark:text-slate-400">3 days ago</p>
                </div>
                <span
                  class="px-2 py-1 bg-slate-100 text-slate-800 dark:bg-slate-600 dark:text-slate-300 rounded text-xs"
                  >Pending</span
                >
              </div>
            </div>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup>
// ProfileView - User profile and statistics
</script>
