import pygame as py
from car import decodeCommand
from config_variables import *

class Node:
    def __init__(self, id, x, y, type, color, label = "", index=0):
        self.id = id #id 
        self.x = x #позиция х
        self.y = y #позиция у
        self.type = type #тип
        self.color = color #цвет
        self.label = label #подпись
        self.index = index #индекс

    #нарисовать ноду
    def draw_node(self, world):
        #цвета
        colorScheme = self.getNodeColors(world)
        #нарисоать круги
        py.draw.circle(world.win, colorScheme[0], (self.x,self.y), NODE_RADIUS)
        py.draw.circle(world.win, colorScheme[1], (self.x,self.y), NODE_RADIUS-2)

        #отрисовать подписи
        if self.type != MIDDLE:
            text = NODE_FONT.render(self.label, 1, BLACK)
            world.win.blit(text, (self.x + (self.type-1) * ((text.get_width() if not self.type else 0) + NODE_RADIUS + 5), self.y - text.get_height()/2))

    def getNodeColors(self, world):
        #ratio - это сила выделения цветом
        #для входных нейронов это их значение, а для выходный 1 если активен и 0 иначе
        if self.type == INPUT:
            ratio = world.bestInputs[self.index]
        elif self.type == OUTPUT:
            ratio = 1 if decodeCommand(world.bestCommands, self.index) else 0
        else:
            ratio = 0

        #вычисление цветов через константы
        col = [[0,0,0], [0,0,0]]
        for i in range(3):
            col[0][i] = int(ratio * (self.color[1][i]-self.color[3][i]) + self.color[3][i])
            col[1][i] = int(ratio * (self.color[0][i]-self.color[2][i]) + self.color[2][i])
        return col

class Connection:
    def __init__(self, input, output, wt):
        self.input = input #входная нода
        self.output = output #выходная нода
        self.wt = wt #вес связи

    #нарисовать связь
    def drawConnection(self, world):
        #цвет зелёный если вес больше нуля и красный иначе
        color = GREEN if self.wt >= 0 else RED
        #толщина линии
        width = int(abs(self.wt * CONNECTION_WIDTH))
        #отрисовка
        py.draw.line(world.win, color, (self.input.x + NODE_RADIUS, self.input.y), (self.output.x - NODE_RADIUS, self.output.y), width)
