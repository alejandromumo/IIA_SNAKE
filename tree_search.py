#!/usr/bin/env python
# -*- coding: utf-8 -*-

################################################################
#  Classes de suporte à implementação do Algoritmo de Pesquisa #
################################################################
from sortedcontainers import SortedListWithKey
from pprint import *
#Class representing a Domain - set of actions(state),result(state,action),pathcost(state,action)
class Domain:
    def __init__(self):
        abstract
    def actions(self,state):
        abstract
    def result(self,state,action):
        abstract
    def pathcost(self,state,action):
        abstract
    def heuristic(self,state,goal):
        abstract

#Class representing a Problem - Domain,Initial State,Goal.
#Queremos ir de initial para Goal e temos uma série de opções à nossa disposição para resolver o problema (Domain)
class Problem:
    def __init__(self,domain,initial,goal):
        self.initial = initial  # Tuple
        self.domain = domain    # Domain
        self.goal = goal        # Tuple

    def goal_test(self,state):   # Have we reached goal yet?
        if self.goal[0] == state[0] and self.goal[1] == state[1]:
            return True
        return False
    def __str__(self):
        return "Problem: initial = {initial} to goal = {goal}".format(initial = self.initial, goal = self.goal)


#Class representing a Node
class Node:
    def __init__(self,state,parent,cost = 0,depth = 0,heuristics = 0, direction = (0,0)):
        self.state = state      #A position x,y- current State  (Let's say F := x,y)
        self.depth = depth      #Depth (0,1,2,3,4...) from root to this node
        self.cost = cost        #A float value - how much did it cost to go from all parents to here
        self.parent = parent    #A node - who is this Node's parent? (Let's say S)
        self.heuristic = heuristics
        self.direction = direction
    def __str__(self):
        return "Node( {state}, c+h = {costh}".format(state=self.state,costh = self.cost + self.heuristic)
    def __repr__(self):
        return str(self)
    def __eq__(self,other):
        if other == None:
            return False
        return self.state[0] == other[0] and self.state[1] == other[1]


#Class representing a search-tree
class SearchTree:
    def __init__(self,problem,depthlimit = -1,check_tail = 0):
        self.problem = problem      # A set of actions,result,initial Node etc
        root = Node(problem.initial,None,0,0,
                self.problem.domain.heuristic(self.problem.initial,self.problem.goal)) # A node
        self.open_nodes = SortedListWithKey(key = lambda x: x.heuristic,iterable = [root])
        self.cost = 0
        self.explored = set()
        self.check_tail = check_tail
        self.exploredNodes = []

    def __str__(self):
        return "Tree({initial}{goal})".format(initial = self.problem.initial, goal = self.problem.goal)
    # A list of states (x,y) representing how did we get from root (of the problem) to a Node
    def get_path(self,node):
        if node.parent == None:
            return [node.state]
        return self.get_path(node.parent) + [node.state]
    # Search for a solution to our problem
    def search(self):
        #####################################################
        #frontier = [root]                                  #
        #loop:                                              #
        #   if frontier is empty : return False             #
        #   path = remove_from_frontier(frontier)           #
        #   s = path.end                                    #
        #   if s is goal : return path                      #
        #   for a in actions:                               #
        #       add_to_frontier([path + a -> result(s,a)])  #
        #####################################################
        self.explored.clear()
        self.exploredNodes.clear()
        while len(self.open_nodes) != 0:

            open_nodes_states = [n.state for n in self.open_nodes] # Confirm - consumes time
            node = self.open_nodes.pop(0)
            self.explored.add(node.state)
            self.exploredNodes.append(node)
            if self.problem.goal_test(node.state):
                self.cost = node.cost
                self.depth = node.depth
                return self.get_path(node)
            open_nodes_states[0:1] = []
            lnewnodes = []
            if node.parent == None:
                actions = self.problem.domain.actions(node)
            else:
                actions = self.problem.domain.actions(node,node.parent)

            for a in actions:
                newstate = self.problem.domain.result(node.state,a) # tuplo
                direction = (newstate[0]-node.state[0],newstate[1]-node.state[1])
                if newstate not in open_nodes_states and newstate not in self.explored:
                    if self.check_tail == 0:
                        newnode = Node(newstate,node,node.cost + 1 , node.depth + 1 ,
                            self.problem.domain.heuristic(newstate,self.problem.goal)+node.cost+1,direction)
                    else:
                        newnode = Node(newstate,node,node.cost + 1 , node.depth + 1 ,
                            self.problem.domain.heuristic_tmp(newstate,self.problem.goal)+node.cost+1,direction)

                    self.open_nodes.add(newnode)
        return None
