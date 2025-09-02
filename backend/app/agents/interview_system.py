"""
Simple interview agent system using OpenAI agents with built-in session management.
"""

from pathlib import Path
from typing import AsyncGenerator, Dict, Any, Optional
from openai.types.responses import ResponseTextDeltaEvent
from agents import Agent, Runner, SQLiteSession


class InterviewAgentSystem:
    """Simple interview system with orchestrator and interviewer agents."""

    def __init__(self):
        self.prompts_dir = Path(__file__).parent.parent.parent / "prompts"
        self.backend_dir = Path(__file__).parent.parent.parent

        # Load prompts
        self.orchestrator_prompt = self._load_prompt("orchestrator_agent_prompt.txt")
        self.interviewer_prompt = self._load_prompt("interviewer_agent_prompt.txt")

        # Load resume and job description
        self.resume_content = self._load_context_file("sample_resume.txt")
        self.job_description_content = self._load_context_file("sample_job_description.txt")

        # Create agents with context
        context_info = self._build_context_info()

        self.interviewer_agent = Agent(
            name="interviewer",
            instructions=self.interviewer_prompt + context_info,
            model="gpt-4o-mini"
        )

        self.orchestrator_agent = Agent(
            name="orchestrator",
            instructions=self.orchestrator_prompt + context_info,
            model="gpt-4o-mini",
            handoffs=[self.interviewer_agent]
        )

        # Update interviewer to handoff back to orchestrator
        self.interviewer_agent.handoffs = [self.orchestrator_agent]

    def _load_prompt(self, filename: str) -> str:
        """Load prompt from text file."""
        try:
            prompt_path = self.prompts_dir / filename
            with open(prompt_path, 'r', encoding='utf-8') as file:
                return file.read().strip()
        except FileNotFoundError:
            return f"You are an AI assistant for {filename.replace('_prompt.txt', '').replace('_', ' ')}."

    def _load_context_file(self, filename: str) -> str:
        """Load context file from backend directory."""
        try:
            context_path = self.backend_dir / filename
            with open(context_path, 'r', encoding='utf-8') as file:
                return file.read().strip()
        except FileNotFoundError:
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

        return "".join(context_parts)

    def _get_session(self, thread_id: str) -> SQLiteSession:
        """Get or create a session for the given thread ID."""
        return SQLiteSession(session_id=thread_id, db_path="conversations.db")

    async def process_message_stream(
        self,
        user_message: str,
        thread_id: str,
        current_agent: str = "orchestrator"
    ) -> AsyncGenerator[str, None]:
        """Process message and stream response from the appropriate agent."""
        try:
            # Get the session for this thread
            session = self._get_session(thread_id)

            # Get the appropriate agent
            agent = self.orchestrator_agent if current_agent == "orchestrator" else self.interviewer_agent

            # Stream response using the agents library with session
            result = Runner.run_streamed(agent, user_message, session=session)

            async for event in result.stream_events():
                # Stream raw text deltas from the LLM
                if event.type == "raw_response_event" and isinstance(event.data, ResponseTextDeltaEvent):
                    if event.data.delta:
                        yield event.data.delta

        except Exception as e:
            yield f"I apologize, but I encountered an error while processing your message. Please try again."

    async def process_message(
        self,
        user_message: str,
        thread_id: str,
        current_agent: str = "orchestrator"
    ) -> str:
        """Process message and return complete response."""
        response_parts = []
        async for chunk in self.process_message_stream(user_message, thread_id, current_agent):
            response_parts.append(chunk)

        return "".join(response_parts)

    def get_interview_status(self) -> Dict[str, Any]:
        """Get current interview status."""
        return {
            "agents_available": ["orchestrator", "interviewer"],
            "status": "active"
        }

    async def reset_interview(self, thread_id: str):
        """Reset interview session by clearing conversation history."""
        session = self._get_session(thread_id)
        await session.clear_session()
