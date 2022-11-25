from config_variables import *
import pygame as py
import os
from math import *
from random import random
from road import *
import numpy as np
from vect2d import vect2d


class Car:
    x = 0
    y = 0       #координаты


    def __init__(self, x, y, turn):
        self.x = x #координата х
        self.y = y #координата у
        self.rot = turn #угол поворота
        self.rot = 0
        self.vel = MAX_VEL/2 #скорость
        self.acc = 0 #ускорение
        self.initImgs() #инициализировать изображения
        self.commands = [0,0,0,0] #команды для управления машиной

    #инициализировать изображения
    def initImgs(self):
        #доступные изображения машин
        img_names = ["yellow_car.png", "red_car.png", "blu_car.png", "green_car.png"]
        #имя случайного изображения
        name = img_names[floor(random()*len(img_names))%len(img_names)]                 
        #назначения выбаного изображения
        self.img = py.transform.rotate(py.transform.scale(py.image.load(os.path.join("imgs", name)).convert_alpha(), (120,69)), -90)
        self.brake_img = py.transform.rotate(py.transform.scale(py.image.load(os.path.join("imgs", "brakes.png")).convert_alpha(), (120,69)), -90)

    #обнаружить столкновения
    def detectCollision(self, road):
        #получить маску
        mask = py.mask.from_surface(self.img)
        #получить размеры
        (width, height) = mask.get_size()
        #найти пересчения с точками дороги
        for v in [road.pointsLeft, road.pointsRight]:
            for p in v:
                x = p.x - self.x + width/2
                y = p.y - self.y + height/2
                try:
                    if mask.get_at((int(x),int(y))):
                        return True
                except IndexError as error:
                    continue
        return False

    #получить ввод
    def getInputs(self, world, road):         #win предназначен для рисования датчиков, если DBG = True
        sensors = []
        for k in range(8):
            sensors.append(SENSOR_DISTANCE)
        #получить уравнения для датчиков
        sensorsEquations = getSensorEquations(self, world)

        #получить расстояния до краёв дороги с датчиков
        for v in [road.pointsLeft, road.pointsRight]:
            i = road.bottomPointIndex
            while v[i].y > self.y - SENSOR_DISTANCE:
                next_index = getPoint(i+1, NUM_POINTS*road.num_ctrl_points)

                getDistance(world, self, sensors, sensorsEquations, v[i], v[next_index])
                i = next_index

        #отрисовка датчиков
        if CAR_DBG:
            for k,s in enumerate(sensors):
                omega = radians(self.rot + 45*k)
                dx = s * sin(omega)
                dy = - s * cos(omega)
                #нарисуйте пересечения датчиков
                if s < SENSOR_DISTANCE:
                    py.draw.circle(world.win, RED, world.getScreenCoords(self.x+dx, self.y+dy), 6)

        #преобразовать в значение между 0 (расстояние = максимальное) и 1 (расстояние = 0)
        for s in range(len(sensors)):
            sensors[s] = 1 - sensors[s]/SENSOR_DISTANCE

        return sensors


    def move(self, road, t):
        self.acc = FRICTION
        #получить комманды
        if decodeCommand(self.commands, ACC):
            self.acc = ACC_STRENGHT
        if decodeCommand(self.commands, BRAKE):
            self.acc = -BRAKE_STREGHT
        if decodeCommand(self.commands, TURN_LEFT):
            self.rot -= TURN_VEL
        if decodeCommand(self.commands, TURN_RIGHT):
            self.rot += TURN_VEL

        #установка максимальной возможный скорости
        timeBuffer = 500
        if MAX_VEL_REDUCTION == 1 or t >= timeBuffer:
            max_vel_local = MAX_VEL
        else:
            ratio = MAX_VEL_REDUCTION + (1 - MAX_VEL_REDUCTION)*(t/timeBuffer)
            max_vel_local = MAX_VEL *ratio

        #ускорение
        self.vel += self.acc
        #ограничение скорости
        if self.vel > max_vel_local:
            self.vel = max_vel_local
        if self.vel < 0:
            self.vel = 0
        #перемещение в нужную сторону
        self.x = self.x + self.vel * sin(radians(self.rot))
        self.y = self.y - self.vel * cos(radians(self.rot)) #я вычитаю, потому что начало координат находится в верхнем левом углу


        return (self.x, self.y)

    #отрисаовка машины
    def draw(self, world):
        #положение на экране
        screen_position = world.getScreenCoords(self.x, self.y)
        #повернуть на нужный угол
        rotated_img = py.transform.rotate(self.img, -self.rot)
        #поместить в нужной место
        new_rect = rotated_img.get_rect(center = screen_position)
        world.win.blit(rotated_img, new_rect.topleft)

        #нарисовать тормозные фонари, если машина тормозит
        if decodeCommand(self.commands, BRAKE):
            rotated_img = py.transform.rotate(self.brake_img, -self.rot)
            new_rect = rotated_img.get_rect(center = screen_position)
            world.win.blit(rotated_img, new_rect.topleft)

    #======================== LOCAL FUNCTIONS ==========================

