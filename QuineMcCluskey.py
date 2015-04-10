# Tufts University EE26 Project
# Written by: Ryan Dougherty

# ==================Imports======================
import sys
from math import log, pow, ceil

# ==================Classes======================
class Terms():
	def __init__(self):
		self.minterms = []
		self.dontcares = []

	def __str__(self):
		return "Minterms: " + str(self.minterms).replace('[','').replace(']','').replace("'",'') + "\nDon't Cares: " + str(self.dontcares).replace('[','').replace(']','').replace("'",'')

	def __repr__(self):
		return self.__str__()

# Group of Binary Terms Organized by number of 1's that can be marked or unmarked
class BinaryGroup():
	def __init__(self):
		self.members = []
		self.marked = []
		self.numOnes = 0

	def __str__(self):
		output = ""
		for member in self.members:
			output = output + ("+" if self.marked[self.members.index(member)] else "-") + member + " "
		return str(self.numOnes)+ ": " + output[:-1]

	def __repr__(self):
		return self.__str__()

class Cube():
	def __init__(self):
		self.groups = []
		self.groupIndicies = {}

	def __str__(self):
		outstring = ""
		for index in sorted(self.groupIndicies):
		 	outstring += str(self.groups[self.groupIndicies[index]]) + '\n'
		return outstring[:-1]

	def __repr__(self):
		return self.__str__()

	def sortGroups(self):
		newGroups = []
		newGroupIndicies = {}
		counter = 0
		for index in sorted(self.groupIndicies):
			newGroups.append(self.groups[self.groupIndicies[index]])
			newGroupIndicies[index] = counter
			counter += 1

		self.groups = newGroups
		self.groupIndicies = newGroupIndicies

class PI_Table():
	def __init__(self):
		self.PIs = []
		self.minterms = []

		self.coveredBy = {}
		self.EPIs = []

	def calcEPIs(self):
		if len(self.minterms):
			maximum = max(map(lambda x:len(convertToBinary(x)),self.minterms))

			for minterm in self.minterms:
				binary = convertToBinary(int(minterm),maximum=maximum)
				self.coveredBy[binary] = []
				for PI in self.PIs:
					if isCovered(binary,PI):
						self.coveredBy[binary].append(PI)
				if len(self.coveredBy[binary]) == 1:
					if not self.coveredBy[binary][0] in self.EPIs:
						self.EPIs.append(self.coveredBy[binary][0])
					
	def removeCovered(self):
		if len(self.minterms):
			toRemove = []
			maximum = max(map(lambda x:len(convertToBinary(x)),self.minterms))
			for minterm in self.minterms:
				binary = convertToBinary(int(minterm),maximum=maximum)
				for EPI in self.EPIs:
					if EPI in self.coveredBy[binary]:
						if minterm not in toRemove:
							toRemove.append(minterm)

			for minterm in toRemove:
				self.minterms.remove(minterm)
				del(self.coveredBy[convertToBinary(int(minterm),maximum=maximum)])

	def __str__(self):
		return "PIs: " + str(self.PIs) + "\n" + "Minterms: " + str(self.minterms) + "\n" + "coveredBy: " + str(self.coveredBy) + "\n" + "EPIs: " + str(self.EPIs) 

	def __repr__(self):
		return self.__str__()

class CloseCover():
	def __init__(self):
		self.PIs = []

	def __str__(self):
		return ""
	def __repr__(self):
		return self.__str__()

# =================Functions=====================
# Parsing Input
def readInput():
	inFile = sys.argv[1]
	f = open(inFile, 'r')
	for line in f:
		parseInput(line)
	return

def parseInput(input):
	length = len(InputTerms)

	inputTerm = Terms()

	parsedInput = input.replace('(','').replace('m','').replace(')','').replace('+','').replace(' ','').replace('\n','').split('d')

	if len(parsedInput) > 0:
		inputTerm.minterms.append(parsedInput[0].split(','))

	if len(parsedInput) > 1:
		inputTerm.dontcares.append(parsedInput[1].split(',')) 

	InputTerms.append(inputTerm)


