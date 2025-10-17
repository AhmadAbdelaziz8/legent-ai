<template>
  <span
    :class="['inline-flex items-center px-2 py-1 rounded-full text-xs font-medium', statusClasses]"
  >
    {{ statusText }}
  </span>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  status: {
    type: String,
    required: true,
  },
})

const statusClasses = computed(() => {
  switch (props.status) {
    case 'completed':
      return 'bg-green-100 text-green-800'
    case 'error':
      return 'bg-red-100 text-red-800'
    case 'processing':
      return 'bg-yellow-100 text-yellow-800'
    case 'pending':
      return 'bg-gray-100 text-gray-800'
    default:
      return 'bg-gray-100 text-gray-800'
  }
})

const statusText = computed(() => {
  switch (props.status) {
    case 'completed':
      return 'Completed'
    case 'error':
      return 'Error'
    case 'processing':
      return 'Processing'
    case 'pending':
      return 'Pending'
    default:
      return 'Unknown'
  }
})
</script>
