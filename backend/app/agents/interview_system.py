"""
Simple interview agent system using OpenAI agents.
"""

from pathlib import Path
from typing import AsyncGenerator, Dict, Any, Optional
from openai.types.responses import ResponseTextDeltaEvent
from agents import Agent, Runner


class InterviewAgentSystem:
    """Simple interview system with orchestrator and interviewer agents."""

    def __init__(self):
        self.prompts_dir = Path(__file__).parent.parent.parent / "prompts"

        # Load prompts
        self.orchestrator_prompt = self._load_prompt("orchestrator_agent_prompt.txt")
        self.interviewer_prompt = self._load_prompt("interviewer_agent_prompt.txt")

        # Create agents
        self.interviewer_agent = Agent(
            name="interviewer",
            instructions=self.interviewer_prompt,
            model="gpt-4o-mini"
        )

        self.orchestrator_agent = Agent(
            name="orchestrator",
            instructions=self.orchestrator_prompt,
            model="gpt-4o-mini",
            handoffs=[self.interviewer_agent]
        )

        # Update interviewer to handoff back to orchestrator
        self.interviewer_agent.handoffs = [self.orchestrator_agent]

        # Interview context
        self.interview_context: Dict[str, Any] = {}

    def _load_prompt(self, filename: str) -> str:
        """Load prompt from text file."""
        try:
            prompt_path = self.prompts_dir / filename
            with open(prompt_path, 'r', encoding='utf-8') as file:
                return file.read().strip()
        except FileNotFoundError:
            return f"You are an AI assistant for {filename.replace('_prompt.txt', '').replace('_', ' ')}."

    def update_interview_context(self, **kwargs):
        """Update the interview context with new information."""
        self.interview_context.update(kwargs)

    def _get_context_message(self) -> str:
        """Get formatted context message for agents."""
        if not self.interview_context:
            return ""

        context_parts = []
        for key, value in self.interview_context.items():
            if value:
                context_parts.append(f"{key.replace('_', ' ').title()}: {value}")

        if context_parts:
            return f"\n\nCONTEXT:\n" + "\n".join(context_parts)
        return ""

    async def process_message_stream(
        self,
        user_message: str,
        thread_id: str,
        current_agent: str = "orchestrator"
    ) -> AsyncGenerator[str, None]:
        """Process message and stream response from the appropriate agent."""
        try:
            # Add context to the message
            context_message = self._get_context_message()
            full_message = user_message + context_message

            # Get the appropriate agent
            agent = self.orchestrator_agent if current_agent == "orchestrator" else self.interviewer_agent

            # Stream response using the agents library
            result = Runner.run_streamed(agent, full_message)

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
            "context": self.interview_context,
            "agents_available": ["orchestrator", "interviewer"],
            "status": "active"
        }

    def reset_interview(self, thread_id: Optional[str] = None):
        """Reset interview session."""
        self.interview_context.clear()