def convertToBinary(input,maximum=None):
	if maximum is None:
		return "{:0b}".format(int(input))
	else:
		return ("{:0%db}"%int(maximum)).format(input)
		

def generateZeroCube(input):
	Zero = Cube()
	maximum = max(map(lambda x:len(convertToBinary(x)),input))

	for number in input:

		binary = convertToBinary(int(number),maximum=maximum)
		numOnes = binary.count('1')
		isInDatastructure = False

		for group in Zero.groups:
			# check to see if the number is already in the datastructure
			if binary in group.members:
				isInDatastructure = True

		if not isInDatastructure:
			# Check to see if there is an existing index for the binary group
			if numOnes in Zero.groupIndicies:
				# Check to see if the binary group already exists within the Cube
				if Zero.groups[Zero.groupIndicies[numOnes]]:
					# Add the new number to the existing binary group
					Zero.groups[Zero.groupIndicies[numOnes]].members.append(binary)
					Zero.groups[Zero.groupIndicies[numOnes]].marked.append(False)
			else:
				# Add the index of the new group to the index dictionary
				Zero.groupIndicies[numOnes] = len(Zero.groups)

				# Make the new Binary Group with the binary number
				newGroup = BinaryGroup()
				newGroup.members.append(binary)
				newGroup.marked.append(False)
				newGroup.numOnes = numOnes
				# Append the new group
				Zero.groups.append(newGroup)
				
	return Zero

def generateNextCube(previousCube):
	previousCube.sortGroups()
	counter = 0

	nextCube = Cube()

	inputs = []
	numberOfOnes = []

	# Compare each number with the group below it
	for i in range(len(previousCube.groups)-1):
		for j in range(len(previousCube.groups[i].members)):
			for k in range(len(previousCube.groups[i+1].members)):
				# Assign the numbers
				num1 = previousCube.groups[i].members[j]
				num2 = previousCube.groups[i+1].members[k]
				reduction = compareValues(num1,num2)

				if reduction != "":
					# Mark the numbers if they can be reduced
					previousCube.groups[i].marked[j] = True
					previousCube.groups[i+1].marked[k] = True
					if not reduction in inputs:
						inputs.append(reduction)
						numberOfOnes.append(previousCube.groups[i].numOnes)

	counter = 0
	for number in inputs:
		numOnes = numberOfOnes[counter]
		isInDatastructure = False

		for group in nextCube.groups:
			# check to see if the number is already in the datastructure
			if number in group.members:
				isInDatastructure = True

		if not isInDatastructure:
			# Check to see if there is an existing index for the binary group
			if numOnes in nextCube.groupIndicies:
				# Check to see if the binary group already exists within the Cube
				if nextCube.groups[nextCube.groupIndicies[numOnes]]:
					# Add the new number to the existing binary group
					nextCube.groups[nextCube.groupIndicies[numOnes]].members.append(number)
					nextCube.groups[nextCube.groupIndicies[numOnes]].marked.append(False)
			else:
				# Add the index of the new group to the index dictionary
				nextCube.groupIndicies[numOnes] = len(nextCube.groups)

				# Make the new Binary Group with the binary number
				newGroup = BinaryGroup()
				newGroup.members.append(number)
				newGroup.marked.append(False)
				newGroup.numOnes = numOnes
				# Append the new group
				nextCube.groups.append(newGroup)

		counter += 1

	if len(nextCube.groups):
		return nextCube
	else:
		return None

				

def compareValues(num1,num2):
	numberOfDifferences = 0
	output = ""
	for i in range (len(num1)):
		if num1[i] != num2[i]:
			output += 'X'
			numberOfDifferences += 1
		else:
			output += num1[i]

	if numberOfDifferences == 1:
		return output
	else:
		return ""

def isCovered(number, PI):
	covered = True
	for i in range(len(number)):
		if (PI[i] != number[i]) and (PI[i] != 'X'):
			covered = False
	return covered

