package main

import (
	"bytes"
	"context"
	"encoding/json"
	"fmt"
	"io"
	"net/http"

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

// SendMessage sends a user message to TuxBackend and returns the assistant reply.
// Kept for backwards compatibility; prefer StreamMessage for new UI.
func (a *App) SendMessage(userMessage string) (string, error) {
	payload, err := json.Marshal([]message{{Role: "user", Query: userMessage}})
	if err != nil {
		return "", err
	}

	resp, err := http.Post("http://localhost:8080/chat/message", "application/json", bytes.NewReader(payload))
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
func (a *App) StreamMessage(chatID string, msgID string, userMessage string) {
	go func() {
		payload, err := json.Marshal([]message{{Role: "user", Query: userMessage}})
		if err != nil {
			runtime.EventsEmit(a.ctx, "chat:error", streamErrorEvent{
				ChatID: chatID, MsgID: msgID, Message: err.Error(),
			})
			return
		}

		resp, err := http.Post("http://localhost:8080/chat/message", "application/json", bytes.NewReader(payload))
		if err != nil {
			runtime.EventsEmit(a.ctx, "chat:error", streamErrorEvent{
				ChatID: chatID, MsgID: msgID, Message: err.Error(),
			})
			return
		}
		defer resp.Body.Close()

		body, err := io.ReadAll(resp.Body)
		if err != nil {
			runtime.EventsEmit(a.ctx, "chat:error", streamErrorEvent{
				ChatID: chatID, MsgID: msgID, Message: err.Error(),
			})
			return
		}

		var messages []message
		if err := json.Unmarshal(body, &messages); err != nil {
			runtime.EventsEmit(a.ctx, "chat:error", streamErrorEvent{
				ChatID: chatID, MsgID: msgID, Message: err.Error(),
			})
			return
		}

		// Find the last non-user message and emit it as a text chunk.
		// When the Python agent gains true streaming, each token can be
		// emitted individually here instead.
		for i := len(messages) - 1; i >= 0; i-- {
			if messages[i].Role != "user" {
				runtime.EventsEmit(a.ctx, "chat:chunk", streamChunkEvent{
					ChatID:  chatID,
					MsgID:   msgID,
					Type:    "text",
					Content: messages[i].Query,
				})
				break
			}
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
