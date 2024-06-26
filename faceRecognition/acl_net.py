"""
-*- coding:utf-8 -*-
CREATED:  2020-6-04 20:12:13
MODIFIED: 2020-6-17 14:04:45
"""
from mtcnn_cv2 import MTCNN
import argparse
import time
import numpy as np
import struct
from websocket import create_connection


import acl
import cv2
import os
from PIL import Image
from capThread import ipcamCapture
from constant import ACL_MEM_MALLOC_HUGE_FIRST, \
    ACL_MEMCPY_HOST_TO_DEVICE, ACL_MEMCPY_DEVICE_TO_HOST, \
    ACL_ERROR_NONE, IMG_EXT
from tools.hnswlibTest import faceSearcher
import utilLib
buffer_method = {
    "in": acl.mdl.get_input_size_by_index,
    "out": acl.mdl.get_output_size_by_index
}

detector = MTCNN()


def check_ret(message, ret):
    if ret != ACL_ERROR_NONE:
        raise Exception("{} failed ret={}"
                        .format(message, ret))


class Net(object):
    def __init__(self, device_id, model_path):
        self.device_id = device_id      # int
        self.model_path = model_path    # string
        self.model_id = None            # pointer
        self.context = None             # pointer

        self.input_data = []
        self.output_data = []
        self.model_desc = None          # pointer when using
        self.load_input_dataset = None
        self.load_output_dataset = None
        #temp store result vetcor
        self.resultCache = {}
        self.init_resource()

    def __del__(self):
        # print("Releasing resources stage:")
        ret = acl.mdl.unload(self.model_id)
        check_ret("acl.mdl.unload", ret)
        if self.model_desc:
            acl.mdl.destroy_desc(self.model_desc)
            self.model_desc = None

        while self.input_data:
            item = self.input_data.pop()
            ret = acl.rt.free(item["buffer"])
            check_ret("acl.rt.free", ret)

        while self.output_data:
            item = self.output_data.pop()
            ret = acl.rt.free(item["buffer"])
            check_ret("acl.rt.free", ret)

        if self.context:
            ret = acl.rt.destroy_context(self.context)
            check_ret("acl.rt.destroy_context", ret)
            self.context = None

        ret = acl.rt.reset_device(self.device_id)
        check_ret("acl.rt.reset_device", ret)
        ret = acl.finalize()
        check_ret("acl.finalize", ret)
        print('Resources released successfully.')

    def init_resource(self):
        print("init resource stage:")
        ret = acl.init()
        check_ret("acl.init", ret)
        ret = acl.rt.set_device(self.device_id)
        check_ret("acl.rt.set_device", ret)

        self.context, ret = acl.rt.create_context(self.device_id)
        check_ret("acl.rt.create_context", ret)

        # load_model
        self.model_id, ret = acl.mdl.load_from_file(self.model_path)
        check_ret("acl.mdl.load_from_file", ret)
        print("model_id:{}".format(self.model_id))

        self.model_desc = acl.mdl.create_desc()
        self._get_model_info()
        print("init resource success")

    def _get_model_info(self,):
        ret = acl.mdl.get_desc(self.model_desc, self.model_id)
        check_ret("acl.mdl.get_desc", ret)
        input_size = acl.mdl.get_num_inputs(self.model_desc)
        output_size = acl.mdl.get_num_outputs(self.model_desc)
        self._gen_data_buffer(input_size, des="in")
        self._gen_data_buffer(output_size, des="out")

    def _gen_data_buffer(self, size, des):
        func = buffer_method[des]
        for i in range(size):
            # check temp_buffer dtype
            temp_buffer_size = func(self.model_desc, i)
            temp_buffer, ret = acl.rt.malloc(temp_buffer_size,
                                             ACL_MEM_MALLOC_HUGE_FIRST)
            check_ret("acl.rt.malloc", ret)

            if des == "in":
                self.input_data.append({"buffer": temp_buffer,
                                        "size": temp_buffer_size})
            elif des == "out":
                self.output_data.append({"buffer": temp_buffer,
                                         "size": temp_buffer_size})

    def _data_interaction(self, dataset, policy=ACL_MEMCPY_HOST_TO_DEVICE):
        temp_data_buffer = self.input_data \
            if policy == ACL_MEMCPY_HOST_TO_DEVICE \
            else self.output_data
        if len(dataset) == 0 and policy == ACL_MEMCPY_DEVICE_TO_HOST:
            for item in self.output_data:
                temp, ret = acl.rt.malloc_host(item["size"])
                if ret != 0:
                    raise Exception("can't malloc_host ret={}".format(ret))
                dataset.append({"size": item["size"], "buffer": temp})

        for i, item in enumerate(temp_data_buffer):
            if policy == ACL_MEMCPY_HOST_TO_DEVICE:
                ptr = acl.util.numpy_to_ptr(dataset[i])
                ret = acl.rt.memcpy(item["buffer"],
                                    item["size"],
                                    ptr,
                                    item["size"],
                                    policy)
                check_ret("acl.rt.memcpy", ret)

            else:
                ptr = dataset[i]["buffer"]
                ret = acl.rt.memcpy(ptr,
                                    item["size"],
                                    item["buffer"],
                                    item["size"],
                                    policy)
                check_ret("acl.rt.memcpy", ret)

    def _gen_dataset(self, type_str="input"):
        dataset = acl.mdl.create_dataset()

        temp_dataset = None
        if type_str == "in":
            self.load_input_dataset = dataset
            temp_dataset = self.input_data
        else:
            self.load_output_dataset = dataset
            temp_dataset = self.output_data

        for item in temp_dataset:
            data = acl.create_data_buffer(item["buffer"], item["size"])
            _, ret = acl.mdl.add_dataset_buffer(dataset, data)

            if ret != ACL_ERROR_NONE:
                ret = acl.destroy_data_buffer(data)
                check_ret("acl.destroy_data_buffer", ret)

    def _data_from_host_to_device(self, images):
        # print("data interaction from host to device")
        # copy images to device
        self._data_interaction(images, ACL_MEMCPY_HOST_TO_DEVICE)
        # load input data into model
        self._gen_dataset("in")
        # load output data into model
        self._gen_dataset("out")
        # print("data interaction from host to device success")

    def _data_from_device_to_host(self):
        # print("data interaction from device to host")
        res = []
        # copy device to host
        self._data_interaction(res, ACL_MEMCPY_DEVICE_TO_HOST)
        # print("data interaction from device to host success")
        result = self.get_result(res)
        self._print_result(result)

    def run(self, images):
        self._data_from_host_to_device(images)
        self.forward()
        self._data_from_device_to_host()

    def forward(self):
        # print('execute stage:')
        ret = acl.mdl.execute(self.model_id,
                              self.load_input_dataset,
                              self.load_output_dataset)
        check_ret("acl.mdl.execute", ret)
        self._destroy_databuffer()
        # print('execute stage success')

    def _print_result(self, result):
        tuple_st = struct.unpack("512f", bytearray(result[0]))
        vals = np.array(tuple_st).flatten()
        vals = utilLib.normL2Vector(vals)
        self.resultCache=vals
        # ws = create_connection("ws://192.168.1.229:8080/ws")
        # recv =  ws.recv()
        # ws.send(np.array2string(vals))
        # recv =  ws.recv()
        # ws.close()

        # np.save("LiData.npy",vals)
        # facesDB.search(vals)
        # print("distance to default:", np.linalg.norm(defaultVal-vals))

        # top_k = vals.argsort()[-1:-6:-1]
        # print("======== top5 inference results: =============")

        # for j in top_k:
        #     print("[%d]: %f" % (j, vals[j]))

    def _destroy_databuffer(self):
        for dataset in [self.load_input_dataset, self.load_output_dataset]:
            if not dataset:
                continue
            number = acl.mdl.get_dataset_num_buffers(dataset)
            for i in range(number):
                data_buf = acl.mdl.get_dataset_buffer(dataset, i)
                if data_buf:
                    ret = acl.destroy_data_buffer(data_buf)
                    check_ret("acl.destroy_data_buffer", ret)
            ret = acl.mdl.destroy_dataset(dataset)
            check_ret("acl.mdl.destroy_dataset", ret)

    def get_result(self, output_data):
        dataset = []
        for temp in output_data:
            size = temp["size"]
            ptr = temp["buffer"]
            data = acl.util.ptr_to_numpy(ptr, (size,), 1)
            dataset.append(data)
        return dataset

