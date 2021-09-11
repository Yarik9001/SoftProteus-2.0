import serial
#Open port 
ser = serial.Serial ("/dev/ttyS0", 9600)   

while 1:
    data = ser.readline()
    print(data)