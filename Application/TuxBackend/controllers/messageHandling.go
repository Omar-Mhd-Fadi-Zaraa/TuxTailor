package controllers

import (
	"bytes"
	"encoding/json"
	"fmt"
	"os/exec"

	"github.com/Omar-Mhd-Fadi-Zaraa/TuxTailor/models"
	"github.com/Omar-Mhd-Fadi-Zaraa/TuxTailor/utils/common"
)

func CallModel(msgs []models.Message) ([]models.Message, error) {

	messageList, err := models.CreateMessageList(msgs)
	if err != nil {
		return nil, err
	}

	payload, err := json.Marshal(messageList)
	if err != nil {
		return nil, err
	}

	scriptPath, err := common.GetPythonScripts() 
	if err != nil {
		return nil, err
	}

	cmd := exec.Command("python3", scriptPath[0])
	cmd.Stdin = bytes.NewReader(payload)

	out, err := cmd.CombinedOutput()
	if err != nil {
		return nil, fmt.Errorf("python script failed: %w: %s", err, string(out))
	}

	var result []models.Message
	if err := json.Unmarshal(out, &result); err != nil {
		return nil, fmt.Errorf("decode python output: %w: %s", err, string(out))
	}

	return result, nil
}
