from tools import *

class Pack:
    def __init__(self):
        self.pack = []
        self.strength = 0
        self.den = None

    def setDen(self, x, y):
        self.den = Den(x, y)

    def addWolf(self, wolf):
        self.pack.append(wolf)

class Den:
    def __init__(self, x, y):
        self.position = Vector(x, y)