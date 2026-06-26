from enum import Enum

from langchain_ollama import ChatOllama
from langchain.agents import create_agent


class ToolCallStatus(str, Enum):
    ERROR: str = "error"
    SUCCESS: str = "success"


class ChatAgent:
    def __init__(self, **kwargs):
        self.bot = ChatOllama(**kwargs)
        self.agent = create_agent(self.bot)
