# -*- coding: utf-8 -*-
from shutil import ExecError
import numpy as np
import requests
from sympy import true
from milvusDB import MilvusDB
import json
import cv2
import time
import threading
from common import HardwareType, MessageCtlType
import websocket




class SocketClient:
    def __init__(self):
        self.isstop = False

        self.socketServer = "ws://192.168.1.229:8080/ws"
        # a six digit number >=100,000
        self.poolID = "123456"
        self.authMsg = {"poolID": self.poolID,
                        "hwType": HardwareType.ATLAS200.value}

        self.messageCarrier = {
            "ctlType": MessageCtlType.USERPK.value, "body": ""}
        self.bodyJsonStr = {'user_pk': 0}
        self.wsapp = websocket.WebSocketApp(
            self.socketServer, on_open=self.on_open, on_message=self.on_message)
        self.wst = threading.Thread(target=self.wsapp.run_forever)
        self.wst.daemon = True
        self.wst.start()
     
        # indicate that is new user command recve
        # new user request from webui
        # will revice user pk and img name, initiate a http request to get img, send to img2vetc(main.py)
        self.modes={"onNewUser":False}
        # the raw img file binary will be store here, and decode it from main thread
        self.imgCache=None
        self.msgCache=None

    def __del__(self):
        # TODO quick out thread
        self.wsapp.close()

    def on_open(self, ws):
        self.wsapp.send(json.dumps(self.authMsg))

    def on_message(self, ws, msg):
        # reponse to message
        self._messageThrough(msg)

    def stop(self):
        self.isstop = True
        self.wsapp.close()
        print('socket thread stopped!')

    def sendUserPK(self, data):
        # data should be int
        self.bodyJsonStr['user_pk'] = data
        self.messageCarrier["body"] = self.bodyJsonStr
        self.wsapp.send(json.dumps(self.messageCarrier))

    def recMsg(self):
        pass
    def _messageThrough(self,msg):
        decodedMsg = json.loads(msg)
        self.msgCache=decodedMsg
        if decodedMsg['ctlType'] == MessageCtlType.IMG2VETC.value:
            # fetch face img from server
            imgUrl = 'http://192.168.1.229:8080/img'
            form={'face_img_name': decodedMsg['body']['face_img_name']}
            res = requests.post(
                imgUrl, data=form, stream=True)
            try:
                if(res.status_code==200):
                    # TODO mabe return error msg, use try catch
                    # print(res.content)
                    self.imgCache=res.raw
                    self.modes["onNewUser"]=True
                else:
                    raise Exception
            except Exception as e:
                #todo error , send to server ,cancel the insert?
                print(e)


# ybyb = SocketClient()

# while 1:
#     time.sleep(1)
#     # ybyb.sendUserPK("7")
#     pass
