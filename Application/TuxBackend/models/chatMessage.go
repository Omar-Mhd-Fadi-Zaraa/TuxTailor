package models

// AgentInvokeRequest is the single contract shared by UI (via Go), Go, and Python.
type AgentInvokeRequest struct {
	ConversationID  string         `json:"conversationId" binding:"required"`
	ClientMessageID string         `json:"clientMessageId" binding:"required"`
	UserID          string         `json:"userId,omitempty"`
	Messages        []AgentMessage `json:"messages" binding:"required,min=1,dive"`
}

// AgentMessage is one turn in the LLM conversation context.
type AgentMessage struct {
	Role       string `json:"role" binding:"required,oneof=user assistant system tool"`
	Content    string `json:"content" binding:"required"`
	ToolCallID string `json:"toolCallId,omitempty"`
	ToolName   string `json:"toolName,omitempty"`
}

// SendMessageDraft is what the UI sends before Go attaches history.
type SendMessageDraft struct {
	ConversationID  string       `json:"conversationId" binding:"required"`
	ClientMessageID string       `json:"clientMessageId" binding:"required"`
	Message         AgentMessage `json:"message" binding:"required"`
}
