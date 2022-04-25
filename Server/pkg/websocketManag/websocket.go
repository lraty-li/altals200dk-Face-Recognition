package websocketManag

import (
	"log"
	"net/http"

	"github.com/gorilla/websocket"
)

//define upgrader
var upgrader = websocket.Upgrader{
	ReadBufferSize:  1024,
	WriteBufferSize: 2014,
	//check origin(request from react)
	CheckOrigin: func(r *http.Request) bool { return true },
}

//define websocket node(upgrade from a http node?)
func Upgrade(w http.ResponseWriter, r *http.Request) (*websocket.Conn, error) {
	ws, err := upgrader.Upgrade(w, r, nil)
	if err != nil {
		log.Println(err)
		return ws, err
	}
	return ws, nil
}

// //define reader to listen
// //new message will be send to websocket node
// func Reader(conn *websocket.Conn) {
// 	for {
// 		// myMessage := []byte(fmt.Sprintf("sendback?"))
// 		//read message
// 		messageType, p, err := conn.ReadMessage()
// 		if err != nil {
// 			log.Println(err)
// 			return
// 		}
// 		fmt.Println(string(p))
// 		//send back
// 		if err := conn.WriteMessage(messageType, p); err != nil {
// 			log.Println(err)
// 		}
// 	}
// }
// func Writer(conn *websocket.Conn) {
// 	for {
// 		fmt.Println("Sending")
// 		messageType, r, err := conn.NextReader()
// 		if err != nil {
// 			fmt.Println(err)
// 			return
// 		}
// 		w, err := conn.NextWriter(messageType)
// 		if err != nil {
// 			fmt.Println(err)
// 			return
// 		}
// 		if _, err = io.Copy(w, r); err != nil {
// 			fmt.Println(err)
// 			return
// 		}
// 		if err := w.Close(); err != nil {
// 			fmt.Println(err)
// 			return
// 		}

// 	}
// }
