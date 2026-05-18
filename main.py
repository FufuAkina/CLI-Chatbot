from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()

# 创建一个api连接器，客户端
client = OpenAI(
    api_key = os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com"
)

# 聊天记录
messages = []
# 循环，多轮对话
while True:
    # 获取用户输入
    user_input =  input("你： ")
    
    if user_input == "exit":
        break
    
    # 保存用户消息
    messages.append(
        {
            "role": "user",
            "content": user_input
        }
    )
    
    # 发送请求
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=messages
    )
    
    ai_reply = response.choices[0].message.content

    print("AI:")
    print(ai_reply)
    
    messages.append(
        {
            "role": "assistant",
            "content": ai_reply
        }
    )