# def transfer_pic(input_path):


def transfer_pic(img):
    # input_path = os.path.abspath(input_path)
    # image_file = Image.open(input_path)
    # image_file = image_file.resize((256, 256))
    # img = np.array(image_file)
    # height = img.shape[0]
    # width = img.shape[1]

    # img = cv2.imread("./data/live.png")
    # cv2.imwrite("live.png", img)

    # opencv haar
    # faces = face_detecter.detectMultiScale(
    #     image=img, scaleFactor=1.1, minNeighbors=5)

    # if len(faces) == 0:
    #     print("no face detected")
    #     return None
    # # get max box only
    # faces = np.array(faces)
    # MaxIndex = np.where(faces == np.max(faces[:, 2]))[0][0]
    # face = faces[MaxIndex]
    # # print("detect face in ", face)
    # if face[3]<100:
    #     # print("maybe it not face")
    #     return None

    # mtcnn
    result = detector.detect_faces(img)
    if len(result) == 0:
        return None
    
    bounding_box = result[0]['box']
    if bounding_box[3]<100:
        return None
    print(bounding_box)

    # for x, y, w, h in face:
    # img = img[y:y+h, x:x+w]
    img = img[bounding_box[1]:bounding_box[1]+bounding_box[3],
              bounding_box[0]:bounding_box[0]+bounding_box[2]]
    
    # cv default is bgr, turn to rgb
    # img = img[:, :, [2, 1, 0]]
    img = cv2.resize(img, (160, 160))
    # 对图片进行切分，取中间区域
    # h_off = (height - 224) // 2
    # w_off = (width - 224) // 2
    # h_off = (height - 160) // 2
    # w_off = (width - 160) // 2
    # crop_img = img[h_off:height - h_off, w_off:width - w_off, :]

    # im = Image.fromarray(crop_img)

    # im.save("{}-out.jpg".format(input_path))

    # rgb to bgr，改变通道顺序
    # img = crop_img[:, :, ::-1]
    # shape = img.shape
    img = img.astype("float32")
    # img[:, :, 0] -= 104
    # img[:, :, 1] -= 117
    # img[:, :, 2] -= 123
    # img = img.reshape([1] + list(shape))
    # img = img.transpose([0, 3, 1, 2])
    # result = np.frombuffer(img.tobytes(), np.float16)

    img = utilLib.prewhiten(img)
    img = img.reshape([1] + list(img.shape))
    img = img.transpose([0, 3, 1, 2])

    result = np.frombuffer(img.tobytes(), np.float32)
    img = None
    return result


