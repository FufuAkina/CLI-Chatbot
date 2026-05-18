from app.client import client
from app.storage import load_history
from app.config import MODEL_NAME

class ChatEngine:
    
    def __init__(self):
        
        self.messages = [
            {
                "role": "system",
                "content": "You are a helpful assistant."
            }
        ]
        
        self.messages.extend(load_history())
        
    def chat_stream(self, user_input):
    
        self.messages.append({
            "role": "user",
            "content": user_input
         })
    
        stream = client.chat.completions.create(
            model = MODEL_NAME,
            messages = self.messages,
            stream = True
        )
    
        ai_reply = ""
    
        for chunk in stream:
            delta = chunk.choices[0].delta.content
            if delta:
               ai_reply += delta
                
    
        self.messages.append(
            {
                "role": "assistant",
                "content": ai_reply
            }
        )
        return ai_reply
    
    def reset(self):
        self.messages = [
            {
                "role":"system",
                "content": "You are a helpful assistant."
            }
        ]
        
    def history(self):
        result = ""
        
        for msg in self.messages:
            
            role = msg["role"]
            content = msg["content"]
            
            result += f"{role}: \n{content} \n\n"
        
        return result    
    