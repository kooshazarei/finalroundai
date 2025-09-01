"""
LangGraph state models.
"""

from typing import TypedDict, List
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage


class ChatState(TypedDict):
    """State definition for LangGraph chat workflow."""

    messages: List[HumanMessage | SystemMessage | AIMessage]
    current_prompt_type: str
    response: str
