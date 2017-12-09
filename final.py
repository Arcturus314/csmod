import random
import time
from operator import itemgetter

HEIGHT    = 25
WIDTH     = 25
NUMSTATES = 5
NUMTRIALS = 50
NUMSTEPS  = 1000
PROPMUT   = 0.3
PROPLIVE  = 0.1
FILENAME  = "output.txt"

class Program:
    def __init__(self):
        """Constructor for the Program class"""
        self.rules = {}

    def __repr__(self):
        """Returns the rule set in a simulator-compatible format"""
        if self.rules == {}: return ""
        keys_list = list(self.rules.keys())
        sorted_keys = sorted(keys_list)
        toPrint = ""
        for key in sorted_keys:
            toPrint += (str(key[0])+" "+key[1]+" "+key[2]+" -> "+self.rules[key][0]+" "+self.rules[key][1]+" "+str(self.rules[key][2])+'\n')
        return toPrint

    def randomize(self):
        """Creates a random rule set that will not cause any wall intersections"""
        self.rules = {}
        possible_surroundings = ["NEWx", "NExS", "NExx", "NxWS", "NxWx", "NxxS", "Nxxx", "xEWS", "xEWx", "xExS", "xExx", "xxWS", "xxWx", "xxxS", "xxxx"]
        possible_detect       = ["m","xm"]
        possible_action       = ["","dm","pm"]
        possible_action2       = ["","dm"]
        possible_dirs         = ["N","S","E","W"]
        for state in range(5):
            for element in possible_surroundings:
                for detect in possible_detect:
                    if detect == "xm": action = random.choice(possible_action2)
                    else: action = random.choice(possible_action)
                    newState = random.choice(range(5))
                    validMove = False
                    while validMove == False:
                        newDir = random.choice(possible_dirs)
                        if newDir not in element:
                            validMove = True
                    key = (state, element, detect)
                    val = (action, newDir, newState)
                    self.rules[key] = val

    def getMove(self, state, surroundings, at):
        return self.rules[(state, surroundings, at)]

    def mutate(self):
        """changes a random rule from self.rules to a different, randomly generated, valid, rule"""
        possible_dirs         = ["N","S","E","W"]
        possible_action       = ["","dm","pm"]
        possible_action2       = ["","dm"]
        randomRuleKey = random.choice(list(self.rules.keys()))
        randomRule = self.rules[randomRuleKey]
        newState = random.choice(range(5))
        newAction = random.choice(possible_action)
        if randomRuleKey[2] == "xm": newAction = random.choice(possible_action2)
        else: newAction = random.choice(possible_action)
        validMove = False
        while validMove == False:
            newDir = random.choice(possible_dirs)
            if newDir not in randomRuleKey[1]:
                validMove = True
        newMove = (newAction, newDir, newState)
        self.rules[randomRuleKey] = newMove

    def crossover(self,other):
        """returns an offspring Program with some rules from self and some from other"""
        cstate = random.choice(range(5))
        returnProgram = Program()
        for state in range(cstate+1):
            for key in list(self.rules.keys()):
                if key[0] == state:
                    returnProgram.rules[key] = self.rules[key]
        for state in range(cstate+1, 5):
            for key in list(other.rules.keys()):
                if key[0] == state:
                    returnProgram.rules[key] = other.rules[key]
        return returnProgram


class World:
    def __init__(self, initial_row, initial_col, program):
        """Constructor for the World class"""
        self.numcookies = 0
        self.prow = initial_row
        self.pcol = initial_col
        self.state = 0
        self.prog = program
        self.room = [ [' ']*WIDTH for row in range(HEIGHT) ]
        for col in range(WIDTH):
            self.room[0][col] = '+'
            self.room[HEIGHT-1][col] = '+'
        for row in range(HEIGHT):
            self.room[row][0] = '+'
            self.room[row][WIDTH-1] = '+'

    def __repr__(self):
        """Returns a human-readable board rendered in ASCII"""
        toPrint = ""
        for row in range(HEIGHT):
            for col in range(WIDTH):
                toPrint += self.room[row][col]
            toPrint += '\n'
        return toPrint

    def getCurrentSurroundings(self):
        """Returns the current Picobot surroundings in a compatible format to its ruleset"""
        around = ""

        if self.room[self.prow][self.pcol] == ".":
            at = "m"
        else:
            at = "xm"

        #wall north
        if self.room[self.prow-1][self.pcol] == "+": around += "N"
        else: around += "x"
        #wall east
        if self.room[self.prow][self.pcol+1] == "+": around += "E"
        else: around += "x"
        #wall west
        if self.room[self.prow][self.pcol-1] == "+": around += "W"
        else: around += "x"
        #wall south
        if self.room[self.prow+1][self.pcol] == "+": around += "S"
        else: around += "x"
