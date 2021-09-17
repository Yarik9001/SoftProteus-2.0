import socket
import threading  # модуль для разделения на потоки
from datetime import datetime  # получение  времени
from time import sleep  # сон
from ast import literal_eval  # модуль для перевода строки в словарик
from os import system
from pyPS4Controller.controller import Controller

class ServerMainPult:
    '''
    Класс описывающий систему бекенд пульта
    log - флаг логирования 
    log cmd - флаг вывода логов с cmd 
    host - хост на котором будет крутиться сервер 
    port- порт для подключения 
    motorpowervalue=1 - программное ограничение мощности моторов 
    joystickrate - частота опроса джойстика 
    '''

    def __init__(self):
        # инициализация атрибутов
        self.HOST = '192.168.1.100'
        self.PORT = 1000
        self.JOYSTICKRATE = 0.1
        self.MotorPowerValue = 1
        self.log = True
        self.telemeria = True
        self.checkConnect = False
        # настройка сервера
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM,)
        self.server.bind((self.HOST, self.PORT))
        self.server.listen(1)
        self.user_socket, self.address = self.server.accept()
        self.checkConnect = True
        if self.logcmd:
            print("ROV-Connected", self.user_socket)

    def ReceiverProteus(self):
        if self.checkConnect:
            data = self.user_socket.recv(512)
            if len(data) == 0:
                self.server.close()
                self.checkConnect = False
                if self.telemeria:
                    print('ROV-disconnection', self.user_socket)
            self.DataInput = dict(literal_eval(str(data.decode('utf-8'))))
            if self.telemeria:
                print("DataInput-", self.DataInput)
            
    def ControlProteus(self, data:dict):
        if self.checkConnect:
            
            self.user_socket.send(str(data).encode('utf-8'))
            if self.telemeria:
                print('DataOutput-', data)
            sleep(self.JOYSTICKRATE)
            print(data)

class MyController(Controller):
    '''
    Класс для взаимодействия с джойстиком PS4 
    (работает только из под линукса из под винды управление только с помощью клавиатуры)
    
    правый джойтик вперед - движение вперед 
    правый джойстик вбок - движение лагом 
    
    левый джойстик вперед - всплытие
    левый джойстик вбок - разворот на месте 
    
    кнопки - корректировка нулевого положения для противодействия течениям и прочей ериси 
    
    кнопка ps - обнуление корректировок 
    
    Торцевые кнопки слева - управление манипулятором 
    
    торцевые кнопки справа - управление поворотом камеры 
    
    '''

    def __init__(self):
        Controller.__init__(self,interface="/dev/input/js0", connecting_using_ds4drv=False)
        self.DataPult = {'j1-val-y': 0, 'j1-val-x': 0,
                         'j2-val-y': 0, 'j2-val-x': 0,
                         'ly-cor': 0, 'lx-cor':0,
                         'ry-cor':0, 'rx-cor': 0}
        
    def transp(self, value):
        return -1 * (value // 328)
    
    def on_L3_up(self, value):
        self.DataPult['j1-val-y'] = -1 * value
        if self.pult.logcmd:
            print('forward')
    
    
    def on_L3_down(self, value):
        self.DataPult['j1-val-y'] = -1* value
        self.pult.DataOutput['y'] = self.transp(value)
        if self.pult.logcmd:
            print('back')
    
    def on_L3_y_at_rest(self):
        self.DataPult['j1-val-y'] = 0
        if self.pult.logcmd:
            print('back')
            
    def on_L3_left(self, value):
        self.DataPult['j1-val-x'] = -1 * value
        if self.pult.logcmd:
            print('left')
    
    def on_L3_right(self, value):
        self.DataPult['j1-val-x'] = -1 * value
        if self.pult.logcmd:
            print('right')
    
    def on_L3_x_at_rest(self):
        self.DataPult['j1-val-x'] = 0
        if self.pult.logcmd:
            print('right')
            
    def on_R3_up(self, value):
        self.DataPult['j2-val-y'] = -1 * value
        if self.pult.logcmd:
            print('up')
    
    def on_R3_down(self, value):
        self.DataPult['j2-val-y'] = -1 * value
        if self.pult.logcmd:
            print('down')
            
    def on_R3_y_at_rest(self):
        self.DataPult['j2-val-y'] = 0
        if self.pult.logcmd:
            print('down')
            
    def on_R3_left(self, value):
        self.DataPult['j2-val-x'] = -1 * value

        if self.pult.logcmd:
            print('turn-left')
            
    def on_R3_right(self, value):
        self.DataPult['j2-val-x'] = -1 * value

        if self.pult.logcmd:
            print('turn-left')
    
    def on_R3_x_at_rest(self):
        self.DataPult['j2-val-x'] = 0
        if self.pult.logcmd:
            print('turn-left')
            
    def on_x_press(self):
        self.DataP['ry-cor'] -= 10
        
    def on_triangle_press(self):
        self.DataOutput['ry-cor'] += 10
    
    def on_square_press(self):
        self.pult.DataOutput['rx-cor'] += 10
        
    def on_circle_press(self):
        self.pult.DataOutput['rx-cor'] -= 10

    def on_up_arrow_press(self):
        self.pult.DataOutput['ly-cor'] -= 10
    
    def on_down_arrow_press(self):
        self.pult.DataOutput['ly-cor'] += 10
    
    def on_left_arrow_press(self):
        self.pult.DataOutput["lx-cor"] -= 10
    
    def on_right_arrow_press(self):
        self.pult.DataOutput['lx-cor'] += 10
        
    def on_playstation_button_press(self):
        self.pult.DataOutput['ly-cor'] = 0
        self.pult.DataOutput['lx-cor'] = 0
        self.pult.DataOutput['rx-cor'] = 0
        self.pult.DataOutput['ry-cor'] = 0
        
        
class MainPost:
    def __init__(self):
        
        # словарик для отправки на аппарат
        self.DataOutput = {'time': None,  # Текущее время
                           'motorpowervalue': 1,  # мощность моторов
                           'x': 0, 'y': 0, 'z': 0, 'r': 0,# по идее мощность моторов
                           'led': False,  # управление светом
                           'manipul': 0,  # Управление манипулятором
                           'motor0': 0, 'motor1': 0,
                           'motor2': 0, 'motor3': 0, 
                           'motor4': 0, 'motor5': 0,# управление подвесом обзорной камеры
                            }
        self.DataInput = {'time': None,'dept': 0,'volt': 0, 'azimut': 0 }
