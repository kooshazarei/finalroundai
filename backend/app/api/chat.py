"""
Chat API endpoints.
"""

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
import logging
from typing import TypedDict, Dict, Any
import os
import json
import uuid
import asyncio

from ..models import ChatMessage, ChatResponse
from ..core import get_logger
from ..services import get_graph_service

logger = get_logger(__name__)
router = APIRouter(prefix="/api", tags=["chat"])

# Static user ID as requested
STATIC_USER_ID = "user123"


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


@router.get("/welcome")
async def get_welcome_message():
    """Get streaming welcome message."""
    async def generate_welcome():
        welcome_text = "Hello! I'm your AI Chat Assistant. How can I help you today?"

        # Stream the welcome message character by character for demo effect
        for char in welcome_text:
            yield f"data: {json.dumps({'content': char, 'done': False})}\n\n"
            await asyncio.sleep(0.02)  # Small delay for typing effect

        yield f"data: {json.dumps({'content': '', 'done': True})}\n\n"

    return StreamingResponse(generate_welcome(), media_type="text/plain")


@router.post("/chat/stream")
async def stream_chat_response(chat_data: ChatMessage):
    """Stream chat response using LangGraph implementation."""
    try:
        logger.info(f"Processing streaming chat message for user: {chat_data.user_id or STATIC_USER_ID}")

        async def generate_response():
            try:
                # Get model name
                model_name = chat_data.prompt_type
                if model_name in ["simple", "default"]:
                    model_name = "gpt-3.5-turbo"

                # Use graph service to process the message
                graph_service = get_graph_service()
                result = await graph_service.process_chat_message(
                    message=chat_data.message,
                    model_name=model_name,
                    session_id=chat_data.thread_id
                )

                response_text = result.get("response", "")

                # Stream the response character by character
                for char in response_text:
                    yield f"data: {json.dumps({'content': char, 'done': False})}\n\n"
                    await asyncio.sleep(0.01)  # Small delay for streaming effect

                # Send final done signal
                yield f"data: {json.dumps({'content': '', 'done': True})}\n\n"

            except Exception as e:
                logger.error(f"Error in graph-based chat: {e}")
                error_msg = f"Sorry, there was an error processing your message: {str(e)}"
                yield f"data: {json.dumps({'error': error_msg, 'done': True})}\n\n"

        return StreamingResponse(generate_response(), media_type="text/plain")

    except Exception as e:
        logger.error(f"Unexpected error in streaming chat endpoint: {e}")
        raise HTTPException(status_code=500, detail=f"Error processing chat: {str(e)}")


@router.post("/chat", response_model=ChatResponse)
async def chat_with_ai(chat_data: ChatMessage):
    """Process a chat message and return AI response using LangGraph."""
    try:
        logger.info(f"Processing chat message for static user: {STATIC_USER_ID}")

        # Get model name
        model_name = chat_data.prompt_type
        if model_name in ["simple", "default"]:
            model_name = "gpt-3.5-turbo"

        # Use graph service to process the message
        graph_service = get_graph_service()
        result = await graph_service.process_chat_message(
            message=chat_data.message,
            model_name=model_name,
            session_id=chat_data.thread_id
        )

        logger.info("Chat message processed successfully with LangGraph")
        return ChatResponse(
            response=result.get("response", ""),
            status="success",
            prompt_type=model_name,
            thread_id=chat_data.thread_id,
            user_id=chat_data.user_id or STATIC_USER_ID
        )

    except Exception as e:
        logger.error(f"Unexpected error in chat endpoint: {e}")
        raise HTTPException(status_code=500, detail=f"Error processing chat: {str(e)}")
