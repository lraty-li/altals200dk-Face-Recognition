package websocketManag

import (
	"container/list"
	"fmt"
	"hardwaresMang/pkg/common"
)

type Pool struct {
	ID          string
	Register    chan *Client
	Unregister  chan *Client
	Clients     map[*Client]bool
	Broadcast   chan common.CtlMsg
	WorkingMode map[string]bool
}

func NewPool(poolID string) *Pool {
	var temp = &Pool{
		ID:          poolID,
		Register:    make(chan *Client),
		Unregister:  make(chan *Client),
		Clients:     make(map[*Client]bool),
		Broadcast:   make(chan common.CtlMsg),
		WorkingMode: make(map[string]bool),
	}

	temp.WorkingMode[common.OnFlashing] = false
	return temp
}
func SearchPool(targetList *list.List, targetId string) *list.Element {
	element := targetList.Front()
	for ; element != nil; element = element.Next() {
		poolId := element.Value.(*Pool)
		if (*poolId).ID == targetId {
			return element
		}
	}
	return element
}

func (pool *Pool) Start() {
	for {
		if pool == nil {
			// pool killed
			return
		}
		select {
		case client := <-pool.Register:
			pool.Clients[client] = true
			break
		case client := <-pool.Unregister:
			//delete client from pool
			delete(pool.Clients, client)
			// fmt.Println("Size of ", pool.ID, " Pool's client len:", len(pool.Clients))
			//if pool empty, delete the pool from list
			if len(pool.Clients) == 0 {
				poolList := common.GetGlobalPoolList()
				poolHdl := SearchPool(poolList, client.Pool.ID)
				poolList.Remove(poolHdl)
				fmt.Println("pool list len:", poolList.Len())
				//TODO delete pool?
				pool = nil
			}

			break
		case message := <-pool.Broadcast:
			fmt.Println("Sending message to all clients in Pool", message.CtlType)

			// fmt.Println(messageCtlType)
			// for client, _ := range pool.Clients {
			// 	if err := client.Conn.WriteJSON(message); err != nil {
			// 		fmt.Println(err)
			// 		return
			// 	}
			// }
			// case client := <-pool.MessageThrough:
		}

	}
}
