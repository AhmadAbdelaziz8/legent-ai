<template>
  <header class="bg-gray-800 text-white shadow-lg">
    <div class="px-6 py-4">
      <div class="flex items-center justify-between">
        <div class="flex items-center space-x-4">
          <h1 class="text-xl font-bold">Legent AI</h1>
          <span class="text-sm text-gray-300">AI Assistant</span>
        </div>

        <div class="flex items-center space-x-4">
          <!-- Status indicator -->
          <div class="flex items-center space-x-2">
            <div class="w-2 h-2 bg-green-400 rounded-full"></div>
            <span class="text-sm text-gray-300">Online</span>
          </div>

          <!-- User info placeholder -->
          <div class="flex items-center space-x-2">
            <div class="w-8 h-8 bg-gray-600 rounded-full flex items-center justify-center">
              <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                <path
                  fill-rule="evenodd"
                  d="M10 9a3 3 0 100-6 3 3 0 000 6zm-7 9a7 7 0 1114 0H3z"
                  clip-rule="evenodd"
                ></path>
              </svg>
            </div>
            <span class="text-sm text-gray-300">User</span>
          </div>
        </div>
      </div>
    </div>
  </header>
</template>

<script setup>
// AppHeader component - simple header with app branding
</script>
