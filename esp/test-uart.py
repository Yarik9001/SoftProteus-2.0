from machine import UART

uart1 = UART(2, baudrate=9600, tx=17, rx=16)
uart1.write('hello')  # write 5 bytes
data = uart1.read(5)         # read up to 5 bytes
print(data)