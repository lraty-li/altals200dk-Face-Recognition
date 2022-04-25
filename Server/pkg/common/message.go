package common

import "encoding/json"

type MessageCtlTypeEnum int

//full struct of message will received
type CtlMsg struct {
	//the control commad type, check MessageCtlTypeEnum
	//but set "int"
	CtlType int `json:"ctlType"`
	//body depends on ctlType, check gateManag.MessageThrough
	Body json.RawMessage `json:"body"`
}

const (
	NULLMESSAGE MessageCtlTypeEnum = iota
	CARDID                         //received id card data
	USERID
	GATECONTROL
	NEWUSER   //received new user command from webui CtlMsg{"CtlType":"NEWUSER","Body":User}
	REFLASHIC // command from webui to read ic card id
	CONTINUE  // command to info hardware continue their working, nomatter if this round success
	AUTH      // TODO deprecated for now,directly received AuthMsg, not CtlMsg{"CtlType":"AUTH","Body":AuthMsg}
	USERDATA  // deprecated; user data struct User(common.go)
	SHOWUSER  // send user data to webui CtlMsg{"CtlType":"SHOWUSER","Body":User}
	USERPK    // the body is eneity's primarily key
	IMG2VETC  // send {"user_pk","img_name"} to 200dk, the 200dk fetch img, convert to face embedding and store it to milvus
)

//the body's stuct of every kind of message
type MsgCard struct {
	Card_Id string `json:"card_id"`
}

type MsgUserId struct {
	User_Id string `json:"user_id"`
}
type MsgUserPK struct {
	User_Pk int `json:"user_pk"`
}

type MsgGateCtl struct {
	// 0 reject
	// 1 open
	Ctl bool `json:"ctl"`
}

type MsgImg2Vetc struct {
	User_Pk       int    `json:"user_pk"`
	Face_img_name string `json:"face_img_name"`
}

//use User struct in common.go
// type MsgUser struct {
// 	Name    string `json:"name"`
// 	User_id string `json:"user_id"`
// 	Card_id string `json:"card_id"`
// 	//boy:true; girl:false
// 	Gender        bool   `json:"gender"`
// 	Face_img_name string `json:"face_img_name"`
// }

type MsgFlashIC struct {
}

type MsgCtn struct {
	//CONTINUE
	Info string `json:"info"`
}

type AuthMsg struct {
	PoolID string `json:"poolID"`
	HwType int    `json:"hwType"`
}

func WrapUpMsg(MsgType MessageCtlTypeEnum, msg *CtlMsg) {
	//build a CylMsg depend on MsgType
	(*msg).CtlType = int(MsgType)
	switch MsgType {
	case NULLMESSAGE:
		{

			nullRaw := json.RawMessage("")
			(*msg).Body = nullRaw
		}
	case CARDID:
		{
		}
	case USERID:
		{
		}
	case GATECONTROL:
		{
		}
	case NEWUSER:
		{
		}
	case REFLASHIC:
		{
		}
	case CONTINUE:
		{
		}
	case AUTH:
		{
		}
	case USERDATA:
		{
		}
	case SHOWUSER:
		{
		}
	}
}
