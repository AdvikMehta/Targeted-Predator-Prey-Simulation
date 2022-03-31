import pygame
import random
from tools import *

PADDING = 10
SIM_WIDTH = 600
SIM_HEIGHT = 600
MAX_POPULATION = 1000
herd = []

min_width = 0

class Deer:
    VEL = 8  # velocity
    FATIGUE = 0.5  # energy cost for moving
    MAX_MOVE_TIME = 30  # number of frames to move in random dir
    MAX_AGE = 2  # maximum life of a deer
    MATURITY_AGE = 2  # age of maturity in secs
    MIN_LITTER_SIZE = 3  # minimum size of litter
    MAX_LITTER_SIZE = 5  # maximum size of litter
    BIRTH_INTERVAL = 0.3  # inrerval between two litters
    REPRODUCTION_PROXIMITY = 100  # spawn offspring within this radius
    REPRODUCTION_THRESHOLD = 90  # energy required to reproduce
    REPRODUCTION_ENERGY = 40  # energy required to reproduce
    TURN_FACTOR = 1  # turn factor when near walls / barriers
    SEPARATION = 0.6
    ALIGNMENT = 0.7
    COHESION = 0.6

    def __init__(self, x, y):
        self.energy = 100
        self.alive = True
        self.moveTime = self.MAX_MOVE_TIME
        self.vel = (0,0)

        self.position = Vector(x, y)
        vec_x = random.uniform(-1, 1)
        vec_y = random.uniform(-1, 1)
        self.velocity = Vector(vec_x, vec_y)
        self.velocity.normalize()
        self.velocity = self.velocity * random.uniform(1.5, 1000)
        self.acceleration = Vector()
        self.max_length = 1
        # self.toggles = {"separation": True, "alignment": True, "cohesion": True}
        self.radius = 100  # radius of perception

    def move(self, flock):
        self.acceleration.reset()

        # if self.toggles["separation"]:
        avoid = self.separation(flock)
        avoid = avoid * self.SEPARATION
        self.acceleration.add(avoid)

        # if self.toggles["cohesion"]:
        coh = self.cohesion(flock)
        coh = coh * self.COHESION
        self.acceleration.add(coh)

        # if self.toggles["alignment"]:
        align = self.alignment(flock)
        align = align * self.ALIGNMENT
        self.acceleration.add(align)

    def separation(self, flockMates):
        total = 0
        steering = Vector()

        for mate in flockMates:
            dist = getDistance(self.position, mate.position)
            if mate is not self and dist < self.radius:
                temp = SubVectors(self.position, mate.position)
                temp = temp / (dist ** 2)
                steering.add(temp)
                total += 1

        if total > 0:
            steering = steering / total
            # steering = steering - self.position
            steering.normalize()
            steering = steering * self.VEL
            steering = steering - self.velocity
            steering.limit(self.max_length)

        return steering

    def alignment(self, flockMates):
        total = 0
        steering = Vector()
        # hue = uniform(0, 0.5)
        for mate in flockMates:
            dist = getDistance(self.position, mate.position)
            if mate is not self and dist < self.radius:
                vel = mate.velocity.Normalize()
                steering.add(vel)

                total += 1

        if total > 0:
            steering = steering / total
            steering.normalize()
            steering = steering * self.VEL
            steering = steering - self.velocity.Normalize()
            steering.limit(self.max_length)
        return steering

    def cohesion(self, flockMates):
        total = 0
        steering = Vector()

        for mate in flockMates:
            dist = getDistance(self.position, mate.position)
            if mate is not self and dist < self.radius:
                steering.add(mate.position)
                total += 1

        if total > 0:
            steering = steering / total
            steering = steering - self.position
            steering.normalize()
            steering = steering * self.VEL
            steering = steering - self.velocity
            steering.limit(self.max_length)

        return steering

    def update(self):
        self.position = self.position + self.velocity
        self.velocity = self.velocity + self.acceleration
        self.velocity.limit(self.VEL)

    def checkBounds(self):
        if self.position.x < PADDING:
            self.velocity.x += self.TURN_FACTOR
        if self.position.x > SIM_WIDTH - PADDING:
            self.velocity.x -= self.TURN_FACTOR
        if self.position.y < min_width + PADDING:
            self.velocity.y += self.TURN_FACTOR
        if self.position.y > SIM_HEIGHT - PADDING:
            self.velocity.y -= self.TURN_FACTOR

    def getEaten(self):
        self.alive = False
        herd.remove(self)

    def isAlive(self):
        return self.alive

    def draw(self, screen):
        pygame.draw.circle(screen, (51,204,255), (self.position.x, self.position.y), 4)

    def move2(self):
        if self.moveTime < self.MAX_MOVE_TIME:
            if (self.position.x <= PADDING and self.vel[0] < 0) or (self.position.x >= 600-PADDING and self.vel[0] > 0):
                self.vel = -self.vel[0], self.vel[1]
            if (self.position.y == PADDING and self.vel[1] < 0) or (self.position.y >= 600-PADDING and self.vel[1] > 0):
                self.vel = self.vel[0], -self.vel[1]
            self.position.x += self.vel[0]
            self.position.y += self.vel[1]
            self.moveTime += 1
            self.energy -= self.FATIGUE
        else:  # 1 frame stop and change dir
            self.moveTime = 0
            self.vel = (random.randint(-5, 5), random.randint(-5, 5))
        self.checkBounds()