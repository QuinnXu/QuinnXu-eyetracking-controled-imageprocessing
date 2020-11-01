#!/usr/bin/python3
# WYD HB
import queue
import threading
import time

from PIL import Image
from PIL import ImageFilter
import numpy as np
#from pylab import *
import matplotlib.pyplot as plt
#import cv2
import os
import random
import time
import threading
import socket
import struct
from ctypes import *

import queue
import threading
import time

class Data(Structure):
    _pack_ = 1
    _fields_ = [("px", c_int),
                ("py", c_int),
                ("d", c_int),
                ("isON", c_int),
                ("member_5", c_int)]
                
                
data = Data()
# process thread
class processThread (threading.Thread):
    def __init__(self, threadID, name, q):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.q = q
    def run(self):
        print ("start thread:" + self.name)
        #image process init
        self.all_image = processImageInit()
        #image process
        process_data(self.name, self.q,self.all_image)        
        print ("exit thread:" + self.name)
        
# receive thread        
class receiveThread(threading.Thread):
    def __init__(self, threadID, name, q):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.q = q
    def run(self):
        print ("start thread:" + self.name)
        # socket init 
        PORT = 7401
        receiver_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        address = ("127.0.0.1", PORT)
        receiver_socket.bind(address)
        
        while True:
            now = time.time()
            print(time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(now)))
            #revceive UDP frame
            message, client = receiver_socket.recvfrom(1024)
            #memmove(addressof(data), (message), sizeof(Data))
            print (message)
            #store to workqueue
            #queueLock.acquire()            
            #self.q.put(data)
            #queueLock.release()
            
        print ("exit thread:" + self.name)
  
#im1 is ROI, im2 is whole image
def HisEq_gamma_ROI(im1, im2,gamma, lowerLimitFactor):
    
#    totalcount=im.size[0]*im.size[1]
    limitcurve=np.loadtxt('D:\\testhistogram\\standard.txt')
    limitcurve=[x*im1.size for x in limitcurve]
#    print(im.size)
 
#limited curve
    #histogram
    #imhist,bins = np.histogram(im.flatten(),bins=1024,range=(0.,65535.))#
    imhist,bins = np.histogram(im1.flatten(),bins=1024)
    #print (bins)
    #limit curve
    for i in range(1024):
        imhist[i]=max(min(limitcurve[i],imhist[i]),lowerLimitFactor*limitcurve[i])
    #plot(imhist)
    #cumulated
    cdf = imhist.cumsum()
    #normalised
    cdf = cdf/cdf[-1]
    #gamma correction
    cdf=cdf**gamma
#    for i in range(1024):
#        print(cdf[i])
#    plt.plot(cdf)
    
    #LUT
#    a = im2.flatten()
#    print(a.size)
    im3 = np.interp(im2.flatten(),bins[:1024],cdf)
    #1D convert to 2D
#    print(im2.shape)
    im3 = im3.reshape(im2.shape)
#    im3=im3*255
#    #convert to image
#    im3 = Image.fromarray(im3) 
    return im3

def processImageInit():
    files='D:\\09_innovation\\2020 hackathon day\\eye tracker\\images\\clean_images\\thorax\\tech\\'
    fileList = os.listdir(files)
    #print(fileList)
    file_number= len(os.listdir(files))
    print(file_number)
    all_image=np.zeros((1024,1024,file_number),int)
    for i in range (file_number):
#    im1 =cv2.imread("D:\\09_innovation\\2020 hackathon day\\images\\clean_images\\techlock\\clean_image_00%d.tif"%(i))
        all_image[:,:,i]=np.array(Image.open(files+fileList[i]))
    return all_image
#    im1=np.array(Image.open("D:\\09_innovation\\2020 hackathon day\\images\\clean_images\\techlock\\clean_image_0%d.tif"%(i)))#路径自己选择
#    print(im1[500,500])
#    im2=np.array(im2)
#print(all_image.mean(axis=0).mean(axis=1))
  
    
def process_data(threadName, q, all_image):
    while True:
        queueLock.acquire()
        if not workQueue.empty():
            data = q.get()
            queueLock.release()
            #memmove(addressof(data), (message), sizeof(Data))
            print ('out of queue px: %d' % data.px, 'py: %d' % data.py, 'd: %d' % data.d,'isON: %d' % data.isON, 'member_5: %d' % data.member_5)
            p1 = data.px
            p2 = data.py
            d  = data.d  
            # handswitch is on, begin to process
            if data.isON == 1:
                 i=0
                 image1=np.zeros((1024,1024),dtype=float)
                 k=8
                 while True:
                        queueLock.acquire()
                        if not workQueue.empty():
                            data = q.get()
                            queueLock.release()
                            p1 = data.px
                            p2 = data.py
                            d  = data.d
                            # handswitch off go to the outer loop
                            if data.isON == 0:
                                 break                      
                        else: 
                            queueLock.release()
                                                                                 
                        im = all_image[int(p1-d/2):int(p1+d/2), int(p2-d/2):int(p2+d/2),:]
                        mean_ROI = im.mean(axis=0).mean(axis=0)
                        #test=im.mean(axis=0).mean(axis=0)           
                        minmean = np.abs(mean_ROI-1416)
                        minmean = list(minmean)
                        a = minmean.index(min(minmean))
#                        print(min(minmean), a)
                        im1 = all_image[:,:,a]
                        im2 = im[:,:,a]
                        image = HisEq_gamma_ROI(im2, im1,0.6, 0.5)                        
#                        image=image.filter(ImageFilter.EDGE_ENHANCE)                        
                        image1 = ((k-1.0)/k)*image1 + (1.0/k)*image
                        image2 = image1*255 
                        
                        imageframe = np.zeros((1024,1024),dtype=float)
                        imageframe[int(p1-d/2):int(p1+d/2), int(p2-d/2)] = 255
                        imageframe[int(p1-d/2):int(p1+d/2), int(p2+d/2)] = 255
                        imageframe[int(p1-d/2), int(p2-d/2):int(p2+d/2)] = 255
                        imageframe[int(p1+d/2), int(p2-d/2):int(p2+d/2)] = 255
                        image2 = image2+imageframe
                        image2[image2>255] = 255
#                        print(image2.mean())
                
                        image2 = Image.fromarray(image2)                     
                        
                        image2=image2.convert("L")
#                        print (image2.size)
                        image2.save('D:\\new\\'+str(i)+'.tif') 
                        i = i + 1
#                        now2 = time.time()
#                        print(now2-now)    
            else:
                time.sleep(0.1)
                                                                
        else:
            queueLock.release()
            time.sleep(1)



#init locker 
queueLock = threading.Lock() 
#init work queue
workQueue = queue.Queue(60)
threads = []

#start thread1 thread process
#thread1 = processThread(10,"Thread_process",workQueue)
#thread1.start()
#threads.append(thread1)

#start thread2 thread recv
thread2 = receiveThread(20, "Thread_recv", workQueue)
thread2.start()
threads.append(thread2)

# 等待所有线程完成
for t in threads:
    t.join()
print ("exit main process")