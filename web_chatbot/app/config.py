from dotenv import load_dotenv
import os

load_dotenv()

API_KEY = os.getenv("DEEPSEEK_API_KEY")

BASE_URL = "https://api.deepseek.com"

MODEL_NAME = "deepseek-chat"

HISTORY_FILE = "data/chat_history.json"