def findPrimeImplicants():

	for term in InputTerms:
		Cubes = []
		PIs = []

		zeroSeed = list(str(term.minterms+term.dontcares).replace('[','').replace(']','').replace("'",'').replace(' ','').split(','));
	
		if len(zeroSeed[0]) == 0:
			return
		
		Zero = generateZeroCube(list(str(term.minterms+term.dontcares).replace('[','').replace(']','').replace("'",'').replace(' ','').split(',')))
		nextCube = generateNextCube(Zero)

		Cubes.append(Zero)
		Cubes.append(nextCube)

		while(nextCube!= None):
			Cubes.append(nextCube)
			oldCube = nextCube
			nextCube = generateNextCube(nextCube)

		for cube in Cubes:
			for group in cube.groups:
				for i in range(len(group.marked)):
					if not group.marked[i]:
						if not group.members[i] in PIs:
							PIs.append(group.members[i])

		PrimeImplicants.append(PIs)
			
def findEssentialPrimeImplicants():
	for i in range(len(PrimeImplicants)):
		PIs = PrimeImplicants[i]
		term = InputTerms[i]

		Table = PI_Table()
		Table.PIs = PIs
		Table.minterms = str(term.minterms).replace('[','').replace(']','').replace("'",'').replace(' ','').split(',')
		if (Table.minterms[0]) =='':
			return
		Table.calcEPIs()
		Table.removeCovered()

		PI_Tables.append(Table)
		EssentialPrimeImplicants.append(Table.EPIs)

def removeAllDominated():
	for i in range(len(PI_Tables)):
		removeDominated(i)

# removes all PIs that are completely dominated by other PIs, then recalculates the table and repeats
# terminates when the PIs are the same before and after
def removeDominated(i):
	PI_Before = []
	while PI_Before != PrimeImplicants:
		PI_Before = PrimeImplicants 
		covers = {}
		for minterm in PI_Tables[i].minterms:
			key = convertToBinary(int(minterm),maximum=len(PI_Tables[i].coveredBy.keys()[0]))
			for PI in PI_Tables[i].coveredBy[key]:
				covers.setdefault(PI, []).append(key)
		toRemove = []
		for PI in covers:
			firstTerms = covers[PI]
			for PI_2 in covers:
				secondTerms = covers[PI_2]
				if(PI != PI_2):
					if(set(secondTerms).issubset(firstTerms)):
						if(firstTerms != secondTerms):
							if(not PI_2 in toRemove):
								toRemove.append((PI_2))
		for PI in toRemove:			
			for minterm in PI_Tables[i].coveredBy:
				if PI in PI_Tables[i].coveredBy[minterm]:
					PI_Tables[i].coveredBy[minterm].remove(PI)
			PI_Tables[i].PIs.remove(PI)
		if(len(PI_Tables[i].minterms) == 0):
			PI_Tables[i].calcEPIs()
			PI_Tables[i].removeCovered()

def petricksMethod():
	# Find the prime implicants that cover the remaining minterms
	for i in range(len(PI_Tables)):
		# make a dictionary of minterms keyed by PI
		covers = {}
		
		for minterm in PI_Tables[i].minterms:
			key = convertToBinary(int(minterm),maximum=len(PI_Tables[i].coveredBy.keys()[0]))
			for PI in PI_Tables[i].coveredBy[key]:
				covers.setdefault(PI, []).append(key)

		# Find the path with the least loss
 		Costs = recurse(covers, PI_Tables[i])
 		if(Costs[1] != []):
 			for implicant in Costs[1]:
 				EssentialPrimeImplicants[i].append(implicant)

def recurse(covers, Table):
	if (not len(covers)):
		return [0,[]]

	newCost = 0
	costs = []
	nexts = []
	# Select a PI from the remaining PI's
	for PI in covers:
		branch = []
		next = []
		
		newTable = PI_Table()
		newTable.minterms = list(Table.minterms)
		newTable.coveredBy = Table.coveredBy.copy()

		# remove the minterms covered by the PI
		for minterm in covers[PI]:
			if (str(int(minterm,2))) in newTable.minterms:
				newTable.minterms.remove((str(int(minterm,2))))
				if minterm in newTable.coveredBy:
					del(newTable.coveredBy[minterm])
		if not newTable.minterms:
			return [len(PI) - PI.count("X"), PI]

		newCovers = covers.copy()
		del(newCovers[PI])

		newCost = float("inf")
		branches = [recurse(newCovers, newTable)]
		
		for branch in branches:
			if branch[0] < newCost:
				newCost = branch[0]
				next = [branch[1], PI]

		costs.append(newCost + len(PI) - PI.count("X"))
		nexts.append(next)
	
	min_cost = float("inf")
	for i in range(len(costs)):
		
		if costs[i] < min_cost:
			min_cost = costs[i]
			next = nexts[i]

	return [min_cost,next]
		

