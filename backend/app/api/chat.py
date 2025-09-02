"""
Chat API endpoints - Simplified.
"""

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
import json
import uuid

from ..models import ChatMessage
from ..agents.interview_system import InterviewAgentSystem

router = APIRouter(prefix="/api", tags=["chat"])

# Single agent system instance
interview_system = InterviewAgentSystem()


@router.post("/chat/thread/new")
async def create_new_thread():
    """Create a new chat thread."""
    return {"thread_id": str(uuid.uuid4())}


@router.post("/chat/stream")
async def stream_chat_response(chat_data: ChatMessage):
    """Stream chat response from interview agents."""
    async def generate_response():
        try:
            async for chunk in interview_system.process_message_stream(
                user_message=chat_data.message,
                thread_id=chat_data.thread_id or "default"
            ):
                yield f"data: {json.dumps({'content': chunk, 'done': False})}\n\n"

            yield f"data: {json.dumps({'content': '', 'done': True})}\n\n"

        except Exception as e:
            yield f"data: {json.dumps({'error': str(e), 'done': True})}\n\n"

    return StreamingResponse(generate_response(), media_type="text/plain")


@router.get("/interview/status")
async def get_interview_status():
    """Get interview status."""
    return interview_system.get_interview_status()


@router.post("/interview/reset")
async def reset_interview(chat_data: ChatMessage):
    """Reset interview session."""
    thread_id = chat_data.thread_id or "default"
    await interview_system.reset_interview(thread_id)
    return {"message": "Interview reset successfully"}
