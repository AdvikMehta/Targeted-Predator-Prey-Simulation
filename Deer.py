import pygame
from vector import *

SIM_WIDTH = 600
SIM_HEIGHT = 600
MARGIN = 20
SIM_SPEED = 0.5

herd = []

class Deer:
    ALIGNMENT_PERCEPTION = 100
    COHESION_PERCEPTION = 150
    SEPARATION_PERCEPTION = 50
    ALIGNMENT_SCALE = 1
    COHESION_SCALE = 1
    SEPARATION_SCALE = 1
    MAX_VELOCITY = 5 * SIM_SPEED
    MAX_FORCE = 0.1
    EDGE_TURN_FACTOR = 1
    PREDATORY_RANGE = 100
    PREDATOR_TURN_FACTOR = 0.5

    COLORS = [((135, 206, 250), (30, 144, 255)),
              ((216, 191, 216), (75, 0, 130))]

    # control max speed for avergage velocity of boids
    # reduce max force for bigger groups with more separation

    def __init__(self, boid_type=0):
        # boid mechanics
        self.position = Vector(randint(0,SIM_WIDTH), randint(0, SIM_WIDTH))
        self.velocity = Vector.random()
        self.velocity.setMag(self.MAX_VELOCITY)
        self.acceleration = Vector(x=0, y=0)
        self.type = boid_type
        self.prev_position = self.position
        self.colors = self.COLORS[self.type]
        # deer attributes
        self.alive = True
        self.energy = 100

    def update(self):
        self.velocity += self.acceleration
        self.velocity.limit(self.MAX_VELOCITY)
        self.position += self.velocity
        self.acceleration.set(0, 0)

    def flock(self, flock):
        alignment = self.alignment(flock)
        cohesion = self.cohesion(flock)
        separation = self.separation(flock)

        alignment.multiply(self.ALIGNMENT_SCALE)
        cohesion.multiply(self.COHESION_SCALE)
        separation.multiply(self.SEPARATION_SCALE)

        self.acceleration.add(alignment)  # F = ma, but m = 1, then F = a
        self.acceleration.add(cohesion)
        self.acceleration.add(separation)

    def alignment(self, flock):
        steering = Vector()  # desired velocity, avg of boids withing perception
        num_boids_in_radius = 0
        for boid in flock:
            if boid is not self and Vector.getDistance(self.position, boid.position) <= self.ALIGNMENT_PERCEPTION\
                    and self.type == boid.type:
                num_boids_in_radius += 1
                steering.add(boid.velocity)
        if num_boids_in_radius > 0:
            steering.divide(num_boids_in_radius)
            steering.setMag(self.MAX_VELOCITY)
            steering.subtract(self.velocity)  # this is the steering force in direction of average
            steering.limit(self.MAX_FORCE)
        return steering

    def cohesion(self, flock):
        steering = Vector()  # desired location, avg of boids withing perception
        num_boids_in_radius = 0
        for boid in flock:
            if boid is not self and Vector.getDistance(self.position, boid.position) <= self.COHESION_PERCEPTION:
                if self.type == boid.type:
                    num_boids_in_radius += 1
                    steering.add(boid.position)
        if num_boids_in_radius > 0:
            steering.divide(num_boids_in_radius)
            steering.subtract(self.position)
            steering.setMag(self.MAX_VELOCITY)
            steering.subtract(self.velocity)  # this is the steering force in direction of average
            steering.limit(self.MAX_FORCE)
        return steering

    def separation(self, flock):
        steering = Vector()  # desired location, avg of boids withing perception
        num_boids_in_radius = 0
        for boid in flock:
            distance = Vector.getDistance(self.position, boid.position)
            if boid is not self and distance < self.SEPARATION_PERCEPTION:
                difference = self.position - boid.position
                difference.divide(distance)  # inversely proportional
                steering.add(difference)
                num_boids_in_radius += 1
        if num_boids_in_radius > 0:
            steering.divide(num_boids_in_radius)
            steering.setMag(self.MAX_VELOCITY)
            steering.subtract(self.velocity)  # this is the steering force in direction of average
            steering.limit(self.MAX_FORCE)
        return steering

    def checkAbsBounds(self):
        if self.position.x > SIM_WIDTH:
            self.position.x = SIM_WIDTH - 2
        elif self.position.x < 0:
            self.position.x = 2
        if self.position.y > SIM_HEIGHT:
            self.position.y = SIM_HEIGHT - 2
        elif self.position.y < 0:
            self.position.y = 2

    def checkBounds(self):
        if self.position.x > SIM_WIDTH - MARGIN:
            self.velocity.x -= self.EDGE_TURN_FACTOR
        elif self.position.x < MARGIN:
            self.velocity.x += self.EDGE_TURN_FACTOR
        if self.position.y > SIM_HEIGHT - MARGIN:
            self.velocity.y -= self.EDGE_TURN_FACTOR
        elif self.position.y < MARGIN:
            self.velocity.y += self.EDGE_TURN_FACTOR
        self.checkAbsBounds()

    def checkPredator2(self, wolf):
        if Vector.getDistance(wolf.position, self.position) < self.PREDATORY_RANGE:
            wolf_dx = self.position.x - wolf.position.x
            wolf_dy = self.position.y - wolf.position.y
            if wolf_dy > 0:  # wolf is above
                if self.position.y > SIM_HEIGHT - MARGIN:
                    if self.position.x < SIM_WIDTH // 2:
                        self.velocity.x += self.EDGE_TURN_FACTOR
                    else:
                        self.velocity.x -= self.EDGE_TURN_FACTOR
                    self.velocity.y -= self.EDGE_TURN_FACTOR
                else:
                    self.velocity.y += self.PREDATOR_TURN_FACTOR
            elif wolf_dy < 0:  # wolf is below
                if self.position.y < MARGIN:
                    if self.position.x < SIM_WIDTH // 2:
                        self.velocity.x += self.EDGE_TURN_FACTOR
                    else:
                        self.velocity.x -= self.EDGE_TURN_FACTOR
                    self.velocity.y += self.EDGE_TURN_FACTOR
                else:
                    self.velocity.y -= self.PREDATOR_TURN_FACTOR
            if wolf_dx > 0:  # wolf is left
                self.velocity.x += self.PREDATOR_TURN_FACTOR
            elif wolf_dx < 0:  # wolf is right
                if self.position.x > SIM_WIDTH - MARGIN:
                    self.velocity.y -= self.PREDATOR_TURN_FACTOR
                else:
                    self.velocity.x -= self.PREDATOR_TURN_FACTOR

    def checkPredator(self, wolf):
        inCorner = False
        if Vector.getDistance(wolf.position, self.position) < self.PREDATORY_RANGE:
            wolf_dx = self.position.x - wolf.position.x
            wolf_dy = self.position.y - wolf.position.y
            if wolf_dy > 0:  # wolf is above
                if self.position.y > SIM_HEIGHT - MARGIN:
                    # bottom corner cases
                    if self.position.x < MARGIN * 3:
                        inCorner = True
                        self.velocity.x += self.EDGE_TURN_FACTOR
                    elif self.position.x > SIM_WIDTH - (MARGIN * 3):
                        inCorner = True
                        self.velocity.x -= self.EDGE_TURN_FACTOR
                    # edge cases
                    elif self.position.x < SIM_WIDTH // 2:
                        self.velocity.x -= self.EDGE_TURN_FACTOR
                    else:
                        self.velocity.x += self.EDGE_TURN_FACTOR
                # general case
                else:
                    self.velocity.y += self.PREDATOR_TURN_FACTOR
            elif wolf_dy < 0:  # wolf is below
                if self.position.y < MARGIN:
                    # top corner cases
                    if self.position.x < MARGIN * 3:
                        inCorner = True
                        self.velocity.x += self.EDGE_TURN_FACTOR
                    elif self.position.x > SIM_WIDTH - (MARGIN * 3):
                        inCorner = True
                        self.velocity.x -= self.EDGE_TURN_FACTOR
                    # edge cases
                    elif self.position.x < SIM_WIDTH // 2:
                        self.velocity.x -= self.EDGE_TURN_FACTOR
                    else:
                        self.velocity.x += self.EDGE_TURN_FACTOR
                # general case
                else:
                    self.velocity.y -= self.PREDATOR_TURN_FACTOR
            if wolf_dx > 0:  # wolf is left
                # edge case
                if self.position.x > SIM_WIDTH - MARGIN and not inCorner:
                    if self.position.y > SIM_HEIGHT // 2:
                        self.velocity.y += self.EDGE_TURN_FACTOR
                    else:
                        self.velocity.y -= self.EDGE_TURN_FACTOR
                # general case
                else:
                    self.velocity.x += self.PREDATOR_TURN_FACTOR
            elif wolf_dx < 0:  # wolf is right
                # edge case
                if self.position.x < MARGIN and not inCorner:
                    if self.position.y > SIM_HEIGHT // 2:
                        self.velocity.y += self.EDGE_TURN_FACTOR
                    else:
                        self.velocity.y -= self.EDGE_TURN_FACTOR
                # general case
                else:
                    self.velocity.x -= self.PREDATOR_TURN_FACTOR

    def getEaten(self):
        self.alive = False
        if self in herd:
            herd.remove(self)

    def getClosestWolf(self, wolves):
        ind = 0
        minDist = SIM_WIDTH  # no wolf can be farther than this
        for i, wolf in enumerate(wolves):
            distance = Vector.getDistance(self.position, wolf.position)
            if distance < minDist:
                ind = i
        return ind

    def draw(self, screen):
        copy = Vector(self.velocity.x, self.velocity.y)
        copy.setMag(8)
        relative_next = self.position + copy
        copy.setMag(4)
        relative_prev = self.position - copy
        pygame.draw.line(screen, (0, 0, 0), (self.position.x, self.position.y), (relative_next.x, relative_next.y))

        pygame.draw.circle(screen, self.colors[0], (relative_prev.x, relative_prev.y), 4)
        pygame.draw.circle(screen, self.colors[1], (self.position.x, self.position.y), 4)