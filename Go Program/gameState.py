
########    gameState    ########

import copy
from constants import *


#Adding stones must only be done through makeMove
#In paticular, group constructor assumes only one stone is in the new group
#Removing stones through captureGroup


class group(object): #Group of solidly connected stones
    def __init__(self, stones, colour):
        self.colour = colour
        self.stones = stones #list of tuples
        self.length = len(stones)
        self.liberties = 4
        self.merged = False #should not be touched after this is set to True
        self.left = self.stones[0][0] #assume only one stone when initialised! 
        self.right = self.stones[0][0]
        self.top = self.stones[0][1]
        self.bottom = self.stones[0][1]
        self.toCapture = set()
        self.toEscape = set()
        
 

    def removeLiberties(self, n):
        self.liberties-=n

class gameState(object):  #Contains game state, methods for updating, and methods that return board information
    def __init__(self):
        self.boardSize=9
        self.board=[[-1 for i in range(0, self.boardSize)]for j in range(0, self.boardSize)]
        self.groups=[]
        self.move=BLACK
        self.noOfGroups=0
        self.komi=6
        self.blackName='Alice'
        self.whiteName='Bob'
        self.blackStonesCaptured=0
        self.whiteStonesCaptured=0
        self.history=[]
        self.interestingGroups=set() #Updated after makeMove - set of groups made interesting by the current move
        self.justMergedGroups=set() #Updated after makeMove - groups merged into group number noOfGroups-1
        

    #Public methods
    
    def makeMove(self,  i,  j,  internal=True): #Implements mechanics of making move: captures, ko, groups, history. Internal means used for playouts - don't write to SGF etc
        if self.isLegalMove(i, j)==False: #(-10,-10) is illegal move marker
            return (-10,-10)
        
                
        self.interestingGroups=set()
        self.justMergedGroups=set()
        if i==-1 and j==-1: #(-1,-1) is a pass move
            self.makePass(internal)
            return (-1,-1)
        #legal move, not suicide
        self.groups.append(group([(i,j)],self.move)) #add group (to be merged later)
        self.board[i][j]=self.noOfGroups #add group to board
        #self.colourBoard[playerNumber(self.move)][i][j]=1 #add stone to colourBoard board
        
        
        #Remove ko markers IMPLEMENT - add this region to iinterestingGroups
        for a in range(0,self.boardSize):
            for b in range(0,self.boardSize):
                if self.board[a][b]==-2:
                    self.board[a][b]=-1
        
        totalCaptured=0
        for item in self.adjEnemyGroups(i,j,self.move):
            if self.groups[item].liberties==1:
                totalCaptured+=self.groups[item].length
                self.interestingGroups|=set(self.touchingGroups(item)) #add groups surrounding captures to interestingGroups
                self.captureGroup(item)
                
            else:
                self.groups[item].removeLiberties(1)

        for item in self.adjSameGroups(i,j,self.move):
            totalCaptured=0 #Going to check totalCaptures==1 next, for ko - set to 0 if played stone is not alone
            self.mergeGroups(item, self.noOfGroups)
            self.justMergedGroups.add(item)

        if totalCaptured==1: #then have captured exactly one, and not adjacent to same-colour stones
            self.recalculateLiberties(self.noOfGroups)
            assert self.groups[self.noOfGroups].liberties!=0, 'Suicide somehow allowed.'
            if self.groups[self.noOfGroups].liberties==1: #then ko!
                for pos in self.adjPoints(i,j):
                    if self.board[pos[0]][pos[1]]==-1:
                        self.board[pos[0]][pos[1]]=-2 #put in ko marker

        
        
       
        for (a, b) in self.pointsInEuclideanRadius(i, j, 3): #Add interesting groups just for being near played stone
            if self.board[a][b]>=0:
                self.interestingGroups.add(self.board[a][b])
        
        for x in self.touchingGroups(self.board[i][j]): #add interesting group for being adjacent to the group just merged (might be a long way away)
            self.interestingGroups.add(x)
       
        for k in self.interestingGroups:
            if self.groups[k].merged==False:
                self.recalculateLiberties(k)
        
        self.noOfGroups+=1
        self.incrementMove()
        self.history.append((i, j))
        return (i,j)
    
    def isLegalMove(self, i, j,): #returns true/false. 
        #NB avoids calling expensive resultingLiberties function
        if i==-1 and j==-1: #(-1,-1) is a pass move
            return True
        if i<0 or j<0:
            return False
        if self.board[i][j]!=-1: #if board not empty there
            return False
        #check for suicide        
        gotSpace=False
        for pos in self.adjPoints(i,j):
            if self.board[pos[0]][pos[1]]<0 or (self.groups[self.board[pos[0]][pos[1]]].colour==self.move and self.groups[self.board[pos[0]][pos[1]]].liberties>1) or (self.groups[self.board[pos[0]][pos[1]]].colour!=self.move and self.groups[self.board[pos[0]][pos[1]]].liberties==1):
                gotSpace=True
        return gotSpace
    
    #---
    def adjPoints(self,  i,  j): #returns list of tuples
        assert i>=0,  'Computing adjacent points to pass move or non-move'
        listOfPoints=[]
        if i>0:
            listOfPoints.append((i-1,j))
        if j>0:
            listOfPoints.append((i,j-1))
        if i<self.boardSize-1:
            listOfPoints.append((i+1,j))
        if j<self.boardSize-1:
            listOfPoints.append((i,j+1))
        return listOfPoints

    
    def diagPoints(self,  i,  j): #returns list of tuples
        assert i>=0,  'Computing diagonal points to pass move or non-move'
        listOfPoints=[]
        if i>0 and j>0:
            listOfPoints.append((i-1,j-1))
        if i>0 and j<self.boardSize-1:
            listOfPoints.append((i-1,j+1))
        if j>0 and i<self.boardSize-1:
            listOfPoints.append((i+1,j-1))
        if i<self.boardSize-1 and j<self.boardSize-1:
            listOfPoints.append((i+1,j+1))
        return listOfPoints
    
    
    def adjDiagPoints(self,  i,  j): # returns list of tuples
        assert i>=0,  'Computing neighbours to pass move or non-move'
        listOfPoints=[]
        listOfPoints.extend(self.adjPoints(i, j))
        listOfPoints.extend(self.diagPoints(i, j))
        return listOfPoints
    
    def adjGroups(self,  i,  j): #returns list of index numbers
        neighbours=[]
        for point in self.adjPoints(i,j):
            if self.board[point[0]][point[1]]>=0:
                neighbours.append(self.board[point[0]][point[1]])
        return condenseList(neighbours)
    
    def diagGroups(self,  i,  j): #returns index numbers
        neighbours=[]
        for point in self.diagPoints(i,j):
            if self.board[point[0]][point[1]]>=0:
                neighbours.append(self.board[point[0]][point[1]])
        return condenseList(neighbours)
    
    def adjDiagGroups(self,  i,  j): #returns index numbers
        neighbours=[]
        for point in self.adjDiagPoints(i,j):
            if self.board[point[0]][point[1]]>=0:
                neighbours.append(self.board[point[0]][point[1]])
        return condenseList(neighbours)
    
    def adjSameGroups(self,  i,  j,  colour=None): #returns index numbers
        colour = colour or self.move
        neighbours=[]
        for point in self.adjPoints(i,j):
            if self.board[point[0]][point[1]]>=0 and self.groups[self.board[point[0]][point[1]]].colour==colour:
                neighbours.append(self.board[point[0]][point[1]])
        return condenseList(neighbours)
    
    def diagSameGroups(self,  i,  j,  colour=None): #returns index numbers
        colour=colour or self.move
        neighbours=[]
        for point in self.diagPoints(i,j):
            if self.board[point[0]][point[1]]>=0 and self.groups[self.board[point[0]][point[1]]].colour==colour:
                neighbours.append(self.board[point[0]][point[1]])
        return condenseList(neighbours)
    
    def adjDiagSameGroups(self,  i,  j,  colour=None): #returns index numbers
        colour = colour or self.move
        neighbours=[]
        for point in self.adjDiagPoints(i,j):
            if self.board[point[0]][point[1]]>=0 and self.groups[self.board[point[0]][point[1]]].colour==colour:
                neighbours.append(self.board[point[0]][point[1]])
        return condenseList(neighbours)

    def adjEnemyGroups(self,  i,  j,  colour=None): #returns index numbers
        colour = colour or self.move
        neighbours=[]
        for point in self.adjPoints(i,j):
            if self.board[point[0]][point[1]]>=0 and self.groups[self.board[point[0]][point[1]]].colour!=colour:
                neighbours.append(self.board[point[0]][point[1]])
        return condenseList(neighbours)

    
    def diagEnemyGroups(self,  i,  j,  colour=None): #returns index numbers
        colour = colour or self.move
        neighbours=[]
        for point in self.diagPoints(i,j):
            if self.board[point[0]][point[1]]>=0 and self.groups[self.board[point[0]][point[1]]].colour!=colour:
                neighbours.append(self.board[point[0]][point[1]])
        return condenseList(neighbours)
    
    def adjDiagEnemyGroups(self,  i,  j,  colour=None): #returns index numbers
        colour = colour or self.move
        neighbours=[]
        for point in self.adjDiagPoints(i,j):
            if self.board[point[0]][point[1]]>=0 and self.groups[self.board[point[0]][point[1]]].colour!=colour:
                neighbours.append(self.board[point[0]][point[1]])
        return condenseList(neighbours)

  
    def adjLiberties(self,  i,  j,  emptySpaces=[-1, -2]): #returns tuples
        neighbours=[]
        for (i, j) in self.adjPoints(i,j):
            if self.board[i][j] in emptySpaces:
                neighbours.append((i, j))
        return neighbours

    def diagLiberties(self,  i,  j,  emptySpaces=[-1, -2]): #returns tuples
        neighbours=[]
        for (i, j) in self.diagPoints(i,j):
            if self.board[i][j] in emptySpaces:
                neighbours.append((i, j))
        return neighbours
    
    def adjDiagLiberties(self,  i,  j,  emptySpaces=[-1, -2]): #returns tuples
        neighbours=[]
        for (i, j) in self.adjDiagPoints(i,j):
            if self.board[i][j] in emptySpaces:
                neighbours.append((i, j))
        return neighbours
    
    def adjSamePoints(self,  i,  j,  colour=None): #returns tuples
        colour=colour or self.move
        neighbours=[]
        for point in self.adjPoints(i,j):
            if self.board[point[0]][point[1]]>=0 and self.groups[self.board[point[0]][point[1]]].colour==colour:
                neighbours.append((point[0], point[1]))
        return neighbours
    
    def diagSamePoints(self,  i,  j,  colour=None): #returns tuples
        colour=colour or self.move
        neighbours=[]
        for point in self.diagPoints(i,j):
            if self.board[point[0]][point[1]]>=0 and self.groups[self.board[point[0]][point[1]]].colour==colour:
                neighbours.append((point[0], point[1]))
        return neighbours
    
    def adjDiagSamePoints(self,  i,  j,  colour=None): #returns tuples
        colour = colour or self.move
        neighbours=[]
        for point in self.adjDiagPoints(i,j):
            if self.board[point[0]][point[1]]>=0 and self.groups[self.board[point[0]][point[1]]].colour==colour:
                neighbours.append((point[0], point[1]))
        return neighbours

    def adjEnemyPoints(self,  i,  j,  colour=None): #returns tuples
        colour=colour or self.move
        neighbours=[]
        for point in self.adjPoints(i,j):
            if self.board[point[0]][point[1]]>=0 and self.groups[self.board[point[0]][point[1]]].colour!=colour:
                neighbours.append((point[0], point[1]))
        return neighbours
    
    def diagEnemyPoints(self,  i,  j,  colour=None): #returns tuples
        colour = colour or self.move
        neighbours=[]
        for point in self.diagPoints(i,j):
            if self.board[point[0]][point[1]]>=0 and self.groups[self.board[point[0]][point[1]]].colour!=colour:
                neighbours.append((point[0], point[1]))
        return neighbours
    
    def adjDiagEnemyPoints(self,  i,  j,  colour=None): #returns tuples
    
        colour = colour or self.move
        neighbours=[]
        for point in self.adjDiagPoints(i,j):
            if self.board[point[0]][point[1]]>=0 and self.groups[self.board[point[0]][point[1]]].colour!=colour:
                neighbours.append((point[0], point[1]))
        return neighbours
        
    # ---
    def touchingLiberties(self,  group,  emptySpaces=[-1, -2]): # returns tuples of adjacent liberties to group
        listOfLiberties=[]
        for stone in self.groups[group].stones:
            for pos in self.adjPoints(stone[0], stone[1]):
                if self.board[pos[0]][pos[1]] in emptySpaces:
                    listOfLiberties.append((pos[0], pos[1]))
        return condenseList(listOfLiberties)
    
    def diagTouchingLiberties(self,  group,  emptySpaces=[-1, -2]): # returns tuples of diagonal liberties to group
        listOfLiberties=[]
        for stone in self.groups[group].stones:
            for pos in self.diagPoints(stone[0], stone[1]):
                if self.board[pos[0]][pos[1]] in emptySpaces:
                    listOfLiberties.append((pos[0], pos[1]))
        return list(set(listOfLiberties)-set(self.touchingLiberties(group,  emptySpaces)))

        
    def touchingStones(self,  group1,  group2): #return the number of stones in group 2 adjacent to group 1 (order important!)
        return self.touchingLiberties(group1,  [group2])

    def touchingGroups(self,  group): #returns group index numbers touching group
        listOfTouchingGroups=[]
        for stone in self.groups[group].stones:
            for pos in self.adjPoints(stone[0],stone[1]):
                if self.board[pos[0]][pos[1]]>=0:
                    listOfTouchingGroups.append(self.board[pos[0]][pos[1]])
        while group in listOfTouchingGroups:
            listOfTouchingGroups.remove(group)
        return condenseList(listOfTouchingGroups)
    
    def resultingLiberties(self, i, j, colour=None): #returns list of tuples: liberties a move at i,j would end up with. Possibly zero.
        colour = colour or self.move
        emptySpaces=[-2,-1]
        for group in self.adjEnemyGroups(i,j,colour):
            if self.groups[group].liberties==1:
                emptySpaces.append(group) #fill emptySpaces list with enemy groups that would be captured
        listOfLiberties=self.adjLiberties(i,j, emptySpaces)
        for group in self.adjSameGroups(i,j,colour):
            listOfLiberties.extend(self.touchingLiberties(group, emptySpaces))
        while (i,j) in listOfLiberties:
            listOfLiberties.remove((i,j))
        listOfLiberties=condenseList(listOfLiberties)
        return listOfLiberties
    def lenResultingLibertiesFromTuple(self, tuple): #needed for key sorting during move generation
        return len(self.resultingLiberties(tuple[0], tuple[1]))
    
    def mergeGroups(self,  a,  b):#merge groups a and b into group b
        for (i,j) in self.groups[a].stones:
            self.board[i][j]=b
        self.groups[b].stones.extend(self.groups[a].stones)
        self.groups[b].length=len(self.groups[b].stones)
        self.groups[a].merged=True
        self.groups[b].left=min(self.groups[a].left,  self.groups[b].left)
        self.groups[b].right=max(self.groups[a].right,  self.groups[b].right)
        self.groups[b].top=min(self.groups[a].top,  self.groups[b].top)
        self.groups[b].bottom=max(self.groups[a].bottom,  self.groups[b].bottom)
    
    
    # -- Stones within a certain distance
    def pointsInTaxicabRadius(self,  i,  j,  r): #returns set of points within a radius of r (taxicab metric) from point (i,j)
        points={(i, j)}
        for d in range(1, r+1):
            for k in range(d+1):
                if self.isOnBoard(i-d+k, j+k):
                    points.add((i-d+k, j+k))
                if self.isOnBoard(i-d+k, j-k):
                    points.add((i-d+k, j-k))
            for k in range(d):
                if self.isOnBoard(i+d-k, j+k):
                    points.add((i+d-k, j+k))
                if self.isOnBoard(i+d-k, j-k):
                    points.add((i+d-k, j-k))
        return points
    
    def libertiesInTaxicabRadius(self,  i,  j,  r): #returns set of points within a radius of r (taxicab metric) from point (i,j)
        points={(i, j)}
        for d in range(1, r+1):
            for k in range(d+1):
                if self.isOnBoard(i-d+k, j+k) and self.board[i-d+k][j+k]<0:
                    points.add((i-d+k, j+k))
                if self.isOnBoard(i-d+k, j-k) and self.board[i-d+k][j-k]<0:
                    points.add((i-d+k, j-k))
            for k in range(d):
                if self.isOnBoard(i+d-k, j+k) and self.board[i+d-k][j+k]<0:
                    points.add((i+d-k, j+k))
                if self.isOnBoard(i+d-k, j-k) and self.board[i+d-k][j-k]<0:
                    points.add((i+d-k, j-k))
        return points

    def pointsInEuclideanRadius(self,  i,  j,  r): #returns set of points within a radius of r (Euclidean metric) from point (i,j)
        points=set()
        for a in range(i-r, i+r+1):
            for b in range(j-r,  j+r+1):
                if self.isOnBoard(a, b) and (a-i)*(a-i)+(b-j)*(b-j)<=r*r:
                    points.add((a, b))
        return points
    
    def libertiesInEuclideanRadius(self,  i,  j,  r): #returns set of points within a radius of r (Euclidean metric) from point (i,j)
        points=set()
        for a in range(i-r, i+r+1):
            for b in range(j-r,  j+r+1):
                if self.isOnBoard(a, b) and self.board[a][b]<0 and (a-i)*(a-i)+(b-j)*(b-j)<=r*r:
                    points.add((a, b))
        return points
    
    def isOnBoard(self, i, j): #returns True if i,j is on board
        if i>=0 and j>=0 and i<self.boardSize and j<self.boardSize:
            return True
        else:
            return False
    
    #--- Pattern recognition
    # 1=colour 2=not-colour 4=liberty, no ko 8 =ko 16=edge 32=group1 64=group2 128=group3, 256=group4, 
    #-x is x-1 complement, so -2 is "not colour stone", -3 is "not enemy stone". That is, complement of n is -n-1. In particular, -1 is anything goes.
    def pattern3x3(self,pattern, i,j, colour, orientations={-4, -3, -2, -1, 1, 2, 3, 4},  verbose=False, markedGroups=[-1, -1, -1, -1]): #3x3 pattern matching
    #pattern is a 3x3 array of codes. Point (i,j) is where we hope the centre to be.
    #return set (possibly empty) of orientations that match (1=no rotation, 2,3,4 = rotate pattern anticlockwise), -1 to -4 for match after left-right flip then those rotations.
    #preprocess to remove symmetry - verbose returns all matches, default is just to return first match
        found=[[0 for b in range(3)]for a in range(3)]
        for a in range(-1, 2): #assign properties of point (i+a,j+b) to found[a+1][b+1]
            for b in range(-1, 2):
                if self.isOnBoard(i+a, j+b):
                    group=self.board[i+a][j+b]
                    if group==-1:
                        found[a+1][b+1]+=4 #liberty, no ko
                    elif group ==-2:
                        found[a+1][b+1]+=8 #ko liberty
                    else: #not empty point:
                        if self.groups[group].colour==colour:
                            found[a+1][b+1]+=1 #matching colour stone
                        else:
                            found[a+1][b+1]+=2 #non-matching colour
                        for n in range(4):
                            if markedGroups[n]!=-1 and group==markedGroups[n]: #group1 through group4
                                found[a+1][b+1]+=2**(n+5)
                else:
                    found[a+1][b+1]+=16 #add for edge of board
        
        hits=set()
        for orientation in orientations: #detect whether each orientation matches
            f=found[:]
            #Rotate found clockwise; equivalent to matching pattern rotated anticlockwise
            if orientation==3 or orientation==-3:
                f=[f[2][::-1],  f[1][::-1],  f[0][::-1]]
            elif orientation==4 or orientation==-4:
                f=[[f[2][0],  f[1][0], f[0][0]], [f[2][1], f[1][1], f[0][1]], [f[2][2], f[1][2], f[0][2]]]
            elif orientation==2 or orientation==-2:
                f=[[f[0][2], f[1][2], f[2][2]], [f[0][1], f[1][1], f[2][1]], [f[0][0], f[1][0], f[2][0]]]
                
            if orientation<0: #flip columns
                f=f[::-1]
                
            if self.bitMatch(pattern,  f):
                if verbose==True:
                    hits.add(orientation)
                else:
                    return {orientation}
        return hits
    
    
    def pattern5x5(self,pattern, i,j, colour, orientations={-4, -3, -2, -1, 1, 2, 3, 4},  verbose=False, markedGroups=[-1, -1, -1, -1],  debug=False): #5x5 pattern matching
    #pattern is a 5x5 array of codes. Point (i,j) is where we hope the centre to be.
    #return set (possibly empty) of orientations that match (1=no rotation, 2,3,4 = rotate pattern anticlockwise), -1 to -4 for match after left-right flip then those rotations.
    #preprocess to remove symmetry - verbose returns all matches, default is just to return first match
        found=[[0 for b in range(5)]for a in range(5)]
        for a in range(-2, 3): #assign properties of point (i+a,j+b) to found[a+1][b+1]
            for b in range(-2, 3):
                if self.isOnBoard(i+a, j+b):
                    group=self.board[i+a][j+b]
                    if group==-1:
                        found[a+2][b+2]+=4 #liberty, no ko
                    elif group ==-2:
                        found[a+2][b+2]+=8 #ko liberty
                    else: #not empty point:
                        if self.groups[group].colour==colour:
                            found[a+2][b+2]+=1 #matching colour stone
                        else:
                            found[a+2][b+2]+=2 #non-matching colour
                        for n in range(4):
                            if markedGroups[n]!=-1 and group==markedGroups[n]: #group1 through group4
                                found[a+2][b+2]+=2**(n+5)
                else:
                    found[a+2][b+2]+=16 #add for edge of board
        if debug:
            print('Found:',  found)
        hits=set()
        for orientation in orientations: #detect whether each orientation matches
            f=found[:]
            #Rotate found clockwise; equivalent to matching pattern rotated anticlockwise
            if orientation==3 or orientation==-3:
                f=[f[4][::-1], f[3][::-1],  f[2][::-1],  f[1][::-1],  f[0][::-1]]
            elif orientation==4 or orientation==-4:
                f=[[f[4][0], f[3][0],  f[2][0],  f[1][0], f[0][0]]  ,  [f[4][1], f[3][1],  f[2][1],  f[1][1], f[0][1]], [f[4][2], f[3][2],  f[2][2],  f[1][2], f[0][2]] , [f[4][3], f[3][3],  f[2][3],  f[1][3], f[0][3]],  [f[4][4], f[3][4],  f[2][4],  f[1][4], f[0][4]] ]
            elif orientation==2 or orientation==-2:
                f=[[f[0][4], f[1][4],  f[2][4],  f[3][4], f[4][4]]  ,  [f[0][3], f[1][3],  f[2][3],  f[3][3], f[4][3]], [f[0][2], f[1][2],  f[2][2],  f[3][2], f[4][2]] , [f[0][1], f[1][1],  f[2][1],  f[3][1], f[4][1]],  [f[0][0], f[1][0],  f[2][0],  f[3][0], f[4][0]] ]
                
            if orientation<0: #flip columns
                f=f[::-1]
                
            if self.bitMatch(pattern,  f,  5,  5):
                if verbose==True:
                    hits.add(orientation)
                else:
                    return {orientation}
        return hits
    
    
    def bitMatch(self, pattern,  found,  a=3,  b=3): #returns true if every bitwise AND is non-zero
        for i in range(a):
            for j in range(b):
                if pattern[i][j]&found[i][j]==0:
                    return False
        return True
    
    def patternCoordinates(self, i, j, a, b, orientation): #Return actual board position of pattern point i+a, j+b (a,b from -1 to 1) given that it was detected at orientation
        if orientation<0:
            a=-a
            orientation=-orientation
        if orientation==1:
            return (i+a, j+b)
        if orientation==2:
            return (i+b, j-a)
        if orientation==3:
            return (i-a, j-b)
        if orientation==4:
            return (i-b, j+a)
    #--
    
    def minEdgeDistance(self,  i,  j):
        return min(i+1,  j+1,  self.boardSize-i,  self.boardSize-j)
    
    
    
    
    #Private methods
    
    def captureGroup(self, target): #removes group from board, adds to captures
        for pos in self.groups[target].stones:
            self.board[pos[0]][pos[1]]=-1 #remove from board
            #self.colourBoard[playerNumber(self.groups[target].colour)][pos[0]][pos[1]]=0 #remove from colourStones board
            if self.groups[target].colour==WHITE:
                self.whiteStonesCaptured+=1 
            else:
                self.blackStonesCaptured+=1
        self.groups[target].merged=True
    
    def recalculateLiberties(self,  group):#recalculates (and reassigns) number of liberties in group
        noOfLiberties=len(self.touchingLiberties(group))
        self.groups[group].liberties=noOfLiberties
        return noOfLiberties
    
    def otherPlayer(self):
        if self.move==BLACK:
            return WHITE
        else:
             return BLACK
    
    def incrementMove(self): #switches move from black to white or vice versa
        if self.move==BLACK:
            self.move=WHITE
        else:
            self.move=BLACK
    
    def makePass(self,  internal=True): #plays a pass
        self.incrementMove()
        self.history.append((-1, -1))
    
    #deepcopy
    def __deepcopy__(self,  memo):
        newcopy=gameState()
        newcopy.board=[0 for i in range(self.boardSize)]
        for i in range(self.boardSize):
            newcopy.board[i]=copy.copy(self.board[i])
        newcopy.noOfGroups=self.noOfGroups
        newcopy.move=self.move
        newcopy.boardSize=self.boardSize
        newcopy.groups=[]
        newcopy.history=copy.copy(self.history)
        for i in range(self.noOfGroups):
            newcopy.groups.append(copy.copy(self.groups[i]))
        return newcopy



#Other
def condenseList(list1): #returns a list with duplicates removed
    list2=[]
    for item in list1:
        if item in list2:
            pass
        else:
            list2.append(item)
    return list2
    
def playerNumber(colour):
    if colour==BLACK:
        return 0
    else:
        return 1
    
