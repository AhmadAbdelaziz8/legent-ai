import { ref, computed } from 'vue'
import { defineStore } from 'pinia'

// export const useCounterStore = defineStore('counter', () => {
//   const count = ref(0)
//   const doubleCount = computed(() => count.value * 2)
//   function increment() {
//     count.value++
//   }

//   return { count, doubleCount, increment }
// })

export const useSessions = defineStore('sessions', () => {
  const sessions = ref([])

  const fetchSessions = async () => {
    const response = await fetch('/api/sessions')
    sessions.value = await response.json()
  }

  const createSession = async (session) => {
    const response = await fetch('/api/sessions', {
      method: 'POST',
      body: JSON.stringify(session),
    })
    sessions.value = await response.json()
  }

  return { sessions, fetchSessions, createSession }
})
