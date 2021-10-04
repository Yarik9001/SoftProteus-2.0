import socket  # библиотека для связи
import threading  # библиотека для потоков
import sys
import serial
import board
import busio
from time import sleep  # библиотека длязадержек
from datetime import datetime  # получение текущего времени
from configparser import ConfigParser  # чтание конфигов
from ast import literal_eval
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn
from adafruit_servokit import ServoKit
import FaBo9Axis_MPU9250
from math import atan2, pi


class ROVProteusClient:
    #Класс ответсвенный за связь с постом 
    def __init__(self):
        self.HOST = '127.0.0.1'
        self.PORT = 1234
        self.telemetria = True
        self.checkConnect = True      
        # Настройки клиента 
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM,)
        self.client.connect((self.HOST, self.PORT))  # подключение адресс  порт

    def ClientDispatch(self, data:dict):
        #Функция для  отправки пакетов на пульт 
        if self.checkConnect:
            data['time'] = str(datetime.now())
            DataOutput = str(data).encode("utf-8")
            self.client.send(data)

    def ClientReceivin(self):
        #Прием информации с поста управления 
        if self.checkConnect:
            data = self.client.recv(512).decode('utf-8')
            if len(data) == 0:
                self.checkConnect = False
                self.client.close()
                return None
            data = dict(literal_eval(str(data)))
            if self.telemetria:
                print(data)
            return data

class Acp:
    def __init__(self):
        '''
        Класс описывающий взаимодействие и опрос датчиков тока 
        '''
        self.i2c = busio.I2C(board.SCL, board.SDA)
        self.ads13 = ADS.ADS1115(self.i2c)
        self.adc46 = ADS.ADS1115(self.i2c, address=0x49)
        a1 = AnalogIn(self.ads13, ADS.P0)
        a2 = AnalogIn(self.ads13, ADS.P1)
        a3 = AnalogIn(self.ads13, ADS.P2)
        a4 = AnalogIn(self.adc46, ADS.P0)
        a5 = AnalogIn(self.adc46, ADS.P1)
        a6 = AnalogIn(self.adc46, ADS.P2)

        self.CorNulA1 = a1.value
        self.CorNulA2 = a2.value
        self.CorNulA3 = a3.value
        self.CorNulA4 = a4.value
        self.CorNulA5 = a5.value
        self.CorNulA6 = a6.value
        
        self.MassOut = {}

    def ReqestAmper(self):
        #Функция опроса датчиков тока 
        a1 = AnalogIn(self.ads13, ADS.P0)
        a2 = AnalogIn(self.ads13, ADS.P1)
        a3 = AnalogIn(self.ads13, ADS.P2)
        a4 = AnalogIn(self.adc46, ADS.P0)
        a5 = AnalogIn(self.adc46, ADS.P1)
        a6 = AnalogIn(self.adc46, ADS.P2)
        # TODO  матан для перевода значений - отсылается уже в амперах
        self.MassOut['a0'] = round(
            (a1.value - self.CorNulA1) * 0.00057321919, 3)
        self.MassOut['a1'] = round(
            (a2.value - self.CorNulA2) * 0.00057321919, 3)
        self.MassOut['a2'] = round(
            (a3.value - self.CorNulA3) * 0.00057321919, 3)
        self.MassOut['a3'] = round(
            (a4.value - self.CorNulA4) * 0.00057321919, 3)
        self.MassOut['a4'] = round(
            (a5.value - self.CorNulA5) * 0.00057321919, 3)
        self.MassOut['a5'] = round(
            (a6.value - self.CorNulA6) * 0.00057321919, 3)
        # возвращает словарь с значениями амрепметра нумерация с нуля
        return self.MassOut

