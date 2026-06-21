from fastapi import FastAPI, HTTPException, Header, APIRouter, Depends, Request
from fastapi.responses import StreamingResponse
from contextlib import asynccontextmanager
import httpx

from schemas import ChatAgentInvokeRequest
from agents import ChatAgent
import consts


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.chat_agent = ChatAgent(consts.MODEL, keep_alive=-1)
    yield
    async with httpx.AsyncClient() as client:
        await client.post(
            f"{consts.OLLAMA_BASE_URL}/api/generate",
            json={"model": consts.MODEL, "keep_alive": 0},
        )


app = FastAPI(lifespan=lifespan)


def get_chat_agent(request: Request) -> ChatAgent:
    return request.app.state.chat_agent


def verify_token(token: str | None):
    if token != "":
        raise HTTPException(status_code=402, detail="Unauthorized request")


@app.post("/health")
def health_check():
    return {"ok": True}


agent = APIRouter(prefix="/agent", tags=["agent"])
app.include_router(agent)


@agent.post("/invoke")
async def invoke_agent(
    req: ChatAgentInvokeRequest, chat_agent: ChatAgent = Depends(get_chat_agent)
):
    return StreamingResponse(chat_agent.invokeAgent(req.to_langchain_messages()))