def printResults():

	# print "\n\nPRINTING RESULTS"
	# for i in range(len(InputTerms)):
		# print "\nINPUT:"
		# print InputTerms[i]
		# print "\nTABLE"
		# print PI_Tables[i]
		# print "\nPRIME IMPLICANTS:"
		# print PrimeImplicants[i]
		# print "\nESSENTIAL PRIME IMPLICANTS:"
		# print EssentialPrimeImplicants[i]
	print "Sum of Products"
	for j in range(len(PrimeImplicants)):
		output = ""
		for implicant in PrimeImplicants[j]:
			if implicant != "X":
				for i in range(len(implicant)):
					if implicant[i] == "0":
						output += chr(65 + i) + "'" 
					if implicant[i] == "1":
						output += chr(65 + i)
				output += "+"
		print output[:-1]
	
# ==================Minterms=====================
def findMinTerms():
	findPrimeImplicants()
	findEssentialPrimeImplicants()
	removeAllDominated()
	petricksMethod()
	printResults()

# ================Maxterms=======================
def createMaxTerms():
	for i in range(len(InputTerms)):
		if len(InputTerms[i].dontcares) > 0:
			part1 = list(map(lambda x : log(int(x),2) if int(x) != 0 else None, InputTerms[i].minterms[0]))
			part2  = list(map(lambda x : log(int(x),2) if int(x) != 0 else None, InputTerms[i].dontcares[0]))
			base = int(ceil(max(part1+part2)))
			MaxTerms.append(list(set(range(int(ceil(pow(2,base))))) - set(map(lambda x : int(x),InputTerms[i].minterms[0])) - set(map(lambda x : int(x),InputTerms[i].dontcares[0]))))
		else:
			base = int(ceil(max(list(map(lambda x : log(int(x),2) if int(x) != 0 else None, InputTerms[i].minterms[0])))))
			MaxTerms.append(list(set(range(int(ceil(pow(2,base))))) - set(map(lambda x : int(x),InputTerms[i].minterms[0]))))	

def printMaxTerms():
	print "Product of Sums"
	for j in range(len(PrimeImplicants)):
		output = ""
		for implicant in PrimeImplicants[j]:
			if implicant != "X":
		
				output += "("
				for i in range(len(implicant)):
					if implicant[i] == "0":
						output += chr(65 + i) + "+"
					if implicant[i] == "1":
						output += chr(65 + i) + "'+"
				output = output[:-1] + ")"
				
				if (implicant.count("0")==1 and implicant.count("1")==0) or (implicant.count("0")==0 and implicant.count("1")==1):
					if output[-3:][1] == "'":
						output = output[:-4] + output[-4:][1] + "'"
					else:
						output = output[:-3] + output[-3:][1]
					
		print output

def findMaxTerms():
	for i in range(len(MaxTerms)):
		del InputTerms[i].minterms
		InputTerms[i].minterms = [list(map(lambda x : str(x),sorted(MaxTerms[i])))]
	findPrimeImplicants()
	
	findEssentialPrimeImplicants()
	removeAllDominated()
	petricksMethod()
	printMaxTerms()

def clearVariables():
	del PrimeImplicants[:]
	del EssentialPrimeImplicants[:]
	del PI_Tables[:]
	
# ===============Global Variables================
InputTerms = []
PrimeImplicants = []
EssentialPrimeImplicants = []
PI_Tables = []
MaxTerms = []

# 'Main'
readInput()
findMinTerms()

clearVariables()

createMaxTerms()
findMaxTerms()



