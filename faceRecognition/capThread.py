# -*- coding: utf-8 -*-
import cv2
import time
import threading

# 接收摄影机串流影像，采用多线程的方式，降低缓冲区栈图帧的问题。
class ipcamCapture:
    def __init__(self, URL):
        self.Frame = []
        self.status = False
        self.isstop = False
        
    # 摄影机连接。
        self.capture = cv2.VideoCapture(URL)

    def start(self):
    # 把程序放进子线程，daemon=True 表示该线程会随着主线程关闭而关闭。
        print('ipcam started!')
        threading.Thread(target=self.queryframe, daemon=True, args=()).start()

    def stop(self):
    # 记得要设计停止无限循环的开关。
        self.isstop = True
        print('ipcam stopped!')
   
    def getframe(self):
    # 当有需要影像时，再回传最新的影像。
        return self.Frame
        
    def queryframe(self):
        while (not self.isstop):
            self.status, self.Frame = self.capture.read()
        
        self.capture.release()
