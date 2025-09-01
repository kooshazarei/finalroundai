"""
Chat API endpoints.
"""

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
import logging
import json

from ..models import ChatMessage, ChatResponse, PromptsResponse
from ..services import chat_workflow_service
from ..core import ChatProcessingError, get_logger

# Import prompt manager from the moved location
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from prompts import prompt_manager

logger = get_logger(__name__)
router = APIRouter(prefix="/api", tags=["chat"])


async def stream_welcome_message():
    """Stream an AI-generated welcome message."""
    try:
        # Use the chat workflow service to generate a personalized welcome message
        welcome_prompt = "Generate a warm, friendly welcome message for a new user starting a chat session."

        logger.info("Generating AI welcome message")

        # Stream the AI-generated welcome message using the welcome prompt type
        async for chunk in chat_workflow_service.stream_chat_response(
            message=welcome_prompt,
            prompt_type="welcome"
        ):
            yield chunk

    except Exception as e:
        logger.error(f"Error streaming AI welcome message: {e}")
        # Fallback to static message if AI generation fails
        fallback_text = """Hello! 👋 I'm your AI Chat Assistant, and I'm here to help you with any questions or tasks you might have.

I can assist you with:
• Answering questions on a wide range of topics
• Helping with creative writing and brainstorming
• Providing technical guidance and explanations
• Problem-solving and analysis
• General conversation and advice

Feel free to ask me anything! What would you like to talk about today?"""

        data = {"content": fallback_text, "done": True}
        yield f"data: {json.dumps(data)}\n\n"


@router.get("/welcome")
async def get_welcome():
    """Stream the welcome message to guide the user."""
    try:
        logger.info("Starting welcome message stream")
        return StreamingResponse(
            stream_welcome_message(),
            media_type="text/plain",
            headers={"Cache-Control": "no-cache", "Connection": "keep-alive"}
        )
    except Exception as e:
        logger.error(f"Error streaming welcome message: {e}")
        raise HTTPException(status_code=500, detail="Failed to stream welcome message")


@router.post("/chat", response_model=ChatResponse)
async def chat_with_ai(chat_data: ChatMessage):
    """Process a chat message and return AI response."""
    try:
        logger.info(f"Processing chat message with prompt type: {chat_data.prompt_type}")

        # Process through workflow
        result = chat_workflow_service.process_chat(
            message=chat_data.message,
            prompt_type=chat_data.prompt_type
        )

        logger.info("Chat message processed successfully")
        return ChatResponse(
            response=result["response"],
            status="success",
            prompt_type=result["current_prompt_type"]
        )

    except ChatProcessingError as e:
        logger.error(f"Chat processing error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error in chat endpoint: {e}")
        raise HTTPException(status_code=500, detail=f"Error processing chat: {str(e)}")


@router.post("/chat/stream")
async def stream_chat_response(chat_data: ChatMessage):
    """Process a chat message and stream AI response directly from LLM."""
    try:
        logger.info(f"Processing streaming chat message with prompt type: {chat_data.prompt_type}")

        # Stream response directly from chat service
        return StreamingResponse(
            chat_workflow_service.stream_chat_response(
                message=chat_data.message,
                prompt_type=chat_data.prompt_type
            ),
            media_type="text/plain",
            headers={"Cache-Control": "no-cache", "Connection": "keep-alive"}
        )

    except ChatProcessingError as e:
        logger.error(f"Chat processing error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error in streaming chat endpoint: {e}")
        raise HTTPException(status_code=500, detail=f"Error processing streaming chat: {str(e)}")


@router.get("/prompts", response_model=PromptsResponse)
async def get_available_prompts():
    """Get all available prompt types."""
    try:
        prompts = list(prompt_manager.get_available_prompts().keys())
        logger.debug(f"Retrieved {len(prompts)} available prompts")
        return PromptsResponse(prompts=prompts)
    except Exception as e:
        logger.error(f"Error retrieving prompts: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve prompts")
