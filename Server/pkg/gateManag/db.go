package gateManag

import (
	"database/sql"
	"fmt"
	"hardwaresMang/pkg/common"

	_ "github.com/go-sql-driver/mysql"
)

var db *sql.DB

func InitDB() (err error) {
	// DSN:Data Source Name
	// username:password@protocol(domain)/tableName
	dsn := "user:password@tcp(127.0.0.1:3306)/faceusers"
	db, err = sql.Open("mysql", dsn)
	if err != nil {
		return err
	}
	// try to connect
	err = db.Ping()
	if err != nil {
		return err
	}
	return nil
}

func InsertUser(newUser *common.User) (err error) {
	sqlStr := "insert into users(name, user_id,card_id,gender,face_img_name) values (?,?,?,?,?)"
	ret, err := db.Exec(sqlStr, (*newUser).Name, (*newUser).User_id, (*newUser).Card_id, (*newUser).Gender, (*newUser).Face_img_name)
	if err != nil {
		fmt.Printf("insert failed, err:%v\n", err)
		return err
	}
	theID, err := ret.LastInsertId() // 新插入数据的id
	if err != nil {
		fmt.Printf("get lastinsert ID failed, err:%v\n", err)
		return err
	}
	(*newUser).Pk = int(theID)
	fmt.Printf("insert success, the id is %d.\n", theID)
	return nil
}
func DeleteByPk(pk int) (err error) {
	deleteSql := "delete from users where pk=?"
	_, err = db.Exec(deleteSql, pk)
	if err != nil {
		fmt.Printf("insert failed, err:%v\n", err)
		return err
	}
	return err
}

func QueryPk(user_pk *int, user *common.User) (err error) {
	sqlStr := "select pk,name,user_id,card_id,gender,face_img_name from users where pk=?"
	err = db.QueryRow(sqlStr, &user_pk).Scan(&user.Pk, &user.Name, &user.User_id, &user.Card_id, &user.Gender, &user.Face_img_name)
	if err != nil {
		fmt.Printf("scan failed, err:%v\n", err)
		return err
	}
	return nil
}

func QueryUserId(user_id *string, user *common.User) (err error) {
	sqlStr := "select pk,name,user_id,card_id,gender,face_img_name from users where user_id=?"
	err = db.QueryRow(sqlStr, &user_id).Scan(&user.Pk, &user.Name, &user.User_id, &user.Card_id, &user.Gender, &user.Face_img_name)
	if err != nil {
		fmt.Printf("scan failed, err:%v\n", err)
		return err
	}
	return nil
}
func QueryCardId(card_id *string, user *common.User) (err error) {
	sqlStr := "select pk,name,user_id,card_id,gender,face_img_name from users where card_id=?"
	fmt.Println("LINE66 db.go", *card_id)

	err = db.QueryRow(sqlStr, &card_id).Scan(&user.Pk, &user.Name, &user.User_id, &user.Card_id, &user.Gender, &user.Face_img_name)

	if err != nil {
		fmt.Printf("scan failed, err:%v\n", err)
		return err
	}
	return nil
}
