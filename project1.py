# By Cameron Decker (csd110)

import sys
import random
import math
import time
import copy
import numpy
from collections import defaultdict
import heapq as heap

class cell(object):
    def __init__(self):
        self.fire = 0
        self.pos = [0,0]
        self.dist = 0       # distance from a block on fire, -1 = blocked/uninitialized
        if random.random() < .3:
            self.blocked = 1
        else:
            self.blocked = 0

class agent:
    def __init__(self):
        self.pos = [0,0]
        self.status = 0 # -1 = dead or no path, 0 = normal (agent hasn't died nor reached goal), 1 = agent has reached goal

    # moves the agent one space according to its path
    # returns 0 on success, -1 if in a fire after moving, and 1 if it reached the goal
    def move(self, maze, path):
        if path == 0:
            self.status = -1
            return
        dest = path.pop(0)
        if dest.pos == self.pos:
            dest = path.pop(0)
        if dest.pos[0] > self.pos[0]:
            self.pos[0] = self.pos[0] + 1
        elif dest.pos[0] < self.pos[0]:
            self.pos[0] = self.pos[0] - 1
        elif dest.pos[1] > self.pos[1]:
            self.pos[1] = self.pos[1] + 1
        elif dest.pos[1] < self.pos[1]:
            self.pos[1] = self.pos[1] - 1
        
        # checks to see if agent is in fire or at goal
        currentspot = maze[self.pos[0],self.pos[1]]
        if currentspot.fire == 1:
            self.status = -1
        elif currentspot.pos == [50,50]:
            self.status = 1

# constucts a new maze (doesn't test it)
def constructmaze():

    maze = numpy.ndarray((51,51), dtype=numpy.object)
    for i in range(51):
        for j in range(51):
            maze[i,j] = cell()
            maze[i,j].pos = [i, j]
            maze[i,j].dist = -1
            if random.random() < .3:
                maze[i,j].blocked = 1
            else:
                maze[i,j].blocked = 0
            maze[i,j].fire = 0
            
    return maze

# returns a valid maze
def getvalidmaze():

    # generates mazes until it finds one that passes all tests
    mazefound = 0
    while mazefound < 5:
        mazefound = 0
        maze = constructmaze()
        maze[0,0].blocked = 0
        maze[25,25].blocked = 0
        maze[0,50].blocked = 0
        maze[50,0].blocked = 0
        maze[50,50].blocked = 0

        mazefound = mazefound + dfs(maze, maze[25,25], maze[0,0])
        mazefound = mazefound + dfs(maze, maze[25,25], maze[0,50])
        mazefound = mazefound + dfs(maze, maze[25,25], maze[50,0])
        mazefound = mazefound + dfs(maze, maze[25,25], maze[50,50])

        maze[25,25].blocked = 1
        maze[25,25].dist = -1
        mazefound = mazefound + dfs(maze, maze[0,0], maze[50,50])
    
    maze[25,25].fire = 1   #sets maze on fire
    return maze

# returns a list of adjacent cells that are not blocked or on fire
def getchildren(maze, x, y):
    children = []
    if x > 0 and maze[x-1,y].blocked != 1 and maze[x-1,y].fire != 1:
        children.append(maze[x-1,y])
    if x+1 < 51 and maze[x+1,y].blocked != 1 and maze[x+1,y].fire != 1:
        children.append(maze[x+1,y])
    if y > 0 and maze[x,y-1].blocked != 1 and maze[x,y-1].fire != 1:
        children.append(maze[x,y-1])
    if y+1 < 51 and maze[x,y+1].blocked != 1 and maze[x,y+1].fire != 1:
        children.append(maze[x,y+1])
    return children

# returns the amount of neighbors of cell [x,y] on fire
def getflamingneighbors(maze, x, y):
    flamingneighbors = 0
    if x > 0 and maze[x-1,y].fire == 1:
        flamingneighbors = flamingneighbors + 1
    if x+1 < 51 and maze[x+1,y].fire == 1:
        flamingneighbors = flamingneighbors + 1
    if y > 0 and maze[x,y-1].fire == 1:
        flamingneighbors = flamingneighbors + 1
    if y+1 < 51 and maze[x,y+1].fire == 1:
        flamingneighbors = flamingneighbors + 1
    return flamingneighbors

# takes starting cell S and uses a DF graph search to determine if a path can be reached to cell G
# returns 1 if there is a possible path, 0 if there is not
def dfs(maze, S, G):
    #starttime = time.clock_gettime(time.CLOCK_REALTIME)
    fringe = []
    closed = []
    fringe.append(S)
    while len(fringe) > 0:
        current = fringe.pop(0)

        if current in closed:
            continue

        if current == G:
            #print("Search completed in", time.clock_gettime(time.CLOCK_REALTIME) - starttime, "seconds (success)")
            return 1
        else:
            if current not in closed:
                for x in getchildren(maze, current.pos[0], current.pos[1]):
                    fringe.insert(0, x)
            closed.append(current)
    #print("Search completed in", time.clock_gettime(time.CLOCK_REALTIME) - starttime, "seconds (fail)")
    return 0

