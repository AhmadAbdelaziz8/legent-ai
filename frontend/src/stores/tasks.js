import { ref, computed } from 'vue'
import { defineStore } from 'pinia'
import { apiService } from '../services/api.js'

export const useTasksStore = defineStore('tasks', () => {
  // State
  const tasks = ref([])
  const currentTask = ref(null)
  const loading = ref(false)
  const error = ref(null)

  // Getters
  const completedTasks = computed(() => tasks.value.filter((task) => task.status === 'completed'))

  const activeTasks = computed(() => tasks.value.filter((task) => task.status === 'active'))

  const taskHistory = computed(() =>
    tasks.value.filter((task) => task.status === 'completed' || task.status === 'failed'),
  )

  // Actions
  const fetchTasks = async () => {
    loading.value = true
    error.value = null
    try {
      tasks.value = await apiService.getTasks()
    } catch (err) {
      error.value = err.message
      console.error('Failed to fetch tasks:', err)
    } finally {
      loading.value = false
    }
  }

  const createTask = async (taskData) => {
    loading.value = true
    error.value = null
    try {
      const newTask = await apiService.createTask(taskData)
      tasks.value.push(newTask)
      return newTask
    } catch (err) {
      error.value = err.message
      console.error('Failed to create task:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  const updateTask = async (taskId, taskData) => {
    loading.value = true
    error.value = null
    try {
      const updatedTask = await apiService.updateTask(taskId, taskData)
      const index = tasks.value.findIndex((task) => task.id === taskId)
      if (index !== -1) {
        tasks.value[index] = updatedTask
      }
      return updatedTask
    } catch (err) {
      error.value = err.message
      console.error('Failed to update task:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  const deleteTask = async (taskId) => {
    loading.value = true
    error.value = null
    try {
      await apiService.deleteTask(taskId)
      tasks.value = tasks.value.filter((task) => task.id !== taskId)
    } catch (err) {
      error.value = err.message
      console.error('Failed to delete task:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  const executeTask = async (taskId) => {
    loading.value = true
    error.value = null
    try {
      const result = await apiService.executeTask(taskId)
      // Update task status
      const task = tasks.value.find((t) => t.id === taskId)
      if (task) {
        task.status = 'executing'
      }
      return result
    } catch (err) {
      error.value = err.message
      console.error('Failed to execute task:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  const setCurrentTask = (task) => {
    currentTask.value = task
  }

  const clearError = () => {
    error.value = null
  }

  return {
    // State
    tasks,
    currentTask,
    loading,
    error,
    // Getters
    completedTasks,
    activeTasks,
    taskHistory,
    // Actions
    fetchTasks,
    createTask,
    updateTask,
    deleteTask,
    executeTask,
    setCurrentTask,
    clearError,
  }
})
