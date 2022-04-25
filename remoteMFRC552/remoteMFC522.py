#!/usr/bin/env python
# -*- coding: utf8 -*-
#
#    Copyright 2014,2018 Mario Gomez <mario.gomez@teubi.co>
#
#    This file is part of MFRC522-Python
#    MFRC522-Python is a simple Python implementation for
#    the MFRC522 NFC Card Reader for the Raspberry Pi.
#
#    MFRC522-Python is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Lesser General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    MFRC522-Python is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Lesser General Public License for more details.
#
#    You should have received a copy of the GNU Lesser General Public License
#    along with MFRC522-Python.  If not, see <http://www.gnu.org/licenses/>.
#

import RPi.GPIO as GPIO
import MFRC522
import signal
import websocket
import json
from common import HardwareType, MessageCtlType
try:
    import thread
except ImportError:
    import _thread as thread
import time

socketServer = "ws://192.168.1.229:8080/ws"
# a six digit number >=100,000
poolID = "123456"
authMsg = {"poolID": poolID,
                 "hwType": HardwareType.IDREADER.value}
continue_reading = True
messageCarrier = {"ctlType": MessageCtlType.CARDID.value, "body": ""}
# Capture SIGINT for cleanup when the script is aborted


def end_read(signal, frame):
    global continue_reading
    wsapp.close()
    print("Ctrl+C captured, ending read.")
    continue_reading = False
    GPIO.cleanup()


# Hook the SIGINT
signal.signal(signal.SIGINT, end_read)

# Create an object of the class MFRC522
MIFAREReader = MFRC522.MFRC522()

cardUidCache = ""

# Welcome message
print("Press Ctrl-C to stop.")


def on_message(wsapp, message):
    print(message)


def on_open(ws):
    # Start to auth (send client type)
    ws.send(json.dumps(authMsg))

    def readingLoop(*args):
        # This loop keeps checking for chips. If one is near it will get the UID and authenticate
        while continue_reading:

            # Scan for cards
            (status, TagType) = MIFAREReader.MFRC522_Request(
                MIFAREReader.PICC_REQIDL)

            # If a card is found
            if status == MIFAREReader.MI_OK:
                print("Card detected")

            # Get the UID of the card
            (status, uid) = MIFAREReader.MFRC522_Anticoll()

            # If we have the UID, continue
            if status == MIFAREReader.MI_OK:

                # Print UID
                # print "Card read UID: %s,%s,%s,%s" % (uid[0], uid[1], uid[2], uid[3])
                cardUidCache = "%s%s%s%s" % (uid[0], uid[1], uid[2], uid[3])
                # wrap msg body
                bodyJsonStr = {'card_id': cardUidCache}
                messageCarrier["body"] = bodyJsonStr
                data = json.dumps(messageCarrier)
                print(data)
                ws.send(data)
                # TODO wait until CONTINUE
                time.sleep(0.1)

    thread.start_new_thread(readingLoop, ())


try:
    wsapp = websocket.WebSocketApp(
        socketServer, on_open=on_open, on_message=on_message)
# except KeyboardInterrupt:

#     print("key board interrupt")
except:
    print("something else went wrong")
# finally:
#     wsapp.close()
#     GPIO.cleanup()

wsapp.run_forever()
