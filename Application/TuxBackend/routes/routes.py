import asyncio
import httpx

from fastapi import FastAPI, HTTPException, APIRouter, Depends, status
from fastapi.responses import StreamingResponse, JSONResponse
from contextlib import asynccontextmanager
from langchain_core.messages import SystemMessage

from models.schemas import (
    ChatAgentRequest,
    ChatAddRequest,
    ChatUpdateRequest,
    UserAddRequest,
    UserLoginRequest,
    UserUpdateRequest,
)
from models.messages import UserMessage
from Agents.agents import ChatAgent
from middlewares.auth import validate_ollama_url
from db.db import Database
from controllers.chatAgentController import (
    get_chat_agent,
    persist_agent_messages,
    stream_filtered_response,
    to_langchain_messages,
)
from controllers.databaseController import (
    AddUserMessage,
    AddChat,
    AddUser,
    Login,
    GetUserSysMessage,
    UpdateUser,
    UpdateChatInfo,
    get_db,
)
import config.consts as consts

base = APIRouter(prefix="/base", tags=["base"])
chat = APIRouter(prefix="/chat", tags=["chat"])
user = APIRouter(prefix="/user", tags=["user"])


@asynccontextmanager
async def lifespan(app: FastAPI):
    if not consts.OLLAMA_BASE_URL:
        raise RuntimeError("OLLAMA_BASE_URL is not set")

    await validate_ollama_url(consts.OLLAMA_BASE_URL)

    app.state.chat_agent = ChatAgent(
        model=consts.CHAT_MODEL, base_url=consts.OLLAMA_BASE_URL, keep_alive=-1
    )

    app.state.db = Database()

    yield

    app.state.db.close()

    async with httpx.AsyncClient() as client:
        await client.post(
            f"{consts.OLLAMA_BASE_URL}/api/generate",
            json={"model": consts.CHAT_MODEL, "keep_alive": 0},
        )


@base.post("/health")
def health_check():
    return {"ok": True}


@chat.post("/invoke")
async def invoke_agent(
    req: ChatAgentRequest,
    chat_agent: ChatAgent = Depends(get_chat_agent),
    db: Database = Depends(get_db),
):
    try:
        msg = UserMessage(req, req.user_message)
        async with asyncio.TaskGroup() as tg:
            tg.create_task(AddUserMessage(msg, db))
            messages_task = tg.create_task(db.GetChatMessages(int(req.chat_id)))
            user_sys_prompt_task = tg.create_task(GetUserSysMessage(req.user_id, db))

        chat_messages = messages_task.result()
        user_sys_prompt = user_sys_prompt_task.result()  # list[Any]
        LCMessages: list = []
        if user_sys_prompt:
            LCMessages.append(SystemMessage(user_sys_prompt))
        LCMessages.extend(to_langchain_messages(chat_messages))
        LCMessages.append(req.to_langchain_msg())

    except Exception as e:
        if isinstance(e, BaseExceptionGroup):
            detail = {
                "message": "Unable to invoke agent",
                "errors": [
                    {"type": type(sub).__name__, "message": str(sub)}
                    for sub in e.exceptions
                ],
            }
        else:
            detail = {
                "message": "Unable to invoke agent",
                "errors": [{"type": type(e).__name__, "message": str(e)}],
            }
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=detail
        )

    result: dict = {}

    async def stream():
        async for line in stream_filtered_response(chat_agent, LCMessages, result):
            yield line
        await persist_agent_messages(result.get("messages", []), req, db)

    return StreamingResponse(stream())


@chat.post("")
async def add_chat(req: ChatAddRequest, db=Depends(get_db)):
    try:
        new_chat_id = await AddChat(req, db)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Couldn't add chat: {e}",
        )

    return JSONResponse(content={"chatId": new_chat_id}, status_code=status.HTTP_200_OK)


@chat.patch("/{chat_id}")
async def update_chat_info(
    chat_id: int, chat_info: ChatUpdateRequest, db=Depends(get_db)
):
    try:
        data = chat_info.model_dump(exclude_unset=True, by_alias=False)
        await UpdateChatInfo(chat_id, db, **data)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Couldn't update chat info: {e}",
        )

    return JSONResponse(
        content={"message": f"chat {chat_id} info uodated"},
        status_code=status.HTTP_200_OK,
    )


@user.post("/signup")
async def add_user(user: UserAddRequest, db=Depends(get_db)):
    try:
        new_user_id = await AddUser(user, db)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Couldn't add user: {e}",
        )

    return JSONResponse(content={"userId": new_user_id}, status_code=status.HTTP_200_OK)


@user.post("/login")
async def log_in(user_info: UserLoginRequest, db=Depends(get_db)):
    try:
        user_id, logged = await Login(user_info.user_name, user_info.password, db)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occured with the database: {e}",
        )

    return (
        JSONResponse(
            content={"userId": user_id, "message": "Logged in!"},
            status_code=status.HTTP_200_OK,
        )
        if logged
        else JSONResponse(
            content={"userId": None, "message": "Username or password is wrong"},
            status_code=status.HTTP_400_BAD_REQUEST,
        )
    )


@user.patch("/{user_id}")
async def update_user_info(
    user_id: int, user_info: UserUpdateRequest, db=Depends(get_db)
):
    try:
        data = user_info.model_dump(by_alias=False, exclude_unset=True)
        await UpdateUser(user_id, db, **data)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Couldn't update user: {e}",
        )

    return JSONResponse(
        content={"message": "User updated"}, status_code=status.HTTP_200_OK
    )
