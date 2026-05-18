from app.client import client
from app.storage import load_history
from app.config import MODEL_NAME

messages = [
    {
        "role": "system",
        "content": "You are a helpful assistant."
    }
]

messages.extend(load_history())

# 核心函数：聊天入口
def chat_stream(user_input):
    
    global messages
    
    messages.append({
        "role":"user",
        "content": user_input    
    })
    
    stream = client.chat.completions.create(
        model = MODEL_NAME,
        messages = messages,
        stream = True
    )
    
    ai_reply = ""
    
    for chunk in stream:
        delta = chunk.choices[0].delta.content
        if delta:
            print(delta, end="", flush=True)
            ai_reply += delta
    print
    
    messages.append({
        "role": "assistant",
        "content": ai_reply
    })
    
    return ai_reply