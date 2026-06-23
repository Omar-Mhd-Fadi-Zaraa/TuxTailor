from fastapi import FastAPI, HTTPException, APIRouter, Depends, Request
from fastapi.responses import StreamingResponse
from contextlib import asynccontextmanager
import httpx

from models.schemas import ChatAgentRequest
from Agents.agents import ChatAgent
from utils.auth import validate_ollama_url
import config.consts as consts

base = APIRouter(prefix="/base", tags=["base"])
agent = APIRouter(prefix="/agent", tags=["agent"])

@asynccontextmanager
async def lifespan(app: FastAPI):
    if not consts.OLLAMA_BASE_URL:
        raise RuntimeError("OLLAMA_BASE_URL is not set")

    # await validate_ollama_url(consts.OLLAMA_BASE_URL)

    # app.state.chat_agent = ChatAgent(
    #     model=consts.CHAT_MODEL, base_url=consts.OLLAMA_BASE_URL, keep_alive=-1
    # )
    yield
    async with httpx.AsyncClient() as client:
        await client.post(
            f"{consts.OLLAMA_BASE_URL}/api/generate",
            json={"model": consts.MODEL, "keep_alive": 0},
        )

def get_chat_agent(request: Request) -> ChatAgent:
    return request.app.state.chat_agent

def verify_token(token: str | None):
    if token != "":
        raise HTTPException(status_code=402, detail="Unauthorized request")

@base.post("/health")
def health_check():
    return {"ok": True}

""" @base.get("/scalar", include_in_schema=False)
def get_scalar_api():
    return get_scalar_api_reference(app.openapi_url) """

@agent.post("/invoke")
async def invoke_agent(
    req: ChatAgentRequest, chat_agent: ChatAgent = Depends(get_chat_agent)
):
    return StreamingResponse(chat_agent.invokeAgent(req.to_langchain_messages()))
