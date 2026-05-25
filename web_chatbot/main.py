from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, field_validator
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
MAX_MESSAGE_LENGTH = 4000

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

    @field_validator('message')
    @classmethod
    def validate_message(cls, v):
        if not v or not v.strip():
            raise ValueError('消息不能为空')
        if len(v) > MAX_MESSAGE_LENGTH:
            raise ValueError(f'消息长度不能超过 {MAX_MESSAGE_LENGTH} 字符')
        return v.strip()

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
        try:
            yield f"SESSION_ID:{session_id}\n"

            stream_result = engine.chat_stream(req.message)

            if stream_result is None:
                yield "ERROR:API调用失败，请稍后重试"
                return

            for chunk in stream_result:
                if chunk:
                    yield chunk

        except Exception as e:
            yield f"ERROR:发生错误: {str(e)}"

    return StreamingResponse(generate(), media_type="text/plain")