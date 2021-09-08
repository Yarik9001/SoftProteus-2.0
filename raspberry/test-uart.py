import serial
ser = serial.Serial ("/dev/ttyAMA0")    #Open named port 
ser.baudrate = 9600                     #Set baud rate to 9600
data = ser.read(10)  
#Read ten characters from serial port to data
while True:
    ser.write('12345')  
    print('12345')  
