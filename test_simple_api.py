#!/usr/bin/env python3
"""
Simple test script for the simplified LangGraph API
"""

import requests
import json

def test_health():
    """Test the health endpoint"""
    try:
        response = requests.get("http://localhost:8000/api/health")
        print("Health endpoint response:")
        print(f"Status: {response.status_code}")
        print(f"Body: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"Health test failed: {e}")
        return False

def test_chat():
    """Test the simplified chat endpoint"""
    try:
        payload = {
            "message": "Hello! Can you tell me what you are and how you work?",
            "prompt_type": "gpt-3.5-turbo"
        }

        response = requests.post(
            "http://localhost:8000/api/chat",
            headers={"Content-Type": "application/json"},
            json=payload
        )

        print("\nChat endpoint response:")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Response: {data['response']}")
            print(f"Model used: {data['prompt_type']}")
            print(f"User ID: {data['user_id']}")
        else:
            print(f"Error: {response.text}")

        return response.status_code == 200
    except Exception as e:
        print(f"Chat test failed: {e}")
        return False

if __name__ == "__main__":
    print("Testing simplified LangGraph API...")

    if test_health():
        print("✅ Health check passed")
    else:
        print("❌ Health check failed")

    if test_chat():
        print("✅ Chat test passed")
    else:
        print("❌ Chat test failed")
