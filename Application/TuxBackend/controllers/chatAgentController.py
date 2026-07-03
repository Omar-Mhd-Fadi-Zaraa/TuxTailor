import asyncio
import json
from typing import Any, AsyncGenerator

from fastapi.requests import Request
from langchain_core.messages import (
    AIMessage,
    AnyMessage,
    HumanMessage,
    SystemMessage,
    ToolMessage,
)

from Agents.agents import ChatAgent
from db.db import Database
from controllers.databaseController import (
    AddAiMessage,
    AddToolMessage,
)
from models.messages import (
    AssistantMessage,
    ToolResponseMessage,
)
from models.schemas import ChatAgentRequest, Role


def get_chat_agent(request: Request) -> ChatAgent:
    return request.app.state.chat_agent


def to_langchain_messages(rows: list[Any]) -> list[AnyMessage]:
    messages: list[AnyMessage] = []
    for row in rows:
        match row[3]:
            case Role.USER:
                messages.append(HumanMessage(content=row[2]))
            case Role.SYSTEM:
                messages.insert(0, SystemMessage(content=row[2]))
            case Role.ASSISTANT:
                messages.append(
                    AIMessage(
                        content=row[2],
                        tool_calls=json.loads(row[5]) if row[5] else [],
                    )
                )
            case Role.TOOL:
                messages.append(ToolMessage(content=row[2], status=row[7]))

    return messages


def _ai_message_content(message: AIMessage) -> str:
    content = message.content
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts: list[str] = []
        for block in content:
            if isinstance(block, str):
                parts.append(block)
            elif isinstance(block, dict) and block.get("type") == "text":
                parts.append(str(block.get("text", "")))
        return "".join(parts)
    return str(content)


def _ai_message_event(message: AIMessage) -> str:
    return (
        json.dumps(
            {
                "type": "ai_message",
                "content": _ai_message_content(message),
                "toolCalls": message.tool_calls or [],
            }
        )
        + "\n"
    )


async def _drain_tool_calls(stream: Any) -> None:
    async for _ in stream.tool_calls:
        pass


async def stream_filtered_response(
    agent: ChatAgent,
    messages: list[AnyMessage],
    result: dict[str, Any],
) -> AsyncGenerator[str, None]:
    """Stream every AIMessage to the client; capture the full agent output when done."""
    input_len = len(messages)
    stream = await agent.agent.astream_events(
        input={"messages": messages}, version="v3"
    )

    drain_task = asyncio.create_task(_drain_tool_calls(stream))
    try:
        async for message in stream.messages:
            async for token in message.text:
                if token:
                    yield json.dumps({"type": "text", "content": token}) + "\n"

            finalized = await message.output
            if isinstance(finalized, AIMessage):
                yield _ai_message_event(finalized)
    finally:
        await drain_task

    final_state = await stream.output()
    result["messages"] = final_state["messages"][input_len:]


async def persist_agent_messages(
    messages: list[AnyMessage],
    request: ChatAgentRequest,
    database: Database,
) -> None:
    last_ai_message: AIMessage | None = None

    for msg in messages:
        if isinstance(msg, AIMessage):
            assistant = AssistantMessage(
                request,
                _ai_message_content(msg),
                tool_calls=msg.tool_calls or [],
            )
            await AddAiMessage(assistant, database)
            last_ai_message = msg
        elif isinstance(msg, ToolMessage):
            if last_ai_message is None:
                raise RuntimeError("Tool message without preceding AI message")
            content = msg.content if isinstance(msg.content, str) else str(msg.content)
            tool = ToolResponseMessage(
                _ai_message_content(last_ai_message),
                request,
                content,
                status=getattr(msg, "status", None),
                tool_call_id=msg.tool_call_id,
                name=msg.name,
            )
            await AddToolMessage(tool, database)
