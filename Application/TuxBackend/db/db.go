package db

import "database/sql"

var DB *sql.DB

func InitDB() {
	var err error

	DB, err = sql.Open("sqlite3", "tuxtailor.db")
	if err != nil {
		panic(err)
	}

	_, err = DB.Exec("PRAGMA forein_keys = ON")
	if err != nil {
		panic(err)
	}

	DB.SetMaxOpenConns(10)
	DB.SetMaxIdleConns(5)
}

func UsersTableCreate() {
	createUsersTable := `
	CREATE TABLE IF NOT EXISTS USERS (
		id INTEGER PRIMARY KEY UNIQUE,
		userName TEXT NOT NULL,
		password TEXT NOT NULL,
		preferences INTEGER
	)
	`

	_, err := DB.Exec(createUsersTable)
	if err != nil {
		panic(err)
	}
}
