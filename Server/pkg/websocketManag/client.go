package websocketManag

import (
	"encoding/json"
	"fmt"
	"hardwaresMang/pkg/common"
	"hardwaresMang/pkg/gateManag"
	"log"

	"github.com/gorilla/websocket"
)

const (

//TODO time limit
//https://github.com/gorilla/websocket/blob/master/examples/filewatch/main.go
// Time allowed to write the file to the client.
// writeWait = 10 * time.Second

// Time allowed to read the next pong message from the client.
// pongWait = 60 * time.Second

// Send pings to client with this period. Must be less than pongWait.
// pingPeriod = (pongWait * 9) / 10

// Poll file for changes with this period.
// filePeriod = 10 * time.Second
)

type Client struct {
	ID   string
	Conn *websocket.Conn
	Pool *Pool
	Type common.HardwareTypeEnum
}

func (c *Client) Read() {
	defer func() {
		c.Pool.Unregister <- c
		c.Conn.Close()
	}()
	// c.Conn.SetReadDeadline(time.Now().Add(pongWait))
	for {
		// text or binary?
		//TODO closing message?
		_, p, err := c.Conn.ReadMessage()
		if err != nil {
			c.Conn.Close()
			log.Println(err)
			return
		}

		//the message received
		var messageRevd common.CtlMsg
		if err := json.Unmarshal([]byte(p), &messageRevd); err == nil {
			//progressing depends on message
			MessageThrough(&messageRevd, c)
		} else {
			fmt.Println("decode msg fail:", err)
		}
		// c.Pool.Broadcast <- messageRev
	}
}

func NewClient(pool *Pool, conn *websocket.Conn, typeInt int) {
	hardwareType, err := common.SwitchHardWareType(typeInt)
	//allocate id randomlly
	clienId := common.RandStringRunes(6)
	fmt.Println("LINE69 client.go clienId", clienId)
	if err != nil {
		fmt.Println("[WARNING] the client type set to DEFAULT")
	}
	client := &Client{
		Conn: conn,
		Pool: pool,
		Type: hardwareType,
		ID:   clienId,
	}
	pool.Register <- client
	client.Read()

}

