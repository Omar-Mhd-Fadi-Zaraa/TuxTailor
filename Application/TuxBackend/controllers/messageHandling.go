package controllers

import (
	"fmt"
	"os/exec"

	"github.com/Omar-Mhd-Fadi-Zaraa/TuxTailor/models"
)

func CallModel(msgs []models.Message) error {
	cmd := exec.Command("/home/omar/Projects/TuxTailor/Agents/sendQuery.py", fmt.Sprintf("%#v", msgs))
	out, err := cmd.Output()
	if err != nil {
		return err
	}
	fmt.Println(string(out))
	return nil
}
