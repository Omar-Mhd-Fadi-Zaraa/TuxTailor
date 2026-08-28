import json
import sqlite3

from fastapi.requests import Request

from db.db import Database
from middlewares.auth import hash_password, verify_password
from models.messages import (
    AssistantBehaviorMessage,
    AssistantMessage,
    ToolResponseMessage,
    UserMessage,
)
from models.schemas import ChatAddRequest, UserAddRequest


def get_db(request: Request) -> Database:
    return request.app.state.db


async def AddUserMessage(userMessage: UserMessage, database: Database) -> None:
    try:
        if isinstance(userMessage.lcmsg.content, list):
            raise TypeError("Message content must be a string")
        await database.AddMessage(
            userMessage.chat_id,
            userMessage.user_id,
            userMessage.lcmsg.content,
            userMessage.role,
            userMessage.date_sent,
        )
    except sqlite3.OperationalError as e:
        raise RuntimeError(f"Couldn't add user message: {e}")


async def AddAiMessage(aiMessage: AssistantMessage, database: Database) -> None:
    try:
        if isinstance(aiMessage.lcmsg.content, list):
            raise TypeError("Message content must be a string")
        tool_calls = aiMessage.lcmsg.tool_calls
        await database.AddMessage(
            aiMessage.chat_id,
            aiMessage.user_id,
            aiMessage.lcmsg.content,
            aiMessage.role,
            aiMessage.date_sent,
            toolCall=bool(tool_calls),
            toolCalls=json.dumps(tool_calls) if tool_calls else None,
        )
    except sqlite3.OperationalError as e:
        raise RuntimeError(f"Couldn't add ai message: {e}")


async def AddToolMessage(toolMessage: ToolResponseMessage, database: Database) -> None:
    try:
        if isinstance(toolMessage.lcmsg.content, list):
            raise TypeError("Message content must be a string")
        await database.AddMessage(
            toolMessage.chat_id,
            toolMessage.user_id,
            toolMessage.lcmsg.content,
            toolMessage.role,
            toolMessage.date_sent,
            toolCallStatus=toolMessage.lcmsg.status,
            preceedingMessage=toolMessage.preceeding_message,
        )
    except sqlite3.OperationalError as e:
        raise RuntimeError(f"Couldn't add tool message: {e}")


async def AddSystemMessage(
    systemMessage: AssistantBehaviorMessage, database: Database
) -> None:
    try:
        if isinstance(systemMessage.lcmsg.content, list):
            raise TypeError("Message content must be a string")
        await database.AddMessage(
            systemMessage.chat_id,
            systemMessage.user_id,
            systemMessage.lcmsg.content,
            systemMessage.role,
            systemMessage.date_sent,
        )
    except sqlite3.OperationalError as e:
        raise RuntimeError(f"Couldnt add system message: {e}")


async def AddChat(chat: ChatAddRequest, database: Database) -> int | None:
    try:
        new_row_id = await database.AddChat(chat.user_id, chat.title, chat.date_created)
    except sqlite3.OperationalError as e:
        raise RuntimeError(f"Couldn't add chat: {e}")

    return new_row_id


async def AddUser(user: UserAddRequest, database: Database) -> int | None:
    try:
        hashed_password = hash_password(user.password)
        user_id = await database.AddUser(
            user.user_name,
            hashed_password,
            user.level,
            user.date_created,
            user.system_prompt,
            user.distro_of_choice,
        )
    except sqlite3.OperationalError as e:
        raise RuntimeError(f"Couldn't add user: {e}")

    return user_id


async def Login(
    user_name: str, password: str, database: Database
) -> tuple[int | None, bool]:
    try:
        row = await database.GetUser(user_name)
        if row is None:
            return None, False
        user_id, hashed_pass = row
        found = verify_password(password, hashed_pass)
    except sqlite3.OperationalError as e:
        raise RuntimeError(f"Couldn't log in: {e}")

    return user_id, found


async def GetUserSysMessage(user_id: int, database: Database) -> str | None:
    try:
        row = await database.GetUserSysPrompt(user_id)
        sys_prompt = row[0] if row[0] else None
    except sqlite3.OperationalError as e:
        raise RuntimeError(f"Couldn't fetch user system prompt: {e}")

    return sys_prompt


async def GetUserChats(user_id: int, database: Database) -> list[tuple[int, str]]:
    try:
        rows = await database.GetUserChats(user_id)
        chat_ids = [(row[0], row[2]) for row in rows] if rows else []
    except sqlite3.OperationalError as e:
        raise RuntimeError(f"Could not get user chats for user {user_id}: {e}")

    return chat_ids


async def GetChatMessages(
    chat_id: int, database: Database
) -> list[tuple[int, str, str]]:
    try:
        messages = await database.GetChatMessages(chat_id)
        message_contents = (
            [(message[0], message[3], message[4]) for message in messages]
            if messages
            else []
        )
    except sqlite3.OperationalError as e:
        raise RuntimeError(f"Could not get chat messages for chat {chat_id}: {e}")

    return message_contents


async def UpdateUser(
    user_id: int,
    databse: Database,
    level: str | None = None,
    system_prompt: str | None = None,
    distro_of_choice: str | None = None,
) -> None:
    try:
        await databse.UpdateUser(user_id, level, system_prompt, distro_of_choice)
    except sqlite3.OperationalError as e:
        raise RuntimeError(f"Couldn't update user: {e}")


async def UpdateChatInfo(
    chat_id: int,
    database: Database,
    title: str | None = None,
    system_prompt: str | None = None,
) -> None:
    try:
        await database.UpdateChat(chat_id, title, system_prompt)
    except sqlite3.OperationalError as e:
        raise RuntimeError(f"Couldn't update chat info: {e}")
