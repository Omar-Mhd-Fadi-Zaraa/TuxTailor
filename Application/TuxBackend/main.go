package main

import (
	"github.com/Omar-Mhd-Fadi-Zaraa/TuxTailor/db"
	"github.com/Omar-Mhd-Fadi-Zaraa/TuxTailor/routes"
	"github.com/gin-gonic/gin"
)

func main() {
	db.InitDB()
	server := gin.Default()
	routes.RegisterRoutes(server)
}
