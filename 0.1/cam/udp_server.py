import cv2
import socket
import pickle
import numpy as np

max_length = 65540

DEBUG = False

max_length = 65000
if DEBUG:
    host = '127.0.0.1'
    port = 2224
else:
    host = '192.168.1.100'
    port = 5001
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((host, port))

frame_info = None
buffer = None
frame = None

print("-> waiting for connection")

while True:
    data, address = sock.recvfrom(max_length)
    
    if len(data) < 100:
        frame_info = pickle.loads(data)

        if frame_info:
            nums_of_packs = frame_info["packs"]

            for i in range(nums_of_packs):
                data, address = sock.recvfrom(max_length)

                if i == 0:
                    buffer = data
                else:
                    buffer += data

            frame = np.frombuffer(buffer, dtype=np.uint8)
            frame = frame.reshape(frame.shape[0], 1)

            frame = cv2.imdecode(frame, cv2.IMREAD_COLOR)
            #frame = cv2.flip(frame, 1)
            #frame = cv2.resize(frame,(960,720))
            
            if frame is not None and type(frame) == np.ndarray:
                cv2.imshow("Stream", frame)
                if cv2.waitKey(1) == 27:
                    break
                
print("goodbye")
