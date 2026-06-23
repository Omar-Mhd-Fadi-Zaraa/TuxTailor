from pydantic import BaseModel, Field, model_validator
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage, SystemMessage, AnyMessage
from typing import List
from enum import Enum

class Role(str,Enum):
    USER: str = "user"
    ASSISTANT: str = "assistant"
    SYSTEM: str = "system"
    TOOL: str = "tool"

class ChatMessage(BaseModel):
    role: Role
    content: str
    tool_call_id: str | None = Field(default=None, alias="toolCallId")
    tool_name: str | None = Field(default=None, alias="toolName")

    model_config = {"populate_by_name": True}

class ChatAgentHandling(BaseModel):
    conversation_id: str = Field(alias="conversationId")
    client_message_id: str = Field(alias="clientMessageId")
    user_id: str | None = Field(default=None, alias="userId")


class ChatAgentResponse(ChatAgentHandling):
    messages: list[ChatMessage]

    model_config = {"populate_by_name": True}

    @model_validator(mode="after")
    def last_message_must_be_assistant(self):
        if not self.messages or self.messages[-1].role != Role.SYSTEM:
            raise ValueError("messages[-1] must be a user message")
        return self

    
class ChatAgentRequest(ChatAgentHandling):
    user_message: str = Field(alias="userMessage")
    
    def to_langchain_msg(self):
        self.user_message = HumanMessage(content=self.user_message)
        return self.user_message