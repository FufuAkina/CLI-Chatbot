class CommandHandler:
    def __init__(self, engine):
        self.engine =  engine
        
        self.commands = {
            "/reset": self.reset,
            "/history": self.history,
            "/exit": self.exit,
            "/help": self.help
        }
        
        self.running = True
        
    def handle(self, user_input):
        if user_input.startswith("/"):
            cmd = user_input.strip()
            
            if cmd in self.commands:
                return self.commands[cmd]()
            else:
                print("[Unkown Command] 输入/help 查看可用命令")
                return None
            
        return "chat" # 普通对话
    
    def reset(self):
        self.engine.reset()
        print("[System] 已重置对话")
        
    def history(self):
        print(self.engine.history())
        
    def exit(self):
        print("[System] 退出中…")
        self.running = False
        
    def help(self):
        print(
        """
    可用命令：
    
    /reset    重置对话
    /history  查看历史
    /exit     退出程序
    /help     帮助
        """
        )