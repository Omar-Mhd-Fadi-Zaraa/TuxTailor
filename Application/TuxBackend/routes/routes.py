import asyncio

from fastapi import FastAPI, HTTPException, APIRouter, Depends,status
from fastapi.responses import StreamingResponse
from contextlib import asynccontextmanager
from langchain_core.messages import HumanMessage
import httpx

from models.schemas import ChatAgentRequest
from models.messages import UserMessage
from Agents.agents import ChatAgent
from middlewares.auth import validate_ollama_url
from db.db import Database
from controllers.chatAgentController import get_chat_agent,to_langchain_messages
from controllers.databaseController import AddUserMessage, get_db
import config.consts as consts

base = APIRouter(prefix="/base", tags=["base"])
chat = APIRouter(prefix="/chat", tags=["chat"])


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
) -> StreamingResponse:
    try:
        msg = UserMessage(req, req.user_message)
        async with asyncio.TaskGroup() as tg:
            tg.create_task(AddUserMessage(msg, db))
            messages_task = tg.create_task(db.GetChatMessages(int(req.chat_id)))

        chat_messages = messages_task.result()  # list[Any]
        LCMessages = to_langchain_messages(chat_messages)  # list[AnyMessage]
        LCMessages.append(HumanMessage(req.user_message))
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
            detail = {"message": "Unable to invoke agent", "errors": [{"type": type(e).__name__, "message": str(e)}]}
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=detail)

    return StreamingResponse(chat_agent.invokeAgent(LCMessages))
