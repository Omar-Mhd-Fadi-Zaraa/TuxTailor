package models

import (
	"encoding/json"
	"errors"
	"fmt"
)

type Preferences struct {
	UserID         int64  `binding:"required"`
	Level          string `binding:"required"`
	Id             int64  `binding:"required"`
	Prompt         string
	DistroOfChoice string
}

func (prefs *Preferences) ToString() (string, error) {
	str := `
	{
		"UserName": "%s",
		"Level": "%s",
		"UserPrompt": "%s",
		"DistroOfChoice": "%s"
	}
	`
	if !json.Valid([]byte(str)) {
		return "", errors.New("Invalid JSON")
	}

	res := fmt.Sprintf(str, prefs.UserID, prefs.Level, prefs.Prompt, prefs.DistroOfChoice)
	return res, nil
}
