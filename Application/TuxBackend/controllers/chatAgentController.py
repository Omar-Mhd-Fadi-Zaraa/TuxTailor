from typing import Any
import json

from fastapi.requests import Request
from langchain_core.messages import AnyMessage,HumanMessage,ToolMessage,AIMessage,SystemMessage

from Agents.agents import ChatAgent
from models.schemas import Role

def get_chat_agent(request: Request) -> ChatAgent:
    return request.app.state.chat_agent


def to_langchain_messages(rows: list[Any]) -> list[AnyMessage]:
    messages: list[AnyMessage] = []
    for row in rows:
        match row[3]:
            case Role.USER:
                messages.append(HumanMessage(content=row[2]))
            case Role.SYSTEM:
                messages.append(SystemMessage(content=row[2]))
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
