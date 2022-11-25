import pygame as py
from config_variables import *
from car import decodeCommand
from vect2d import vect2d
from node import *

py.font.init()

class NN:

    def __init__(self, config, genome, pos):
        self.input_nodes = [] #входные ноды
        self.output_nodes = [] #выходные ноды
        self.nodes = [] #все ноды
        self.genome = genome #геном
        self.pos = (int(pos[0]+NODE_RADIUS), int(pos[1])) #позиция
        input_names = ["Сенсор В", "Сенсор ВП", "Сенсор П", #имена для входного слоя
                        "Сенсор НП", "Сенсор Н", "Сенсор НЛ", 
                        "Сенсор Н", "Сенсор НВ", "Скорость"]
        output_names = ["Газ", "Тормоз", "Повернуть налево", "повернуть направо"] #имена для выходного слоя
        middle_nodes = [n for n in genome.nodes.keys()] #ноды промежуточног слоя
        nodeIdList = [] #список id нод

        #создаём ноды для входного слоя
        h = (INPUT_NEURONS-1)*(NODE_RADIUS*2 + NODE_SPACING) #отступ
        for i, input in enumerate(config.genome_config.input_keys):#цикл по входным нейронам
            #новая нода
            n = Node(input, pos[0], pos[1]+int(-h/2 + i*(NODE_RADIUS*2 + NODE_SPACING)), INPUT, [GREEN_PALE, GREEN, DARK_GREEN_PALE, DARK_GREEN], input_names[i], i)
            #добавляется в общий список
            self.nodes.append(n)
            #id добавляется в свой список
            nodeIdList.append(input)

        #аналогичный цикл для выходных нейронов
        h = (OUTPUT_NEURONS-1)*(NODE_RADIUS*2 + NODE_SPACING)
        for i,out in enumerate(config.genome_config.output_keys):
            n = Node(out+INPUT_NEURONS, pos[0] + 2*(LAYER_SPACING+2*NODE_RADIUS), pos[1]+int(-h/2 + i*(NODE_RADIUS*2 + NODE_SPACING)), OUTPUT, [RED_PALE, RED, DARK_RED_PALE, DARK_RED], output_names[i], i)
            self.nodes.append(n)
            middle_nodes.remove(out)
            nodeIdList.append(out)

        #аналогичный цикл для нейронов внутреннего слоя
        h = (len(middle_nodes)-1)*(NODE_RADIUS*2 + NODE_SPACING)
        for i, m in enumerate(middle_nodes):
            n = Node(m, self.pos[0] + (LAYER_SPACING+2*NODE_RADIUS), self.pos[1]+int(-h/2 + i*(NODE_RADIUS*2 + NODE_SPACING)), MIDDLE, [BLUE_PALE, DARK_BLUE, BLUE_PALE, DARK_BLUE])
            self.nodes.append(n)
            nodeIdList.append(m)

        #связи
        self.connections = []
        #для каждой связи в геноме создаём свою связь по id
        for c in genome.connections.values():
            if c.enabled:
                input, output = c.key
                self.connections.append(Connection(self.nodes[nodeIdList.index(input)],self.nodes[nodeIdList.index(output)], c.weight))

    #отрисовать сеть
    def draw(self, world):
        #отрисовать связи
        for c in self.connections:
            c.drawConnection(world)
        #отрисовать ноды
        for node in self.nodes:
            node.draw_node(world)































#----
