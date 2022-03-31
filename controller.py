import pygame
import os
import math
import Den
from Wolf import Wolf, wolves, dens
from Deer import Deer, herd

pygame.init()

WIN_WIDTH = 600
SIM_WIDTH = 600
WIN_HEIGHT = 700
SIM_HEIGHT = 600
PADDING = 10

min_width = 0

STAT_FONT14 = pygame.font.Font((os.path.join("assets/fonts","times-new-roman.ttf")), 14)

def spawnDeer(num):
    for _ in range(num // 2):
        herd.append(Deer(1))
    for _ in range(num // 2):
        herd.append(Deer(0))

def spawnWolf(pack, num):
    for _ in range(num):
        wolves.append(Wolf(pack))

def drawWindow(screen):
    screen.fill((255,255,255))
    for deer in herd:
        deer.draw(screen)
    for wolf in wolves:
        wolf.draw(screen)
        # drawDebugLine(screen, wolf)

    text = STAT_FONT14.render("Hunger: " + str(wolves[0].hunger), True, (0, 0, 0))
    screen.blit(text, (10, SIM_HEIGHT + 5))
    text = STAT_FONT14.render("Energy: " + str(wolves[0].energy), True, (0, 0, 0))
    screen.blit(text, (10, SIM_HEIGHT + 20))
    text = STAT_FONT14.render("Idle: " + str(wolves[0].idle), True, (0, 0, 0))
    screen.blit(text, (10, SIM_HEIGHT + 35))
    text = STAT_FONT14.render("Number of deer: " + str(len(herd)), True, (0, 0, 0))
    screen.blit(text, (10, SIM_HEIGHT + 50))

    for den in dens:
        pygame.draw.circle(screen, (0, 0, 0), (den.position.x, den.position.y), 20, 1)

    pygame.display.update()

def getTarget(wolf):
    if len(herd) > 0:
        minDist = math.sqrt((wolf.position.y - herd[0].position.y) ** 2 + (wolf.position.x - herd[0].position.x) ** 2)
        minInd = 0
        for i in range(1, len(herd)):
            dist = math.sqrt((wolf.position.y - herd[i].position.y) ** 2 + (wolf.position.x - herd[i].position.x) ** 2)
            if dist < minDist:
                minDist = dist
                minInd = i
        return herd[minInd]

def drawDebugLine(screen, wolf):
    for pair in wolf.debug_line:
        pygame.draw.line(screen, (0,0,0), pair[0], pair[1])

def checkKillings(pack):
    if len(pack) > 0:
        for wolf in pack:
            if wolf.target:
                dist = math.sqrt((wolf.position.x + 8 - wolf.target.position.x - 4)**2 + (wolf.position.y + 8 - wolf.target.position.y - 4)**2)
                if dist < 20:
                    if wolf.target is not wolf.den:
                        wolf.eat(wolf.target)
                    else:
                        wolf.idle = True
                    wolf.target = None

def main():
    running = True
    screen = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
    clock = pygame.time.Clock()
    pygame.display.set_caption("Wolf-Deer Simulator")

    spawnDeer(100)
    pack1 = Den.Pack()
    pack2 = Den.Pack()
    pack1.setDen(150, 150)
    pack2.setDen(450, 450)
    spawnWolf(pack1, 5)
    spawnWolf(pack2, 5)

    while running:
        clock.tick(30)

        # event listening
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                pygame.quit()
                quit()

        for wolf in wolves:
            wolf.grow()
            wolf.checkBounds()
            if wolf.isHungry():
                wolf.move(getTarget(wolf))
            else:
                wolf.move(None)
        for deer in herd:
            for wolf in wolves:
                deer.checkPredator(wolf)
            deer.checkBounds()
            deer.flock(herd)
            deer.update()

        checkKillings(wolves)

        drawWindow(screen)

    pygame.quit()
    quit()

main()