from typing import Literal
from pydantic import BaseModel, Field, model_validator
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage, SystemMessage, AnyMessage
from typing import List

Role = Literal["user", "assistant", "system", "tool"]


class ChatAgentMessage(BaseModel):
    role: Role
    content: str
    tool_call_id: str | None = Field(default=None, alias="toolCallId")
    tool_name: str | None = Field(default=None, alias="toolName")

    model_config = {"populate_by_name": True}


class ChatAgentInvokeRequest(BaseModel):
    conversation_id: str = Field(alias="conversationId")
    client_message_id: str = Field(alias="clientMessageId")
    user_id: str | None = Field(default=None, alias="userId")
    messages: list[ChatAgentMessage]

    model_config = {"populate_by_name": True}

    @model_validator(mode="after")
    def last_message_must_be_user(self) -> ChatAgentInvokeRequest:
        if not self.messages or self.messages[-1].role != "user":
            raise ValueError("messages[-1] must be a user message")
        return self

    def to_langchain_messages(self) -> List[AnyMessage]:
        langChainMessages: List[AnyMessage] = []
        for msg in self.messages:
            match msg.role:
                case "user":
                    langChainMessages.append(HumanMessage(msg.content))
                case "assistant":
                    langChainMessages.append(AIMessage(msg.content))
                case "system":
                    langChainMessages.append(SystemMessage(msg.content))
                case "tool":
                    langChainMessages.append(ToolMessage(msg.content))

        return langChainMessages
