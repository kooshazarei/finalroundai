"""
Example usage of the LangGraph chat implementation.
"""

import asyncio
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from app.services import get_graph_service


async def demo_chat_graph():
    """Demonstrate the chat graph functionality."""
    print("🚀 LangGraph Chat Demo")
    print("=" * 40)

    # Get the graph service
    graph_service = get_graph_service()

    # Example messages to test
    test_messages = [
        "Hello! What's the weather like today?",
        "Can you help me with Python programming?",
        "What are the benefits of using LangGraph?",
        "Tell me a joke about AI"
    ]

    for i, message in enumerate(test_messages, 1):
        print(f"\n🔍 Test {i}: {message}")
        print("-" * 30)

        try:
            # Process the message using the graph
            result = await graph_service.process_chat_message(
                message=message,
                model_name="gpt-3.5-turbo",
                session_id=f"demo_session_{i}"
            )

            print(f"✅ Response: {result.get('response', 'No response')}")
            print(f"📝 Session ID: {result.get('session_id', 'None')}")
            print(f"💬 Messages in conversation: {len(result.get('messages', []))}")

        except Exception as e:
            print(f"❌ Error: {str(e)}")


async def demo_simple_conversation():
    """Demonstrate a simple conversation flow."""
    print("\n\n🗣️  Simple Conversation Demo")
    print("=" * 40)

    graph_service = get_graph_service()
    session_id = "conversation_demo"

    conversation = [
        "Hi, my name is John",
        "What's my name?",
        "Can you remember what I told you about myself?"
    ]

    for i, message in enumerate(conversation, 1):
        print(f"\n👤 User: {message}")

        try:
            result = await graph_service.process_chat_message(
                message=message,
                model_name="gpt-3.5-turbo",
                session_id=session_id
            )

            print(f"🤖 AI: {result.get('response', 'No response')}")

        except Exception as e:
            print(f"❌ Error: {str(e)}")


if __name__ == "__main__":
    # Check if API key is set
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ Error: OPENAI_API_KEY environment variable is not set")
        print("Please set your OpenAI API key in the .env file")
        exit(1)

    # Run the demos
    asyncio.run(demo_chat_graph())
    asyncio.run(demo_simple_conversation())
