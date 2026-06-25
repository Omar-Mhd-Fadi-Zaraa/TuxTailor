from fastapi.requests import Request

from db.db import Database
from models.messages import (
    UserMessage,
    AssistantMessage,
    AssistantBehaviorMessage,
    ToolResponseMessage,
)


def get_db(request: Request) -> Database:
    return request.app.state.db


async def AddUserMessage(
    userMessage: UserMessage, database: Database
) -> RuntimeError | None:
    try:
        await database.AddMessage(
            userMessage.chat_id,
            userMessage.user_id,
            userMessage.lcmsg.content,
            userMessage.role,
            userMessage.date_sent,
        )
    except Exception as e:
        raise RuntimeError(f"Couldntn add user message: {e}")


async def AddAiMessage(
    aiMessage: AssistantMessage, database: Database
) -> RuntimeError | None:
    try:
        await database.AddMessage(
            aiMessage.chat_id,
            aiMessage.user_id,
            aiMessage.lcmsg.content,
            aiMessage.role,
            aiMessage.date_sent,
            toolCall=True if aiMessage.lcmsg.tool_calls else False,
            toolCalls=aiMessage.lcmsg.tool_calls,
        )
    except Exception as e:
        raise RuntimeError(f"Unable to add ai message: {e}")


async def AddToolMessage(
    toolMessage: ToolResponseMessage, database: Database
) -> RuntimeError | None:
    try:
        await database.AddMessage(
            toolMessage.chat_id,
            toolMessage.user_id,
            toolMessage.lcmsg.content,
            toolMessage.role,
            toolMessage.date_sent,
            toolCallStatus=toolMessage.lcmsg.status,
            preceedingMessage=toolMessage.preceeding_message.content,
        )
    except Exception as e:
        raise RuntimeError(f"Couldnt add tool message: {e}")


async def AddSystemMessage(
    systemMessage: AssistantBehaviorMessage, database: Database
) -> RuntimeError | None:
    try:
        await database.AddMessage(
            systemMessage.chat_id,
            systemMessage.user_id,
            systemMessage.lcmsg.content,
            systemMessage.role,
            systemMessage.date_sent,
        )
    except Exception as e:
        raise RuntimeError(f"Couldnt add system message: {e}")
