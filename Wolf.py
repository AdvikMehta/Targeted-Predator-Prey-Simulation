import pygame
import os
import time
import random
import math
from vector import Vector

WOLF_ADULT_IMG = pygame.transform.scale(pygame.image.load(os.path.join("assets/imgs","wolf-adult.png")),  (16, 16))
WOLF_CUB_IMG = pygame.transform.scale(pygame.image.load(os.path.join("assets/imgs","wolf-cub.png")),  (8, 8))

SIM_WIDTH = 600
SIM_HEIGHT = 600
SIM_SPEED = 0.5

wolves = []
dens = []
avgWolfAge = 0
maxWolfAge = 0
totalWolvesExisted = 0
MAX_POPULATION = 20

class Wolf:
    # Health
    MAX_ENERGY = 100
    MAX_HUNGER = 100
    MAX_AGE = 200
    IDLE_GAIN = 0.05
    WALK_FATIGUE = 0.08
    RUN_FATIGUE = 0.2
    HUNGER_FATIGUE = 0.17
    MAX_WALK_VEL = 2 * SIM_SPEED  # 2
    MAX_RUN_VEL = 6 * SIM_SPEED  # 5

    # Reproduction
    SPAWN_DEN_PROXIMITY = 10
    MATURITY_AGE = 4  # age of maturity
    MIN_LITTER_SIZE = 1  # minimum size of litter
    MAX_LITTER_SIZE = 4  # maximum size of litter
    BIRTH_INTERVAL = 4  # inrerval between two litters
    REPRODUCTION_PROXIMITY = 100  # spawn offspring within this radius
    REPRODUCTION_THRESHOLD = 95  # minimum energy required to reproduce
    REPRODUCTION_ENERGY = 40  # energy loss during reproduction

    # Misc
    FOOD_ENERGY = 20
    COST_CONTROL_BIAS = 0.70  # depends on MAX_WALK_VEL

    def __init__(self, pack):
        self.energy = self.MAX_ENERGY
        self.hunger = self.MAX_HUNGER
        self.age = 0
        self.gender = random.randint(0, 1)
        self.spawn_time = time.time()
        self.lastMealTime = self.spawn_time
        self.birthTime = self.spawn_time
        self.timeSinceLastBirth = 0
        self.pack = pack
        self.den = self.pack.den
        if self.den not in dens:
            dens.append(self.den)
        self.target = None
        self.is_returning = None
        self.idle = True
        self.alive = True
        self.mature = False
        self.debug_line = []

        x = self.den.position.x + random.randint(-self.SPAWN_DEN_PROXIMITY, self.SPAWN_DEN_PROXIMITY)
        y = self.den.position.y + random.randint(-self.SPAWN_DEN_PROXIMITY, self.SPAWN_DEN_PROXIMITY)
        self.position = Vector(x, y)

    def move(self, target):
        if self.target is not None:
            self.moveTowardsTarget()
        elif self.isHungry():
            if target is not None:
                self.target = target
                self.idle = False
        elif not self.idle:
            # undecided
            distance_until_den = math.sqrt((self.position.x - self.den.position.x)**2 + (self.position.y - self.den.position.y)**2)
            # to correct distance due to zigzag motion while coming back
            corrected_distance_until_den = distance_until_den / self.COST_CONTROL_BIAS
            num_frames_until_den = corrected_distance_until_den / self.MAX_WALK_VEL
            return_energy_cost = num_frames_until_den * self.WALK_FATIGUE
            return_hunger_cost = num_frames_until_den * self.HUNGER_FATIGUE

            if self.energy - return_energy_cost < 10\
                    or self.hunger - return_hunger_cost < 10:
                self.idle = True
            else:
                self.target = self.den

    def moveTowardsTarget(self):
        if self.target == self.den:
            vel = self.MAX_WALK_VEL
        else:
            vel = self.MAX_RUN_VEL
        rad = math.atan2(self.target.position.y - self.position.y, self.target.position.x - self.position.x)
        dy = vel * math.sin(rad)
        dx = vel * math.cos(rad)
        self.position.x += int(dx)
        self.position.y += int(dy)

    def checkBounds(self):
        if self.position.x > SIM_WIDTH:
            self.position.x = SIM_WIDTH
        elif self.position.x < 0:
            self.position.x = 0
        if self.position.y > SIM_HEIGHT:
            self.position.y = SIM_HEIGHT
        elif self.position.y < 0:
            self.position.y = 0

    def eat(self, prey):
        self.energy += self.FOOD_ENERGY
        if self.energy > self.MAX_ENERGY:
            self.energy = self.MAX_ENERGY
        self.hunger = self.MAX_HUNGER
        prey.getEaten()

    def isHungry(self):
        return self.hunger < 50

    def grow(self):
        self.age = time.time() - self.spawn_time
        self.timeSinceLastBirth = time.time() - self.birthTime

        if self.age > self.MAX_AGE or self.energy < 0 or self.hunger > self.MAX_HUNGER:
            self.kill()
        elif self.age > self.MATURITY_AGE:
            self.mature = True
        if self.mature and self.timeSinceLastBirth > self.BIRTH_INTERVAL and self.energy > self.REPRODUCTION_THRESHOLD and len(wolves) < MAX_POPULATION:
            self.reproduce()

        # Fatigue
        self.hunger -= self.HUNGER_FATIGUE
        if self.idle:
            self.energy += self.IDLE_GAIN
            if self.energy > self.MAX_ENERGY:
                self.energy = self.MAX_ENERGY
        elif self.target == self.den:
            self.energy -= self.WALK_FATIGUE
        else:
            self.energy -= self.RUN_FATIGUE

    def isAlive(self):
        return self.alive

    def reproduce(self):
        self.birthTime = time.time()
        self.energy -= self.REPRODUCTION_ENERGY
        self.timeSinceLastBirth = 0
        litterSize = random.randint(self.MIN_LITTER_SIZE, self.MAX_LITTER_SIZE)
        for _ in range(litterSize):
            wolves.append(Wolf(self.pack))

    def kill(self):
        global totalWolvesExisted, avgWolfAge, maxWolfAge
        self.energy = 0
        self.alive = False
        wolves.remove(self)
        totalWolvesExisted += 1
        avgWolfAge = ((avgWolfAge * (totalWolvesExisted - 1)) + self.age) / totalWolvesExisted
        maxWolfAge = max(self.age, maxWolfAge)

    def draw(self, screen):
        screen.blit(WOLF_ADULT_IMG, (self.position.x, self.position.y))