def getSensorEquations(self, world):       #возвращает уравнения прямых (в переменной y) машины в порядке [по вертикали ,по диагонали, по горизонтали, по диагонали по убыванию]
    eq = []
    for i in range(4):
        omega = radians(self.rot + 45*i)
        dx = SENSOR_DISTANCE * sin(omega)
        dy = - SENSOR_DISTANCE * cos(omega)

        if CAR_DBG:             #нарисуйте линии датчиков
            py.draw.lines(world.win, GREEN, False, [world.getScreenCoords(self.x+dx, self.y+dy), world.getScreenCoords(self.x-dx, self.y-dy)], 2)

        coef = getSegmentEquation(self, vect2d(x = self.x+dx, y = self.y+dy))
        eq.append(coef)
    return eq

def getSegmentEquation(p, q):          #уравнения в переменной y между двумя точками (с учетом системы координат с инвертированным y) в общем виде ax + by + c = 0

    a = p.y - q.y
    b = q.x -p.x
    c = p.x*q.y - q.x*p.y

    return (a,b,c)

def getDistance(world, car, sensors, sensorsEquations, p, q):     #учитывая сегмент (m, q), я вычисляю расстояние и помещаю его в соответствующий датчик
    (a2,b2,c2) = getSegmentEquation(p, q)

    for i,(a1,b1,c1) in enumerate(sensorsEquations):
        #получить пересечение между датчиком и сегментом

        if a1!=a2 or b1!=b2:
            d = b1*a2 - a1*b2
            if d == 0:
                continue
            y = (a1*c2 - c1*a2)/d
            x = (c1*b2 - b1*c2)/d
            if (y-p.y)*(y-q.y) > 0 or (x-p.x)*(x-q.x) > 0:        #если пересечение не лежит между a и b, перейдите к следующей итерации
                continue
        else:       #совпадающие прямые
            (x, y) = (abs(p.x-q.x), abs(p.y-q.y))

        #получить расстояние
        dist = ((car.x - x)**2 + (car.y - y)**2)**0.5

        #вставить в sensor в правильном направлении
        omega = car.rot +45*i                               #угол прямой линии датчика (и его противоположности)
        alpha = 90- degrees(atan2(car.y - y, x-car.x))     #угол относительно вертикали (например, car.rot)
        if cos(alpha)*cos(omega)*100 + sin(alpha)*sin(omega)*100 > 0:
            index = i
        else:
            index = i + 4

        if dist < sensors[index]:
            sensors[index] = dist
#расшивровать комманду
def decodeCommand(commands, type):
    #если значение комманды больше определённого числа, то команда активна
    if commands[type] > ACTIVATION_TRESHOLD:
        if type == ACC and commands[type] > commands[BRAKE]:
            return True
        elif type == BRAKE and commands[type] > commands[ACC]:
            return True
        elif type == TURN_LEFT and commands[type] > commands[TURN_RIGHT]:
            return True
        elif type == TURN_RIGHT and commands[type] > commands[TURN_LEFT]:
            return True
    return False








    #----
