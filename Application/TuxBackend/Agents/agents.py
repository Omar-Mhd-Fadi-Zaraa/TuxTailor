from collections.abc import AsyncIterator
from enum import Enum
from typing import Any, AsyncGenerator, Dict, List
import asyncio
import json

from langchain_ollama import ChatOllama
from langchain_core.messages import AnyMessage
from langchain.agents import create_agent

_INTERLEAVE_DONE = object()


async def _async_interleave(
    *streams: AsyncIterator[tuple[str, Any]],
) -> AsyncGenerator[tuple[str, Any], None]:
    queue: asyncio.Queue[Any] = asyncio.Queue()
    tasks: list[asyncio.Task[None]] = []

    async def pump(stream: AsyncIterator[tuple[str, Any]]) -> None:
        async for item in stream:
            await queue.put(item)
        await queue.put(_INTERLEAVE_DONE)

    for stream in streams:
        tasks.append(asyncio.create_task(pump(stream)))

    finished = 0
    try:
        while finished < len(tasks):
            item = await queue.get()
            if item is _INTERLEAVE_DONE:
                finished += 1
            else:
                yield item
    finally:
        for task in tasks:
            if not task.done():
                task.cancel()
        await asyncio.gather(*tasks, return_exceptions=True)


async def _message_events(stream: Any) -> AsyncIterator[tuple[str, Any]]:
    async for message in stream.messages:
        yield ("messages", message)


async def _tool_call_events(stream: Any) -> AsyncIterator[tuple[str, Any]]:
    async for call in stream.tool_calls:
        yield ("tool_calls", call)


class ToolCallStatus(str, Enum):
    ERROR: str = "error"
    SUCCESS: str = "success"


class ChatAgent:
    def __init__(self, **kwargs):
        self.bot = ChatOllama(**kwargs)
        self.agent = create_agent(self.bot)

    async def invokeAgent(
        self, messages: List[AnyMessage]
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """Yield NDJSON-compatible dicts for agent text, tool calls, and completion."""
        stream = await self.agent.astream_events(
            input={"messages": messages}, version="v3"
        )

        async for kind, item in _async_interleave(
            _message_events(stream),
            _tool_call_events(stream),
        ):
            if kind == "messages":
                async for token in item.text:
                    yield json.dumps({"type": "text", "content": token}) + "\n"
            elif kind == "tool_calls":
                yield json.dumps(
                    {
                        "type": "tool_start",
                        "toolName": item.tool_name,
                        "toolInput": item.input,
                    }
                ) + "\n"
                yield json.dumps(
                    {
                        "type": "tool_end",
                        "toolName": item.tool_name,
                        "toolOutput": item.output,
                    }
                ) + "\n"

        yield json.dumps({"type": "text", "content": token}) + "\n"
