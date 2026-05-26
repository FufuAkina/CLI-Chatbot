from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, field_validator
from fastapi.responses import FileResponse
from fastapi.responses import StreamingResponse
from typing import Optional
from contextlib import asynccontextmanager
import time

from app.chat import ChatEngine
from app.logger import logger
from app.prompts import get_prompt_template, list_all_templates
import uuid

@asynccontextmanager
async def lifespan(app: FastAPI):
    # 启动
    logger.info("应用启动")
    yield
    # 关闭
    logger.info(f"应用关闭，清理 {len(sessions)} 个会话")

app = FastAPI(lifespan=lifespan)

# 性能监控中间件
@app.middleware("http")
async def performance_middleware(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time

    # 记录慢请求（超过1秒）
    if process_time > 1.0:
        logger.warning(f"慢请求: {request.method} {request.url.path} - {process_time:.2f}s")
    else:
        logger.info(f"{request.method} {request.url.path} - {process_time:.2f}s")

    response.headers["X-Process-Time"] = str(process_time)
    return response

# 添加 CORS 支持
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
    if expired_sessions:
        logger.info(f"清理 {len(expired_sessions)} 个过期会话")
    for sid in expired_sessions:
        sessions.pop(sid, None)
        session_last_active.pop(sid, None)

class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None
    role: Optional[str] = None
    custom_prompt: Optional[str] = None

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

@app.get("/roles")
def get_roles():
    """获取所有可用的角色模板"""
    return {"roles": list_all_templates()}

@app.post("/session")
def create_session():
    session_id = str(uuid.uuid4())
    sessions[session_id] = ChatEngine()
    return SessionResponse(session_id=session_id)

@app.post("/chat")
def chat(req: ChatRequest):

    cleanup_old_sessions()

    # 获取 system prompt（优先使用自定义 prompt）
    if req.custom_prompt:
        system_prompt = req.custom_prompt
        role_name = "自定义角色"
    else:
        role_key = req.role or "default"
        template = get_prompt_template(role_key)
        system_prompt = template["system_prompt"]
        role_name = template["name"]

    if not req.session_id or req.session_id not in sessions:
        session_id = str(uuid.uuid4())
        sessions[session_id] = ChatEngine(system_prompt=system_prompt)
        logger.info(f"创建新会话: {session_id}, 角色: {role_name}")
    else:
        session_id = req.session_id

    session_last_active[session_id] = time.time()

    engine = sessions[session_id]

    logger.info(f"会话 {session_id[:8]} 收到消息: {req.message[:50]}...")

    def generate():
        try:
            yield f"SESSION_ID:{session_id}\n"

            stream_result = engine.chat_stream(req.message)

            if stream_result is None:
                logger.error(f"会话 {session_id[:8]} API调用失败")
                yield "ERROR:API调用失败，请稍后重试"
                return

            for chunk in stream_result:
                if chunk:
                    yield chunk

            logger.info(f"会话 {session_id[:8]} 响应完成")

        except Exception as e:
            logger.error(f"会话 {session_id[:8]} 发生错误: {str(e)}")
            yield f"ERROR:发生错误: {str(e)}"

    return StreamingResponse(generate(), media_type="text/plain")