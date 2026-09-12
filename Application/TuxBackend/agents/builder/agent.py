from langchain.agents import create_agent
from langchain_ollama import ChatOllama


class BuilderAgent:
    def __init__(self, **kwargs) -> None:
        self.bot = ChatOllama(**kwargs)
        self.agent = create_agent(self.bot)
