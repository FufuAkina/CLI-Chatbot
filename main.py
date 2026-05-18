from openai import OpenAI
from dotenv import load_dotenv
import os
import json

load_dotenv()

# 创建一个api连接器，客户端
client = OpenAI(
    api_key = os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com"
)

# 读取历史消息
HISTORY_FILE = "chat_history.json"

def load_history():
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_history(messages):
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(messages, f, ensure_ascii=False, indent=2)
        
# 加system prompt
messages = [
    {
        "role": "system",
        "content": "You are a helpful, concise assistant."
    }
]

messages.extend(load_history())  # 加载历史

while True:
    # 获取用户输入
    user_input =  input("你： ")
    
    if not user_input.strip():
        continue
    
    if user_input == "exit":
        break
    
    if user_input == "/reset":
        messages = [messages[0]]
        print("🆗 对话已重置")
        continue
    
    if user_input =="/history":
        for m in messages:
            role = m["role"]
            content = m["content"]
            print(f"{role}: {content}")
        continue
            
    
    # 保存用户消息
    messages.append(
        {
            "role": "user",
            "content": user_input
        }
    )
    
    # streaming + response
    print("AI: ", end="")
    
    try:
        stream = client.chat.completions.create(
            model = "deepseek-chat",
            messages = messages,
            stream = True
        )  # 此时stream是一个数据流对象，不是完整的response
    except Exception as e:
        print("\n × API Error:", e)
        continue
    
    ai_reply = ""
    
    for chunk in stream:       # chunk: 一小块返回数据
        
        delta = chunk.choices[0].delta.content
        
        if delta:
            print(delta, end="", flush=True)
            ai_reply += delta
            
    print()
    
    messages.append({
        "role": "assistant",
        "content": ai_reply
    })
    
    # 保存对话历史（不含system）
    save_history([m for m in messages if m["role"] != "system"])
    # 加上下文长度控制，保留system和最近10轮对话
    messages = [messages[0]] + messages[-20:]