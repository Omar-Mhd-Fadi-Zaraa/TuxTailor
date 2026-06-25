from enum import Enum

from pydantic import BaseModel, ConfigDict, Field
from langchain_core.messages import HumanMessage


class Role(str, Enum):
    USER: str = "user"
    ASSISTANT: str = "assistant"
    SYSTEM: str = "system"
    TOOL: str = "tool"


class ChatAgentRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    user_id: int| None = Field(default=None, alias="userId")
    chat_id: int = Field(alias="chatId")
    user_message: str = Field(alias="userMessage")
    date_sent: str = Field(alias="dateSent")

    def to_langchain_msg(self):
        return HumanMessage(content=self.user_message)



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


