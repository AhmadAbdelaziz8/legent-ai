"""
VNC management routes for model interaction
"""

import asyncio
import subprocess
import psutil
from datetime import datetime
from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/vnc", tags=["vnc"])


class VNCStatus(BaseModel):
    is_running: bool
    port: int
    pid: Optional[int] = None
    host: str = "localhost"
    url: str
    error: Optional[str] = None


class VNCConfig(BaseModel):
    host: str = "localhost"
    port: int = 6080
    vnc_port: int = 5900
    width: int = 1024
    height: int = 768
    password: Optional[str] = None


class VNCSession(BaseModel):
    session_id: str
    status: str
    config: VNCConfig
    created_at: str
    last_activity: Optional[str] = None


# Global VNC session storage (in production, use a database)
vnc_sessions: Dict[str, VNCSession] = {}


@router.get("/status", response_model=VNCStatus)
async def get_vnc_status():
    """Get current VNC server status"""
    try:
        # Check if noVNC is running on port 6080
        novnc_running = False
        novnc_pid = None

        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                if proc.info['cmdline'] and any('novnc' in str(cmd).lower() for cmd in proc.info['cmdline']):
                    novnc_running = True
                    novnc_pid = proc.info['pid']
                    break
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

        # Check if x11vnc is running on port 5900
        x11vnc_running = False
        x11vnc_pid = None

        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                if proc.info['cmdline'] and any('x11vnc' in str(cmd).lower() for cmd in proc.info['cmdline']):
                    x11vnc_running = True
                    x11vnc_pid = proc.info['pid']
                    break
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

        is_running = novnc_running and x11vnc_running
        url = f"http://localhost:6080/vnc.html?autoconnect=true&resize=scale&quality=6"

        return VNCStatus(
            is_running=is_running,
            port=8080,  # Docker maps 6080 to 8080
            pid=novnc_pid,
            host="localhost",
            url=url.replace(":6080", ":8080"),  # Use mapped port
            error=None if is_running else "VNC services not running"
        )

    except Exception as e:
        logger.error(f"Error checking VNC status: {e}")
        return VNCStatus(
            is_running=False,
            port=8080,  # Docker maps 6080 to 8080
            pid=None,
            host="localhost",
            url="",
            error=str(e)
        )


@router.post("/start")
async def start_vnc(background_tasks: BackgroundTasks):
    """Start VNC services"""
    try:
        # Check if already running
        status = await get_vnc_status()
        if status.is_running:
            return {"message": "VNC services already running", "status": status}

        # Start VNC services in background
        background_tasks.add_task(start_vnc_services)

        return {"message": "Starting VNC services...", "status": "starting"}

    except Exception as e:
        logger.error(f"Error starting VNC: {e}")
        raise HTTPException(
            status_code=500, detail=f"Failed to start VNC: {str(e)}")


@router.post("/stop")
async def stop_vnc():
    """Stop VNC services"""
    try:
        stopped_services = []

        # Stop noVNC
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                if proc.info['cmdline'] and any('novnc' in str(cmd).lower() for cmd in proc.info['cmdline']):
                    proc.terminate()
                    stopped_services.append("noVNC")
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

        # Stop x11vnc
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                if proc.info['cmdline'] and any('x11vnc' in str(cmd).lower() for cmd in proc.info['cmdline']):
                    proc.terminate()
                    stopped_services.append("x11vnc")
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

        return {"message": f"Stopped VNC services: {', '.join(stopped_services)}"}

    except Exception as e:
        logger.error(f"Error stopping VNC: {e}")
        raise HTTPException(
            status_code=500, detail=f"Failed to stop VNC: {str(e)}")


@router.post("/restart")
async def restart_vnc(background_tasks: BackgroundTasks):
    """Restart VNC services"""
    try:
        # Stop first
        await stop_vnc()

        # Wait a moment
        await asyncio.sleep(2)

        # Start again
        background_tasks.add_task(start_vnc_services)

        return {"message": "Restarting VNC services..."}

    except Exception as e:
        logger.error(f"Error restarting VNC: {e}")
        raise HTTPException(
            status_code=500, detail=f"Failed to restart VNC: {str(e)}")


