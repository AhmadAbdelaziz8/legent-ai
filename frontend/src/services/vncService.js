/**
 * VNC Service for managing VNC connections and interactions
 */

import { api } from './api.js'

class VNCService {
  constructor() {
    this.isConnected = false
    this.isConnecting = false
    this.error = null
    this.vncHost = 'localhost'
    this.vncPort = 8080 // Docker maps 6080 to 8080
    this.listeners = new Map()
  }

  /**
   * Connect to VNC server
   * @param {string} host - VNC server host
   * @param {number} port - VNC server port
   * @returns {Promise<boolean>} - Connection success
   */
  async connect(host = this.vncHost, port = this.vncPort) {
    if (this.isConnecting || this.isConnected) {
      return this.isConnected
    }

    this.isConnecting = true
    this.error = null
    this.vncHost = host
    this.vncPort = port

    try {
      // Check VNC status via API
      const status = await api.vnc.getStatus()

      if (status.is_running) {
        this.isConnected = true
        this.isConnecting = false
        this.emit('connected', { host, port, status })
        return true
      } else {
        // Try to start VNC services
        await api.vnc.start()

        // Wait a moment and check again
        await new Promise((resolve) => setTimeout(resolve, 3000))
        const newStatus = await api.vnc.getStatus()

        if (newStatus.is_running) {
          this.isConnected = true
          this.isConnecting = false
          this.emit('connected', { host, port, status: newStatus })
          return true
        } else {
          throw new Error(status.error || 'VNC services failed to start')
        }
      }
    } catch (err) {
      this.error = `Failed to connect to VNC server at ${host}:${port}: ${err.message}`
      this.isConnecting = false
      this.emit('error', this.error)
      return false
    }
  }

  /**
   * Disconnect from VNC server
   */
  async disconnect() {
    if (!this.isConnected) return

    try {
      // Optionally stop VNC services
      // await api.vnc.stop()
    } catch (err) {
      console.warn('Error stopping VNC services:', err)
    }

    this.isConnected = false
    this.isConnecting = false
    this.emit('disconnected')
  }

  /**
   * Get VNC URL for iframe embedding
   * @param {Object} options - VNC connection options
   * @returns {string} - VNC URL
   */
  getVNCUrl(options = {}) {
    const {
      autoconnect = true,
      resize = 'scale',
      quality = 6,
      compression = 6,
      show_dot = false,
      view_only = false,
    } = options

    const params = new URLSearchParams({
      autoconnect: autoconnect.toString(),
      resize,
      quality: quality.toString(),
      compression: compression.toString(),
      show_dot: show_dot.toString(),
      view_only: view_only.toString(),
    })

    return `http://${this.vncHost}:${this.vncPort}/vnc.html?${params.toString()}`
  }

  /**
   * Send mouse event to VNC
   * @param {Object} event - Mouse event data
   */
  sendMouseEvent(event) {
    if (!this.isConnected) return

    // This would typically be handled by the VNC client
    console.log('Mouse event:', event)
  }

  /**
   * Send keyboard event to VNC
   * @param {Object} event - Keyboard event data
   */
  sendKeyboardEvent(event) {
    if (!this.isConnected) return

    // This would typically be handled by the VNC client
    console.log('Keyboard event:', event)
  }

  /**
   * Take screenshot of VNC session
   * @returns {Promise<string>} - Base64 encoded screenshot
   */
  async takeScreenshot() {
    if (!this.isConnected) {
      throw new Error('Not connected to VNC')
    }

    try {
      const result = await api.vnc.getScreenshot()
      return result.screenshot
    } catch (err) {
      console.error('Failed to take VNC screenshot:', err)
      throw err
    }
  }

  /**
   * Add event listener
   * @param {string} event - Event name
   * @param {Function} callback - Callback function
   */
  on(event, callback) {
    if (!this.listeners.has(event)) {
      this.listeners.set(event, [])
    }
    this.listeners.get(event).push(callback)
  }

  /**
   * Remove event listener
   * @param {string} event - Event name
   * @param {Function} callback - Callback function
   */
  off(event, callback) {
    if (!this.listeners.has(event)) return

    const callbacks = this.listeners.get(event)
    const index = callbacks.indexOf(callback)
    if (index > -1) {
      callbacks.splice(index, 1)
    }
  }

  /**
   * Emit event to listeners
   * @param {string} event - Event name
   * @param {*} data - Event data
   */
  emit(event, data) {
    if (!this.listeners.has(event)) return

    this.listeners.get(event).forEach((callback) => {
      try {
        callback(data)
      } catch (err) {
        console.error('Error in VNC event listener:', err)
      }
    })
  }

  /**
   * Get connection status
   * @returns {Object} - Status information
   */
  getStatus() {
    return {
      isConnected: this.isConnected,
      isConnecting: this.isConnecting,
      error: this.error,
      host: this.vncHost,
      port: this.vncPort,
    }
  }
}

// Create singleton instance
const vncService = new VNCService()

export default vncService
export { VNCService }
