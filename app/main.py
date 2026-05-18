from app.storage import save_history
from app.chat import ChatEngine

engine = ChatEngine()

while True:
    
    user_input = input("\n你: ")
    
    if user_input == "exit":
        break
    
    if user_input == "reset":
        engine.reset()
        print("OK! 已重置对话。(●ˇ∀ˇ●)")
        continue
    
    if user_input == "history":
        print(engine.history())
        continue
    
    print("\nAI: ", end="", flush=True)
    
    for char in engine.chat_stream(user_input):
        print(char, end="", flush=True)
    
    ai_reply = engine.chat_stream(user_input)
    
    
    save_history(
        [m for m in engine.messages 
         if m["role"] != "system"]
    )
    