import uuid
import json
from typing import List, Optional, Dict
import os

import redis
from fastapi import FastAPI, HTTPException, Header, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from conversationalRAG import generate_reply

app = FastAPI()

# Add CORS middleware to enable cross-origin requests
# This middleware allows the frontend webpage (served from a different origin/domain)
# to make API requests to this FastAPI backend server
#
# The current settings are very permissive for development:
# - allow_origins=["*"]: Accepts requests from any domain
# - allow_credentials=True: Allows sending cookies and authentication headers
# - allow_methods=["*"]: Accepts all HTTP methods (GET, POST, etc)
# - allow_headers=["*"]: Accepts all HTTP headers
#
# For production, you should restrict these settings for security:
# - allow_origins should list only your frontend domain(s), e.g.:
#   ["https://mychatapp.com", "https://api.mychatapp.com"]
# - allow_methods should specify only needed methods, e.g.:
#   ["GET", "POST"]
# - allow_headers should list required headers, e.g.:
#   ["Content-Type", "Authorization"]
# Example production configuration:
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["https://mychatapp.com"],
#     allow_credentials=True,
#     allow_methods=["GET", "POST"],
#     allow_headers=["Content-Type", "Authorization"],
# )
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Initialize Redis client (default localhost:6379)
redis_client = redis.Redis(host="localhost", port=6379, db=0, decode_responses=True)

# TTL for each session (in seconds); adjust as needed
SESSION_TTL = 30 * 60  # 30 minutes
API_KEY = os.environ.get("API_KEY", "AdiKatan432!")  # Default to "123" if running locally

def verify_api_key(x_api_key: str = Header(...)):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API Key")

class ChatRequest(BaseModel):
    session_id: Optional[str] = None
    message: str

class SessionRequest(BaseModel):
    session_id: Optional[str] = None

class ChatResponse(BaseModel):
    session_id: str
    reply: str
    history: List[Dict[str, str]]

class SessionResponse(BaseModel):
    session_id: str


def get_or_create_session(session_id: Optional[str]) -> str:
    """
    If session_id is provided and exists in Redis, return it.
    Otherwise, generate a new UUID and initialize an empty history in Redis.
    """
    if session_id:
        if redis_client.exists(session_id):
            return session_id
    # Create new session
    new_id = str(uuid.uuid4())
    # Store an empty JSON list in Redis
    redis_client.set(new_id, json.dumps([]), ex=SESSION_TTL)
    return new_id


def fetch_history(session_id: str) -> List[Dict[str, str]]:
    raw = redis_client.get(session_id)
    if not raw:
        # If key expired or missing, treat as invalid
        raise HTTPException(status_code=404, detail="Session expired or not found")
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return []


def save_history(session_id: str, history: List[Dict[str, str]]):
    """
    Trim history to last MAX_TURNS and store back in Redis with TTL reset.
    """
    MAX_TURNS = 20
    trimmed = history[-MAX_TURNS:]
    redis_client.set(session_id, json.dumps(trimmed), ex=SESSION_TTL)


# def generate_reply(history: List[Dict[str, str]]) -> str:
#     """
#     Generate reply based on conversation history using Gemini.
#     """
#     if not history:
#         return "Hello! How can I help you today?"
    
#     # Load knowledge base
#     knowledge_base = load_knowledge_base('knowledge.jsonl')
#     return get_gemini_response(history, knowledge_base)


@app.post("/chat", response_model=ChatResponse, dependencies=[Depends(verify_api_key)])
def chat(req: ChatRequest):
    # 1. Obtain or create session_id
    session_id = get_or_create_session(req.session_id)

    # 2. Fetch existing history from Redis
    history = fetch_history(session_id)

    # 3. Append user message
    history.append({"role": "user", "text": req.message})

    # 4. Generate bot reply, append to history
    bot_reply = generate_reply(history)
    history.append({"role": "bot", "text": bot_reply})

    # 5. Save updated history (with trimming) back to Redis
    save_history(session_id, history)

    return ChatResponse(
        session_id=session_id,
        reply=bot_reply,
        history=history.copy()
    )

@app.post("/session", response_model=SessionResponse, dependencies=[Depends(verify_api_key)])
def session(req: SessionRequest):
    # 1. Obtain or create session_id
    session_id = get_or_create_session(req.session_id)

    return SessionResponse(
        session_id=session_id)

@app.get("/health")
def health_check():
    return {"status": "ok"}
