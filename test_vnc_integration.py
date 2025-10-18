#!/usr/bin/env python3
"""
Test script for VNC integration and screenshot functionality
"""

import asyncio
import requests
import base64
import json
from pathlib import Path

# Configuration
BASE_URL = "http://localhost:8000"
VNC_URL = "http://localhost:6080"

async def test_vnc_services():
    """Test VNC service endpoints"""
    print("🧪 Testing VNC Services...")
    
    try:
        # Test VNC status
        response = requests.get(f"{BASE_URL}/vnc/status")
        print(f"✅ VNC Status: {response.status_code}")
        if response.status_code == 200:
            print(f"   Response: {response.json()}")
        
        # Test VNC start
        response = requests.post(f"{BASE_URL}/vnc/start")
        print(f"✅ VNC Start: {response.status_code}")
        
        # Test screenshot endpoint
        response = requests.get(f"{BASE_URL}/vnc/screenshot")
        print(f"✅ Screenshot: {response.status_code}")
        if response.status_code == 200:
            screenshot_data = response.json()
            print(f"   Screenshot timestamp: {screenshot_data.get('timestamp')}")
            print(f"   Screenshot data length: {len(screenshot_data.get('screenshot', ''))}")
        
        # Test VNC interaction
        interaction_data = {
            "action": "click",
            "x": 100,
            "y": 100,
            "button": 1
        }
        response = requests.post(f"{BASE_URL}/vnc/interact", json=interaction_data)
        print(f"✅ VNC Interaction: {response.status_code}")
        
    except Exception as e:
        print(f"❌ VNC Services Test Failed: {e}")

async def test_agent_with_screenshots():
    """Test agent service with screenshot capability"""
    print("\n🧪 Testing Agent Service with Screenshots...")
    
    try:
        # Create a test session
        session_data = {
            "initial_prompt": "Take a screenshot of the desktop and tell me what you see",
            "provider": "anthropic"
        }
        
        response = requests.post(f"{BASE_URL}/sessions", json=session_data)
        print(f"✅ Session Creation: {response.status_code}")
        
        if response.status_code == 200:
            session = response.json()
            session_id = session['id']
            print(f"   Session ID: {session_id}")
            
            # Wait a bit for the agent to process
            print("   Waiting for agent to process...")
            await asyncio.sleep(5)
            
            # Check session status
            response = requests.get(f"{BASE_URL}/sessions/{session_id}")
            if response.status_code == 200:
                session_info = response.json()
                print(f"   Session Status: {session_info.get('status')}")
            
            # Get messages
            response = requests.get(f"{BASE_URL}/sessions/{session_id}/messages")
            if response.status_code == 200:
                messages = response.json()
                print(f"   Messages count: {len(messages)}")
                
                # Check for screenshots in messages
                for message in messages:
                    if message.get('base64_image'):
                        print(f"   ✅ Found screenshot in message {message['id']}")
                        print(f"      Screenshot size: {len(message['base64_image'])} characters")
                    else:
                        print(f"   📝 Message {message['id']}: {message.get('content', {}).get('text', 'No text')[:100]}...")
        
    except Exception as e:
        print(f"❌ Agent Screenshot Test Failed: {e}")

async def test_frontend_integration():
    """Test frontend VNC integration"""
    print("\n🧪 Testing Frontend Integration...")
    
    try:
        # Test if frontend is accessible
        response = requests.get("http://localhost:3000")
        print(f"✅ Frontend Access: {response.status_code}")
        
        # Test VNC web interface
        response = requests.get(VNC_URL)
        print(f"✅ VNC Web Interface: {response.status_code}")
        
    except Exception as e:
        print(f"❌ Frontend Integration Test Failed: {e}")

async def test_database_schema():
    """Test database schema for screenshot support"""
    print("\n🧪 Testing Database Schema...")
    
    try:
        # This would require database connection testing
        # For now, we'll just verify the migration file exists
        migration_file = Path("backend/migrations/add_screenshot_column.sql")
        if migration_file.exists():
            print("✅ Database migration file exists")
            print(f"   Migration content: {migration_file.read_text()}")
        else:
            print("❌ Database migration file not found")
            
    except Exception as e:
        print(f"❌ Database Schema Test Failed: {e}")

async def main():
    """Run all VNC integration tests"""
    print("🚀 Starting VNC Integration Tests...")
    print("=" * 50)
    
    await test_vnc_services()
    await test_agent_with_screenshots()
    await test_frontend_integration()
    await test_database_schema()
    
    print("\n" + "=" * 50)
    print("✅ VNC Integration Tests Complete!")
    print("\n📋 Summary:")
    print("   - VNC services should be running on port 6080")
    print("   - Backend API should be running on port 8000")
    print("   - Frontend should be running on port 3000")
    print("   - Database should have screenshot column added")
    print("\n🔧 Next Steps:")
    print("   1. Run the database migration")
    print("   2. Start the backend services")
    print("   3. Start the frontend")
    print("   4. Test the chat interface with computer use prompts")

if __name__ == "__main__":
    asyncio.run(main())


