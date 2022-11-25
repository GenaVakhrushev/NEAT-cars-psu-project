import pygame as py

class World:

    initialPos = (0,0)
    bestCarPos = (0,0)

    def __init__(self, starting_pos, world_width, world_height):
        self.initialPos = starting_pos #начальная позиция
        self.bestCarPos = (0, 0) #лучшая позиция машины
        self.win  = py.display.set_mode((world_width, world_height)) #окно игры
        self.win_width = world_width #ширина экрана
        self.win_height = world_height #высота экрана
        self.score = 0 #счёт
        self.bestGenome = None #лучшый геном

    #обновить лучшую позицию машины
    def updateBestCarPos(self, pos):
        self.bestCarPos = pos

    #получить экранные координаты
    def getScreenCoords(self, x, y):
        return (int(x + self.initialPos[0] - self.bestCarPos[0]), int(y + self.initialPos[1] - self.bestCarPos[1]))

    #получить лучшую позицию машины
    def getBestCarPos(self):
        return self.bestCarPos

    #обновить счёт
    def updateScore(self, new_score):
        self.score = new_score

    #получить счёт
    def getScore(self):
        return self.score
