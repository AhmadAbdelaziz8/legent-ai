# VNC Integration for Legent AI

This document describes the VNC integration that allows the LLM to take screenshots and interact with a desktop environment.

## Overview

The system now supports:
- **VNC Server**: x11vnc running on display :1 (port 5900)
- **Web Interface**: noVNC accessible at http://localhost:6080
- **Screenshot Capture**: Automatic screenshots during computer use
- **Visual Feedback**: LLM can see and interact with the desktop

## Architecture

### Backend Components

1. **VNC Routes** (`backend/app/routes/vnc.py`)
   - `/vnc/status` - Check VNC service status
   - `/vnc/start` - Start VNC services
   - `/vnc/screenshot` - Take a screenshot
   - `/vnc/interact` - Send interaction commands

2. **Agent Service** (`backend/app/service/agent_service.py`)
   - Automatically starts VNC services when needed
   - Integrates with computer use tools
   - Handles screenshot streaming

3. **Database Schema**
   - Added `base64_image` column to messages table
   - Stores screenshots as base64 encoded text

### Frontend Components

1. **ChatPanel.vue**
   - Displays screenshots in chat messages
   - Handles screenshot modal
   - Shows visual feedback from LLM actions

2. **VNCViewer.vue**
   - VNC connection interface
   - Screenshot capture functionality
   - Desktop interaction controls

3. **VNC Service** (`frontend/src/services/vncService.js`)
   - VNC connection management
   - Screenshot API integration
   - Event handling

## How It Works

### 1. LLM Computer Use Flow

```
User sends message → Agent starts VNC → LLM takes screenshot → 
LLM analyzes image → LLM plans action → LLM executes action → 
LLM takes follow-up screenshot → Process repeats
```

### 2. Screenshot Integration

The LLM automatically:
- Takes screenshots before and after each action
- Analyzes the visual state of the desktop
- Plans next actions based on what it sees
- Executes computer interactions (clicks, typing, etc.)
- Verifies results with follow-up screenshots

### 3. Message Structure

Messages now support screenshots:

```json
{
  "id": 1,
  "session_id": 1,
  "role": "assistant",
  "content": {
    "text": "I can see the desktop with Firefox open",
    "base64_image": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAA..."
  },
  "created_at": "2024-01-01T12:00:00Z"
}
```

## Setup Instructions

### 1. Database Migration

Run the database migration to add screenshot support:

```sql
-- Add base64_image column to messages table
ALTER TABLE messages ADD COLUMN base64_image TEXT;
```

### 2. Backend Setup

The backend automatically starts VNC services when needed. Ensure these dependencies are installed:

```bash
# System dependencies (already in Dockerfile)
xvfb x11vnc xterm xdotool scrot imagemagick
```

### 3. Frontend Setup

The frontend components are already integrated:
- `ChatPanel.vue` displays screenshots
- `VNCViewer.vue` provides VNC interface
- `vncService.js` handles VNC connections

### 4. Environment Variables

Ensure these are set in your environment:

```bash
DISPLAY=:1
WIDTH=1024
HEIGHT=768
```

## Usage

### 1. Starting a Computer Use Session

```javascript
// The agent automatically starts VNC when needed
const response = await fetch('/sessions', {
  method: 'POST',
  body: JSON.stringify({
    initial_prompt: "Open Firefox and navigate to google.com",
    provider: "anthropic"
  })
})
```

### 2. Taking Screenshots

```javascript
// Take a screenshot via API
const screenshot = await fetch('/vnc/screenshot')
const data = await screenshot.json()
console.log('Screenshot:', data.screenshot)
```

### 3. VNC Interactions

```javascript
// Click at coordinates
await fetch('/vnc/interact', {
  method: 'POST',
  body: JSON.stringify({
    action: 'click',
    x: 100,
    y: 100,
    button: 1
  })
})

// Type text
await fetch('/vnc/interact', {
  method: 'POST',
  body: JSON.stringify({
    action: 'type',
    text: 'Hello World'
  })
})
```

## Testing

Run the integration test:

```bash
python test_vnc_integration.py
```

This will test:
- VNC service endpoints
- Screenshot functionality
- Agent integration
- Frontend connectivity

## Troubleshooting

### VNC Not Starting

1. Check if x11vnc is installed
2. Verify display :1 is available
3. Check port 5900 is not in use

### Screenshots Not Working

1. Verify scrot or gnome-screenshot is installed
2. Check DISPLAY environment variable
3. Ensure X11 forwarding is working

### Frontend Not Connecting

1. Check VNC service is running
2. Verify noVNC is accessible at port 6080
3. Check browser console for errors

## Security Considerations

- VNC is running without password (development only)
- Screenshots contain sensitive information
- Consider authentication for production use
- Implement rate limiting for screenshot requests

## Performance Notes

- Screenshots are base64 encoded (larger than binary)
- Consider compression for large images
- Implement caching for repeated screenshots
- Monitor memory usage with many screenshots

## Future Enhancements

1. **Screenshot Compression**: Reduce image size
2. **Video Recording**: Record desktop sessions
3. **Multi-User Support**: Multiple VNC sessions
4. **Authentication**: Secure VNC access
5. **Mobile Support**: Touch interactions


