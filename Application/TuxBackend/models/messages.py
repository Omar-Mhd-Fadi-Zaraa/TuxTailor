from datetime import datetime, timezone

from langchain_core.messages import HumanMessage, AIMessage, ToolMessage, SystemMessage

from .schemas import Role, ChatAgentRequest


class message:
    date_sent: str
    role: Role
    chat_id: int
    user_id: int

    def __init__(self, request: ChatAgentRequest):
        self.chat_id = request.chat_id
        self.user_id = request.user_id


class UserMessage(message):
    def __init__(self, request: ChatAgentRequest, content: str, **kwargs):
        message.__init__(self, request)
        self.lcmsg = HumanMessage(content, **kwargs)
        self.date_sent = request.date_sent
        self.role = Role.USER


class AssistantMessage(message):
    def __init__(self, reqeust: ChatAgentRequest, content: str, **kwargs):
        message.__init__(self, reqeust)
        self.lcmsg = AIMessage(content, **kwargs)
        self.date_sent = datetime.now(timezone.utc)
        self.role = Role.ASSISTANT


class ToolResponseMessage(message):
    def __init__(
        self,
        preceeding_message: str,
        request: ChatAgentRequest,
        content: str,
        **kwargs
    ):
        message.__init__(self, request)
        self.lcmsg = ToolMessage(content, **kwargs)
        self.preceeding_message = preceeding_message
        self.role = Role.TOOL
        self.date_sent = datetime.now(timezone.utc)


class AssistantBehaviorMessage(message):
    def __init__(self, request: ChatAgentRequest, content: str, **kwargs):
        message.__init__(self, request)
        self.lcmsg = SystemMessage(content, **kwargs)
        self.date_sent = datetime.now(timezone.utc)
        self.role = Role.SYSTEM
