from app.storage import save_history
from app.chat import messages
from app.chat import chat_stream

while True:
    
    user_input = input("\n你: ")
    
    if user_input == "exit":
        break
    
    print("\nAI: ", end="", flush=True)
    
    ai_reply = chat_stream(user_input)
    
    save_history(
        [m for m in messages if m["role"] != "system"]
    )
    