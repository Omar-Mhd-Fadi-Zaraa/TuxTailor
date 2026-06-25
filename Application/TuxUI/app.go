package main

import (
	"bufio"
	"bytes"
	"context"
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"strconv"
	"strings"
	"time"

	"github.com/wailsapp/wails/v2/pkg/runtime"
)

// App struct
type App struct {
	ctx context.Context
}

// NewApp creates a new App application struct
func NewApp() *App {
	return &App{}
}

// startup is called when the app starts. The context is saved
// so we can call the runtime methods
func (a *App) startup(ctx context.Context) {
	a.ctx = ctx
}

// Greet returns a greeting for the given name
func (a *App) Greet(name string) string {
	return fmt.Sprintf("Hello %s, It's show time!", name)
}

type message struct {
	Role  string `json:"role"`
	Query string `json:"query"`
}

type chatAgentRequest struct {
	ChatID      int    `json:"chatId"`
	UserMessage string `json:"userMessage"`
	DateSent    string `json:"dateSent"`
	UserID      *int   `json:"userId,omitempty"`
}

type agentStreamEvent struct {
	Type       string          `json:"type"`
	Content    string          `json:"content,omitempty"`
	ToolName   string          `json:"toolName,omitempty"`
	ToolInput  json.RawMessage `json:"toolInput,omitempty"`
	ToolOutput json.RawMessage `json:"toolOutput,omitempty"`
}

const defaultBackendURL = "http://localhost:8000"

func resolveBackendURL(url string) string {
	url = strings.TrimSpace(url)
	if url == "" {
		return defaultBackendURL
	}
	return strings.TrimRight(url, "/")
}

func parseBackendChatID(chatID string) int {
	id, err := strconv.Atoi(chatID)
	if err != nil || id < 1 {
		return 1
	}
	return id
}

func defaultUserID() *int {
	id := 1
	return &id
}

func emitError(ctx context.Context, chatID, msgID, message string) {
	runtime.EventsEmit(ctx, "chat:error", streamErrorEvent{
		ChatID: chatID, MsgID: msgID, Message: message,
	})
}

func formatToolPayload(raw json.RawMessage) string {
	if len(raw) == 0 {
		return ""
	}
	var pretty any
	if err := json.Unmarshal(raw, &pretty); err != nil {
		return string(raw)
	}
	encoded, err := json.Marshal(pretty)
	if err != nil {
		return string(raw)
	}
	return string(encoded)
}

func handleAgentStreamEvent(ctx context.Context, chatID, msgID string, event agentStreamEvent) {
	switch event.Type {
	case "text":
		if event.Content == "" {
			return
		}
		runtime.EventsEmit(ctx, "chat:chunk", streamChunkEvent{
			ChatID: chatID, MsgID: msgID, Type: "text", Content: event.Content,
		})
	case "tool_start":
		content := fmt.Sprintf("Using tool: %s", event.ToolName)
		if payload := formatToolPayload(event.ToolInput); payload != "" {
			content += "\n" + payload
		}
		runtime.EventsEmit(ctx, "chat:chunk", streamChunkEvent{
			ChatID: chatID, MsgID: msgID, Type: "thinking", Content: content + "\n",
		})
	case "tool_end":
		content := fmt.Sprintf("Tool finished: %s", event.ToolName)
		if payload := formatToolPayload(event.ToolOutput); payload != "" {
			content += "\n" + payload
		}
		runtime.EventsEmit(ctx, "chat:chunk", streamChunkEvent{
			ChatID: chatID, MsgID: msgID, Type: "thinking", Content: content + "\n",
		})
	}
}

// SendMessage sends a user message to TuxBackend and returns the assistant reply.
// Kept for backwards compatibility; prefer StreamMessage for new UI.
func (a *App) SendMessage(userMessage string) (string, error) {
	payload, err := json.Marshal([]message{{Role: "user", Query: userMessage}})
	if err != nil {
		return "", err
	}

	resp, err := http.Post(defaultBackendURL+"/chat/message", "application/json", bytes.NewReader(payload))
	if err != nil {
		return "", err
	}
	defer resp.Body.Close()

	body, err := io.ReadAll(resp.Body)
	if err != nil {
		return "", err
	}

	var messages []message
	if err := json.Unmarshal(body, &messages); err != nil {
		return "", err
	}

	for i := len(messages) - 1; i >= 0; i-- {
		if messages[i].Role != "user" {
			return messages[i].Query, nil
		}
	}

	return "", fmt.Errorf("no assistant reply in response")
}

