#!/usr/bin/env python3
"""
Test script to validate VNC integration
"""

import asyncio
import requests
import time
import sys

API_BASE_URL = "http://localhost:8000"


def test_vnc_status():
    """Test VNC status endpoint"""
    print("Testing VNC status endpoint...")
    try:
        response = requests.get(f"{API_BASE_URL}/vnc/status")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ VNC Status: {data}")
            return data
        else:
            print(f"❌ VNC Status failed: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ VNC Status error: {e}")
        return None


def test_vnc_start():
    """Test VNC start endpoint"""
    print("Testing VNC start endpoint...")
    try:
        response = requests.post(f"{API_BASE_URL}/vnc/start")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ VNC Start: {data}")
            return True
        else:
            print(f"❌ VNC Start failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ VNC Start error: {e}")
        return False


def test_vnc_sessions():
    """Test VNC sessions endpoint"""
    print("Testing VNC sessions endpoint...")
    try:
        response = requests.get(f"{API_BASE_URL}/vnc/sessions")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ VNC Sessions: {data}")
            return True
        else:
            print(f"❌ VNC Sessions failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ VNC Sessions error: {e}")
        return False


def test_vnc_screenshot():
    """Test VNC screenshot endpoint"""
    print("Testing VNC screenshot endpoint...")
    try:
        response = requests.get(f"{API_BASE_URL}/vnc/screenshot")
        if response.status_code == 200:
            data = response.json()
            print(
                f"✅ VNC Screenshot: {len(data.get('screenshot', ''))} characters")
            return True
        else:
            print(f"❌ VNC Screenshot failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ VNC Screenshot error: {e}")
        return False


def test_vnc_interact():
    """Test VNC interaction endpoint"""
    print("Testing VNC interaction endpoint...")
    try:
        response = requests.post(f"{API_BASE_URL}/vnc/interact", json={
            "action": "click",
            "x": 100,
            "y": 100,
            "button": 1
        })
        if response.status_code == 200:
            data = response.json()
            print(f"✅ VNC Interaction: {data}")
            return True
        else:
            print(f"❌ VNC Interaction failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ VNC Interaction error: {e}")
        return False


def main():
    """Run all VNC tests"""
    print("🚀 Starting VNC Integration Tests")
    print("=" * 50)

    # Test basic connectivity
    print("\n1. Testing API connectivity...")
    try:
        response = requests.get(f"{API_BASE_URL}/")
        if response.status_code == 200:
            print("✅ API is accessible")
        else:
            print("❌ API is not accessible")
            return False
    except Exception as e:
        print(f"❌ API connectivity error: {e}")
        return False

    # Test VNC endpoints
    print("\n2. Testing VNC endpoints...")

    # Test status
    status = test_vnc_status()

    # Test sessions
    test_vnc_sessions()

    # Test start (if not already running)
    if not status or not status.get('is_running', False):
        print("\n3. Starting VNC services...")
        test_vnc_start()

        # Wait for services to start
        print("Waiting for VNC services to start...")
        time.sleep(5)

        # Test status again
        status = test_vnc_status()

    # Test screenshot if running
    if status and status.get('is_running', False):
        print("\n4. Testing VNC functionality...")
        test_vnc_screenshot()
        test_vnc_interact()

    print("\n" + "=" * 50)
    print("🎉 VNC Integration Tests Complete")

    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
