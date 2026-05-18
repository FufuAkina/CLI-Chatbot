from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()

# 创建一个api连接器，客户端
client = OpenAI(
    api_key = os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com"
)

# 发起请求
response = client.chat.completions.create(
    model="deepseek-chat",
    messages=[
        {"role":"user", "content":"你好"}
    ]
)

print(response.choices[0].message.content)