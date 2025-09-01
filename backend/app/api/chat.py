"""
Chat API endpoints.
"""

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
import json
import uuid
import asyncio
from typing import Dict

from ..models import ChatMessage
from ..core import get_logger
from ..services.llm_service import create_llm_service

logger = get_logger(__name__)
router = APIRouter(prefix="/api", tags=["chat"])

# Static user ID
STATIC_USER_ID = "User123"


@router.post("/chat/thread/new")
async def create_new_thread():
    """Create a new chat thread."""
    try:
        thread_id = str(uuid.uuid4())
        logger.info(f"Created new thread: {thread_id}")
        return {"thread_id": thread_id, "status": "success"}
    except Exception as e:
        logger.error(f"Error creating new thread: {e}")
        raise HTTPException(status_code=500, detail=f"Error creating thread: {str(e)}")


@router.post("/chat/stream")
async def stream_chat_response(chat_data: ChatMessage):
    """Stream chat response using the LLM service."""
    try:
        # Always use static user ID
        effective_user_id = STATIC_USER_ID
        logger.info(f"Processing streaming chat message for user: {effective_user_id}")
        print(f"🚀 Starting stream execution for thread_id: {chat_data.thread_id}")
        print(f"📝 Message: {chat_data.message}")

        async def generate_response():
            try:
                # Create LLM service directly
                llm_service = create_llm_service()
                print(f"✅ LLM service initialized successfully")

                # Generate response using the LLM service
                response = await llm_service.generate_response(
                    user_message=chat_data.message,
                    system_prompt="You are a helpful AI assistant."
                )

                # Stream the response back
                yield f"data: {json.dumps({'content': response, 'done': False})}\n\n"

                print(f"✅ Response generated successfully")
                # Send final done signal
                yield f"data: {json.dumps({'content': '', 'done': True})}\n\n"

            except Exception as e:
                logger.error(f"Error in LLM processing: {e}")
                print(f"❌ Error during stream execution: {str(e)}")
                error_msg = f"Sorry, there was an error processing your message: {str(e)}"
                yield f"data: {json.dumps({'error': error_msg, 'done': True})}\n\n"

        print(f"🎯 Returning streaming response...")
        return StreamingResponse(generate_response(), media_type="text/plain")

    except Exception as e:
        logger.error(f"Unexpected error in streaming chat endpoint: {e}")
        print(f"💥 Unexpected error in streaming chat endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing chat: {str(e)}")
