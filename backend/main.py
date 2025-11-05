#!/usr/bin/env python3
"""
FastAPI Backend for Google Drive Chat
Integrates Claude Agent SDK with custom Google Drive MCP server
"""

import os
import sys
from pathlib import Path
from typing import Optional, AsyncGenerator
import json

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import asyncio

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import our agent
from backend.agent import get_agent


app = FastAPI(title="Google Drive Chat API")

# Configure CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],  # Next.js dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Models
class ChatMessage(BaseModel):
    message: str
    session_id: Optional[str] = None


class ChatResponse(BaseModel):
    response: str
    session_id: str


# In-memory session storage (replace with database in production)
sessions = {}


@app.get("/")
async def root():
    """Health check endpoint."""
    return {
        "status": "ok",
        "service": "Google Drive Chat API",
        "version": "0.1.0"
    }


@app.get("/api/health")
async def health_check():
    """Health check for the API."""
    return {"status": "healthy"}


@app.post("/api/chat", response_model=ChatResponse)
async def chat(chat_message: ChatMessage):
    """
    Send a message to the Claude agent and get a response.
    This is a simple HTTP endpoint (non-streaming).
    """
    session_id = chat_message.session_id or f"session_{len(sessions) + 1}"

    if session_id not in sessions:
        sessions[session_id] = {
            "messages": [],
            "created_at": "now"
        }

    # Store the message
    sessions[session_id]["messages"].append({
        "role": "user",
        "content": chat_message.message
    })

    # Get conversation history (all messages except the current one we just added)
    conversation_history = sessions[session_id]["messages"][:-1] if len(sessions[session_id]["messages"]) > 1 else None

    # Get agent and query it
    agent = get_agent()
    response_text = await agent.query(
        chat_message.message,
        session_id=session_id,
        conversation_history=conversation_history
    )

    sessions[session_id]["messages"].append({
        "role": "assistant",
        "content": response_text
    })

    return ChatResponse(
        response=response_text,
        session_id=session_id
    )


@app.websocket("/api/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for streaming chat responses from Claude Agent.
    """
    await websocket.accept()

    try:
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            message_data = json.loads(data)

            user_message = message_data.get("message", "")
            session_id = message_data.get("session_id", f"ws_session_{id(websocket)}")

            # Initialize session if needed
            if session_id not in sessions:
                sessions[session_id] = {
                    "messages": [],
                    "created_at": "now"
                }

            # Store user message
            sessions[session_id]["messages"].append({
                "role": "user",
                "content": user_message
            })

            # Send acknowledgment
            await websocket.send_json({
                "type": "ack",
                "session_id": session_id
            })

            # Stream response from Claude Agent
            agent = get_agent()
            full_response = ""

            # Get conversation history (all messages except the current one we just added)
            # This provides full context to the agent
            conversation_history = sessions[session_id]["messages"][:-1] if len(sessions[session_id]["messages"]) > 1 else None

            async for chunk in agent.stream_query(
                user_message,
                session_id=session_id,
                conversation_history=conversation_history
            ):
                full_response += chunk
                await websocket.send_json({
                    "type": "chunk",
                    "content": chunk
                })

            # Send completion signal
            await websocket.send_json({
                "type": "done",
                "content": full_response
            })

            # Store assistant response
            sessions[session_id]["messages"].append({
                "role": "assistant",
                "content": full_response
            })

    except WebSocketDisconnect:
        print(f"Client disconnected")
    except Exception as e:
        print(f"WebSocket error: {e}")
        await websocket.send_json({
            "type": "error",
            "content": str(e)
        })


@app.get("/api/sessions")
async def list_sessions():
    """List all active chat sessions."""
    return {
        "sessions": [
            {
                "session_id": sid,
                "message_count": len(session["messages"]),
                "created_at": session["created_at"]
            }
            for sid, session in sessions.items()
        ]
    }


@app.get("/api/sessions/{session_id}")
async def get_session(session_id: str):
    """Get details of a specific session."""
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")

    return {
        "session_id": session_id,
        "messages": sessions[session_id]["messages"],
        "created_at": sessions[session_id]["created_at"]
    }


@app.delete("/api/sessions/{session_id}")
async def delete_session(session_id: str):
    """Delete a session."""
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")

    del sessions[session_id]
    return {"status": "deleted", "session_id": session_id}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
