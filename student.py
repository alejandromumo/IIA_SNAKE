	#!/usr/bin/env python
# -*- coding: utf-8 -*-

from snake import Snake
from constants import *
from tree_search import *
import numpy as np
from pprint import *
import copy
from queue import *
class Student(Snake):
    # TODO LIST:
    #   - Caminho aberto para a cauda
    #   - U's (mapa1)
    #   - Ir para áreas limpas e comer tempo
    #   - Concatenate paths
    #   - Turnos
    # BUG LIST:
    #   - Pontuação negativa (Confirm)
    #   - Explored muito grande por vezes
    #   - Enrola-se
    #   - Caminho para a cauda explora demasiado
    #   - Suicide : (1,0) start dir
    #   - Espeta-se com a cauda

    def __init__(self,body=[(0,0)] , direction=(1,0),name = "Student"):
        self.foodposition = None    # Posição sabida da comida. Serve para detectar se a comida se mexeu demasiado
        self.path = None            # Path entre o agente e a comida
        self.enemyHead = None       # Posição da cabeça inimiga
        self.lastpos = None         # Última posição conhecida pela snake. Serve para saber a olddir entre árvores
        self.field = None           # Campo. Matriz com o campo.
        self.first_time = True      # Serve para inicializar na primeira passagem determinados parametros.
        self.pathlen = 0            # Comprimento inicial do path. Serve para recalcular o path em ~50% se preciso
        self.maze = None
        self.enemy_tail = None   # Posição da cauda do inimigo.
        self.my_tail = None         # Posição da cauda da snake
        self.complement = [(up,down),(down,up),(right,left),(left,right)]
        self.original_field = None
        self.changed = []           # Vizinhança do inimigo que precisa de ser mudada
        self.need_processing = []   #
        self.food_accessible = False
        self.landmarks = []       # Lista de dictionaries. Landmark -> matrix (dictionary ={landmark:matrix})
        self.landmarks_pos = []
        super().__init__(body,direction,name)

    def pathlen(self,a,b):
        return int( ((a[0]-b[0])**2 + (a[1]-b[1])**2 )**0.5)

    def add(self,a,b):
        return a[0]+b[0],a[1]+b[1]

    def update(self,points=None, mapsize=None, count=None,agent_time=None):
        self.my_points = [y for (x,y) in points if x == self.name][0]
        self.enemy_points = [y for (x,y) in points if x != self.name][0]
        self.mapsize = mapsize
        self.count = count
        self.agent_time = agent_time
        pass

    def updateDirection(self,maze):
        #Na primeira passagem, cria-se a matriz field e a sua cópia.
        position = self.body[0]
        if self.first_time == True:
            self.field = field(self.mapsize)
            self.field.setObstacles_raw(maze.obstacles)
            self.need_processing = self.field.setObstacles_heatMap(obstacles = maze.obstacles)
            self.first_time = False
            self.tree = None
            self.foodposition = maze.foodpos
            self.original_field = self.field.getCopy()
            self.generateLandMarks()
        else:
            if len(self.need_processing) > 0:
                self.need_processing = self.field.spread(self.need_processing)

        # Roll back info matrix (enemy head surroundings)
        for s in self.changed:
            self.field.field[s[0]][s[1]] = self.original_field[s[0]][s[1]]

        # Update enemy position.
        enemy = self.getEnemyPos(maze)
        if self.enemy_tail != None:
            self.field.field[self.enemy_tail[1]][self.enemy_tail[0]] = self.original_field[self.enemy_tail[1]][self.enemy_tail[0]]
        self.enemy_tail = enemy[len(enemy) - 1]
        self.field.setEnemy(enemy)

        # Update my position.
        if self.my_tail != None:
            self.field.field[self.my_tail[1]][self.my_tail[0]] = self.original_field[self.my_tail[1]][self.my_tail[0]]
        self.my_tail = self.body[len(self.body)-1]
        self.field.setPlayer(self.body)


        self.maze = maze

        if self.field.field[maze.foodpos[1]][maze.foodpos[0]] == -3:
            self.food_accessible = False
        else:
            self.food_accessible = True

        # Check enemy head surroundings
        if self.my_points >= self.enemy_points:
            self.changed = self.field.update_enemy_head(enemy[0])
        else:
            self.changed = self.field.update_enemy_head(enemy[0],value = -3)

        ################################# SEARCHS ###################################
        #
        # Já há caminho?
        #   Se sim:
        #       Verifica se é preciso recalcula-lo (Comprometido ou está a ficar perigoso)
        #           Se sim:
        #               Recalcula
        #       Se não for possível chegar à comida, tenta a cauda.
        #
        #   Se não:
        #       calcula o caminho até ao goal
        #   Se não conseguiu nada:
        #       Joga safe
        #   Segue o caminho
        #################################################################################

        if self.food_accessible == False:
            self.calculatePath(position,self.my_tail)
        else:
            if self.path != None:
                if self.food_accessible == True and self.calculateIfCompromissed(position) == 0:
                    self.calculatePathConditions(position)
                if self.path == None:
                    if len(self.body) == 1:
                        self.path = None
                    else:
                        self.calculatePath(position,self.my_tail,check_tail = 0)
            else:
                self.calculatePath(position,maze.foodpos)

        if self.path == None:
            r = 1
            move = None
            for action in self.actions_tmp(position,self.lastpos):

                x = self.result(position,action)
                tile = self.field.field[x[1]][x[0]]
                if tile == 0:
                    move = action
                    break
                elif tile == -1:
                    r = -1
                    move = action
                elif tile == -2 and r == 1:
                    r = -2
                    move = action
                if move != None:
                    self.lastpos = position
                    self.direction = move
        else:
            self.lastpos = position
            if len(self.path) > 1:
                self.path = self.path[1:]
            newstate = self.path[0]
            if len(self.path) == 1:
                self.path = None
            direc = self.getDir(newstate,position)
            self.direction = direc



    #up = (0,-1) down = (0,1) left = (-1,0) right = (1,0)
    def calculatePath(self,position,foodpos,check_tail = 0):
        self.foodposition = foodpos
        p = Problem(self,position,foodpos)
        t = SearchTree(p,check_tail)
        self.path = t.search()
        self.tree = t
        if self.path != None:
            self.pathlen = len(self.path)

    def calculatePathConditions(self,position):
        food_distance_moved = self.pitagoras(self.maze.foodpos,self.path[len(self.path)-1])
        self.foodposition = self.maze.foodpos
        ratio_path = (len(self.path) / self.pathlen)
        ##########
        # Recalcular o caminho se:
        # -> A comida se tiver mexido demasiado e eu estiver relativamente perto dela
        #
        ##########
        if food_distance_moved >= 4 or self.heuristic_tmp(position,self.foodposition) <= 2:
            self.calculatePath(position,self.maze.foodpos)
            return 1
        return 0

    def calculateIfCompromissed(self,position):
        if self.path != None:
            for c in self.path:
                fieldnxny = self.field.field[c[1]][c[0]]
                if fieldnxny == -3 or fieldnxny == 2:
                    self.calculatePath(position,self.maze.foodpos)
                    return 1
        return 0
    def getValidNeighbours(self,state):
        neighbours = []
        for i in range(0,10):
            if self.field.field[state[0]+i][state[1]] != -3:
                return (state[0]+i,state[1])
            if self.field.field[state[0]+i][state[1]+i] != -3:
                return (state[0]+i,state[1]+i)
            if self.field.field[state[0]][state[1]+i] != -3:
                return (state[0],state[1]+i)
            if self.field.field[state[0]-i][state[1]+i] != -3:
                return (state[0]-i,state[1]+i)
            if self.field.field[state[0]-i][state[1]] != -3:
                return (state[0]-i,state[1])
            if self.field.field[state[0]-i][state[1]-i] != -3:
                return (state[0]-i,state[1]-i)
            if self.field.field[state[0]][state[1]-i] != -3:
                return (state[0],state[1]-i)
            if self.field.field[state[0]+i][state[1]-i] != -3:
                return (state[0]+i,state[1]-i)

    def generateLandMarks(self):
        # Pick numLandMarks landmarks
        #   For each landmark create a dictionary landmark : matrix
        #   Compute all costs from landmark to other states
        # Add to list of landmarks

        # Chose numLandMarks and store it into list landMarkStates
        k = 3
        hspacing = self.mapsize[1]/k
        vspacing = self.mapsize[0]/k
        for i in range(0,k):
            for j in range(0,k):
                landmark = ( round(hspacing/2 + hspacing*i), round(vspacing/2 + vspacing*j))

                if self.field.field[landmark[0]][landmark[1]] == -3:
                    landmark = self.getValidNeighbours(landmark)
                self.landmarks_pos.append(landmark)


        for i in range(0,len(self.landmarks_pos)):
            grid = np.zeros((self.mapsize[1],self.mapsize[0]))
            self.calculateDistancesFromLandmark(grid,self.landmarks_pos[i])
            self.landmarks.append(grid)

    def calculateDistancesFromLandmark(self,matrix,position):
        fifo = Queue()
        fifo.put(Node(position,0))
        while not fifo.empty():
            first = fifo.get()
            l = first.position[0]
            c = first.position[1]
            if  l > 0 and l < self.mapsize[1] and c > 0 and c < self.mapsize[0] and self.field.field[l][c] != -3:
                if matrix[l][c] == 0:
                    matrix[l][c] = first.distance
                    fifo.put(Node((l+1,c),first.distance+1))
                    fifo.put(Node((l,c-1),first.distance+1))
                    fifo.put(Node((l-1,c),first.distance+1))
                    fifo.put(Node((l,c+1),first.distance+1))

        matrix[position[0]][position[1]] = 0


    def printstatus(self,maze):
        print("Status: obstacles - " + str(maze.obstacles))
        print("\n\nStatus: playerbody - " + str(self.body))
        print("\n\nStatus: enemybody - " + str(self.getEnemyPos(maze)))



    def getDir(self,newstate,position):
        x,y = newstate[0] - position[0] , newstate[1] - position[1]

        if abs(x + y) == 1:
            return x,y
        else:
            if x == self.field.width - 1:
                x = ((x/x) * -1)
            elif x == -(self.field.width - 1) :
                x = (x/x)
            elif y == self.field.height - 1:
                y = ((y/y) * -1)
            elif y == -(self.field.height - 1):
                y = (y/y)


        return x,y
    def getEnemyPos(self,maze): #TODO: Não precisa de percorrer a lista toda. Pode simplesmente atualizar
        #KNOW THE OPPONENT PLAYER BY COMPARING TO OUR POS#########################
        EnemyPos = [x for x in maze.playerpos if x not in self.body]
        #print(EnemyPos)
        #COMPARE WITH PREVIOUS POSITION
        return EnemyPos

    def getOpenNodes(self):
        if self.tree != None:
            return self.tree.open_nodes
        return None

    def getExplored(self):
        if self.tree != None:
            return self.tree.explored

    def getExploredNodes(self):
        if self.tree != None:
            return self.tree.exploredNodes


    ########## Definition of a Problem ######################

    # Devolve uma lista de acções possíveis sobre state (up,down,left,right)
    def actions(self,node,parent = None):
         #new direction can't be up if current direction is down...and so on
        if parent == None:
            if self.lastpos == None:
                olddir = self.direction
            else:
                olddir = self.getDir(node.state,self.lastpos)
            node.direction = olddir

        dirX,dirY = node.direction[0],node.direction[1]
        valid_tmp = []
        for d in directions:
            x,y = d[0],d[1]
            if x == -dirX and y == -dirY:
                continue
            newstate = self.result(node.state,d)
            fieldnxny = self.field.field[newstate[1]][newstate[0]]
            if fieldnxny == -3 or fieldnxny == 2 or (fieldnxny == 1):
                pass
            else:
                valid_tmp.append(d)
        return valid_tmp


    def actions_tmp(self,state,oldstat = None):
         #new direction can't be up if current direction is down...and so on
        if oldstat == None:
            if len(self.body) == 1 and self.lastpos != None:
                olddir = self.getDir(state,self.lastpos)
            elif len(self.body) == 1 and self.lastpos == None:
                olddir = self.direction
            else:
                olddir = self.getDir(state,self.lastpos) # TODO self.lastpos
        else:
            olddir = self.getDir(state,oldstat)

        invaliddir = [x for (x,y) in self.complement if y == olddir] #se estamos a ir :down, não podemos ir up etc
        validdir = [dir for dir in directions if not ( dir in invaliddir )] #é válida se não for inválida (left,right,up or down)

        #Verificar que não há um obstáculo nem o próprio agente
        valid_tmp = []
        for v in validdir:
            newstate = self.result(state,v)
            fieldnxny = self.field.field[newstate[1]][newstate[0]]
            if fieldnxny == -3 or fieldnxny == 2 or (fieldnxny == 1):
                pass
            else:
                valid_tmp.append(v)
        return valid_tmp

    # Devolve um estado que é obtido através da aplicação de action em state
    def result(self,state,action):
        x,y = (state[0] + action[0] , state[1] + action[1])
        x = (int) (self.mapsize[0] + x) % self.mapsize[0]
        y = (int) (self.mapsize[1] + y) % self.mapsize[1]


        return x,y

    # Devolve um inteiro que é o custo de realizar action em state
    def cost(self,state,action):
    	return 1

    def heuristic_tmp(self,state,goal_state):
        m = self.manhattan(state,goal_state)
        p = self.pitagoras(state,goal_state)

        return ((m+p)/2)

    def heuristic(self,state,goal_state):
        h1 = abs(goal_state[0] - state[0])
        h2 = abs(goal_state[0] + self.mapsize[0] - state[0])
        v1 = abs(goal_state[1] - state[1])
        v2 = abs(goal_state[1] + self.mapsize[1] - state[1])
        state_value = 0
        #state_value = (self.field.field[state[1]][state[0]])**4
        #state_value = state_value / (state_value + 1)
        if(h1 < h2):
            if(v1 < v2):
                d = (h1 + v1 + abs((h1 - v1)/(self.mapsize[0] + self.mapsize[1])) + state_value)
            else:
                d = (h1 + v2 + abs((h1 - v2)/(self.mapsize[0] + self.mapsize[1])) + state_value)
        else:
            if (v1 < v2):
                d = (h2 + v1 + abs((h2 - v1)/(self.mapsize[0] + self.mapsize[1])) + state_value)
            else:
                d = (h2 + v2 + abs((h2 - v2)/(self.mapsize[0] + self.mapsize[1])) + state_value)

        for i in range(0,len(self.landmarks)):
            ltH = self.landmarks[i][state[1]][state[0]]
            ltT = self.landmarks[i][goal_state[1]][goal_state[0]]
            d2 = abs(ltH - ltT)
            if( d < d2):
                d = d2
        return d

    def pitagoras(self,a,b): # TODO wrap around 
        return (((a[0]-b[0])**2 + (a[1]-b[1])**2 )**0.5)

    def manhattan(self,state,goal_state): # TODO wrap aroun
        return abs(state[0] - goal_state[0]) + abs(state[1] - goal_state[1])