# performs a BFS from S to G, returning the path if it's possible and 0 if it's not
def shortestpath(maze, S, G):
    #starttime = time.clock_gettime(time.CLOCK_REALTIME)
    fringe = []
    closed = []
    fringe.append([S])
    while len(fringe) > 0:
        path = fringe.pop(0)
        current = path[-1]
        if current in closed:
            continue
        if current == G:
            #print("Search completed in", time.clock_gettime(time.CLOCK_REALTIME) - starttime, "seconds (success)")
            return path
        else:
            for x in getchildren(maze, current.pos[0], current.pos[1]):
                newpath = list(path)
                newpath.append(x)
                fringe.append(newpath)
            closed.append(current)
    #print("Search completed in", time.clock_gettime(time.CLOCK_REALTIME) - starttime, "seconds (fail)")
    return 0

def printmaze(maze, newagent, path):
    for x in maze:
        for y in x:
            if path == 0:
                print("No path given!")
                break
            symbol = '.'
            if y in path:
                symbol = 'O'
            if y.blocked:
                symbol = 'X'
            if y.fire:
                symbol = 'F'
            if newagent.pos == y.pos:
                symbol = '@'

            print(symbol, end = ' ')
            #print(y.dist, end=' ')
        print("")

def printtime(starttime):
    print("")
    print("Completed in", time.clock_gettime(time.CLOCK_REALTIME) - starttime, "seconds")
    print("------------------------------------------------------")

# spreads the fire one step
def spreadfire(maze, flammability):
    firerisks = []
    # compiles a list of all cells at risk for igniting
    for i in maze:
        for j in i:
            if j.fire == 1:
                for risk in getchildren(maze, j.pos[0], j.pos[1]):
                    if risk.blocked == 1:
                        continue

                    # lights cells adjacent to flaming cells on fire if check is passed
                    if random.random() < 1 - math.pow(1 - flammability, getflamingneighbors(maze, risk.pos[0], risk.pos[1])):
                        risk.fire = 1

# returns a simulation of the given maze 3 steps ahead
def simulatemaze(maze, flammability):
    simmaze = copy.deepcopy(maze)
    for i in range(3):
        spreadfire(simmaze, flammability)
    return simmaze

# checks the path for fire, returning 1 if part of the path is on fire and 0 if not
def checkpath(path):
    for x in path:
        if x.fire == 1:
            return 1
    return 0

# checks the path for fire, returning 1 if part of the path is on fire and 0 if not
def agent4checkpath(maze, path):
    if path == 0:
        return 1
    for x in path:
        if maze[x.pos[0],x.pos[1]].fire == 1:
            return 1
    return 0


# checks the path for fire in simulated maze, returning 1 if part of the path is on fire and 0 if not
def checksimulatedpath(simmaze, path):
    for x in path:
        if simmaze[x.pos[0],x.pos[1]].fire == 1:
            return 1
    return 0

# finds the distance of every cell from the fire for agent 4
def fireprob(maze):

    maxdistance = 0

    S = maze[25,25]
    fringe = []
    closed = []                                 # <-------- REPLACE WITH DICT
    checked = []
    fringe.append(S)
    while len(fringe) > 0:
        current = fringe.pop(0)

        if current in closed:
            continue

        else:
            for x in getchildren(maze, current.pos[0], current.pos[1]):
                if x not in checked:
                    x.dist = current.dist+1
                    if maxdistance < x.dist:
                        maxdistance = x.dist
                checked.append(x)
                fringe.append(x)
        closed.append(current)
    #print("Search completed in", time.clock_gettime(time.CLOCK_REALTIME) - starttime, "seconds (fail)")
    for x in maze:
        for y in x:
            if y.dist != -1:
                y.dist = (y.dist - maxdistance) * -1
            else:
                y.dist = 2601
    return 0

# will run numberoftests tests using agent 1 and return the number of successes/numberoftests
def agent1test(flammability, numberoftests):

    successes = 0

    for i in range(numberoftests):

        newagent = agent()
        maze = getvalidmaze()
        path = shortestpath(maze, maze[0,0], maze[50,50])

        # loops as long as the agent is moving
        while newagent.status == 0:
            newagent.move(maze, path)
            spreadfire(maze, flammability)

        if newagent.status == 1:
            successes = successes + 1
    print(flammability, ",", successes/numberoftests)

