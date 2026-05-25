from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.responses import FileResponse
from fastapi.responses import StreamingResponse
from typing import Optional
import time

from app.chat import ChatEngine
import uuid

app = FastAPI()

sessions = {}
session_last_active = {}

MAX_SESSION_AGE = 3600

def cleanup_old_sessions():
    current_time = time.time()
    expired_sessions = [
        sid for sid, last_active in session_last_active.items()
        if current_time - last_active > MAX_SESSION_AGE
    ]
    for sid in expired_sessions:
        sessions.pop(sid, None)
        session_last_active.pop(sid, None)

class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None

class SessionResponse(BaseModel):
    session_id: str

@app.get("/")
def home():
    return FileResponse("static/index.html")

@app.post("/session")
def create_session():
    session_id = str(uuid.uuid4())
    sessions[session_id] = ChatEngine()
    return SessionResponse(session_id=session_id)

@app.post("/chat")
def chat(req: ChatRequest):

    cleanup_old_sessions()

    if not req.session_id or req.session_id not in sessions:
        session_id = str(uuid.uuid4())
        sessions[session_id] = ChatEngine()
    else:
        session_id = req.session_id

    session_last_active[session_id] = time.time()

    engine = sessions[session_id]

    def generate():
        yield f"SESSION_ID:{session_id}\n"
        for chunk in engine.chat_stream(req.message):
            if chunk:
                yield chunk

    return StreamingResponse(generate(), media_type="text/plain")