#!/usr/bin/env python3
"""
Test the chat API endpoints with the new LangGraph implementation.
"""

import requests
import json
import sys
import os
from datetime import datetime

# API base URL
BASE_URL = "http://localhost:8000"

def test_health():
    """Test health endpoint."""
    print("🏥 Testing health endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Health check passed: {data['status']}")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False

def test_root():
    """Test root endpoint."""
    print("\n🏠 Testing root endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Root endpoint: {data['message']}")
            return True
        else:
            print(f"❌ Root endpoint failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Root endpoint error: {e}")
        return False

def test_new_thread():
    """Test creating a new thread."""
    print("\n🧵 Testing new thread creation...")
    try:
        response = requests.post(f"{BASE_URL}/api/chat/thread/new")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ New thread created: {data['thread_id']}")
            return data['thread_id']
        else:
            print(f"❌ Thread creation failed: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Thread creation error: {e}")
        return None

def test_chat_endpoint(thread_id):
    """Test the regular chat endpoint with LangGraph."""
    print("\n💬 Testing chat endpoint with LangGraph...")

    payload = {
        "message": "Hello! Can you tell me you're using LangGraph?",
        "prompt_type": "gpt-3.5-turbo",
        "thread_id": thread_id,
        "user_id": "test_user"
    }

    try:
        response = requests.post(
            f"{BASE_URL}/api/chat",
            json=payload,
            headers={"Content-Type": "application/json"}
        )

        if response.status_code == 200:
            data = response.json()
            print(f"✅ Chat response: {data['response'][:100]}...")
            print(f"📝 Status: {data['status']}")
            print(f"🔧 Model: {data['prompt_type']}")
            return True
        else:
            print(f"❌ Chat failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Chat error: {e}")
        return False

def test_welcome_stream():
    """Test the welcome streaming endpoint."""
    print("\n👋 Testing welcome stream...")
    try:
        response = requests.get(f"{BASE_URL}/api/welcome")
        if response.status_code == 200:
            content = ""
            for line in response.iter_lines():
                if line.startswith(b"data: "):
                    try:
                        data = json.loads(line[6:])
                        if data.get('content'):
                            content += data['content']
                        if data.get('done'):
                            break
                    except json.JSONDecodeError:
                        continue
            print(f"✅ Welcome message: {content}")
            return True
        else:
            print(f"❌ Welcome stream failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Welcome stream error: {e}")
        return False

def main():
    """Run all tests."""
    print("🚀 Testing AI Chat Assistant with LangGraph")
    print("=" * 50)

    # Check if we need to set OPENAI_API_KEY (for actual chat testing)
    if not os.getenv("OPENAI_API_KEY"):
        print("⚠️  Note: OPENAI_API_KEY not set - chat may not work")

    tests_passed = 0
    total_tests = 5

    # Test health
    if test_health():
        tests_passed += 1

    # Test root
    if test_root():
        tests_passed += 1

    # Test new thread
    thread_id = test_new_thread()
    if thread_id:
        tests_passed += 1

    # Test welcome stream
    if test_welcome_stream():
        tests_passed += 1

    # Test chat (only if we have a thread ID)
    if thread_id:
        if test_chat_endpoint(thread_id):
            tests_passed += 1
    else:
        print("\n💬 Skipping chat test (no thread ID)")

    print(f"\n🎯 Results: {tests_passed}/{total_tests} tests passed")

    if tests_passed == total_tests:
        print("🎉 All tests passed! LangGraph implementation is working correctly.")
        return True
    else:
        print("⚠️  Some tests failed. Check the output above for details.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
