"""
Simple interview agent system using OpenAI agents with built-in session management.
Enhanced with error handling and latency optimization.
"""

from pathlib import Path
from typing import AsyncGenerator, Dict, Any, Optional
from openai.types.responses import ResponseTextDeltaEvent
from agents import Agent, Runner, SQLiteSession
import json
import time
import uuid
import nest_asyncio

from ..core.logging_config import get_logger, get_agent_logger, log_agent_interaction
from ..services.openai_error_handler import default_error_handler, with_retry
from ..services.circuit_breaker import openai_circuit_breaker, CircuitBreakerOpenError
from ..services.latency_optimizer import default_latency_optimizer


class InterviewAgentSystem:
    """Simple interview system with orchestrator and interviewer agents."""

    def __init__(self):
        self.logger = get_logger("interview_system")
        self.agent_logger = get_agent_logger()

        self.logger.info("Initializing Interview Agent System...")

        self.prompts_dir = Path(__file__).parent.parent.parent / "prompts"
        self.backend_dir = Path(__file__).parent.parent.parent

        # Load prompts
        self.logger.info("Loading agent prompts...")
        self.orchestrator_prompt = self._load_prompt("orchestrator_agent_prompt.txt")
        self.interviewer_prompt = self._load_prompt("interviewer_agent_prompt.txt")
        self.evaluator_prompt = self._load_prompt("evaluator_agent_prompt.txt")
        self.topic_manager_prompt = self._load_prompt("topic_manager_agent_prompt.txt")

        # Load resume and job description
        self.logger.info("Loading context files...")
        self.resume_content = self._load_context_file("sample_resume.txt")
        self.job_description_content = self._load_context_file("sample_job_description.txt")

        # Create agents with context
        context_info = self._build_context_info()
        self.logger.info("Creating agents with context...")

        # Create agents first without handoffs
        self.evaluator_agent = Agent(
            name="evaluator",
            instructions=self.evaluator_prompt + context_info,
            model="gpt-4o-mini"
        )

        self.topic_manager_agent = Agent(
            name="topic_manager",
            instructions=self.topic_manager_prompt + context_info,
            model="gpt-4o-mini"
        )

        self.interviewer_agent = Agent(
            name="interviewer",
            instructions=self.interviewer_prompt + context_info,
            model="gpt-4o-mini"
        )

        self.orchestrator_agent = Agent(
            name="orchestrator",
            instructions=self.orchestrator_prompt + context_info,
            model="gpt-4o-mini",
            handoffs=[self.interviewer_agent, self.evaluator_agent, self.topic_manager_agent]
        )

        # Set handoffs after all agents are created
        self.evaluator_agent.handoffs = [self.orchestrator_agent, self.topic_manager_agent]
        self.topic_manager_agent.handoffs = [self.orchestrator_agent, self.interviewer_agent]
        self.interviewer_agent.handoffs = [self.orchestrator_agent]

        self.logger.info("Interview Agent System initialized successfully")
        print(f"\n{'='*60}")
        print("INTERVIEW AGENT SYSTEM INITIALIZED")
        print(f"{'='*60}")
        print(f"✓ Orchestrator Agent: {self.orchestrator_agent.name}")
        print(f"✓ Interviewer Agent: {self.interviewer_agent.name}")
        print(f"✓ Evaluator Agent: {self.evaluator_agent.name}")
        print(f"✓ Topic Manager Agent: {self.topic_manager_agent.name}")
        print(f"✓ Resume Content: {'Loaded' if self.resume_content else 'Not found'}")
        print(f"✓ Job Description: {'Loaded' if self.job_description_content else 'Not found'}")
        print(f"{'='*60}\n")

    def _load_prompt(self, filename: str) -> str:
        """Load prompt from text file."""
        try:
            prompt_path = self.prompts_dir / filename
            with open(prompt_path, 'r', encoding='utf-8') as file:
                content = file.read().strip()
                self.logger.info(f"Loaded prompt: {filename} ({len(content)} characters)")
                return content
        except FileNotFoundError:
            self.logger.warning(f"Prompt file not found: {filename}, using fallback")
            return f"You are an AI assistant for {filename.replace('_prompt.txt', '').replace('_', ' ')}."

    def _load_context_file(self, filename: str) -> str:
        """Load context file from backend directory."""
        try:
            context_path = self.backend_dir / filename
            with open(context_path, 'r', encoding='utf-8') as file:
                content = file.read().strip()
                self.logger.info(f"Loaded context file: {filename} ({len(content)} characters)")
                return content
        except FileNotFoundError:
            self.logger.warning(f"Context file not found: {filename}")
            return ""

    def _build_context_info(self) -> str:
        """Build context information for agents."""
        context_parts = []

        if self.resume_content:
            context_parts.append(f"\n\nCANDIDATE RESUME:\n{self.resume_content}")

        if self.job_description_content:
            context_parts.append(f"\n\nJOB DESCRIPTION:\n{self.job_description_content}")

        if context_parts:
            context_parts.insert(0, "\n\nIMPORTANT CONTEXT:")
            context_parts.append("\nUse this information to tailor the interview questions and assessment to the specific role and candidate background.")

        context_info = "".join(context_parts)
        self.logger.info(f"Built context info: {len(context_info)} characters")
        return context_info

    def _get_session(self, thread_id: str) -> SQLiteSession:
        """Get or create a session for the given thread ID."""
        session = SQLiteSession(session_id=thread_id, db_path="conversations.db")
        self.logger.debug(f"Retrieved session for thread: {thread_id}")
        return session

    async def process_message_stream(
        self,
        user_message: str,
        thread_id: str
    ) -> AsyncGenerator[str, None]:
        """Process message and stream response from the orchestrator agent with enhanced error handling."""
        operation_id = f"{thread_id}_{uuid.uuid4().hex[:8]}"
        start_time = time.time()

        # Log the incoming message
        log_agent_interaction(
            self.agent_logger,
            agent_name="SYSTEM",
            thread_id=thread_id,
            interaction_type="USER_INPUT",
            message=f"Received message: {user_message[:100]}{'...' if len(user_message) > 100 else ''}",
            extra_data={"full_message": user_message, "message_length": len(user_message), "operation_id": operation_id}
        )

        try:
            # Use circuit breaker to protect against cascading failures
            async def _process_with_agent():
                # Get the session for this thread
                session = self._get_session(thread_id)

                log_agent_interaction(
                    self.agent_logger,
                    agent_name="ORCHESTRATOR",
                    thread_id=thread_id,
                    interaction_type="PROCESSING_START",
                    message="Starting message processing with orchestrator agent",
                    extra_data={"operation_id": operation_id}
                )

                # Always use orchestrator agent - it will handle handoffs to interviewer as needed
                return Runner.run_streamed(self.orchestrator_agent, user_message, session=session)

            # Execute with circuit breaker protection
            result = await openai_circuit_breaker.call(_process_with_agent)

            # Create async generator for streaming with latency optimization
            async def _stream_generator():
                response_chunks = []
                chunk_count = 0

                async for event in result.stream_events():
                    # Stream raw text deltas from the LLM
                    if event.type == "raw_response_event" and isinstance(event.data, ResponseTextDeltaEvent):
                        if event.data.delta:
                            chunk_count += 1
                            response_chunks.append(event.data.delta)
                            yield event.data.delta

                # Log completion
                processing_time = time.time() - start_time
                full_response = "".join(response_chunks)

                log_agent_interaction(
                    self.agent_logger,
                    agent_name="ORCHESTRATOR",
                    thread_id=thread_id,
                    interaction_type="PROCESSING_COMPLETE",
                    message=f"Completed in {round(processing_time, 2)}s, {chunk_count} chunks, {len(full_response)} chars",
                    extra_data={
                        "processing_time_seconds": round(processing_time, 2),
                        "total_chunks": chunk_count,
                        "response_length": len(full_response),
                        "operation_id": operation_id
                    }
                )

            # Stream with latency optimization
            async for chunk in default_latency_optimizer.stream_with_timeout(_stream_generator(), operation_id):
                yield chunk

        except CircuitBreakerOpenError as e:
            processing_time = time.time() - start_time

            log_agent_interaction(
                self.agent_logger,
                agent_name="SYSTEM",
                thread_id=thread_id,
                interaction_type="CIRCUIT_BREAKER_OPEN",
                message=f"Circuit breaker is open: {str(e)}",
                extra_data={
                    "processing_time_seconds": round(processing_time, 2),
                    "operation_id": operation_id,
                    "circuit_breaker_state": openai_circuit_breaker.get_state()
                }
            )

            self.logger.warning(f"Circuit breaker is open for thread {thread_id}: {e}")
            yield "I'm currently experiencing high load. Please try again in a few moments."

        except Exception as e:
            processing_time = time.time() - start_time

            log_agent_interaction(
                self.agent_logger,
                agent_name="SYSTEM",
                thread_id=thread_id,
                interaction_type="ERROR",
                message=f"Error processing message: {str(e)}",
                extra_data={
                    "processing_time_seconds": round(processing_time, 2),
                    "error_type": type(e).__name__,
                    "user_message": user_message,
                    "operation_id": operation_id
                }
            )

            self.logger.error(f"Error in process_message_stream: {e}", exc_info=True)
            yield f"I apologize, but I encountered an error while processing your message. Please try again."

    async def process_message(
        self,
        user_message: str,
        thread_id: str
    ) -> str:
        """Process message and return complete response."""
        response_parts = []
        async for chunk in self.process_message_stream(user_message, thread_id):
            response_parts.append(chunk)

        return "".join(response_parts)

    def get_interview_status(self) -> Dict[str, Any]:
        """Get current interview status with performance metrics."""
        status = {
            "total_questions": 10,
            "features": ["skip", "next"],
            "agents": ["orchestrator", "interviewer", "evaluator", "topic_manager"],
            "status": "active",
            "instructions": "Say 'skip' or 'next' to move to the next question. Progress will be shown as 'Question X of 10'.",
            "performance": default_latency_optimizer.get_performance_stats(),
            "circuit_breaker": openai_circuit_breaker.get_state()
        }

        self.logger.info("Interview status requested")
        print(f"\n{'='*50}")
        print("INTERVIEW STATUS")
        print(f"{'='*50}")
        print(f"Status: {status['status']}")
        print(f"Total Questions: {status['total_questions']}")
        print(f"Available Features: {', '.join(status['features'])}")
        print(f"Active Agents: {', '.join(status['agents'])}")
        print(f"Performance Grade: {status['performance'].get('performance_grade', 'N/A')}")
        print(f"Circuit Breaker: {status['circuit_breaker']['state']}")
        print(f"{'='*50}\n")

        return status

    async def reset_interview(self, thread_id: str):
        """Reset interview session by clearing conversation history."""
        log_agent_interaction(
            self.agent_logger,
            agent_name="SYSTEM",
            thread_id=thread_id,
            interaction_type="RESET_START",
            message="Starting interview reset"
        )

        session = self._get_session(thread_id)
        await session.clear_session()

        log_agent_interaction(
            self.agent_logger,
            agent_name="SYSTEM",
            thread_id=thread_id,
            interaction_type="RESET_COMPLETE",
            message="Interview reset completed successfully"
        )

        print(f"\n🔄 INTERVIEW RESET")
        print(f"Thread ID: {thread_id}")
        print(f"Session cleared successfully")
        print("-" * 50)
