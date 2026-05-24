from fastapi import FastAPI
from pydantic import BaseModel  #BaseModel是fastapi的数据校验系统，自动解析json
from fastapi.responses import FileResponse

from app.chat import ChatEngine

app = FastAPI()   #app是整个Web Application

engine = ChatEngine() #大模型聊天逻辑

class ChatRequest(BaseModel):
    message: str

@app.get("/")   #Route 当有人ge网站根路径时，执行下列函数
def home():
    return FileResponse("static/index.html")   #把html文件返回给浏览器

@app.post("/chat")
def chat(req: ChatRequest):
    
    user_message = req.message  #req已经不是JSON,而是解析好的python对象
    
    ai_reply = ""
    
    for chunk in engine.chat_stream(user_message):
        
        if chunk:
            ai_reply += chunk
    
    return {
        "reply":ai_reply
    }