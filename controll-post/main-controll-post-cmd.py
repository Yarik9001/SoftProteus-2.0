import socket
import threading  # модуль для разделения на потоки
import logging
import coloredlogs
from datetime import datetime  # получение  времени
from time import sleep  # сон
from ast import literal_eval  # модуль для перевода строки в словарик
from pyPS4Controller.controller import Controller


class MedaLogging:
    def __init__(self):
        self.mylogs = logging.getLogger(__name__)
        self.mylogs.setLevel(logging.DEBUG)
        # обработчик записи в лог-файл
        self.file = logging.FileHandler("Main.log")
        self.fileformat = logging.Formatter(
            "%(asctime)s:%(levelname)s:%(message)s")
        self.file.setLevel(logging.DEBUG)
        self.file.setFormatter(self.fileformat)
        # обработчик вывода в консоль лог файла
        self.stream = logging.StreamHandler()
        self.streamformat = logging.Formatter(
            "%(levelname)s:%(module)s:%(message)s")
        self.stream.setLevel(logging.DEBUG)
        self.stream.setFormatter(self.streamformat)
        # инициализация обработчиков
        self.mylogs.addHandler(self.file)
        self.mylogs.addHandler(self.stream)
        coloredlogs.install(level=logging.DEBUG, logger=self.mylogs,
                            fmt='%(asctime)s [%(levelname)s] - %(message)s')

        self.mylogs.info('start-logging')

    def debug(self, message):
        self.mylogs.debug(message)

    def info(self, message):
        self.mylogs.info(message)

    def warning(self, message):
        self.mylogs.warning(message)

    def critical(self, message):
        self.mylogs.critical(message)

    def error(self, message):
        self.mylogs.error(message)


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

    def __init__(self, logger:MedaLogging):
        # инициализация атрибутов
        self.HOST = '192.168.1.100'
        self.PORT = 1251
        self.JOYSTICKRATE = 0.1
        self.MotorPowerValue = 1
        self.telemetria = False
        self.checkConnect = False
        self.logger = logger
        # настройка сервера
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM,)
        self.server.bind((self.HOST, self.PORT))
        self.server.listen(1)
        self.user_socket, self.address = self.server.accept()
        self.checkConnect = True
        
        self.logger.info(f'ROV-Connected - {self.user_socket}')

    def ReceiverProteus(self):
        if self.checkConnect:
            data = self.user_socket.recv(512)
            if len(data) == 0:
                self.server.close()
                self.checkConnect = False
                self.logger.info(f'ROV-disconnection - {self.user_socket}')
                return None
            data = dict(literal_eval(str(data.decode('utf-8'))))
            if self.telemetria:
                self.logger.debug(f'DataInput - {str(data)}')
            return data

    def ControlProteus(self, data: dict):
        if self.checkConnect:
            self.user_socket.send(str(data).encode('utf-8'))
            if self.telemetria:
                self.logger.debug(str(data))


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
        Controller.__init__(self, interface="/dev/input/js0", connecting_using_ds4drv=False)
        self.DataPult = {'j1-val-y': 0, 'j1-val-x': 0,
                         'j2-val-y': 0, 'j2-val-x': 0,
                         'ly-cor': 0, 'lx-cor': 0,
                         'ry-cor': 0, 'rx-cor': 0,
                         'man': 0, 'servo-cam': 0,
                         'led': False, 'auto-dept': False}
        self.log = True
        self.telemetria = False
        self.optionscontrol = False
    # переключение режимов корректировок

    def on_options_press(self):
        self.optionscontrol = not self.optionscontrol
    # функция перевода данных с джойстиков

    def transp(self, value):
        return -1 * (value // 328)
    # блок опроса функций джойстиков

    def on_L3_up(self, value):
        self.DataPult['j1-val-y'] = -1 * value
        if self.telemetria:
            print('forward')

    def on_L3_down(self, value):
        self.DataPult['j1-val-y'] = -1 * value
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
        if self.telemetria:
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
    # блок внесения корректировок с кнопок и управления светом, поворотом камеры, манипулятором

    def on_x_press(self):
        if self.optionscontrol:
            if self.DataPult['ry-cor'] >= - 50:
                self.DataPult['ry-cor'] -= 10
        else:
            if self.DataPult['servo-cam'] <= 170:
                self.DataPult['servo-cam'] += 10

    def on_triangle_press(self):
        if self.optionscontrol:
            if self.DataPult['ry-cor'] <= 50:
                self.DataPult['ry-cor'] += 10
        else:
            if self.DataPult['servo-cam'] >= 10:
                self.DataPult['servo-cam'] -= 10

    def on_square_press(self):
        if self.optionscontrol:
            if self.DataPult['rx-cor'] <= 50:
                self.DataPult['rx-cor'] += 10
        else:
            if self.DataPult['man'] <= 170:
                self.DataPult['man'] += 10

    def on_circle_press(self):
        if self.optionscontrol:
            if self.DataPult['rx-cor'] >= -50:
                self.DataPult['rx-cor'] -= 10
        else:
            if self.DataPult['man'] >= 10:
                self.DataPult['man'] -= 10

    def on_up_arrow_press(self):
        if self.optionscontrol:
            if self.DataPult['ly-cor'] >= -50:
                self.DataPult['ly-cor'] -= 10
        else:
            self.DataPult['led'] = not self.DataPult['led']

    def on_down_arrow_press(self):
        if self.optionscontrol:
            if self.DataPult['ly-cor'] <= 50:
                self.DataPult['ly-cor'] += 10
        else:
            self.DataPult['auto-dept'] = not self.DataPult['auto-dept']

    def on_left_arrow_press(self):
        if self.DataPult["lx-cor"] >= -50:
            self.DataPult["lx-cor"] -= 10

    def on_right_arrow_press(self):
        if self.DataPult['lx-cor'] <= 50:
            self.DataPult['lx-cor'] += 10
    # функция обнуления (работает в обоих режимах)

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
                           'man': 0,  # Управление манипулятором
                           'servo': 0,  # управление наклоном камеры
                           'motor0': 0, 'motor1': 0,  # значения мощности на каждый мотор
                           'motor2': 0, 'motor3': 0,
                           'motor4': 0, 'motor5': 0}
        # словарик получаемый с аппарата
        self.DataInput = {'time': None, 'dept': 0, 'volt': 0, 'azimut': 0}
        self.lodi = MedaLogging()

        self.Server = ServerMainPult(self.lodi)  # поднимаем сервер
        self.lodi.info('ServerMainPult - init')
        self.checkKILL = False
        self.Controllps4 = MyController()  # поднимаем контролеер
        self.lodi.info('MyController - init')
        self.DataPult = self.Controllps4.DataPult
        self.RateCommandOut = 0.1
        self.telemetria = False
        self.correctCom = True
        self.lodi.info('MainPost-init')

    def RunController(self):
        self.lodi.info('MyController-listen')
        self.Controllps4.listen()


    def RunCommand(self):
        self.lodi.info('MainPost-RunCommand')
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
        def transformation(value: int):
            # Функция перевода значений АЦП с джойстика в проценты
            value = (32768 - value) // 655
            return value

        def defense(value: int):
            if value > 100:
                value = 100
            elif value < 0:
                value = 0
            return value

        while True:
            data = self.DataPult
            # математика преобразования значений с джойстика в значения для моторов
            
            if self.telemetria:
                self.lodi.debug(f'DataPult - {data}')
                
            if self.correctCom:
                J1_Val_Y = transformation(data['j1-val-y']) + data['ly-cor']
                J1_Val_X = transformation(data['j1-val-x']) + data['lx-cor']
                J2_Val_Y = transformation(data['j2-val-y']) + data['ry-cor']
                J2_Val_X = transformation(data['j2-val-x']) + data['lx-cor']
            else:
                J1_Val_Y = transformation(data['j1-val-y'])
                J1_Val_X = transformation(data['j1-val-x'])
                J2_Val_Y = transformation(data['j2-val-y'])
                J2_Val_X = transformation(data['j2-val-x'])

            self.DataOutput['motor0'] = defense(
                J1_Val_Y + J1_Val_X + J2_Val_X - 100)
            self.DataOutput['motor1'] = defense(
                J1_Val_Y - J1_Val_X - J2_Val_X + 100)
            self.DataOutput['motor2'] = defense(
                (-1 * J1_Val_Y) - J1_Val_X + J2_Val_X + 100)
            self.DataOutput['motor3'] = defense(
                (-1 * J1_Val_Y) + J1_Val_X - J2_Val_X + 100)

            self.DataOutput['motor4'] = defense(J2_Val_Y)
            self.DataOutput['motor5'] = defense(J2_Val_Y)

            self.DataOutput["time"] = str(datetime.now())

            self.DataOutput['led'] = data['led']
            self.DataOutput['man'] = data['man']
            self.DataOutput['servo'] = data['servo-cam']
            
            if self.telemetria:
                self.lodi.debug('DataOutput - {self.DataOutput}')
                
            self.Server.ControlProteus(self.DataOutput)
            self.DataInput = self.Server.ReceiverProteus()
            
            if self.telemetria:
                self.lodi.debug('DataInput - {self.DataInput}')
                
            if self.checkKILL:
                self.Server.server.close()
                self.lodi.info('command-stop')
                break
            
            sleep(self.RateCommandOut)

    def CommandLine(self):
        while True:
            command = input() # ввод с клавиатуры
            if  command == 'stop':
                self.checkKILL = True
                self.Controllps4.cilled()
                break
            

    def RunMain(self):
        self.ThreadJoi = threading.Thread(target=self.RunController)
        self.ThreadCom = threading.Thread(target=self.RunCommand)
        self.ThreadComLine = threading.Thread(target=self.CommandLine)

        self.ThreadJoi.start()
        self.ThreadCom.start()
        self.ThreadComLine.start()


if __name__ == '__main__':
    post = MainPost()
    post.RunMain()
