package main

import (
	"github.com/Omar-Mhd-Fadi-Zaraa/TuxTailor/controllers"
	"github.com/Omar-Mhd-Fadi-Zaraa/TuxTailor/models"
)

func main() {
	// db.InitDB()
	// server := gin.Default()
	// routes.RegisterRoutes(server)

	// test := models.Preferences{
	// 	DistroOfChoice: "Arch",
	// 	UserID:         1,
	// 	Level:          "Beginner",
	// 	Id:             1,
	// 	Prompt:         "You are a helpful assistant",
	// }

	// fmt.Println(test.ToString())

	msg := models.Message{
		Role:  "user",
		Query: "What can you do",
	}

	err :=controllers.CallModel([]models.Message{msg})
	if err != nil {
		println(err.Error())
	}
}
