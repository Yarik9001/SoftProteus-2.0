from machine import Pin, PWM
from time import sleep

pwm0 = PWM(Pin(13), freq=50)# create PWM object from a pin
pwm0.duty(120)
sleep(2)
pwm0.duty(20)
sleep(2)
pwm0.duty(70)
sleep(2)
for i in range(20,121):
    pwm0.duty(i)# set duty cycle
    print(i)
    sleep(0.1)
