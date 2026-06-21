from dotenv import load_dotenv
from os import getenv

load_dotenv()
MODEL = getenv("CHAT_MODEL")
ENDPOINT = getenv("CHAT_ENDPOINT")
