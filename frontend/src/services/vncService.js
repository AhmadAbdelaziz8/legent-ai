import { vncApi } from './api.js'

class VNCService {
  constructor() {
    this.connected = false
    this.connecting = false
    this.error = null
    this.listeners = new Map()
  }

  // Event handling
  on(event, callback) {
    if (!this.listeners.has(event)) {
      this.listeners.set(event, [])
    }
    this.listeners.get(event).push(callback)
  }

  off(event, callback) {
    if (this.listeners.has(event)) {
      const callbacks = this.listeners.get(event)
      const index = callbacks.indexOf(callback)
      if (index > -1) {
        callbacks.splice(index, 1)
      }
    }
  }

  emit(event, data) {
    if (this.listeners.has(event)) {
      this.listeners.get(event).forEach((callback) => callback(data))
    }
  }

  async connect(host = 'localhost', port = 8080) {
    try {
      this.connecting = true
      this.error = null
      this.emit('connecting')

      // Check VNC status
      const status = await vncApi.getStatus()
      if (!status.running) {
        // Start VNC if not running
        await vncApi.start()
      }

      this.connected = true
      this.connecting = false
      this.emit('connected')
      return true
    } catch (err) {
      this.error = err.message
      this.connected = false
      this.connecting = false
      this.emit('error', err)
      return false
    }
  }

  disconnect() {
    this.connected = false
    this.error = null
    this.emit('disconnected')
  }

  getVNCUrl(options = {}) {
    const { host = 'localhost', port = 8080, path = '' } = options
    return `http://${host}:${port}${path}`
  }

  async takeScreenshot() {
    if (!this.connected) {
      throw new Error('VNC not connected')
    }

    try {
      const response = await vncApi.getScreenshot()
      return response.screenshot
    } catch (err) {
      this.error = err.message
      this.emit('error', err)
      throw err
    }
  }

  async interact(action, data = {}) {
    if (!this.connected) {
      throw new Error('VNC not connected')
    }

    try {
      const response = await vncApi.interact(action, data)
      return response
    } catch (err) {
      this.error = err.message
      this.emit('error', err)
      throw err
    }
  }

  // Mouse interactions
  async click(x, y, button = 1) {
    return this.interact('click', { x, y, button })
  }

  async rightClick(x, y) {
    return this.click(x, y, 3)
  }

  async doubleClick(x, y) {
    return this.interact('click', { x, y, button: '--repeat 2 --delay 10 1' })
  }

  // Keyboard interactions
  async type(text) {
    return this.interact('type', { text })
  }

  async key(key) {
    return this.interact('key', { key })
  }

  // Utility methods
  getStatus() {
    return {
      connected: this.connected,
      connecting: this.connecting,
      error: this.error,
    }
  }
}

// Export singleton instance
export const vncService = new VNCService()
export default vncService