#        print(around,at)
        return around, at

    def step(self):
        """One Picobot set given the rules in self.program"""
        surroundings, at = self.getCurrentSurroundings()
        newP = self.prog.getMove(self.state, surroundings, at)

        #changing state
        self.state = newP[2]

        #setting pebble
        if newP[0] == "dm" and at == "xm":
  #          print("dropping at",self.room[self.prow][self.pcol])
            self.numcookies += 1
            if self.numcookies <= 5:
                self.room[self.prow][self.pcol]="."
        if newP[0] == "pm" and at == "m":
 #           print("picking up at",self.room[self.prow][self.pcol])
            self.numcookies -= 1
            self.room[self.prow][self.pcol]="o"

        #moving picobot
        if newP[1] == "N": self.prow-=1
        if newP[1] == "S": self.prow+=1
        if newP[1] == "E": self.pcol+=1
        if newP[1] == "W": self.pcol-=1

    def stepPrint(self):
        for i in range(50):
            self.step()
            print(self)
            time.sleep(0.1)

    def run(self, steps):
        """Runs step steps number of times"""
        for i in range(steps):
            self.step()

    def fractionVisitedCells(self):
#        print("cookies:",self.numcookies)
        if self.numcookies > 5: return 0.0
        totalCells = 0
        totalVisited = 0
        for row in range(HEIGHT-2):
            for col in range(WIDTH-2):
                totalCells += 1
                if self.room[row+1][col+1] == 'o' or self.room[row+1][col+1] == 'P': totalVisited += 1
        return float(totalVisited) / float(totalCells)

def makeNewPop(size):
    """produces a new list of programs"""
    returnList = []
    for i in range(size):
        newP = Program()
        newP.randomize()
        returnList += [newP]
    return returnList

def evaluateFitness(program, trials, steps):
    """evaluates the fitness of program P over multiple starting positions"""
    fitnessSum = 0
    for i in range(trials):
        randomRow = 1
        randomCol = 1 
        w = World(randomRow, randomCol, program)
        rectangley = random.choice(range(HEIGHT-5))
        rectanglex = random.choice(range(WIDTH-5))
        rectangleh = random.choice(range(5))
        rectanglew = random.choice(range(5))
        for j in range(rectangleh):
            for k in range(rectanglew):
                w.room[j+rectangleh][k+rectanglew] = '+'
        w.run(steps)
        fitnessSum += w.fractionVisitedCells()
    return fitnessSum/float(trials) 

def saveToFile(filename, p): 
    """saves data from program P to a file"""
    f = open(filename,"w")
    print(p, file=f)
    f.close()

def GA(popsize, numgens):
    """main method and user interface for the genetic algorithm"""
    pop = makeNewPop(popsize)
    mutateList = [1]+[0]*(int(1/PROPMUT)-1)
    averageList = []
    bestList    = []
    for i in range(numgens):
        progList = []
        sumFitness = 0
        bestFitness = 0
        for program in pop:
            fitness = evaluateFitness(program, NUMTRIALS, NUMSTEPS)
            sumFitness += fitness
            if fitness > bestFitness:
                bestFitness = fitness
            progList.append((fitness, program))
        sortProgs = sorted(progList, key=itemgetter(0))
        bestProgs = sortProgs[-1*int(popsize*PROPLIVE):]
        pop = []
        for j in range(popsize-int(popsize*PROPLIVE)):
            tempProg = random.choice(bestProgs)[1].crossover(random.choice(bestProgs)[1])
            if random.choice(mutateList) == 1:
                tempProg.mutate()
            pop.append(tempProg)
        for element in bestProgs:
            pop.append(element[1])
        averageFit = sumFitness/float(popsize)
        averageList.append(averageFit)
        bestList.append(bestFitness)
        print("Generation:",i,"\n   Average fitness:",averageFit,"\n   Best fitness:",bestFitness)
    print("Best Program:\n",bestProgs[-1][1])
    saveToFile(FILENAME, bestProgs[-1][1])
    makeCSV(averageList, bestList)

def makeCSV(averageList, maxList):
    """makes a CSV file with average and best information for each generation"""
    outputFile = ""
    for i in range(len(averageList)):
        outputFile += str(i)+","+str(averageList[i])+","+str(maxList[i])+"\n"
    f = open("graphs.csv","w")
    f.write(outputFile)
    f.close()

#restricting to 5 pebbles- delete any pebbles once 5 have been placed?
#   Return fitness of 0 if >5 pebbles placed?

