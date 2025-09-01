from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from typing import TypedDict, List, AsyncGenerator
import os
import json
import asyncio
from dotenv import load_dotenv
from prompts import prompt_manager

# Load environment variables
load_dotenv()

app = FastAPI(title="AI Chat Assistant", version="1.0.0")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://frontend:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# State definition for LangGraph
class ChatState(TypedDict):
    messages: List[HumanMessage | SystemMessage | AIMessage]
    current_prompt_type: str
    response: str

# Initialize OpenAI chat model
def get_chat_model():
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="OpenAI API key not configured")
    return ChatOpenAI(
        model="gpt-3.5-turbo",
        openai_api_key=api_key,
        temperature=0.7
    )

# LangGraph nodes
def prepare_conversation(state: ChatState):
    """Prepare the conversation with system prompt."""
    prompt_type = state.get("current_prompt_type", "default")
    system_prompt = prompt_manager.get_prompt(prompt_type)

    # Add system message if not already present
    messages = state["messages"]
    if not messages or not isinstance(messages[0], SystemMessage):
        messages = [SystemMessage(content=system_prompt)] + messages

    return {"messages": messages, "current_prompt_type": prompt_type}

def generate_response(state: ChatState):
    """Generate AI response using the chat model."""
    try:
        chat_model = get_chat_model()
        messages = state["messages"]

        # Get AI response
        response = chat_model.invoke(messages)

        # Update messages with AI response
        updated_messages = messages + [response]

        return {
            "messages": updated_messages,
            "response": response.content,
            "current_prompt_type": state.get("current_prompt_type", "default")
        }
    except Exception as e:
        error_msg = f"Error generating response: {str(e)}"
        return {
            "messages": state["messages"],
            "response": error_msg,
            "current_prompt_type": state.get("current_prompt_type", "default")
        }

# Create the LangGraph workflow
def create_chat_workflow():
    """Create the LangGraph workflow for chat processing."""
    workflow = StateGraph(ChatState)

    # Add nodes
    workflow.add_node("prepare_conversation", prepare_conversation)
    workflow.add_node("generate_response", generate_response)

    # Add edges
    workflow.set_entry_point("prepare_conversation")
    workflow.add_edge("prepare_conversation", "generate_response")
    workflow.add_edge("generate_response", END)

    return workflow.compile()

# Initialize the workflow
chat_workflow = create_chat_workflow()

# Pydantic models
class ChatMessage(BaseModel):
    message: str
    prompt_type: str = "default"

class ChatResponse(BaseModel):
    response: str
    status: str = "success"
    prompt_type: str = "default"

# Welcome message for streaming
WELCOME_MESSAGE = """Hello! 👋 I'm your AI Chat Assistant, and I'm here to help you with any questions or tasks you might have.

I can assist you with:
• Answering questions on a wide range of topics
• Helping with creative writing and brainstorming
• Providing technical guidance and explanations
• Problem-solving and analysis
• General conversation and advice

Feel free to ask me anything! What would you like to talk about today?"""

async def stream_welcome_message() -> AsyncGenerator[str, None]:
    """Stream the welcome message character by character."""
    words = WELCOME_MESSAGE.split()
    for i, word in enumerate(words):
        if i > 0:
            yield " "
        for char in word:
            yield char
            await asyncio.sleep(0.02)  # Small delay for typing effect
        await asyncio.sleep(0.05)  # Slightly longer pause between words

@app.get("/")
async def root():
    return {"message": "AI Chat Assistant API is running with LangGraph"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.get("/api/prompts")
async def get_available_prompts():
    """Get all available prompt types."""
    return {"prompts": list(prompt_manager.get_available_prompts().keys())}

@app.get("/api/welcome")
async def stream_welcome():
    """Stream the welcome message to guide the user."""
    async def generate():
        async for chunk in stream_welcome_message():
            # Send each character as JSON
            data = {"content": chunk, "done": False}
            yield f"data: {json.dumps(data)}\n\n"

        # Send completion signal
        data = {"content": "", "done": True}
        yield f"data: {json.dumps(data)}\n\n"

    return StreamingResponse(
        generate(),
        media_type="text/plain",
        headers={"Cache-Control": "no-cache", "Connection": "keep-alive"}
    )

@app.post("/api/chat", response_model=ChatResponse)
async def chat_with_ai(chat_data: ChatMessage):
    try:
        # Prepare initial state
        initial_state = {
            "messages": [HumanMessage(content=chat_data.message)],
            "current_prompt_type": chat_data.prompt_type,
            "response": ""
        }

        # Run the workflow
        result = chat_workflow.invoke(initial_state)

        return ChatResponse(
            response=result["response"],
            status="success",
            prompt_type=result["current_prompt_type"]
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing chat: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
