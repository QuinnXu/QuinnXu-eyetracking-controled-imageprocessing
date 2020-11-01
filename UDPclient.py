#import socket

#client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
#while True:
#    msg = input("please input something:")   
#    server_address = ("127.0.0.1", 8000)  
#    client_socket.sendto(msg.encode(), server_address)
    
# -*- coding: utf-8 -*-

import socket
import time
import random
import struct
from ctypes import *

class Data(Structure):
    _pack_ = 1   #让结构体内存连续
    _fields_ = [("px",c_int),
                ("member_2", c_int),
                ("member_3", c_int),
                ("member_4", c_int),
                ("member_5", c_int)]

data = Data()
#data.px= random.randint(100,900)
#data.member_2= random.randint(100,900)
data.member_3= 300
data.member_4= 1
data.member_5= 1000

PORT = 8000
sender_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
receiver_address = ("127.0.0.1", PORT)

while True:
    start = time.time()
    data.px= random.randint(200,800)
    data.member_2= random.randint(200,800)
    print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(start)))
    sender_socket.sendto(data, receiver_address)
    print ('px: %d' % data.px, 'member_2: %d' % data.member_2, 'member_3: %d' % data.member_3,'member_4: %d' % data.member_4, 'member_5: %d' % data.member_5)
    time.sleep(2)