func MessageThrough(ctlMessage *common.CtlMsg, client *Client) {
	messageCtlType := common.SwitchMessageCtlType(ctlMessage.CtlType)
	switch messageCtlType {
	case common.NULLMESSAGE:
		{
			//default null message, do nothing
			fmt.Println("[WARNING] Empty msg")
			return
		}
	case common.CARDID:
		{
			//id card readed
			//body: card id

			//decode message
			var messageBody common.MsgCard
			var tempMsg []byte
			if err := json.Unmarshal([]byte(ctlMessage.Body), &messageBody); err == nil {
				if client.Pool.WorkingMode[common.OnFlashing] {
					//on flashing ic card id
					//send id card id to webui
					tempMsg, err = json.Marshal(messageBody)
					fakeBrocast(common.CARDID, common.WEBUI, client, tempMsg)

					//reest mode to normal
					client.Pool.WorkingMode[common.OnFlashing] = false
					return
				}
				//query user, control gate
				var tempUser common.User
				err := gateManag.QueryCardId(&(messageBody.Card_Id), &tempUser)
				if err != nil {
					fmt.Printf("QueryCardId failed, err:%v\n", err)
					//TODO reject gate
					return
				}
				//open gate
				msgGate := new(common.MsgGateCtl)
				msgGate.Ctl = true
				tempMsg, err = json.Marshal(msgGate)
				fakeBrocast(common.GATECONTROL, common.MOTOR, client, tempMsg)

				//send query row to all webui
				tempMsg, err = json.Marshal(tempUser)
				fakeBrocast(common.SHOWUSER, common.WEBUI, client, tempMsg)
				// container := new(common.CtlMsg)

				// container.CtlType = int(common.SHOWUSER)
				// temp, _ := json.Marshal(tempUser)
				// container.Body = temp

				// for c := range client.Pool.Clients {
				// 	if c.Type == common.WEBUI {
				// 		c.Conn.WriteJSON((*container))
				// 	}
				// }
				// container = nil
			} else {
				fmt.Println("[ERROR]decode msg body fail:", err)

			}

			//TODO send CONTINUE
		}
	case common.USERID:
		{
			// face readed and found userid
			//body: face id ,the same id of user

			//decode message
			var messageBody common.MsgUserId
			if err := json.Unmarshal([]byte(ctlMessage.Body), &messageBody); err == nil {

				//query user, control gate

				var tempUser common.User
				err := gateManag.QueryUserId(&(messageBody.User_Id), &tempUser)
				if err != nil {
					fmt.Printf("QueryCardId failed, err:%v\n", err)
					//TODO reject gate
					return
				}
				//TODO open gate
			} else {
				fmt.Println("decode msg body fail:", err)
			}
		}
	case common.USERPK:
		{
			//decode message
			var messageBody common.MsgUserPK
			var tempMsg []byte
			if err := json.Unmarshal([]byte(ctlMessage.Body), &messageBody); err == nil {

				//query user, control gate

				var tempUser common.User
				err := gateManag.QueryPk(&(messageBody.User_Pk), &tempUser)
				if err != nil {
					fmt.Printf("Query user pk failed, err:%v\n", err)
					//TODO reject gate
					return
				}
				//open gate
				msgGate := new(common.MsgGateCtl)
				msgGate.Ctl = true
				tempMsg, err = json.Marshal(msgGate)
				fakeBrocast(common.GATECONTROL, common.MOTOR, client, tempMsg)

				//send result to webui
				tempMsg, err = json.Marshal(tempUser)
				fakeBrocast(common.SHOWUSER, common.WEBUI, client, tempMsg)

			} else {
				fmt.Println("decode msg body fail:", err)
			}
		}
	case common.GATECONTROL:
		{
			// gate control(steering gear) message received
			//body: bool of if pass
			//respone: send message to hradwareType == GATEMANG
		}
	case common.NEWUSER:
		{
			//from webui, add new user
			//body: user data collection(json string)

			//decode message
			var messageBody common.User
			var tempMsg []byte
			if err := json.Unmarshal([]byte(ctlMessage.Body), &messageBody); err == nil {

				// TODO img file name too long?
				err := gateManag.InsertUser(&messageBody)
				if err != nil {
					fmt.Printf("insert user failed, err:%v\n", err)
					msgCtn := new(common.MsgCtn)
					msgCtn.Info = "inser failed"
					tempMsg, err = json.Marshal(msgCtn)
					fakeBrocast(common.CONTINUE, common.WEBUI, client, tempMsg)
					return
				}
				//send to 200dk , img2vetcor
				msgImg2Vetc := new(common.MsgImg2Vetc)
				msgImg2Vetc.Face_img_name = messageBody.Face_img_name
				msgImg2Vetc.User_Pk = messageBody.Pk
				tempMsg, err = json.Marshal(msgImg2Vetc)
				fakeBrocast(common.IMG2VETC, common.ATLAS200, client, tempMsg)

				//send feedback
				msgCtn := new(common.MsgCtn)
				msgCtn.Info = "inser finish"
				tempMsg, err = json.Marshal(msgCtn)
				fakeBrocast(common.CONTINUE, common.WEBUI, client, tempMsg)

			} else {
				fmt.Println("decode msg body fail:", err)
			}
		}
	case common.REFLASHIC:
		{
			//send to onflasing, the card id received next time will be directly send to webui
			fmt.Println("LINE230 client.go set on flashing")
			client.Pool.WorkingMode[common.OnFlashing] = true
		}
	}
}

//todo the brocast func (only one?)
func fakeBrocast(msgType common.MessageCtlTypeEnum, msgTarget common.HardwareTypeEnum, client *Client, msgBody []byte) {
	//build up msg and brocast
	msgContainer := new(common.CtlMsg)
	msgContainer.CtlType = int(msgType)
	msgContainer.Body = msgBody
	for c := range client.Pool.Clients {
		if c.Type == msgTarget {
			c.Conn.WriteJSON((*msgContainer))
		}
	}
}
