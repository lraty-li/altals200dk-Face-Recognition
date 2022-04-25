package main

import (
	"encoding/json"
	"fmt"
	"hardwaresMang/pkg/common"
	"hardwaresMang/pkg/gateManag"
	"hardwaresMang/pkg/websocketManag"
	"io"
	"io/ioutil"
	"net/http"
	"os"
)

func serverWs(w http.ResponseWriter, r *http.Request) {
	//upgrade to websocket(conn)
	//connect?
	conn, err := websocketManag.Upgrade(w, r)
	if err != nil {
		fmt.Println("[ERROR] upgrade connection failed")
	}
	//send back to ask client info(groupId,harewareType)
	_, p, err := conn.ReadMessage()
	if err != nil {
		fmt.Println("[ERROR] reading auth msg", err)
	}
	var authMsg common.AuthMsg
	if err := json.Unmarshal([]byte(p), &authMsg); err == nil {
		fmt.Println("LINE27 main.go", authMsg)

		var poolId string = authMsg.PoolID
		//event the poolID is "", still new pool

		hardwarePools := common.GetGlobalPoolList()
		pool := websocketManag.SearchPool(hardwarePools, poolId)
		if pool == nil {
			// not exist, push and  create new pool
			pool := websocketManag.NewPool(poolId)
			hardwarePools.PushBack(pool)
			go pool.Start()

			websocketManag.NewClient(pool, conn, authMsg.HwType)

		} else {
			// pool exist, add new client
			websocketManag.NewClient(pool.Value.(*websocketManag.Pool), conn, authMsg.HwType)
		}

	} else {
		fmt.Println("[ERROR] closing connection for decode auth msg fail:", err)
		conn.Close()
	}

}

func servImg(w http.ResponseWriter, r *http.Request) {
	//return img(the file name in form) to requst
	w.Header().Set("Access-Control-Allow-Origin", "*")
	w.Header().Set("Access-Control-Allow-Methods", "POST")
	w.Header().Set("Access-Control-Allow-Headers",
		"Accept, Content-Type, Content-Length, Accept-Encoding, X-CSRF-Token, Authorization")
	err := r.ParseForm()
	common.ErrorHandle(err, w)

	filePath := "imgs/" + r.PostFormValue("face_img_name")
	fileBytes, err := ioutil.ReadFile(filePath)
	common.ErrorHandle(err, w)

	w.Write([]byte(fileBytes))
}

func storImg(w http.ResponseWriter, r *http.Request) {
	//restore img to local

	w.Header().Set("Access-Control-Allow-Origin", "*")
	w.Header().Set("Access-Control-Allow-Methods", "POST")
	w.Header().Set("Access-Control-Allow-Headers",
		"Accept, Content-Type, Content-Length, Accept-Encoding, X-CSRF-Token, Authorization")

	err := r.ParseForm()
	if err != nil {
		fmt.Println(err)
	}
	uploadFile, fileHandle, err := r.FormFile("face_img_name")
	common.ErrorHandle(err, w)

	// save img
	saveFile, err := os.OpenFile("./imgs/"+fileHandle.Filename, os.O_WRONLY|os.O_CREATE, 0666)
	common.ErrorHandle(err, w)
	io.Copy(saveFile, uploadFile)

	defer uploadFile.Close()
	defer saveFile.Close()
	// 上传图片成功
	w.Write([]byte("upload finish"))
}

func setupRoutes() {
	http.HandleFunc("/", func(w http.ResponseWriter, r *http.Request) {
		fmt.Fprintf(w, "Hello")
	})

	//map "/ws" to serverWs func
	http.HandleFunc("/ws", serverWs)
	http.HandleFunc("/storImg", storImg)
	http.HandleFunc("/img", servImg)

}

func main() {
	fmt.Println("start on 8080")
	gateManag.InitDB()

	setupRoutes()
	http.ListenAndServe(":8080", nil)
}
