package main

import (
	"bufio"
	"bytes"
	"context"
	"encoding/json"
	"errors"
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

func (a *App) startup(ctx context.Context) {
	a.ctx = ctx
}

func (a *App) Greet(name string) string {
	return fmt.Sprintf("Hello %s, It's show time!", name)
}

const defaultBackendURL = "http://localhost:8000"

func resolveBackendURL(raw string) string {
	raw = strings.TrimSpace(raw)
	if raw == "" {
		return defaultBackendURL
	}
	return strings.TrimRight(raw, "/")
}

func parseBackendChatID(chatID string) int {
	id, err := strconv.Atoi(chatID)
	if err != nil || id < 1 {
		return 1
	}
	return id
}

func readResponseBody(resp *http.Response) ([]byte, error) {
	defer resp.Body.Close()
	return io.ReadAll(resp.Body)
}

func apiErrorMessage(status int, body []byte) string {
	if len(body) == 0 {
		return fmt.Sprintf("backend returned %d", status)
	}

	var payload struct {
		Detail  any    `json:"detail"`
		Message string `json:"message"`
	}
	if err := json.Unmarshal(body, &payload); err == nil {
		if payload.Message != "" {
			return payload.Message
		}
		if payload.Detail != nil {
			switch detail := payload.Detail.(type) {
			case string:
				return detail
			default:
				encoded, err := json.Marshal(payload.Detail)
				if err == nil {
					return string(encoded)
				}
			}
		}
	}

	return strings.TrimSpace(string(body))
}

type userLoginRequest struct {
	UserName string `json:"userName"`
	Password string `json:"password"`
}

type userAddRequest struct {
	UserName       string  `json:"userName"`
	Password       string  `json:"password"`
	Level          string  `json:"level"`
	DateCreated    string  `json:"dateCreated"`
	SystemPrompt   *string `json:"systemPrompt,omitempty"`
	DistroOfChoice *string `json:"distroOfChoice,omitempty"`
}

type userUpdateRequest struct {
	Level          *string `json:"level,omitempty"`
	SystemPrompt   *string `json:"systemPrompt,omitempty"`
	DistroOfChoice *string `json:"distroOfChoice,omitempty"`
}

type chatAddRequest struct {
	UserID      int    `json:"userId"`
	Title       string `json:"title"`
	DateCreated string `json:"dateCreated"`
}

type chatUpdateRequest struct {
	Title        *string `json:"title,omitempty"`
	SystemPrompt *string `json:"systemPrompt,omitempty"`
}

type chatAgentRequest struct {
	Token       string `json:"token"`
	UserID      int    `json:"userId"`
	ChatID      int    `json:"chatId"`
	UserMessage string `json:"userMessage"`
	DateSent    string `json:"dateSent"`
}

type agentStreamEvent struct {
	Type       string          `json:"type"`
	Content    string          `json:"content,omitempty"`
	ToolName   string          `json:"toolName,omitempty"`
	ToolInput  json.RawMessage `json:"toolInput,omitempty"`
	ToolOutput json.RawMessage `json:"toolOutput,omitempty"`
}

func optionalString(value string) *string {
	trimmed := strings.TrimSpace(value)
	if trimmed == "" {
		return nil
	}
	return &trimmed
}

// Signup registers a new user via POST /user/signup.
func (a *App) Signup(
	userName string,
	password string,
	level string,
	systemPrompt string,
	distroOfChoice string,
	backendURL string,
) (int, error) {
	baseURL := resolveBackendURL(backendURL)
	reqBody := userAddRequest{
		UserName:       strings.TrimSpace(userName),
		Password:       password,
		Level:          strings.TrimSpace(level),
		DateCreated:    time.Now().UTC().Format(time.RFC3339),
		SystemPrompt:   optionalString(systemPrompt),
		DistroOfChoice: optionalString(distroOfChoice),
	}

	payload, err := json.Marshal(reqBody)
	if err != nil {
		return 0, err
	}

	resp, err := http.Post(baseURL+"/user/signup", "application/json", bytes.NewReader(payload))
	if err != nil {
		return 0, err
	}

	body, err := readResponseBody(resp)
	if err != nil {
		return 0, err
	}

	if resp.StatusCode != http.StatusOK {
		return 0, fmt.Errorf("%s", apiErrorMessage(resp.StatusCode, body))
	}

	var result struct {
		UserID int `json:"userId"`
	}
	if err := json.Unmarshal(body, &result); err != nil {
		return 0, err
	}

	if result.UserID < 1 {
		return 0, fmt.Errorf("signup succeeded but no user id was returned")
	}

	return result.UserID, nil
}

// Login authenticates via POST /user/login.
func (a *App) Login(userName, password, backendURL string) (int, error) {
	baseURL := resolveBackendURL(backendURL)
	reqBody := userLoginRequest{
		UserName: strings.TrimSpace(userName),
		Password: password,
	}

	payload, err := json.Marshal(reqBody)
	if err != nil {
		return 0, err
	}

	resp, err := http.Post(baseURL+"/user/login", "application/json", bytes.NewReader(payload))
	if err != nil {
		return 0, err
	}

	body, err := readResponseBody(resp)
	if err != nil {
		return 0, err
	}

	var result struct {
		UserID  *int   `json:"userId"`
		Message string `json:"message"`
	}
	if err := json.Unmarshal(body, &result); err != nil {
		return 0, err
	}

	if resp.StatusCode != http.StatusOK || result.UserID == nil || *result.UserID < 1 {
		if result.Message != "" {
			return 0, fmt.Errorf("%s", result.Message)
		}
		return 0, fmt.Errorf("%s", apiErrorMessage(resp.StatusCode, body))
	}

	return *result.UserID, nil
}

// UpdateUser patches profile fields via PATCH /user/{user_id}.
func (a *App) UpdateUser(
	userID int,
	level string,
	systemPrompt string,
	distroOfChoice string,
	backendURL string,
) error {
	baseURL := resolveBackendURL(backendURL)
	reqBody := userUpdateRequest{
		Level:          optionalString(level),
		SystemPrompt:   optionalString(systemPrompt),
		DistroOfChoice: optionalString(distroOfChoice),
	}

	payload, err := json.Marshal(reqBody)
	if err != nil {
		return err
	}

	endpoint := fmt.Sprintf("%s/user/%d", baseURL, userID)
	req, err := http.NewRequest(http.MethodPatch, endpoint, bytes.NewReader(payload))
	if err != nil {
		return err
	}
	req.Header.Set("Content-Type", "application/json")

	resp, err := http.DefaultClient.Do(req)
	if err != nil {
		return err
	}

	body, err := readResponseBody(resp)
	if err != nil {
		return err
	}

	if resp.StatusCode != http.StatusOK {
		return fmt.Errorf("%s", apiErrorMessage(resp.StatusCode, body))
	}

	return nil
}

// CreateChat creates a chat via POST /chat.
func (a *App) CreateChat(userID int, title, backendURL string) (int, error) {
	baseURL := resolveBackendURL(backendURL)
	reqBody := chatAddRequest{
		UserID:      userID,
		Title:       strings.TrimSpace(title),
		DateCreated: time.Now().UTC().Format(time.RFC3339),
	}
	if reqBody.Title == "" {
		reqBody.Title = "New Chat"
	}

	payload, err := json.Marshal(reqBody)
	if err != nil {
		return 0, err
	}

	resp, err := http.Post(baseURL+"/chat", "application/json", bytes.NewReader(payload))
	if err != nil {
		return 0, err
	}

	body, err := readResponseBody(resp)
	if err != nil {
		return 0, err
	}

	if resp.StatusCode != http.StatusOK {
		return 0, fmt.Errorf("%s", apiErrorMessage(resp.StatusCode, body))
	}

	var result struct {
		ChatID int `json:"chatId"`
	}
	if err := json.Unmarshal(body, &result); err != nil {
		return 0, err
	}

	if result.ChatID < 1 {
		return 0, fmt.Errorf("chat created but no chat id was returned")
	}

	return result.ChatID, nil
}

// UpdateChat patches chat title/system prompt via PATCH /chat/{chat_id}.
func (a *App) UpdateChat(
	chatID int,
	title string,
	systemPrompt string,
	backendURL string,
) error {
	baseURL := resolveBackendURL(backendURL)
	reqBody := chatUpdateRequest{
		Title:        optionalString(title),
		SystemPrompt: optionalString(systemPrompt),
	}

	payload, err := json.Marshal(reqBody)
	if err != nil {
		return err
	}

	endpoint := fmt.Sprintf("%s/chat/%d", baseURL, chatID)
	req, err := http.NewRequest(http.MethodPatch, endpoint, bytes.NewReader(payload))
	if err != nil {
		return err
	}
	req.Header.Set("Content-Type", "application/json")

	resp, err := http.DefaultClient.Do(req)
	if err != nil {
		return err
	}

	body, err := readResponseBody(resp)
	if err != nil {
		return err
	}

	if resp.StatusCode != http.StatusOK {
		return fmt.Errorf("%s", apiErrorMessage(resp.StatusCode, body))
	}

	return nil
}

type message struct {
	Role  string `json:"role"`
	Query string `json:"query"`
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
	case "ai_message":
		// Finalized message; text tokens were already streamed.
	}
}

