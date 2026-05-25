from app.storage import save_history
from app.chat import ChatEngine
from app.commands import CommandHandler

from colorama import  init, Fore, Style
init(autoreset=True)

import time

engine = ChatEngine(load_history_file=True)
cmd = CommandHandler(engine)

def print_user(text):
    print(Fore.CYAN + "你： " + Style.RESET_ALL + text)

def print_ai_start():
    print(Fore.GREEN + "\n AI: ", end="", flush=True)
    
def print_system(text):
    print(Fore.YELLOW + "[System]" + text)
    
while cmd.running:
    
    user_input = input(Fore.CYAN + "\n你: ")
    
    result = cmd.handle(user_input)
    
    # 如果是命令（不是聊天）
    if result != "chat":
        continue
    
    print_ai_start()
    
    try:
        for char in engine.chat_stream(user_input):
            print(char, end="", flush=True)
            time.sleep(0.01)   # Streaming逐词出现
    
    except KeyboardInterrupt:
        print(Fore.RED + "\n[中断]")
        
    print()
    
    save_history(
        [m for m in engine.messages 
         if m["role"] != "system"]
    )
    