package models

import (
	"fmt"
)

type Message struct {
	Query string
	Role  string
}

func CreateMessageList(msgs []Message) ([]map[string]string, error) {
	var messageList []map[string]string
	for i, msg := range msgs {
		if msg.Role == "" {
			return nil, fmt.Errorf("Message %d does not have a role", i)
		}

		if msg.Query == "" {
			return nil, fmt.Errorf("Message %d does not have a query", i)
		}

		messageList = append(messageList, map[string]string{
			"role":  msg.Role,
			"query": msg.Query,
		})
	}

	return messageList, nil
}
