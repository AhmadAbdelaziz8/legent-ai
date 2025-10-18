<template>
  <div class="h-screen w-full bg-white flex items-center justify-center">
    <div class="text-center">
      <div class="mb-8">
        <div
          class="w-20 h-20 bg-slate-600 rounded-2xl flex items-center justify-center mx-auto mb-6 shadow-xl"
        >
          <svg class="w-10 h-10 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M13 10V3L4 14h7v7l9-11h-7z"
            ></path>
          </svg>
        </div>
        <h1 class="text-4xl font-bold text-slate-900 mb-2">Legent AI</h1>
        <p class="text-lg text-slate-600">AI Assistant Platform</p>
      </div>

      <div class="flex flex-col gap-4">
        <router-link
          to="/dashboard"
          class="inline-flex items-center px-6 py-3 bg-slate-600 hover:bg-slate-700 text-white font-semibold rounded-lg transition-all duration-300 shadow-lg hover:shadow-xl transform hover:scale-105"
        >
          <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2-2v10a2 2 0 002 2z"
            ></path>
          </svg>
          Go to Dashboard
        </router-link>

        <div class="text-sm text-slate-500">
          <p>Welcome to Legent AI - Your intelligent workspace assistant</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
// HomeView - Landing page
</script>
