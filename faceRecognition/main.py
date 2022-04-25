# keep this on first line?
from milvusDB import MilvusDB
import json

from common import HardwareType, MessageCtlType
from socketThread import SocketClient

try:
    import thread
except ImportError:
    import _thread as thread
from acl_net import *
from capThread import *

parser = argparse.ArgumentParser()
parser.add_argument('--device', type=int, default=0)
parser.add_argument('--model_path', type=str,
                    default="./model/faceNet-caffe-NCHW.om")
parser.add_argument('--images_path', type=str, default="./data")
args = parser.parse_args()
print("Using device id:{}\nmodel path:{}\nimages path:{}"
      .format(args.device, args.model_path, args.images_path))

net = Net(args.device, args.model_path)
faceDB = MilvusDB()
camera_path = "rtmp://192.168.1.201:1935/live/rov"

# 连接摄影机
ipcam = ipcamCapture(camera_path)
# 启动子线程
ipcam.start()
# 暂停1秒，确保影像已经填充
time.sleep(1)

detector = MTCNN()
socketClient = SocketClient()
# the recognition pause to swait for CONTINUE form server
PAUSE = False


def img2vetc(frame):
    # frame : img to be progress
    # return :face vetor or none
    if frame is None:
        return None
    # TODO the net will always return a vetcor
    net.run([frame])
    # ndarrya[floate32]
    return net.resultCache


def detectFace(frame):
    result = detector.detect_faces(frame)
    if len(result) == 0:
        return None

    bounding_box = result[0]['box']
    if bounding_box[3] < 100:
        # not consider as face
        return None
    print("face detc in", bounding_box)

    # for x, y, w, h in face:
    # img = img[y:y+h, x:x+w]
    img = frame[bounding_box[1]:bounding_box[1]+bounding_box[3],
                bounding_box[0]:bounding_box[0]+bounding_box[2]]

    img = cv2.resize(img, (160, 160))

    img = img.astype("float32")

    img = utilLib.prewhiten(img)
    img = img.reshape([1] + list(img.shape))
    # cv2 is bgr, turn to rgb
    img = img.transpose([0, 3, 1, 2])

    result = np.frombuffer(img.tobytes(), np.float32)
    img = None
    return result


def on_message(wsapp, message):
    print(message)


def mainLoop(*args):
    if not ipcam.capture.isOpened():
        raise IOError("could't open webcamera or video")
    while(ipcam.capture.isOpened()):
        if(socketClient.modes["onNewUser"]):
            # new user request recvd
            image = np.asarray(
                bytearray(socketClient.imgCache.read()), dtype="uint8")
            image = cv2.imdecode(image, cv2.IMREAD_COLOR)
            face = detectFace(image)
            if face is None:
                continue
            vetc = img2vetc(face)
            # {"ctlType":11,"body":{"user_pk":40,"face_img_name":"1650769056689.jpg"}}
            faceDB.inserData(
                socketClient.msgCache['body']['user_pk'], vetc.tolist())
            #clear
            socketClient.msgCache=None
            socketClient.imgCache=None
            socketClient.modes["onNewUser"]=False
        else:
            frame = ipcam.getframe()
            # if ret: #check get frame status
            #frame is bgr
            face = detectFace(frame)
            if face is None:
                continue
            vetc = img2vetc(face)
            result = faceDB.queryVetc(vetc.tolist())
            if len(result) >= 1:
                # send first user pk
                print("send pk ", result[0])
                socketClient.sendUserPK(int(result[0]))


mainLoop()
