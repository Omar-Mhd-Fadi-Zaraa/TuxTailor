from dotenv import load_dotenv
from os import getenv

load_dotenv()
CHAT_MODEL = getenv("CHAT_MODEL")
OLLAMA_BASE_URL = getenv("OLLAMA_BASE_URL")