if __name__ == '__main__':

    facesDB = faceSearcher()
    parser = argparse.ArgumentParser()
    parser.add_argument('--device', type=int, default=0)
    parser.add_argument('--model_path', type=str,
                        default="./model/faceNet-caffe-NCHW.om")
    parser.add_argument('--images_path', type=str, default="./data")
    args = parser.parse_args()
    print("Using device id:{}\nmodel path:{}\nimages path:{}"
          .format(args.device, args.model_path, args.images_path))

    net = Net(args.device, args.model_path)
    images_list = [os.path.join(args.images_path, img)
                   for img in os.listdir(args.images_path)
                   if os.path.splitext(img)[1] in IMG_EXT]

    # for image in images_list:
    #     print("images:{}".format(image))
    #     img = transfer_pic(image)
    #     net.run([img])

    camera_path = "rtmp://192.168.1.201:1935/live/rov"

    # 连接摄影机
    ipcam = ipcamCapture(camera_path)

    # 启动子线程
    ipcam.start()

    # 暂停1秒，确保影像已经填充
    time.sleep(1)
    # vid = cv2.VideoCapture(camera_path)
    count = 2
    if not ipcam.capture.isOpened():
        raise IOError("could't open webcamera or video")
    while(ipcam.capture.isOpened() and count > 0):
        frame = ipcam.getframe()
        # if ret: #check get frame status
        #frame is bgr
        faceImg = transfer_pic(frame)
        if faceImg is None:
            continue
        net.run([faceImg])
        # count = count-1

    # print("the result Dict:",net.resultDic)
    # utilLib.printAllDistance(net.resultDic)

    print("*****run finish******")
