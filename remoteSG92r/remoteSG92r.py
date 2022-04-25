# -*- coding: UTF-8 -*-
from email import header
import RPi.GPIO as GPIO
import time
import json
from common import HardwareType, MessageCtlType
import websocket

socketServer = "ws://192.168.1.229:8080/ws"
# a six digit number >=100,000
poolID = "123456"
authMsg = {"poolID": poolID,
                 "hwType": HardwareType.MOTOR.value}
# messageCarrier = {"ctlType": MessageCtlType.CARDID, "body": ""}


def servo(angle):
    GPIO.setmode(GPIO.BCM)
    pin1 = 26  # 斜台
    GPIO.setup(pin1, GPIO.OUT, initial=GPIO.LOW)
    p1 = GPIO.PWM(pin1, 50)  # 设置频率为50KHz,20ms左右的时基脉冲(1/0.020s=50HZ)
    p1.start(0)

    try:
        p1.ChangeDutyCycle(2.5+angle/360*20)  # 通过用户输入的角度来改变舵机的角度
        time.sleep(0.5)  # 一秒钟完成转动
        print("done")
    except KeyboardInterrupt:
        pass

    p1.stop()
    GPIO.cleanup()


def on_open(wsapp):
    # Start to auth (send client type)
    wsapp.send(json.dumps(authMsg))


def on_message(wsapp, message):
    print(message)
    # not checking , open gate directly
    servo(1)

    # check if walker through the gate, in this time ,block all gate controling command,
    # and seet a cold up time after walker throught the gate

    #keep the face recognition initiative, the gate control passive(dont let face recognition & card reading stop)

    # messageDic = json.loads(message)
    # angle = messageDic['Body']
    # print(int(angle))

print("start")

try:
    wsapp = websocket.WebSocketApp(socketServer, on_open=on_open, on_message=on_message)
except KeyboardInterrupt:

    print("key board interrupt")
except:
    print("something went wrong")
finally:
    wsapp.close()
    GPIO.cleanup()
wsapp.run_forever()
