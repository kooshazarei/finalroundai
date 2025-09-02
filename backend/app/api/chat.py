"""
Chat API endpoints - Simplified.
"""

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
import json
import uuid
import time

from ..models import ChatMessage
from ..agents.interview_system import InterviewAgentSystem
from ..core.logging_config import get_logger, get_agent_logger, log_agent_interaction

router = APIRouter(prefix="/api", tags=["chat"])

# Single agent system instance
interview_system = InterviewAgentSystem()

# Get loggers
logger = get_logger("chat_api")
agent_logger = get_agent_logger()


@router.post("/chat/thread/new")
async def create_new_thread():
    """Create a new chat thread."""
    thread_id = str(uuid.uuid4())

    log_agent_interaction(
        agent_logger,
        agent_name="API",
        thread_id=thread_id,
        interaction_type="THREAD_CREATED",
        message="New chat thread created",
        extra_data={"thread_id": thread_id}
    )

    logger.info(f"Created new thread: {thread_id}")
    print(f"\n🆕 NEW THREAD CREATED")
    print(f"Thread ID: {thread_id}")
    print("-" * 50)

    return {"thread_id": thread_id}


@router.post("/chat/stream")
async def stream_chat_response(chat_data: ChatMessage):
    """Stream chat response from interview agents."""
    start_time = time.time()
    thread_id = chat_data.thread_id or "default"

    log_agent_interaction(
        agent_logger,
        agent_name="API",
        thread_id=thread_id,
        interaction_type="STREAM_REQUEST",
        message="Received streaming chat request",
        extra_data={
            "message": chat_data.message[:100] + "..." if len(chat_data.message) > 100 else chat_data.message,
            "prompt_type": chat_data.prompt_type,
            "full_message_length": len(chat_data.message)
        }
    )

    async def generate_response():
        try:
            chunk_count = 0
            response_parts = []

            async for chunk in interview_system.process_message_stream(
                user_message=chat_data.message,
                thread_id=thread_id
            ):
                chunk_count += 1
                response_parts.append(chunk)
                yield f"data: {json.dumps({'content': chunk, 'done': False})}\n\n"

            # Log final response
            processing_time = time.time() - start_time
            full_response = "".join(response_parts)

            log_agent_interaction(
                agent_logger,
                agent_name="API",
                thread_id=thread_id,
                interaction_type="STREAM_COMPLETE",
                message=f"Completed in {round(processing_time, 2)}s, {chunk_count} chunks",
                extra_data={
                    "processing_time_seconds": round(processing_time, 2),
                    "total_chunks": chunk_count,
                    "response_length": len(full_response)
                }
            )

            yield f"data: {json.dumps({'content': '', 'done': True})}\n\n"

        except Exception as e:
            processing_time = time.time() - start_time

            log_agent_interaction(
                agent_logger,
                agent_name="API",
                thread_id=thread_id,
                interaction_type="STREAM_ERROR",
                message=f"Error during streaming: {str(e)}",
                extra_data={
                    "processing_time_seconds": round(processing_time, 2),
                    "error_type": type(e).__name__,
                    "user_message": chat_data.message
                }
            )

            logger.error(f"Error in stream_chat_response: {e}", exc_info=True)
            yield f"data: {json.dumps({'error': str(e), 'done': True})}\n\n"

    return StreamingResponse(generate_response(), media_type="text/plain")


@router.get("/interview/status")
async def get_interview_status():
    """Get interview status."""
    logger.info("Interview status requested")
    return interview_system.get_interview_status()


@router.post("/interview/reset")
async def reset_interview(chat_data: ChatMessage):
    """Reset interview session."""
    thread_id = chat_data.thread_id or "default"

    log_agent_interaction(
        agent_logger,
        agent_name="API",
        thread_id=thread_id,
        interaction_type="RESET_REQUEST",
        message="Interview reset requested via API"
    )

    await interview_system.reset_interview(thread_id)

    logger.info(f"Interview reset completed for thread: {thread_id}")
    return {"message": "Interview reset successfully"}
