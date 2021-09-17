import socket
import threading  # модуль для разделения на потоки
from datetime import datetime  # получение  времени
from time import sleep  # сон
from ast import literal_eval  # модуль для перевода строки в словарик
from pyPS4Controller.controller import Controller

class ServerMainPult:
    '''
    Класс описывающий систему бекенд- пульта
    log - флаг логирования 
    log cmd - флаг вывода логов с cmd 
    host - хост на котором будет крутиться сервер 
    port- порт для подключения 
    motorpowervalue=1 - программное ограничение мощности моторов 
    joystickrate - частота опроса джойстика 
    '''

    def __init__(self):
        # инициализация атрибутов
        self.HOST = '127.0.0.1'
        self.PORT = 1234
        self.JOYSTICKRATE = 0.1
        self.MotorPowerValue = 1
        self.log = True
        self.telemetria = True
        self.checkConnect = False
        # настройка сервера
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM,)
        self.server.bind((self.HOST, self.PORT))
        self.server.listen(1)
        self.user_socket, self.address = self.server.accept()
        self.checkConnect = True
        if self.telemetria:
            print("ROV-Connected", self.user_socket)

    def ReceiverProteus(self):
        if self.checkConnect:
            data = self.user_socket.recv(512)
            if len(data) == 0:
                self.server.close()
                self.checkConnect = False
                if self.telemetria:
                    print('ROV-disconnection', self.user_socket)
                    return None
            data = dict(literal_eval(str(data.decode('utf-8'))))
            if self.telemetria:
                print("DataInput-", data)
            return data
            
            
    def ControlProteus(self, data:dict):
        if self.checkConnect:
            self.user_socket.send(str(data).encode('utf-8'))
            if self.telemetria:
                print('DataOutput-', data)


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
        self.log = True
        self.telemetria = True
        
    def transp(self, value):
        return -1 * (value // 328)
    
    def on_L3_up(self, value):
        self.DataPult['j1-val-y'] = -1 * value
        if self.telemetria:
            print('forward')
    
    
    def on_L3_down(self, value):
        self.DataPult['j1-val-y'] = -1* value
        if self.telemetria:
            print('back')
    
    def on_L3_y_at_rest(self):
        self.DataPult['j1-val-y'] = 0
        if self.telemetria:
            print('back')
            
    def on_L3_left(self, value):
        self.DataPult['j1-val-x'] = -1 * value
        if self.telemetria:
            print('left')
    
    def on_L3_right(self, value):
        self.DataPult['j1-val-x'] = -1 * value
        if self.telemetria:
            print('right')
    
    def on_L3_x_at_rest(self):
        self.DataPult['j1-val-x'] = 0
        if self.pult.logcmd:
            print('right')
            
    def on_R3_up(self, value):
        self.DataPult['j2-val-y'] = -1 * value
        if self.telemetria:
            print('up')
    
    def on_R3_down(self, value):
        self.DataPult['j2-val-y'] = -1 * value
        if self.telemetria:
            print('down')
            
    def on_R3_y_at_rest(self):
        self.DataPult['j2-val-y'] = 0
        if self.telemetria:
            print('down')
            
    def on_R3_left(self, value):
        self.DataPult['j2-val-x'] = -1 * value
        if self.telemetria:
            print('turn-left')
            
    def on_R3_right(self, value):
        self.DataPult['j2-val-x'] = -1 * value
        if self.telemetria:
            print('turn-left')
    
    def on_R3_x_at_rest(self):
        self.DataPult['j2-val-x'] = 0
        if self.telemetria:
            print('turn-left')
            
    def on_x_press(self):
        if self.DataPult['ry-cor'] >=10:
            self.DataPult['ry-cor'] -= 10
        
    def on_triangle_press(self):
        if self.DataPult['ry-cor'] <= 90:
            self.DataPult['ry-cor'] += 10
    
    def on_square_press(self):
        if self.DataPult['rx-cor'] <= 90:
            self.DataPult['rx-cor'] += 10
        
    def on_circle_press(self):
        if self.DataPult['rx-cor'] >= 10:
            self.DataPult['rx-cor'] -= 10

    def on_up_arrow_press(self):
        if self.DataPult['ly-cor'] >=10:
            self.DataPult['ly-cor'] -= 10
    
    def on_down_arrow_press(self):
        if self.DataPult['ly-cor'] >=10:
            self.DataPult['ly-cor'] += 10
    
    def on_left_arrow_press(self):
        if self.DataPult["lx-cor"] >=10:
            self.DataPult["lx-cor"] -= 10
    
    def on_right_arrow_press(self):
        if self.DataPult['lx-cor'] <=90:
            self.DataPult['lx-cor'] += 10
        
    def on_playstation_button_press(self):
        self.DataPult['ly-cor'] = 0
        self.DataPult['lx-cor'] = 0
        self.DataPult['rx-cor'] = 0
        self.DataPult['ry-cor'] = 0


class MainPost:
    def __init__(self):
        # словарик для отправки на аппарат
        self.DataOutput = {'time': None,  # Текущее время
                           'motorpowervalue': 1,  # мощность моторов
                           'led': False,  # управление светом
                           'manipul': 0,  # Управление манипулятором
                           'servo': 0, # управление наклоном камеры 
                           'motor0': 0, 'motor1': 0, # значения мощности на каждый мотор 
                           'motor2': 0, 'motor3': 0, 
                           'motor4': 0, 'motor5': 0}
        # словарик получаемый с аппарата 
        self.DataInput = {'time': None,'dept': 0,'volt': 0, 'azimut': 0 }
        
        self.Server = ServerMainPult() # поднимаем сервер 
        self.Controllps4 = MyController() # поднимаем контролеер 
        self.DataPult = self.Controllps4.DataPult
        self.RateCommandOut= 0.1
        self.telemetria = True
        
    def RunController(self):
        self.Controllps4.listen()
        
    def RunCommand(self):
        '''
        Движение вперед - (1 вперед 2 вперед 3 назад 4 назад) 
        Движение назад - (1 назад 2 назад 3 вперед 4 вперед)
        Движение лагом вправо - (1 назад 2 вперед 3 вперед 4 назад)
        Движение лагом влево - (1 вперед 2 назад 3 назад 4 вперед)
        Движение вверх - (5 вниз 6 вниз)
        Движение вниз - (5 вверх 6 вверх)
        Поворот направо 
        Поворот налево 
        '''
        def transformation(value:int):
            #Функция перевода значений АЦП с джойстика в проценты
            value = (32768 - value) // 655
            return value
        
        def defense(value:int):
            if value > 100:
                value = 100
            elif value < 0:
                value = 0 
            return value
        while True:
            data = self.DataPult
            
            J1_Val_Y = transformation(data['j1-val-y'])
            J1_Val_X = transformation(data['j1-val-x'])
            J2_Val_Y = transformation(data['j2-val-y'])
            J2_Val_X = transformation(data['j2-val-x'])
            
            self.DataOutput['motor0'] = defense(J1_Val_Y + J1_Val_X + J2_Val_X - 100)
            self.DataOutput['motor1'] = defense(J1_Val_Y - J1_Val_X - J2_Val_X + 100)
            self.DataOutput['motor2'] = defense((-1 * J1_Val_Y) - J1_Val_X + J2_Val_X + 100)
            self.DataOutput['motor3'] = defense((-1 * J1_Val_Y) + J1_Val_X - J2_Val_X + 100)
            self.DataOutput['motor4'] = defense(J2_Val_Y)
            self.DataOutput['motor5'] = defense(J2_Val_Y)
            
            self.DataOutput["time"] = str(datetime.now())
            
            # математика преобразования значений с джойстика в значения для моторов 
            self.Server.ControlProteus(self.DataOutput)
            self.DataInput = self.Server.ReceiverProteus()
            if self.telemetria:
                print(self.DataInput)
            sleep(self.RateCommandOut)
        
    def RunMain(self):
        ThreadJoi = threading.Thread(target=self.RunController)
        ThreadCom = threading.Thread(target=self.RunCommand)
        
        ThreadJoi.start()
        ThreadCom.start()


if __name__ == '__main__':
    post = MainPost()
    post.RunMain()