def agent2test(flammability, numberoftests):

    successes = 0

    for i in range(numberoftests):

        newagent = agent()
        maze = getvalidmaze()
        path = shortestpath(maze, maze[0,0], maze[50,50])

        # loops as long as the agent is moving
        while newagent.status == 0:
            if checkpath(path):  # checks if the current path is invalid (on fire), and if it is then replans
                path = shortestpath(maze, maze[newagent.pos[0],newagent.pos[1]], maze[50,50])
            newagent.move(maze, path)
            spreadfire(maze, flammability)

        if newagent.status == 1:
            successes = successes + 1
    print(flammability, ",", successes/numberoftests)

def agent3test(flammability, numberoftests):

    successes = 0

    for i in range(numberoftests):

        newagent = agent()
        maze = getvalidmaze()
        path = shortestpath(maze, maze[0,0], maze[50,50])

        # loops as long as the agent is moving
        while newagent.status == 0:
            simmaze = simulatemaze(maze, flammability)      # gets a simulation of the maze 3 steps ahead
            if checksimulatedpath(simmaze, path):  # checks if the simulated path is invalid (on fire), and if it is then replans
                path = shortestpath(simmaze, maze[newagent.pos[0],newagent.pos[1]], simmaze[50,50])
                if path == 0: # will try to get a simulated path one more time
                    simmaze = simulatemaze(maze, flammability)
                    path = shortestpath(simmaze, maze[newagent.pos[0],newagent.pos[1]], simmaze[50,50])
                    if path == 0:
                        break
            newagent.move(maze, path)
            spreadfire(maze, flammability)

        if newagent.status == 1:
            successes = successes + 1
    print(flammability, ",", successes/numberoftests)

def agent4test(flammability, numberoftests):
    successes = 0

    for i in range(numberoftests):

        newagent = agent()
        maze = getvalidmaze()
        
        # initial plan is based on a simulation of the maze 50 steps ahead
        simmaze = copy.deepcopy(maze)
        for i in range(50):
            spreadfire(simmaze, flammability)
        path = shortestpath(simmaze, simmaze[0,0], simmaze[50,50])  

        while newagent.status == 0: # loops as long as the agent is moving
            if agent4checkpath(maze, path):  # checks if the current path is invalid (on fire), and if it is then replans
                
                # first tries to make path based on maze as predicted 5 steps ahead
                simmaze = copy.deepcopy(maze)
                for i in range(5):
                    spreadfire(simmaze, flammability)
                path = shortestpath(simmaze, simmaze[newagent.pos[0],newagent.pos[1]], simmaze[50,50])

                # ...otherwise makes a path based on current maze (also happens when initial plan is impossible)
                if path == 0:
                    path = shortestpath(maze, maze[newagent.pos[0],newagent.pos[1]], maze[50,50])

                newagent.move(maze, path)
                spreadfire(maze, flammability)
            newagent.move(maze, path)
            spreadfire(maze, flammability)

        if newagent.status == 1:
            successes = successes + 1
    print(flammability, ",", successes/numberoftests)

# tests [attempts] many mazes with flammability values determined by [range] on [agents]
# where attempts = an integer, range = list of flammability values, and agents = a list of integers 1 - 3
def runtests(attempts, range, agents):
    totalstarttime = time.clock_gettime(time.CLOCK_REALTIME) 

    print("Sample Size:", attempts, "attempts")
    print("------------------------------------------------------")

    if 1 in agents:
        starttime = time.clock_gettime(time.CLOCK_REALTIME)
        print("Agent 1:")
        print("Flammability, average success rate")
        for i in range:
            agent1test(i, attempts)
        printtime(starttime)

    if 2 in agents:
        starttime = time.clock_gettime(time.CLOCK_REALTIME)
        print("Agent 2:")
        print("Flammability, average success rate")
        for i in range:
            agent2test(i, attempts)
        printtime(starttime)

    if 3 in agents:
        starttime = time.clock_gettime(time.CLOCK_REALTIME)
        print("Agent 3:")
        print("Flammability, average success rate")
        for i in range:
            agent3test(i, attempts)
        printtime(starttime)

    if 4 in agents:
        starttime = time.clock_gettime(time.CLOCK_REALTIME)
        print("Agent 4:")
        print("Flammability, average success rate")
        for i in range:
            agent4test(i, attempts)
        printtime(starttime)

    print("Took a total of", time.clock_gettime(time.CLOCK_REALTIME) - totalstarttime, "seconds")

def main():

    # redirects print() to out.txt
    f = open('out.txt', 'w')
    sys.stdout = f

    attempts = 100      # number of attempts to run
    ranges = [0.0, 0.05, .1, .15, .2, .25, .3, .35, .4, .45, .5]      # flammability values to test
    agents = [1,2,3,4]    # agents to test


    runtests(attempts, ranges, agents)
    

main()