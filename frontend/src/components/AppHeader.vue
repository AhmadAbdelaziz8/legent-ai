<template>
  <header class="bg-gradient-to-r from-slate-800 to-slate-900 text-white shadow-xl border-b border-slate-700">
    <div class="px-6 py-4">
      <div class="flex items-center justify-between">
        <div class="flex items-center space-x-4">
          <!-- Logo and branding -->
          <div class="flex items-center space-x-3">
            <div class="w-10 h-10 bg-gradient-to-br from-blue-500 to-purple-600 rounded-lg flex items-center justify-center shadow-lg">
              <svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"></path>
              </svg>
            </div>
            <div>
              <h1 class="text-xl font-bold bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent">
                Legent AI
              </h1>
              <span class="text-sm text-slate-300">AI Assistant Platform</span>
            </div>
          </div>
        </div>

        <div class="flex items-center space-x-6">
          <!-- Status indicator with animation -->
          <div class="flex items-center space-x-3">
            <div class="relative">
              <div class="w-3 h-3 bg-green-400 rounded-full animate-pulse"></div>
              <div class="absolute inset-0 w-3 h-3 bg-green-400 rounded-full animate-ping opacity-75"></div>
            </div>
            <span class="text-sm font-medium text-slate-200">Online</span>
          </div>

          <!-- User profile -->
          <div class="flex items-center space-x-3">
            <div class="w-9 h-9 bg-gradient-to-br from-slate-600 to-slate-700 rounded-full flex items-center justify-center shadow-lg ring-2 ring-slate-600">
              <svg class="w-5 h-5 text-slate-200" fill="currentColor" viewBox="0 0 20 20">
                <path fill-rule="evenodd" d="M10 9a3 3 0 100-6 3 3 0 000 6zm-7 9a7 7 0 1114 0H3z" clip-rule="evenodd"></path>
              </svg>
            </div>
            <div class="hidden sm:block">
              <span class="text-sm font-medium text-slate-200">User</span>
              <div class="text-xs text-slate-400">Active</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </header>
</template>

<script setup>
// AppHeader component - simple header with app branding
</script>