@router.get("/sessions")
async def get_vnc_sessions():
    """Get all VNC sessions"""
    return {"sessions": list(vnc_sessions.values())}


@router.post("/sessions")
async def create_vnc_session(config: VNCConfig):
    """Create a new VNC session"""
    try:
        import uuid
        from datetime import datetime

        session_id = str(uuid.uuid4())
        session = VNCSession(
            session_id=session_id,
            status="created",
            config=config,
            created_at=datetime.now().isoformat()
        )

        vnc_sessions[session_id] = session

        return {"session": session, "message": "VNC session created"}

    except Exception as e:
        logger.error(f"Error creating VNC session: {e}")
        raise HTTPException(
            status_code=500, detail=f"Failed to create VNC session: {str(e)}")


@router.delete("/sessions/{session_id}")
async def delete_vnc_session(session_id: str):
    """Delete a VNC session"""
    try:
        if session_id not in vnc_sessions:
            raise HTTPException(
                status_code=404, detail="VNC session not found")

        del vnc_sessions[session_id]
        return {"message": "VNC session deleted"}

    except Exception as e:
        logger.error(f"Error deleting VNC session: {e}")
        raise HTTPException(
            status_code=500, detail=f"Failed to delete VNC session: {str(e)}")


async def start_vnc_services():
    """Start VNC services in background"""
    try:
        # Start x11vnc
        subprocess.Popen([
            "x11vnc",
            "-display", ":1",
            "-forever",
            "-shared",
            "-wait", "50",
            "-rfbport", "5900",
            "-nopw"
        ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        # Wait a moment for x11vnc to start
        await asyncio.sleep(2)

        # Start noVNC
        subprocess.Popen([
            "/opt/noVNC/utils/novnc_proxy",
            "--vnc", "localhost:5900",
            "--listen", "6080",
            "--web", "/opt/noVNC"
        ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        logger.info("VNC services started successfully")

    except Exception as e:
        logger.error(f"Error starting VNC services: {e}")


@router.get("/screenshot")
async def get_vnc_screenshot():
    """Get a screenshot of the VNC session"""
    try:
        import base64
        from PIL import Image
        import io

        # Take screenshot using scrot
        result = subprocess.run([
            "scrot", "-o", "/tmp/vnc_screenshot.png"
        ], capture_output=True, text=True)

        if result.returncode != 0:
            raise HTTPException(
                status_code=500, detail="Failed to take screenshot")

        # Read and encode the screenshot
        with open("/tmp/vnc_screenshot.png", "rb") as f:
            image_data = f.read()

        base64_image = base64.b64encode(image_data).decode()

        return {
            "screenshot": f"data:image/png;base64,{base64_image}",
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        logger.error(f"Error taking VNC screenshot: {e}")
        raise HTTPException(
            status_code=500, detail=f"Failed to take screenshot: {str(e)}")


@router.post("/interact")
async def vnc_interact(action: str, data: Dict[str, Any]):
    """Send interaction commands to VNC session"""
    try:
        if action == "click":
            x = data.get("x", 0)
            y = data.get("y", 0)
            button = data.get("button", 1)

            subprocess.run([
                "xdotool", "mousemove", str(x), str(y)
            ])
            subprocess.run([
                "xdotool", "click", str(button)
            ])

        elif action == "type":
            text = data.get("text", "")
            subprocess.run([
                "xdotool", "type", text
            ])

        elif action == "key":
            key = data.get("key", "")
            subprocess.run([
                "xdotool", "key", key
            ])

        return {"message": f"VNC interaction '{action}' executed successfully"}

    except Exception as e:
        logger.error(f"Error executing VNC interaction: {e}")
        raise HTTPException(
            status_code=500, detail=f"Failed to execute VNC interaction: {str(e)}")
