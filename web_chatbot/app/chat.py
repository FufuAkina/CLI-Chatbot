from app.client import client
from app.storage import load_history
from app.config import MODEL_NAME, DEFAULT_SYSTEM_PROMPT

import openai
import time
import threading
import itertools
import sys

# 优化: loading animation
def loading(stop_flag):
    for c in itertools.cycle(["|", "/", "-", "\\"]):
        if stop_flag["stop"]:
            break
        sys.stdout.write("\rAI thinking " + c)
        sys.stdout.flush()
        time.sleep(0.1)
        
class ChatEngine:

    def __init__(self, load_history_file=False, show_loading=False, system_prompt=None):

        self.system_prompt = system_prompt or DEFAULT_SYSTEM_PROMPT

        self.messages = [
            {
                "role": "system",
                "content": self.system_prompt
            }
        ]

        if load_history_file:
            self.messages.extend(load_history())

        self.show_loading = show_loading

    def chat_stream(self, user_input, max_retries=3):

        if not user_input.strip():
            return None

        self.messages.append({
            "role": "user",
            "content": user_input
        })

        ai_reply = ""

        # 在调用API之前:loading animation (仅CLI模式)
        stop_flag = {"stop": False}
        t = None

        if self.show_loading:
            t = threading.Thread(
                target=loading,
                args=(stop_flag,)
            )
            t.start()

        for attempt in range(max_retries):

            try:

                stream = client.chat.completions.create(
                    model = MODEL_NAME,
                    messages = self.messages,
                    stream = True,
                    timeout = 30
                )

                # 一旦进入stream， 就停止loading
                if self.show_loading:
                    stop_flag["stop"] = True
                    t.join()
                    print("\r", end="")

                for chunk in stream:
                    try:
                        delta = chunk.choices[0].delta.content
                        if delta:
                            ai_reply += delta
                            yield delta

                    except Exception:
                        continue

                # 跳出retry
                break

            except openai.RateLimitError:
                wait_time = 2 ** attempt
                if self.show_loading:
                    print(f"\n[Ratelimit] 等待 {wait_time}s 后重试…")
                time.sleep(wait_time)

            except openai.APITimeoutError:
                if self.show_loading:
                    print("\n[Timeout] 请求超时， 重试中…")

            except openai.APIConnectionError:
                if self.show_loading:
                    print("\n[Network] 网络错误，重试中…")

            except Exception as e:
                if self.show_loading:
                    print(f"\n[Unknown Error] {e}")

                # 回滚user message(防止污染)
                if self.messages and self.messages[-1]["role" ] == "user" :
                    self.messages.pop()

                return None

            finally:
                if len(ai_reply.strip()) > 0:
                    self.messages.append(
                    {
                        "role": "assistant",
                        "content": ai_reply
                    }
                    )
                
        
          
    
    def reset(self):
        self.messages = [
            {
                "role":"system",
                "content": self.system_prompt
            }
        ]
        
    def history(self):
        result = ""
        
        for msg in self.messages:
            
            role = msg["role"]
            content = msg["content"]
            
            result += f"{role}: \n{content} \n\n"
        
        return result