class PwmControl:
    def __init__(self):
        # диапазон шим модуляции 
        self.pwmMin = 1000
        self.pwmMax = 1950
        # коофиценты корректировки мощности на каждый мотор 
        self.CorDrk0 = 1
        self.CorDrk1 = 1
        self.CorDrk2 = 1
        self.CorDrk3 = 1
        self.CorDrk4 = 1
        self.CorDrk5 = 1
        # инициализация платы 
        self.kit = ServoKit(channels=16)

        self.drk0 = self.kit.servo[0]
        self.drk0.set_pulse_width_range(self.pwmMin, self.pwmMax)
        self.drk1 = self.kit.servo[1]
        self.drk1.set_pulse_width_range(self.pwmMin, self.pwmMax)
        self.drk2 = self.kit.servo[2]
        self.drk2.set_pulse_width_range(self.pwmMin, self.pwmMax)
        self.drk3 = self.kit.servo[3]
        self.drk3.set_pulse_width_range(self.pwmMin, self.pwmMax)
        self.drk4 = self.kit.servo[4]
        self.drk4.set_pulse_width_range(self.pwmMin, self.pwmMax)
        self.drk5 = self.kit.servo[5]
        self.drk5.set_pulse_width_range(self.pwmMin, self.pwmMax)
        
        # инициализация моторов 
        self.drk0.angle = 180
        self.drk1.angle = 180
        self.drk2.angle = 180
        self.drk3.angle = 180
        self.drk4.angle = 180
        self.drk5.angle = 180
        sleep(2)
        self.drk0.angle = 0
        self.drk1.angle = 0
        self.drk2.angle = 0
        self.drk3.angle = 0
        self.drk4.angle = 0
        self.drk5.angle = 0
        sleep(2)
        self.drk0.angle = 87
        self.drk1.angle = 87
        self.drk2.angle = 87
        self.drk3.angle = 87
        self.drk4.angle = 87
        self.drk5.angle = 87
        sleep(3)

    def ControlMotor(self, mass: dict):
        # отправка шим сигналов на моторы
        self.drk0.angle = mass['m0']
        self.drk1.angle = mass['m1']
        self.drk2.angle = mass['m2']
        self.drk3.angle = mass['m3']
        self.drk4.angle = mass['m4']
        self.drk5.angle = mass['m5']

class Compass:
    # класс описывающий общение с модулем навигации mpu9250
    def __init__(self):
        self.mpu9250 = FaBo9Axis_MPU9250.MPU9250()
    
    def reqiest(self):
        # возвращает словарь с значениями азимута 
        mag = self.mpu9250.readMagnet()
        return {'azim':(round((atan2(mag['x'], mag['y']) * 180 / pi), 3))}

class Dept:
    # класс описывающий общение с датчиком глубины 
    def __init__(self):
        pass
    

class ReqiestSensor:
    # класс-адаптер обьеденяющий в себе сбор информации с всех сенсоров 
    def __init__(self):
        self.acp = Acp() # обект класса ацп 
        self.mpu9250 = Compass() # обьект класса compass 
        self.dept = None 
    
    def reqiest(self):
        # опрос датчиков; возвращает обьект класса словарь 
        massacp  = self.acp.ReqestAmper()
        massaz = self.mpu9250.reqiest()
        
        massout = {**massacp, **massaz}
        return massout



class MainApparat:
    def __init__(self):
        self.DataInput = {'time': None,  # Текущее время
                            'motorpowervalue': 1,  # мощность моторов
                            'led': False,  # управление светом
                            'manipul': 0,  # Управление манипулятором
                            'servo': 0, # управление наклоном камеры 
                            'motor0': 0, 'motor1': 0, # значения мощности на каждый мотор 
                            'motor2': 0, 'motor3': 0, 
                            'motor4': 0, 'motor5': 0}
        # массив отсылаемый на аппарат 
        self.DataOutput = {'time': None,'dept': 0,'volt': 0, 'azimut': 0 }

        self.client = ROVProteusClient()
        self.sensor = ReqiestSensor()


    def RunMainApparat(self):
        # прием информации с поста управления 
        # отработка по принятой информации 
        # сбор информации с датчиков 
        # отправка телеметрии на пост управления
        while True:
            controllmass = self.client.ClientReceivin()
            print(controllmass)
            self.client.ClientDispatch({'time': None,'dept': 0,'volt': 0, 'azimut': 0 })

if __name__ == '__main__':
    apparat = MainApparat()
    apparat.RunMainApparat()