func streamAgentResponse(ctx context.Context, chatID, msgID string, body io.Reader) error {
	reader := bufio.NewReader(body)
	gotEvent := false

	for {
		line, err := reader.ReadBytes('\n')
		trimmed := strings.TrimSpace(string(line))
		if trimmed != "" {
			var event agentStreamEvent
			if err := json.Unmarshal([]byte(trimmed), &event); err != nil {
				return fmt.Errorf("invalid stream event: %w", err)
			}
			handleAgentStreamEvent(ctx, chatID, msgID, event)
			gotEvent = true
		}

		if err != nil {
			if err == io.EOF {
				break
			}
			if gotEvent && errors.Is(err, io.ErrUnexpectedEOF) {
				break
			}
			return err
		}
	}

	return nil
}

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

type streamChunkEvent struct {
	ChatID  string `json:"chatId"`
	MsgID   string `json:"msgId"`
	Type    string `json:"type"`
	Content string `json:"content"`
}

type streamDoneEvent struct {
	ChatID string `json:"chatId"`
	MsgID  string `json:"msgId"`
}

type streamErrorEvent struct {
	ChatID  string `json:"chatId"`
	MsgID   string `json:"msgId"`
	Message string `json:"message"`
}

type streamMediaEvent struct {
	ChatID    string `json:"chatId"`
	MsgID     string `json:"msgId"`
	MediaType string `json:"mediaType"`
	URL       string `json:"url"`
	Alt       string `json:"alt,omitempty"`
}

