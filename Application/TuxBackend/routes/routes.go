package routes

import "github.com/gin-gonic/gin"

func RegisterRoutes(server *gin.Engine)  {
	// Endpoints for handling chat related requests
	chat := server.Group("/chat")
	chat.POST("/message")
	chat.POST("/confirmation")
	chat.GET("/message")
	
	// Endpoints for handling user related requests
	users := server.Group("/users")
	users.POST("/preferences")
	users.POST("/login")
	users.GET("/preferences")

	// Endpoints for handling file realted requests
	files := server.Group("/files")
	files.GET("/isodownload")
}