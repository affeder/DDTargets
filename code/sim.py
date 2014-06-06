#!/usr/bin/python
import numpy
import math
import argparse


parser = argparse.ArgumentParser(description='Model DDT populations')

#parser.add_argument('Number of cells', metavar='N', type=int, nargs='+',
#                   help='Number of cells in a generation')

parser.add_argument('-N', '--NUMCELLS', default = 500, help='Number of cells in each generation', type = int)
parser.add_argument('-f', '--FREQUENCY', default = .5, help='Initial frequency of DR viral strains', type = int)
parser.add_argument('-MOI',  default = 5, help='Initial MOI of infection', type = int)
parser.add_argument('-r', '--RATE', default = 100, help='Number of capsid proteins produced per viral particle', type = int)
parser.add_argument('-c', '--CAPSIDSIZE', default = 60, help='Number of capsid proteins per capsid', type = int)
parser.add_argument('-l', '--LENGTH', default = 10, help='Number of generations the simulation should run', type = int)

args = parser.parse_args()

print "#", args

class Cell:
    'Common base class for all cells'
    numCells = 0

    def __init__(self):
        self.virus_list = []
        self.numCaps = [0,0]
        self.capsid_list = []
        
    def displayCount(self):
        print "Total cells %d" % Cell.numCells

    def displayEmployee(self):
        print "Name : ", self.name,  ", Salary: ", self.salary

    def addVirusPopulation(self, num, resistanceProportion):
        s = numpy.random.binomial(1, resistanceProportion, num)
        for i in range(num) :
            self.virus_list.append(Virus(s[i]))

    def addVirion(self, resist):
#        print "infected by ", resist
        self.virus_list.append(Virus(resist))
        
    def printViruses(self):
        for obj in self.virus_list :
            obj.displayVirus()

    def produceCapsidProtein(self):
        for obj in self.virus_list :
            self.numCaps[ obj.resist] = self.numCaps[ obj.resist] + obj.produce()
    
    def passNumCaps(self):
        return self.numCaps

    def assembleCapsids(self):
        while(sum(self.numCaps) > args.CAPSIDSIZE):

            self.capsid_list.append(Capsid(self))

#        for obj in self.capsid_list :
#            print obj

    def infect_all(self, cell):

        self.samp = numpy.random.random_integers(low = 0, high =max(0, len(self.capsid_list)-1), size = len(self.virus_list))

        for i in range(len(self.virus_list)):

#            print "considering..."
#            print self.capsid_list[self.samp[i]].capsType

            if self.capsid_list[self.samp[i]].willSurvive():

                cell.addVirion(self.virus_list[i].resist)
#                print "survival", self.virus_list[i].resist
#            else:
#                print "death"

    def infect(self, cell):
        #choose a random capsid created by the cell
        self.samp = numpy.random.random_integers(low = 0, high =max(0, len(self.capsid_list)-1), size = 1)

        #If the capsid can survive the drug
        if self.capsid_list[self.samp].willSurvive():

            #Choose the strain to be inside the capsid
            self.tmp = numpy.random.random_integers(low = 0, high =max(0, len(self.virus_list)-1), size = 1)
            
            #Add the strain inside the capsid to the target cell
            cell.addVirion(self.virus_list[self.tmp].resist)

        #Remove the capsid
        self.capsid_list.pop(self.samp)
        

    def __str__(self):
        return " ".join(["Cell is infected with", str(len(self.virus_list)),"Capsid length is",str(len(self.capsid_list))])

    
class Capsid:

    def __init__(self, Host):
        #print Host.numCaps;

        self.capsType = [0,0]
        while(sum(self.capsType) < args.CAPSIDSIZE):
            self.tmp = self.fill(Host)
#            self.capsType[self.tmp] = self.capsType[self.tmp] +1
            
    def fill(self, Host):
        if(sum(Host.numCaps) > 0):
            self.val = numpy.random.binomial(1, 1- (Host.numCaps[0])/sum(Host.numCaps), 1)

            Host.numCaps[self.val] = Host.numCaps[self.val] -1
            self.capsType[self.val] = self.capsType[self.val] +1

    def __str__(self):
        return "-".join(str(x) for x in self.capsType)

    def willSurviveOld(self):
        if self.capsType[0] < threshold:
            return 1
        else:
            return 0

    def willSurvive(self):
        self.surviveprob = 1-self.capsType[0]/args.CAPSIDSIZE
        if numpy.random.binomial(1, self.surviveprob, 1) == 1:
            return 1
        else:
            return 0
        
class Virus:

    def __init__(self, resistance):
        self.resist = resistance
    
    def displayVirus(self):
        print "Resistance status:", self.resist

    def produce(self):
        return math.ceil(numpy.random.normal(args.RATE + mult* self.resist, 1, 1)[0])

class Culture:

    def __init__(self, size, numViruses, resistProp):
        self.cellPop = []
        self.numViruses = numViruses
        self.resistProp = resistProp
        for i in range(size):
            self.cellPop.append(Cell())

    def transfer(self, culture):

        for startCell in self.cellPop:

#            print "Infecting with ", startCell
            
            while(len(startCell.capsid_list) > 0):

                index = numpy.random.random_integers(low = 0, high =max(0, (culture.numCells()-1)), size = 1)
                                                     
                startCell.infect(culture.cellPop[index])
#                print "Infected Cell: ", index, "\n", culture.cellPop[index]


    def numCells(self):
#        print len(self.cellPop)
        return len(self.cellPop)
    
    def initialize(self):

        for cell in self.cellPop:
            cell.addVirusPopulation(self.numViruses, self.resistProp)

    def makeCapsidProtein(self):

        for cell in self.cellPop:
            cell.produceCapsidProtein()

    def makeCapsids(self):

        for cell in self.cellPop:
            cell.assembleCapsids()

    def printAll(self):
        for cell in self.cellPop:
            print cell

    def summary(self):
        self.numViruses = []
        self.resistStats = []
        self.capsidStats = []
        self.capsidResist = []
        for cell in self.cellPop:
            self.numViruses.append(len(cell.virus_list))
            self.tmp = 0
            for virus in cell.virus_list:
                if(virus.resist == 1):
                    self.tmp = self.tmp +1
            self.resistStats.append(self.tmp)
            self.capsidStats.append(len(cell.capsid_list))

            self.tmp = []
            for capsid in cell.capsid_list:
                self.tmp.append(capsid.capsType[0])
            if(len(self.tmp) == 0):
                self.tmp = [0]
            self.capsidResist.append(numpy.mean(self.tmp))

#        print " ".join(["Avg Virus/cell:", str(numpy.mean(self.numViruses)),"\nResist viruses/cell:", str(numpy.mean(self.resistStats)),"\nAvg numCapsids/cell:",str(numpy.mean(self.capsidStats)), "\nAvg WT proteins/capsid:", str(numpy.mean(self.capsidResist))])

        print "\t".join([str(numpy.mean(self.numViruses)), str(numpy.mean(self.resistStats)),str(numpy.mean(self.capsidStats)), str(numpy.mean(self.capsidResist))])


mult = 0
threshold = 45


initPop = Culture(args.NUMCELLS, args.MOI, args.FREQUENCY)
initPop.initialize()
initPop.makeCapsidProtein()
initPop.makeCapsids()
initPop.summary()

for i in range(args.LENGTH):

    newCulture = Culture(1000, 0, 0)
    initPop.transfer(newCulture)
    newCulture.makeCapsidProtein()
    newCulture.makeCapsids()
    newCulture.summary()
    initPop = newCulture

