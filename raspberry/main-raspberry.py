import serial
from time import sleep
#Open port
ser = serial.Serial ("/dev/serial0", 19200)   

while 1:
    data = ser.readline()
    ser.write('70-70-70-70-70-70-70-70\n'.encode())
    print(data)
    sleep(0.01)