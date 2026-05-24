from fastapi import FastAPI
from pydantic import BaseModel  #BaseModel是fastapi的数据校验系统，自动解析json
from fastapi.responses import FileResponse
from fastapi.responses import StreamingResponse

from app.chat import ChatEngine

app = FastAPI()   #app是整个Web Application

class ChatRequest(BaseModel):
    message: str

@app.get("/")   #Route 当有人ge网站根路径时，执行下列函数
def home():
    return FileResponse("static/index.html")   #把html文件返回给浏览器

@app.post("/chat")
def chat(req: ChatRequest):
    
    engine = ChatEngine()    #每次请求独立
    
    def generate():
        for chunk in engine.chat_stream(req.message):
            if chunk:
                yield chunk
                
    return StreamingResponse(generate(), media_type="text/plain")