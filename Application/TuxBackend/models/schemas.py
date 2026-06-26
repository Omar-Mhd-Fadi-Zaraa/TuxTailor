from enum import Enum

from pydantic import BaseModel, ConfigDict, Field
from langchain_core.messages import HumanMessage


class Role(str, Enum):
    USER: str = "user"
    ASSISTANT: str = "assistant"
    SYSTEM: str = "system"
    TOOL: str = "tool"


# Message related requests
class ChatAgentRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    access_token: str = Field(alias="token")
    user_id: int = Field(alias="userId")
    chat_id: int = Field(alias="chatId")
    user_message: str = Field(alias="userMessage")
    date_sent: str = Field(alias="dateSent")

    def to_langchain_msg(self):
        return HumanMessage(content=self.user_message)


# User-related requests
class UserAddRequest(BaseModel):
    user_name: str = Field(alias="userName")
    password: str = Field(alias="password")
    level: str = Field(alias="level")
    date_created: str = Field(alias="dateCreated")
    system_prompt: str | None = Field(default=None, alias="systemPrompt")
    distro_of_choice: str | None = Field(default=None, alias="distroOfChoice")


class UserLoginRequest(BaseModel):
    user_name: str = Field(alias="userName")
    password: str = Field(alias="password")


class UserUpdateRequest(BaseModel):
    level: str | None = Field(default=None, alias="level")
    system_prompt: str | None = Field(default=None, alias="systemPrompt")
    distro_of_choice: str | None = Field(default=None, alias="distroOfChoice")


# Chat-related requests
class ChatAddRequest(BaseModel):
    user_id: int = Field(alias="userId")
    title: str = Field(alias="title")
    date_created: str = Field(alias="dateCreated")


class ChatUpdateRequest(BaseModel):
    title: str | None = Field(default=None, alias="title")
    system_prompt: str | None = Field(default=None, alias="systemPrompt")


# class ChatMessage(BaseModel):
#     role: Role
#     content: str
#     tool_call_id: str | None = Field(default=None, alias="toolCallId")
#     tool_name: str | None = Field(default=None, alias="toolName")

#     model_config = {"populate_by_name": True}
#
# class ChatAgentResponse(ChatAgentHandling):
#     messages: list[ChatMessage]

#     model_config = {"populate_by_name": True}

#     @model_validator(mode="after")
#     def last_message_must_be_assistant(self):
#         if not self.messages or self.messages[-1].role != Role.SYSTEM:
#             raise ValueError("messages[-1] must be a user message")
#         return self
