import pygame as py
import neat
import time
import os
import random
from car import Car
from road import Road
from world import World
from NNdraw import NN
from config_variables import *
py.font.init()

#фон
bg = py.Surface((WIN_WIDTH, WIN_HEIGHT))
bg.fill(GRAY)

#отрисовать окно
def draw_win(cars, road, world, GEN):  
    #отрисовать дорогу
    road.draw(world)
    #отрисовать машины
    for car in cars:
        car.draw(world)

    #отобразить лучший счёт и поколение
    text = STAT_FONT.render("Лучший счёт машины: "+str(int(world.getScore())), 1, BLACK)
    world.win.blit(text, (world.win_width-text.get_width() - 10, 10))
    text = STAT_FONT.render("Поколение: "+str(GEN), 1, BLACK)
    world.win.blit(text, (world.win_width-text.get_width() - 10, 50))

    #отрисовать сеть
    world.bestNN.draw(world)

    #обновить картинку
    py.display.update()
    world.win.blit(bg, (0,0))       #blit фона сразу после обновления, поэтому, если у меня есть draw перед draw_win, они не покрываются фоном

def main(genomes = [], config = []):
    global GEN #поколение
    GEN += 1

    nets = [] #сети
    ge = [] #геномы
    cars = [] #машины
    t = 0 #время

    #создать мир
    world = World(STARTING_POS, WIN_WIDTH, WIN_HEIGHT)
    world.win.blit(bg, (0,0))

    #сети для отрисовки
    NNs = []

    #обработать геномы
    for _,g in genomes:
        net = neat.nn.FeedForwardNetwork.create(g, config) #создать сеть по геному
        nets.append(net) #добавить сеть в список
        cars.append(Car(0, 0, 0)) #создать машину
        g.fitness = 0 #сбросить fitness
        ge.append(g) # добавить геном в список
        NNs.append(NN(config, g, (120, 210))) #создать сеть для отрисовки

    #создать дорогу
    road = Road(world)
    #создать часы
    clock = py.time.Clock()

    #начать симуляцию
    run = True
    while run:
        #обновить время и счёт
        t += 1
        clock.tick(FPS)
        world.updateScore(0)

        #выход
        for event in py.event.get():
            if event.type == py.QUIT:
                run = False
                py.quit()
                quit()

        (xb, yb) = (0,0) #координаты лучшей машины
        i = 0
        #управлять каждой машиной
        while(i < len(cars)):
            car = cars[i]

            #считать ввод
            input = car.getInputs(world, road)
            #добавить скорость к вводу
            input.append(car.vel/MAX_VEL)
            #пропустить ввод через сеть
            car.commands = nets[i].activate(tuple(input))

            #подвинуть машину
            y_old = car.y
            (x, y) = car.move(road,t)

            #t служит для предотвращения удаления машин в первых кадрах tot (в первых кадрах getCollision () всегда возвращает true)
            #удалить машину, если она задела край дороги или сильно отстала от лидера или поехала вниз или едет слишком медленно
            if t>10 and (car.detectCollision(road) or y > world.getBestCarPos()[1] + BAD_GENOME_TRESHOLD or y>y_old or car.vel < 0.1): 
                ge[i].fitness -= 1 #пометить сеть как менее подходящую
                cars.pop(i)
                nets.pop(i)
                ge.pop(i)
                NNs.pop(i)
            else:
                ge[i].fitness += -(y - y_old)/100 + car.vel*SCORE_VEL_MULTIPLIER #пометить сеть как более подходящую
                #отобразить счёт лучшей машины и её сеть
                if(ge[i].fitness > world.getScore()):
                    world.updateScore(ge[i].fitness)
                    world.bestNN = NNs[i]
                    world.bestInputs = input
                    world.bestCommands = car.commands
                i += 1

            #обновить лучшие координаты
            if y < yb:
                (xb, yb) = (x, y)

        #прекратить симуляцию, если машин не осталось
        if len(cars) == 0:
            run = False
            break

        #обновить лучшую позицию машины
        world.updateBestCarPos((xb, yb))
        #обновить дорогу
        road.update(world)
        #отрисовать мир
        draw_win(cars, road, world, GEN)


#NEAT function
def run(config_path):
    #создать концигурацию
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction, neat.DefaultSpeciesSet, neat.DefaultStagnation, config_path)
    #создать популяцию
    p = neat.Population(config)
    #создать репортер
    p.add_reporter(neat.StdOutReporter(True))
    stats =neat.StatisticsReporter()
    p.add_reporter(stats)

    #запустить симуляцию
    winner = p.run(main, 10000)

if __name__ == "__main__":
    local_dir = os.path.dirname(__file__) #определить директорию
    config_path = os.path.join(local_dir, "config_file.txt") #определить конфигурационный файл
    run(config_path) #запуситить neat


#нужны описания, инструкция, ссылка