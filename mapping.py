
import random
import math



class Map(object):
    x = 100
    y = 100
    towns = []


    @staticmethod
    def create():
        x_ord = random.randrange(Map.x + 1)
        y_ord = random.randrange(Map.y + 1)
        ords = (x_ord, y_ord)
        
        if ords in Map.towns:
            Map.create()
        
        else:
            Map.towns.append(ords)
            return ords
             
             
    @staticmethod
    def dist(ord1 ,ord2):
        x1, y1 = ord1
        x2, y2 = ord2

        return abs(math.sqrt(math.pow(x1 - x2, 2) + math.pow(y1 - y2, 2)))
    



