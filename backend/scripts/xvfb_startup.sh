#!/bin/bash
set -e

DPI=96
RES_AND_DEPTH=${WIDTH}x${HEIGHT}x24

# Function to check if Xvfb is actually responding
is_xvfb_responding() {
    xdpyinfo >/dev/null 2>&1
    return $?
}

# Function to clean up stale Xvfb process
cleanup_stale_xvfb() {
    local lock_file="/tmp/.X${DISPLAY_NUM}-lock"
    local unix_socket="/tmp/.X11-unix/X${DISPLAY_NUM}"
    
    # Check if display responds
    if ! is_xvfb_responding; then
        echo "Xvfb on display ${DISPLAY} is not responding, cleaning up..."
        
        # Kill any stale Xvfb processes on this display
        pkill -9 "Xvfb.*${DISPLAY}" || true
        
        # Remove stale lock file
        if [ -e "$lock_file" ]; then
            rm -f "$lock_file"
            echo "Removed stale lock file: $lock_file"
        fi
        
        # Remove stale socket
        if [ -e "$unix_socket" ]; then
            rm -f "$unix_socket"
            echo "Removed stale socket: $unix_socket"
        fi
        
        return 1
    fi
    return 0
}

# Function to check if Xvfb is ready
wait_for_xvfb() {
    local timeout=10
    local start_time=$(date +%s)
    while ! xdpyinfo >/dev/null 2>&1; do
        if [ $(($(date +%s) - start_time)) -gt $timeout ]; then
            echo "Xvfb failed to start within $timeout seconds" >&2
            return 1
        fi
        sleep 0.1
    done
    return 0
}

# Clean up stale Xvfb if needed
cleanup_stale_xvfb || true

# Start Xvfb
Xvfb $DISPLAY -ac -screen 0 $RES_AND_DEPTH -retro -dpi $DPI -nolisten tcp -nolisten unix &
XVFB_PID=$!

# Wait for Xvfb to start
if wait_for_xvfb; then
    echo "Xvfb started successfully on display ${DISPLAY}"
    echo "Xvfb PID: $XVFB_PID"
else
    echo "Xvfb failed to start"
    kill $XVFB_PID 2>/dev/null || true
    exit 1
fi