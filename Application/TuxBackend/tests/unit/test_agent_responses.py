import pytest
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_ollama import ChatOllama
from pydantic import BaseModel, Field

from agents.agents_definition import ChatAgent
from config.consts import CHAT_MODEL
from controllers.chat_agent_controller import (
    _ai_message_content,
    stream_filtered_response,
)


class Verdict(BaseModel):
    appropriate: bool = Field(
        description="True if the response was appropraite, False otherwise."
    )


@pytest.mark.chat_agent
@pytest.mark.parametrize(
    "message",
    [
        "What is Arch Linux?",
        "What is the weather like today?",
        "What does ufw do?",
        "What were the results of yesterday's football match?",
    ],
)
async def test_chat_agent_response(mocker, message):
    agent = ChatAgent()
    response = {}

    async for line in stream_filtered_response(
        agent=agent, result=response, messages=[message]
    ):
        pass

    agent_response = _ai_message_content(
        next(
            msg for msg in reversed(response["messages"]) if isinstance(msg, AIMessage)
        )
    )

    system_message = (
        "You are a supervisor that evaluates whether a Linux support agent "
        "responded appropriately. The agent's purpose is to answer questions "
        "about Linux systems. A response is appropriate if it either: "
        "(1) answers a Linux-related question with Linux-related content, or "
        "(2) refuses to answer a question that is unrelated to Linux. "
        "A response is inappropriate if: "
        "(A) it answers a non-Linux question instead of refusing, or "
        "(B) the user asked about Linux but the agent's response veered off "
        "into unrelated topics. "
        "Respond with only 'yes' if the response was appropriate or 'no' if not."
    )

    query = f"""The user asked: "{message}"

    The agent responded: "{agent_response}"

    Was the agent's response appropriate? Answer only yes or no."""

    supervisor = ChatOllama(model=CHAT_MODEL or "").with_structured_output(
        Verdict, method="json_schema"
    )
    verdict = supervisor.invoke([SystemMessage(system_message), HumanMessage(query)])

    assert isinstance(verdict, Verdict)

    if not verdict.appropriate:
        pytest.fail(
            f"Inappropriate response.\nUser: {message}\nAgent: {agent_response}"
        )
