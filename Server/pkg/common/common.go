package common

import (
	"container/list"
)

type User struct {
	Pk      int    `json:"pk"`
	Name    string `json:"name"`
	User_id string `json:"user_id"`
	Card_id string `json:"card_id"`
	//boy:true; girl:false
	Gender        bool   `json:"gender"`
	Face_img_name string `json:"face_img_name"`
}

// the "Mode" map used to indicate the working modes now in the poll
//OnFlashing:ture reading ic card id to webui
//			false got ic card id to query user, decide whether to open the gate
type PoolWorkingModeEnum string

const (
	OnFlashing = "OnFlashing"
)

type SqlTypeEnum int

const (
	QueryByCardId SqlTypeEnum = iota
	QueryByUserID
	NewUser
	DelByPk
)

var hardwarePools list.List

type HardwareTypeEnum int

const (
	DEFAULT HardwareTypeEnum = iota
	CAMERA
	IDREADER
	ATLAS200
	WEBUI
	GATEMANG
	MOTOR
	FACEREG //face register, weiui
)

var letterRunes = []rune("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789")
