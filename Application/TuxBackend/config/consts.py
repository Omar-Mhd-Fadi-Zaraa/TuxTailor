from dotenv import load_dotenv
from os import getenv

load_dotenv()
CHAT_MODEL = getenv("CHAT_MODEL")
OLLAMA_BASE_URL = getenv("OLLAMA_BASE_URL")
JWT_SECRET_KEY = getenv("JWT_SECRET_KEY")
JWT_ALGORITHM = getenv("JWT_ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))
