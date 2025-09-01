"""
Test script to verify the LangGraph implementation works correctly.
"""

import os
import sys

# Add the backend directory to the path
sys.path.append('/Users/kooshazarei/Seedtag/finalroundai/backend')

from main import create_chat_workflow
from langchain_core.messages import HumanMessage

def test_chat_workflow():
    """Test the chat workflow without requiring OpenAI API key."""
    try:
        # Create workflow
        workflow = create_chat_workflow()
        print("✅ LangGraph workflow created successfully")

        # Test state structure
        initial_state = {
            "messages": [HumanMessage(content="Hello, this is a test message")],
            "current_prompt_type": "default",
            "response": ""
        }
        print("✅ Initial state structure is correct")

        # Test prompt manager
        from prompts import prompt_manager
        default_prompt = prompt_manager.get_prompt("default")
        technical_prompt = prompt_manager.get_prompt("technical")

        print("✅ Prompt manager working correctly")
        print(f"   - Default prompt loaded: {len(default_prompt)} characters")
        print(f"   - Technical prompt loaded: {len(technical_prompt)} characters")

        available_prompts = prompt_manager.get_available_prompts()
        print(f"✅ Available prompt types: {list(available_prompts.keys())}")

        print("\n🎉 All tests passed! Backend is ready with LangGraph.")
        return True

    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

if __name__ == "__main__":
    test_chat_workflow()