### Suport classes

class field():
    def __init__(self, mapsize, obstacles = None):
        # -1 : obstacles
        #  1 : player
        #  0 : empty
        #  2 : enemy
        #  3 : food
        self.width = mapsize[0]
        self.height = mapsize[1]
        self.field = np.zeros((self.height,self.width))

    def setObstacles_raw(self,obstacles):
        for o in obstacles:
            self.field[o[1]][o[0]] = -3

    def setObstacles_heatMap(self,obstacles):
        obstacles = set(obstacles)
        need_processing = []
        for o in obstacles:
            l,c = o[1],o[0]

            # Check North
            if l != 0:
                if self.field[l-1][c] != -3:
                    self.field[l-1][c] -=  1
                    if self.field[l-1][c] == -3:
                        need_processing.append((l-1,c))

            else:
                if self.field[self.height-1][c] != -3:
                    self.field[self.height-1][c] -= 1
                    if self.field[self.height-1][c] == -3:
                        need_processing.append((self.height-1,c))

            # Check South
            if l!= self.height -1:
                if self.field[l+1][c] != -3:
                    self.field[l+1][c] -= 1
                    if self.field[l+1][c] == -3:
                        need_processing.append((l+1,c))
            else:
                if self.field[0][c] != -3:
                    self.field[0][c] -= 1
                    if self.field[0][c] == -3:
                        need_processing.append((0,c))

            # Check West
            if c != 0:
                if self.field[l][c-1] != -3:
                    self.field[l][c-1] -= 1
                    if self.field[l][c-1] == -3:
                        need_processing.append((l,c-1))

            else:
                if self.field[l][self.width-1] != -3:
                    self.field[l][self.width-1] -= 1
                    if self.field[l][self.width-1] == -3:
                        need_processing.append((l,self.width-1))

            # Check East
            if c != self.width -1:
                if self.field[l][c+1] != -3:
                    self.field[l][c+1] -= 1
                    if self.field[l][c+1] == -3:
                        need_processing.append((l,c+1))
            else:
                if self.field[l][0] != -3:
                    self.field[l][0] -= 1
                    if self.field[l][0] == -3:
                        need_processing.append((l,0))

        return need_processing

    def spread(self,need_processing):
        while need_processing != []:
            o = need_processing[0]
            need_processing = need_processing[1:]
            l,c = o[0],o[1]

            # Check North
            if l != 0:
                if self.field[l-1][c] != -3:
                    self.field[l-1][c] -=  1
                    if self.field[l-1][c] == -3:
                        need_processing.append((l-1,c))

            else:
                if self.field[self.height-1][c] != -3:
                    self.field[self.height-1][c] -= 1
                    if self.field[self.height-1][c] == -3:
                        need_processing.append((self.height-1,c))

            # Check South
            if l!= self.height -1:
                if self.field[l+1][c] != -3:
                    self.field[l+1][c] -= 1
                    if self.field[l+1][c] == -3:
                        need_processing.append((l+1,c))
            else:
                if self.field[0][c] != -3:
                    self.field[0][c] -= 1
                    if self.field[0][c] == -3:
                        need_processing.append((0,c))

            # Check West
            if c != 0:
                if self.field[l][c-1] != -3:
                    self.field[l][c-1] -= 1
                    if self.field[l][c-1] == -3:
                        need_processing.append((l,c-1))

            else:
                if self.field[l][self.width-1] != -3:
                    self.field[l][self.width-1] -= 1
                    if self.field[l][self.width-1] == -3:
                        need_processing.append((l,self.width-1))

            # Check East
            if c != self.width -1:
                if self.field[l][c+1] != -3:
                    self.field[l][c+1] -= 1
                    if self.field[l][c+1] == -3:
                        need_processing.append((l,c+1))
            else:
                if self.field[l][0] != -3:
                    self.field[l][0] -= 1
                    if self.field[l][0] == -3:
                        need_processing.append((l,0))
        return need_processing

    def setPlayer(self,player):
        for p in player:
            self.field[p[1]][p[0]] = 1

    def setEnemy(self,enemy):
        for e in enemy:
            self.field[e[1]][e[0]] = 2

    def setFood(self,food):
        self.field[food[1]][food[0]] = 3

    def update_enemy_head(self,enemy,value = -2):
        l,c = enemy[1],enemy[0]
        changed = []

        # Check North
        if l != 0:
            if self.field[l-1][c] != -3 and self.field[l-1][c] != 2:
                self.field[l-1][c] =  value
                changed.append((l-1,c))
        else:
            if self.field[self.height-1][c] != -3 and self.field[self.height-1][c]:
                self.field[self.height-1][c] = value
                changed.append((self.height-1,c))

        # Check South
        if l!= self.height -1:
            if self.field[l+1][c] != -3 and self.field[l+1][c] != 2:
                self.field[l+1][c] = value
                changed.append((l+1,c))
        else:
            if self.field[0][c] != -3 and self.field[0][c] != 2:
                self.field[0][c] = value
                changed.append((0,c))

        # Check West
        if c != 0:
            if self.field[l][c-1] != -3 and self.field[l][c-1] != 2:
                self.field[l][c-1] = value
                changed.append((l,c-1))
        else:
            if self.field[l][self.width-1] != -3 and self.field[l][self.width-1] != 2:
                self.field[l][self.width-1] = value
                changed.append((l,self.width-1))

        # Check East
        if c != self.width -1:
            if self.field[l][c+1] != -3 and self.field[l][c+1] != 2:
                self.field[l][c+1] = value
                changed.append((l,c+1))
        else:
            if self.field[l][0] != -3 and self.field[l][0] != 2:
                self.field[l][0] = value
                changed.append((l,0))
        return changed

    def getCopy(self):
        copy = np.zeros((self.height,self.width))
        for l in range(0,self.height):
            for c in range(0,self.width):
                copy[l][c] = self.field[l][c]

        return copy



    def __str__(self):
        return "Field: = {field}".format(field = self.field)

class Node():
    def __init__(self,position,distance):
        self.position = position
        self.distance = distance
    def getPosition(self):
        return self.position
    def getDistance(self):
        return self.distance
