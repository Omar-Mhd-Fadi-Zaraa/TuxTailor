from enum import Enum

from langchain.agents import create_agent
from langchain_ollama import ChatOllama

from .agent_tools import search_the_internet


class ToolCallStatus(str, Enum):
    ERROR = "error"
    SUCCESS = "success"


class ChatAgent:
    def __init__(self, **kwargs):
        self.bot = ChatOllama(**kwargs)
        self.agent = create_agent(self.bot, tools=[search_the_internet])