type streamConfirmEvent struct {
	ChatID  string   `json:"chatId"`
	MsgID   string   `json:"msgId"`
	Prompt  string   `json:"prompt"`
	Options []string `json:"options"`
}

func (a *App) StreamMessage(
	chatID string,
	msgID string,
	userMessage string,
	backendURL string,
	userID int,
) {
	go func() {
		baseURL := resolveBackendURL(backendURL)
		reqBody := chatAgentRequest{
			Token:       "",
			UserID:      userID,
			ChatID:      parseBackendChatID(chatID),
			UserMessage: userMessage,
			DateSent:    time.Now().UTC().Format(time.RFC3339),
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
			emitError(a.ctx, chatID, msgID, apiErrorMessage(resp.StatusCode, body))
			return
		}

		if err := streamAgentResponse(a.ctx, chatID, msgID, resp.Body); err != nil {
			emitError(a.ctx, chatID, msgID, err.Error())
			return
		}

		runtime.EventsEmit(a.ctx, "chat:done", streamDoneEvent{
			ChatID: chatID,
			MsgID:  msgID,
		})
	}()
}

func (a *App) SendConfirmation(chatID string, msgID string, option string) {
	runtime.EventsEmit(a.ctx, "chat:confirmation:reply", map[string]string{
		"chatId": chatID,
		"msgId":  msgID,
		"option": option,
	})
}
