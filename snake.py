from constants import *
import logging

class Snake:
    def __init__(self, body, direction, name):
        self.body=body #initially located here
        self.name=name
        self.direction=self.newdirection=direction
        self.IsDead=False
        self.points = 0

        ## Added for Stats
        self.points_gained = 0
        self.lost_points = 0
        self.food_eaten = 0
        self.food_lost = 0
        self.crashed = 0
        self.winner = 0
        self.times = []
        logging.basicConfig(format=':%(levelname)s:%(message)s', level=logging.DEBUG)
    def updateBody(self, body):
        self.body = body
    def update(self,points=None, mapsize=None, count=None, agent_time=None):
        pass #send players stats about the game 
    def updateDirection(self,game):
        self.direction=self.newdirection #the next direction is stored in newdirection....logic is updated here
    def processkey(self,key):
        pass #nothing to do here it is just to support human players

