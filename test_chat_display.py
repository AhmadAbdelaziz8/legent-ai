#!/usr/bin/env python3
"""
Test script to verify chat messages are displaying correctly
"""

import requests
import json
import time

def test_chat_flow():
    """Test the complete chat flow"""
    print("🧪 Testing Chat Message Display...")
    
    # Test 1: Create a new session
    print("\n1. Creating new session...")
    session_data = {
        "initial_prompt": "Hello, can you help me test the chat system?",
        "provider": "anthropic"
    }
    
    response = requests.post("http://localhost:8000/sessions", json=session_data)
    if response.status_code == 200:
        session = response.json()
        session_id = session['id']
        print(f"✅ Session created: {session_id}")
    else:
        print(f"❌ Failed to create session: {response.status_code}")
        return
    
    # Test 2: Wait for agent to process
    print("\n2. Waiting for agent to process...")
    time.sleep(5)
    
    # Test 3: Check messages
    print("\n3. Checking messages...")
    response = requests.get(f"http://localhost:8000/messages/session/{session_id}")
    if response.status_code == 200:
        messages = response.json()
        print(f"✅ Messages retrieved: {len(messages)} messages")
        
        for i, message in enumerate(messages):
            print(f"   Message {i+1}:")
            print(f"     Role: {message['role']}")
            print(f"     Content: {message['content']}")
            print(f"     Has screenshot: {'Yes' if message.get('base64_image') else 'No'}")
            print(f"     Created: {message['created_at']}")
    else:
        print(f"❌ Failed to get messages: {response.status_code}")
    
    # Test 4: Check session status
    print("\n4. Checking session status...")
    response = requests.get(f"http://localhost:8000/sessions/{session_id}")
    if response.status_code == 200:
        session_info = response.json()
        print(f"✅ Session status: {session_info.get('status')}")
    else:
        print(f"❌ Failed to get session info: {response.status_code}")

if __name__ == "__main__":
    test_chat_flow()


