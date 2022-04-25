package common

import (
	"container/list"
	"fmt"
	"math/rand"
	"net/http"
)

func SwitchHardWareType(typeInt int) (hwType HardwareTypeEnum, err error) {
	//typeStr from authMsg
	//return : harewareType(default is HardwareTypeEnum.DEFAULT) & if error
	hardwareType := DEFAULT

	// typeInt, err := strconv.Atoi(typeStr)
	if err != nil {
		fmt.Println("[ERROR]getting hardware type error, set to default")
		return hardwareType, err
	} else {
		switch typeInt {
		case int(CAMERA):
			{
				hardwareType = CAMERA
			}
		case int(IDREADER):
			{
				hardwareType = IDREADER

			}
		case int(ATLAS200):
			{
				hardwareType = ATLAS200
			}
		case int(WEBUI):
			{
				hardwareType = WEBUI
			}
		case int(GATEMANG):
			{
				hardwareType = GATEMANG
			}
		case int(MOTOR):
			{
				hardwareType = MOTOR
			}

		}
	}
	return hardwareType, nil
}

func SwitchMessageCtlType(typeInt int) MessageCtlTypeEnum {
	messageType := NULLMESSAGE

	switch typeInt {
	case int(NULLMESSAGE):
		{
			messageType = NULLMESSAGE
		}
	case int(CARDID):
		{
			messageType = CARDID
		}
	case int(USERID):
		{
			messageType = USERID
		}
	case int(GATECONTROL):
		{
			messageType = GATECONTROL
		}
	case int(NEWUSER):
		{
			messageType = NEWUSER
		}

	case int(REFLASHIC):
		{
			messageType = REFLASHIC
		}
	case int(CONTINUE):
		{
			messageType = CONTINUE
		}
	case int(AUTH):
		{
			messageType = AUTH
		}
	case int(USERDATA):
		{
			messageType = USERDATA
		}
	case int(SHOWUSER):
		{
			messageType = SHOWUSER
		}
	case int(USERPK):
		{
			messageType = USERPK
		}
	case int(IMG2VETC):
		{
			messageType = IMG2VETC
		}
	}
	return messageType
}

// func slistContains(targetSlice []string, targetStr string) (index int) {
// 	for i := 0; i < len(targetSlice); i++ {
// 		if targetSlice[i] == targetStr {
// 			return i
// 		}
// 	}
// 	return -1
// }

func GetElementByIndex(list *list.List, index int) *list.Element {
	if index > list.Len() {
		fmt.Println("index over bound")
	}
	element := list.Front()
	for i := index; i > 0; element = element.Next() {
		i -= 1
	}
	return element
}

func GetGlobalPoolList() *list.List {
	return &hardwarePools
}

func RandStringRunes(n int) string {
	//gnerate random string in  n  long
	b := make([]rune, n)
	for i := range b {
		b[i] = letterRunes[rand.Intn(len(letterRunes))]
	}
	return string(b)
}

func ErrorHandle(err error, w http.ResponseWriter) {
	if err != nil {
		w.Write([]byte(err.Error()))
	}
}

func ErrorPrinter(formate string, err error) {

}
