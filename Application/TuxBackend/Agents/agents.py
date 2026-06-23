from langchain_ollama import ChatOllama
from langchain_core.messages import AnyMessage
from langchain.agents import create_agent
from typing import List, AsyncGenerator, Dict, Any


class ChatAgent(ChatOllama):

    def __init__(self, name, bases, dict, /, **kwds):
        super().__init__(name, bases, dict, **kwds)
        self.agent = create_agent(self)


    """invokeAgent yields NDJSON compatible dicts for the agent response, tool call, and finally a dict showing that the response is done."""
    async def invokeAgent(
        self, messages: List[AnyMessage]
    ) -> AsyncGenerator[Dict[str, Any]]:
        stream = self.agent.astream_events(input={"messages": messages}, version="v3")

        async for kind, item in self.stream.interleave("messages", "tool_calls"):
            if kind == "messages":
                async for token in item.text:
                    yield {"type": "text", "conent": token}
            elif kind == "tool_calls":
                yield {
                    "type": "tool_start",
                    "toolName": item.tool_name,
                    "toolInput": item.input,
                }
                yield {
                    "type": "tool_end",
                    "toolName": item.tool_name,
                    "toolOutput": item.output,
                }

        yield {"type": "done", "state": self.stream.output}
