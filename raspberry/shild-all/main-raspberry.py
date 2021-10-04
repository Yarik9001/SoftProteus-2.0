import socket  # библиотека для связи
import threading  # библиотека для потоков
import sys
import serial
from time import sleep  # библиотека длязадержек
from datetime import datetime  # получение текущего времени
from configparser import ConfigParser  # чтание конфигов
from ast import literal_eval
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn
from adafruit_servokit import ServoKit

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
'''
class ShieldTnpa:
    def __init__(self):
        # Создание обьекта для взаимодействия с низким уровнем по uart
        self.PORT = "/dev/serial0"
        self.RATE = 19200
        self.serialPort = serial.Serial(self.PORT, self.RATE)
        self.checkConnect = True   
    
    def ShildDispatch(self, data:list):
        # отправка на аппарат
        if self.checkConnect:
            data = (str(data) + '\n').encode()
            self.serialPort.write(data)
            
    def ShildReceivin(self):
        # прием информации с аппарата 
        if self.checkConnect:
            data = self.serialPort.readline()
            if len(str(data)) <= 5:
                return None
            data = [int(i) for i in ((str(data)[2:-3]).split('-'))]
            return data 
'''


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

    def mainAmperemeter(self):
        '''
        Функция опроса датчиков тока 
        '''
        while True:
            a1 = AnalogIn(self.ads13, ADS.P0)
            a2 = AnalogIn(self.ads13, ADS.P1)
            a3 = AnalogIn(self.ads13, ADS.P2)
            a4 = AnalogIn(self.adc46, ADS.P0)
            a5 = AnalogIn(self.adc46, ADS.P1)
            a6 = AnalogIn(self.adc46, ADS.P2)
            # TODO  матан для перевода значений - отсылается уже в амперах
            self.rov.client.MassOut['a1'] = round(
                (a1.value - self.CorNulA1) * 0.00057321919, 3)
            self.rov.client.MassOut['a2'] = round(
                (a2.value - self.CorNulA2) * 0.00057321919, 3)
            self.rov.client.MassOut['a3'] = round(
                (a3.value - self.CorNulA3) * 0.00057321919, 3)
            self.rov.client.MassOut['a4'] = round(
                (a4.value - self.CorNulA4) * 0.00057321919, 3)
            self.rov.client.MassOut['a5'] = round(
                (a5.value - self.CorNulA5) * 0.00057321919, 3)
            self.rov.client.MassOut['a6'] = round(
                (a6.value - self.CorNulA6) * 0.00057321919, 3)
            sleep(0.25)


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
        self.shield = ShieldTnpa()
        
    def RunCommand(self):
        while True:
            # блок отправки значений на аппарат
            self.DataInput = self.client.ClientReceivin()
            dat = self.DataInput
            datalist  = [dat['motor0'], dat['motor1'], dat['motor2'],
                        dat['motor3'], dat['motor4'], dat['motor5'], 
                        dat['servo'], dat['manipul']]
            self.shield.ShildDispatch(datalist)
            
            # блок приема ответа с телеметрией 
            inputlist = self.shield.ShildReceivin()
            self.DataOutput['volt'] = inputlist[0]
            self.DataOutput['dept'] = inputlist[1]
            self.DataOutput['azimut'] = inputlist[2]
            self.DataOutput['time'] = str(datetime.now())
            
            self.client.ClientDispatch(self.DataOutput)
            

