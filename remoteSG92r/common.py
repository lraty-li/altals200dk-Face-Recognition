from enum import Enum

# hardwareType:
# 0 camera
# 1 Id card reader
# 2 face to vector
# 3 web ui
# 4 gate manager
# 5 steering gear


class HardwareType(Enum):
    DEFAULT = 0
    CAMERA = 1
    IDREADER = 2
    ATLAS200 = 3
    WEBUI = 4
    GATEMANG = 5
    MOTOR = 6
    FACEREG = 7  # face register(webui)

# message type:
# 0 null
# 1 CardId
# 2 man id
# 3 gate control
# 4 new user(eneity)


class MessageCtlType(Enum):
    NULLMESSAGE = 0
    CARDID = 1  # received/send id card data
    USERID = 2
    GATECONTROL = 3
    # received new user command from webui CtlMsg{"CtlType":"NEWUSER","Body":MsgUser}
    NEWUSER = 4
    REFLASHIC = 5    # command from webui to read ic card id
    CONTINUE = 6    # command to info hardware continue their working, nomatter if this round success
    # TODO deprecated for now,directly received AuthMsg, not CtlMsg{"CtlType":"AUTH","Body":AuthMsg}
    AUTH = 7
    USERDATA = 8  # user data struct MsgUser
    # send user data to webui CtlMsg{"CtlType":"SHOWUSER","Body":MsgUser}
    SHOWUSER = 9
    USERPK = 10  # the body is eneity's primarily key