// streamChunkEvent is the payload emitted on the "chat:chunk" event.
type streamChunkEvent struct {
	ChatID  string `json:"chatId"`
	MsgID   string `json:"msgId"`
	Type    string `json:"type"` // "text" or "thinking"
	Content string `json:"content"`
}

// streamDoneEvent is the payload emitted on the "chat:done" event.
type streamDoneEvent struct {
	ChatID string `json:"chatId"`
	MsgID  string `json:"msgId"`
}

// streamErrorEvent is the payload emitted on the "chat:error" event.
type streamErrorEvent struct {
	ChatID  string `json:"chatId"`
	MsgID   string `json:"msgId"`
	Message string `json:"message"`
}

// streamMediaEvent is the payload emitted on the "chat:media" event.
type streamMediaEvent struct {
	ChatID    string `json:"chatId"`
	MsgID     string `json:"msgId"`
	MediaType string `json:"mediaType"` // "audio", "video", "image"
	URL       string `json:"url"`
	Alt       string `json:"alt,omitempty"`
}

// streamConfirmEvent is the payload emitted on the "chat:confirmation" event.
type streamConfirmEvent struct {
	ChatID  string   `json:"chatId"`
	MsgID   string   `json:"msgId"`
	Prompt  string   `json:"prompt"`
	Options []string `json:"options"`
}

// StreamMessage sends a user message to TuxBackend and streams the response
// back to the frontend via Wails events.
// Events emitted:  chat:chunk | chat:media | chat:confirmation | chat:done | chat:error
func (a *App) StreamMessage(chatID string, msgID string, userMessage string, backendURL string) {
	go func() {
		baseURL := resolveBackendURL(backendURL)
		reqBody := chatAgentRequest{
			ChatID:      parseBackendChatID(chatID),
			UserMessage: userMessage,
			DateSent:    time.Now().UTC().Format(time.RFC3339),
			UserID:      defaultUserID(),
		}

		payload, err := json.Marshal(reqBody)
		if err != nil {
			emitError(a.ctx, chatID, msgID, err.Error())
			return
		}

		resp, err := http.Post(baseURL+"/chat/invoke", "application/json", bytes.NewReader(payload))
		if err != nil {
			emitError(a.ctx, chatID, msgID, err.Error())
			return
		}
		defer resp.Body.Close()

		if resp.StatusCode != http.StatusOK {
			body, _ := io.ReadAll(resp.Body)
			message := fmt.Sprintf("backend returned %d", resp.StatusCode)
			if len(body) > 0 {
				message = string(body)
			}
			emitError(a.ctx, chatID, msgID, message)
			return
		}

		scanner := bufio.NewScanner(resp.Body)
		scanner.Buffer(make([]byte, 0, 64*1024), 1024*1024)

		for scanner.Scan() {
			line := strings.TrimSpace(scanner.Text())
			if line == "" {
				continue
			}

			var event agentStreamEvent
			if err := json.Unmarshal([]byte(line), &event); err != nil {
				emitError(a.ctx, chatID, msgID, fmt.Sprintf("invalid stream event: %v", err))
				return
			}

			handleAgentStreamEvent(a.ctx, chatID, msgID, event)
		}

		if err := scanner.Err(); err != nil {
			emitError(a.ctx, chatID, msgID, err.Error())
			return
		}

		runtime.EventsEmit(a.ctx, "chat:done", streamDoneEvent{
			ChatID: chatID,
			MsgID:  msgID,
		})
	}()
}

// SendConfirmation forwards a user's confirmation choice to the backend.
// The backend (when implemented) listens for the "chat:confirmation:reply" event.
func (a *App) SendConfirmation(chatID string, msgID string, option string) {
	runtime.EventsEmit(a.ctx, "chat:confirmation:reply", map[string]string{
		"chatId": chatID,
		"msgId":  msgID,
		"option": option,
	})
}
