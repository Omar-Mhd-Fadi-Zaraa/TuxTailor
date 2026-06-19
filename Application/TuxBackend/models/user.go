package models

import "github.com/Omar-Mhd-Fadi-Zaraa/TuxTailor/db"

type User struct {
	Id       int64 `binding:"required"`
	UserName int64 `binding:"required"`
	Password int64 `binding:"required"`
	Prefs    int64
}

func (u *User) AddUser() error {
	query := "INSERT into USERS VALUES (?,?,?,?)"

	pQuery, err := db.DB.Prepare(query)
	if err != nil {
		return err
	}
	defer pQuery.Close()

	result, err := pQuery.Exec(u.Id, u.UserName, u.Password)
	if err != nil {
		return err
	}

	_, err = result.LastInsertId()
	return err
}
