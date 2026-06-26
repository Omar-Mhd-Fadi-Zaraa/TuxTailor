from fastapi.requests import Request

from db.db import Database
from models.messages import (
    UserMessage,
    AssistantMessage,
    AssistantBehaviorMessage,
    ToolResponseMessage,
)
from middlewares.auth import hash_password,verify_password
from models.schemas import ChatAddRequest, UserAddRequest


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
        raise RuntimeError(f"Couldn't add user message: {e}")


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
        raise RuntimeError(f"Couldn't add ai message: {e}")


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
        raise RuntimeError(f"Couldnit add tool message: {e}")


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


async def AddChat(chat: ChatAddRequest, database: Database) -> RuntimeError | int:
    try:
        new_row_id = await database.AddChat(chat.user_id, chat.title, chat.date_created)
    except Exception as e:
        raise RuntimeError(f"Couldn't add chat: {e}")

    return new_row_id


async def AddUser(user: UserAddRequest, database: Database) -> RuntimeError | int:
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
    except Exception as e:
        raise RuntimeError(f"Couldn't add user: {e}")
    
    return user_id


async def Login(
    user_name: str, password: str, database: Database
) -> RuntimeError | tuple[int | None, bool]:
    try:
        row = await database.GetUser(user_name)
        if row is None:
            return None, False
        user_id, hashed_pass = row
        found = verify_password(password, hashed_pass)
    except Exception as e:
        raise RuntimeError(f"Couldn't log in: {e}")

    return user_id, found


async def GetUserSysMessage(user_id: int, database: Database) -> RuntimeError | str | None:
    try:
        row = await database.GetUserSysPrompt(user_id)
        sys_prompt = row[0] if row[0] else None
    except Exception as e:
        raise RuntimeError(f"Couldn't fetch user system prompt: {e}")

    return sys_prompt


async def UpdateUser(
    user_id: int,
    databse: Database,
    level: str | None = None,
    system_prompt: str | None = None,
    distro_of_choice: str | None = None,
) -> RuntimeError | None:
    try:
        await databse.UpdateUser(user_id, level, system_prompt, distro_of_choice)
    except Exception as e:
        raise RuntimeError(f"Couldn't update user: {e}")
    
async def UpdateChatInfo(chat_id:int, database:Database,title:str|None=None,system_prompt:str|None=None) -> RuntimeError | None:
    try: 
        await database.UpdateChat(chat_id,title,system_prompt)
    except Exception as e:
        raise RuntimeError(f"Couldn't update chat info: {e}")
