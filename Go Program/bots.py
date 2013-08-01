
#########    bots    ########

#Contains:
#	HumanBot
#	RandomBot
#	CaptureBot
#	BetterBot

import random
import sys
import copy
import pygame
from pygame.locals import *
import gui
from gui import * #isOnBoard, getBoardCoordinates
from constants import *

pygame.init()

class HumanBot(object):
    def __init__(self):
        pass

    def getName(self):
        return 'Human'
    
    def getMove(self,  game):
        pygame.event.get()#clear waiting events
        while True:
            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == MOUSEBUTTONDOWN:
                    mousex, mousey = event.pos
                    if gui.isOnBoard(mousex,mousey):
                        i, j = gui.getBoardCoordinates(mousex,mousey)
                        if game.isLegalMove(i,j):
                            return (i,j) 
                    if mousex>boardWidth and mousey>boardWidth-100: #detect pass
                        return (-1, -1)
	
    def debugDraw(self, game):
        pass


class RandomBot(object):
    def __init__(self):
        pass
    
    def getName(self):
        return 'RandomBot v'+str(random.randrange(1, 10))+'.'+str(random.randrange(0, 10))
    
    def getMove(self,  game):
        possibles=[]
        for i in range(0,game.boardSize):
            for j in range(0,game.boardSize):
                if game.isLegalMove(i,j):
                    possibles.append((i,j))
        if len(possibles)==0:
            return (-1,-1) 
        
        return random.choice(possibles)
import random

#This code is getting messy. Use at your own risk!

#THIS CODE IS FROZEN
#STOP FIDDLING WITH THIS CRAP
#WRITE SOMETHING BETTER INSTEAD
# lol  -JJ

class CaptureBot(object):
    def __init__(self):
        pass
    
    def getName(self):
        return 'CaptureBot'
    
    def getMove(self,  game):
        value=0
        possibles=[(-1,-1)]
        maxValue=-10
        for i in range(0,game.boardSize):
            for j in range(0,game.boardSize):
                value=0
                if game.isLegalMove(i,j)==False:
                    value=-10000
                    #print('Illegal Move')
                    continue
    
                
                if len(game.adjLiberties(i,j))==4:
                    value+=10 #slight preference for empty space with single stones
                if len(game.adjLiberties(i,j))==3:
                    value+=7 #slight preference for empty space with single stones
                resultingLibs=len(game.resultingLiberties(i,j,game.move))
                value+=resultingLibs
                
                stonesToSave = 0 #compute number of friendly stones in atari here
                for group in game.adjSameGroups(i,j,game.move):
                    if game.groups[group].liberties==1:
                        stonesToSave+=game.groups[group].length
                stonesToCapture = 0 #compute number of enemy stones in atari here
                for group in game.adjEnemyGroups(i,j,game.move):
                    if game.groups[group].liberties==1:
                        stonesToCapture+=game.groups[group].length
                        for friendlyGroup in game.touchingGroups(group):
                            if game.groups[friendlyGroup].liberties==1:
                                stonesToSave+=game.groups[friendlyGroup].length
    
                if (stonesToSave>0 ) or len(game.adjLiberties(i,j))>1 or len(game.adjEnemyGroups(i,j,game.move))>1:
                    if len(game.adjPoints(i, j))==4 or len(game.resultingLiberties(i, j, game.otherPlayer()))>2 or stonesToSave>0:
                        value+=100*stonesToCapture
                    else: #allow it to take on first line if connecting would connect to large enough group
                        sizeOfLump=0
                        for grp in game.adjEnemyGroups(i, j):
                            sizeOfLump+=game.groups[grp].length
                        if sizeOfLump>4:
                            value+=100*stonesToCapture
                      
                if (stonesToCapture>0 and len(game.adjSameGroups(i, j))==0) or resultingLibs>1:
                    if len(game.adjPoints(i, j))==4 or resultingLibs>2: #Prevent stupid first-line connections that die
                        value+=100*stonesToSave
                    else: #allow it to connect on first line if connecting would connect to large enough group
                        sizeOfLump=0
                        for grp in game.adjSameGroups(i, j):
                            sizeOfLump+=game.groups[grp].length
                        if sizeOfLump>4:
                            value+=100*stonesToSave
    
                if resultingLibs==1 and stonesToCapture==0:
                    value-=40 #self-atari bad!
    
                for group in game.adjEnemyGroups(i,j,game.move):
                    if game.groups[group].liberties<=min(4,resultingLibs) and game.groups[group].liberties>1:
                        value+=30 #reduce liberties
                        if game.groups[group].liberties==2: #favour atari
                            value+=30
                    if resultingLibs==1 and game.groups[group].liberties==2:
                        value+=10*game.groups[group].length #atari anything 5 stones or bigger, even with self-atari
    
                value+=len(game.adjPoints(i, j))
    
                if len(game.adjEnemyGroups(i,j,game.move))>0 and len(game.adjSameGroups(i,j,game.move))>1:
                    value+=20 #favour connecting
    
                if (i==1 or j==1 or i==game.boardSize-2 or j==game.boardSize-2) and game.noOfGroups<9:
                    value-=5 # avoid second line at start
                    
                
                nb=game.adjDiagSameGroups(i, j) #dealing with eyes
                if len(nb)==1:
                    nbGroup=game.groups[nb[0]]
                    if nbGroup.length>=5 and len(game.adjLiberties(i, j))==2 and len(game.touchingLiberties(nb[0]))<=3:
                        (a, b)=game.adjLiberties(i, j)[0]
                        (c, d)=game.adjLiberties(i, j)[1]
                        if (a-c)^2+(b-d)^2>1:#liberties not adjacent
                            value+=10
                    if len(game.adjDiagLiberties(i, j))<=2 and len(game.adjEnemyGroups(i, j))==0: #don't fill eyes
                        value-=30
                if len(nb)==2 and len(game.adjDiagLiberties(i, j))+len(game.diagEnemyGroups(i, j))<=2 and len(game.adjPoints(i, j))>3: #still don't fill eyes
                    value-=20
                
                         
                #Add to list is equal to max; replace list if greater
                if value>maxValue:
                    possibles=[(i,j)]
                    maxValue=value
                elif value==maxValue:
                    possibles.append((i,j))
        if possibles==[(-1,-1)]:
            return (-1,-1)
        if (-1,-1) in possibles:
            possibles.remove((-1,-1))
        #Second pass with equal value list
        maxFineTuneValue=0
        fineTuneValue=0
        fineTunePossibles=[]
        for (i,j) in possibles:
            fineTuneValue=0
            if maxValue>20 and len(game.adjSameGroups(i,j,game.move))==0:
                for pos in game.diagSameGroups(i,j,game.move):
                    fineTuneValue+=10 #if more than random placement involved, favour the one with most diagonals
    
            if len(game.adjSameGroups(i,j,game.move))+ len(game.diagSameGroups(i,j,game.move))==1 and len(game.adjEnemyGroups(i,j,game.move))==1 and (i==0 or j==0 or i==game.boardSize-1 or j==game.boardSize-1):
                for nb in game.adjEnemyGroups(i,j,game.move):
                    if game.groups[nb].liberties>2:
                        fineTuneValue+=50 #edge move
    
    
            if maxValue<10:
                fineTuneValue+=10*len(game.adjLiberties(i,j,game.move)) #three-in-a-row rule
    
    
                       
            if fineTuneValue>maxFineTuneValue:
                fineTunePossibles=[(i,j)]
                maxFineTuneValue=fineTuneValue
            elif fineTuneValue==maxFineTuneValue:
                fineTunePossibles.append((i,j))
    
                
    
        selectedMove=random.choice(fineTunePossibles)
        print(maxValue)
        if game.noOfGroups>2*game.boardSize*game.boardSize: #pass out stupid games
            print('Quitting very long game')
            return (-1, -1)
        return selectedMove

    def debugDraw(self, game):
        pass
        

#This code is getting messy. Use at your own risk!

#THIS CODE IS FROZEN
#STOP FIDDLING WITH THIS CRAP
#WRITE SOMETHING BETTER INSTEAD
# lol  -JJ

class CaptureBot(object):
    def __init__(self):
        pass
    
    def getName(self):
        return 'CaptureBot'
    
    def getMove(self,  game):
        value=0
        possibles=[(-1,-1)]
        maxValue=-10
        for i in range(0,game.boardSize):
            for j in range(0,game.boardSize):
                value=0
                if game.isLegalMove(i,j)==False:
                    value=-10000
                    #print('Illegal Move')
                    continue
    
                
                if len(game.adjLiberties(i,j))==4:
                    value+=10 #slight preference for empty space with single stones
                if len(game.adjLiberties(i,j))==3:
                    value+=7 #slight preference for empty space with single stones
                resultingLibs=len(game.resultingLiberties(i,j,game.move))
                value+=resultingLibs
                
                stonesToSave = 0 #compute number of friendly stones in atari here
                for group in game.adjSameGroups(i,j,game.move):
                    if game.groups[group].liberties==1:
                        stonesToSave+=game.groups[group].length
                stonesToCapture = 0 #compute number of enemy stones in atari here
                for group in game.adjEnemyGroups(i,j,game.move):
                    if game.groups[group].liberties==1:
                        stonesToCapture+=game.groups[group].length
                        for friendlyGroup in game.touchingGroups(group):
                            if game.groups[friendlyGroup].liberties==1:
                                stonesToSave+=game.groups[friendlyGroup].length
    
                if (stonesToSave>0 ) or len(game.adjLiberties(i,j))>1 or len(game.adjEnemyGroups(i,j,game.move))>1:
                    if len(game.adjPoints(i, j))==4 or len(game.resultingLiberties(i, j, game.otherPlayer()))>2 or stonesToSave>0:
                        value+=100*stonesToCapture
                    else: #allow it to take on first line if connecting would connect to large enough group
                        sizeOfLump=0
                        for grp in game.adjEnemyGroups(i, j):
                            sizeOfLump+=game.groups[grp].length
                        if sizeOfLump>4:
                            value+=100*stonesToCapture
                      
                if (stonesToCapture>0 and len(game.adjSameGroups(i, j))==0) or resultingLibs>1:
                    if len(game.adjPoints(i, j))==4 or resultingLibs>2: #Prevent stupid first-line connections that die
                        value+=100*stonesToSave
                    else: #allow it to connect on first line if connecting would connect to large enough group
                        sizeOfLump=0
                        for grp in game.adjSameGroups(i, j):
                            sizeOfLump+=game.groups[grp].length
                        if sizeOfLump>4:
                            value+=100*stonesToSave
    
                if resultingLibs==1 and stonesToCapture==0:
                    value-=40 #self-atari bad!
    
                for group in game.adjEnemyGroups(i,j,game.move):
                    if game.groups[group].liberties<=min(4,resultingLibs) and game.groups[group].liberties>1:
                        value+=30 #reduce liberties
                        if game.groups[group].liberties==2: #favour atari
                            value+=30
                    if resultingLibs==1 and game.groups[group].liberties==2:
                        value+=10*game.groups[group].length #atari anything 5 stones or bigger, even with self-atari
    
                value+=len(game.adjPoints(i, j))
    
                if len(game.adjEnemyGroups(i,j,game.move))>0 and len(game.adjSameGroups(i,j,game.move))>1:
                    value+=20 #favour connecting
    
                if (i==1 or j==1 or i==game.boardSize-2 or j==game.boardSize-2) and game.noOfGroups<9:
                    value-=5 # avoid second line at start
                    
                
                nb=game.adjDiagSameGroups(i, j) #dealing with eyes
                if len(nb)==1:
                    nbGroup=game.groups[nb[0]]
                    if nbGroup.length>=5 and len(game.adjLiberties(i, j))==2 and len(game.touchingLiberties(nb[0]))<=3:
                        (a, b)=game.adjLiberties(i, j)[0]
                        (c, d)=game.adjLiberties(i, j)[1]
                        if (a-c)^2+(b-d)^2>1:#liberties not adjacent
                            value+=10
                    if len(game.adjDiagLiberties(i, j))<=2 and len(game.adjEnemyGroups(i, j))==0: #don't fill eyes
                        value-=30
                if len(nb)==2 and len(game.adjDiagLiberties(i, j))+len(game.diagEnemyGroups(i, j))<=2 and len(game.adjPoints(i, j))>3: #still don't fill eyes
                    value-=20
                
                         
                #Add to list is equal to max; replace list if greater
                if value>maxValue:
                    possibles=[(i,j)]
                    maxValue=value
                elif value==maxValue:
                    possibles.append((i,j))
        if possibles==[(-1,-1)]:
            return (-1,-1)
        if (-1,-1) in possibles:
            possibles.remove((-1,-1))
        #Second pass with equal value list
        maxFineTuneValue=0
        fineTuneValue=0
        fineTunePossibles=[]
        for (i,j) in possibles:
            fineTuneValue=0
            if maxValue>20 and len(game.adjSameGroups(i,j,game.move))==0:
                for pos in game.diagSameGroups(i,j,game.move):
                    fineTuneValue+=10 #if more than random placement involved, favour the one with most diagonals
    
            if len(game.adjSameGroups(i,j,game.move))+ len(game.diagSameGroups(i,j,game.move))==1 and len(game.adjEnemyGroups(i,j,game.move))==1 and (i==0 or j==0 or i==game.boardSize-1 or j==game.boardSize-1):
                for nb in game.adjEnemyGroups(i,j,game.move):
                    if game.groups[nb].liberties>2:
                        fineTuneValue+=50 #edge move
    
    
            if maxValue<10:
                fineTuneValue+=10*len(game.adjLiberties(i,j,game.move)) #three-in-a-row rule
    
    
                       
            if fineTuneValue>maxFineTuneValue:
                fineTunePossibles=[(i,j)]
                maxFineTuneValue=fineTuneValue
            elif fineTuneValue==maxFineTuneValue:
                fineTunePossibles.append((i,j))
    
                
    
        selectedMove=random.choice(fineTunePossibles)
        print(maxValue)
        if game.noOfGroups>2*game.boardSize*game.boardSize: #pass out stupid games
            print('Quitting very long game')
            return (-1, -1)
        return selectedMove

    def debugDraw(self, game):
        pass
        
class BetterBot(object):
    def __init__(self):
        self.teams=[] #list of teams; ith entry is a team containing group i 
        self.connections=set() #connections between two groups. One for every pair of groups.
        self.interestingTeams=set() #Used for limiting the updating - basically all teams involving game.interestingGroups
        self.oldGameState=0
    
    def getName(self):
        return 'BetterBot'
    
    def getMove(self, game):
        if len(game.history)<=1:
            self.oldGameState = copy.deepcopy(game)
            self.updateConnectionsAndTeams(game)
        else:
            self.oldGameState.makeMove(game.history[len(game.history)-2][0], game.history[len(game.history)-2][1])
            self.updateConnectionsAndTeams(self.oldGameState)
            self.updateConnectionsAndTeams(game)
            self.oldGameState = copy.deepcopy(game)
            
        possibleMoves=set()#each elt is a tuple of: [move tuple; value; explanatory string for testing] (must be tuple, since list is not hashable so can't have set of lists)
        
        listOfTeams=self.setOfTeams(game)
        #generate moves that give teams space or take away space
        for team in listOfTeams:
            if team.colour==game.move: #if unsettled friendly team:
                a=self.possibleChangeInSpace(game,  team)
                if team.status==2:
                    for x in a:
                        possibleMoves.add((x[0], int((x[1]*3)/2),  str(int((x[1]*3)/2))+' for '+ x[2]+' (unsettled)'))
                else:
                    for x in a:
                        possibleMoves.add((x[0], x[1],  str(x[1])+' for '+ x[2]))
        
        #Begin loop through all moves
        for i in range(game.boardSize):
            for j in range(game.boardSize):
                
                if game.isLegalMove(i, j): #add points for not being too low
                    if i==2 or i==3 or i==game.boardSize-3 or i==game.boardSize-4:
                        possibleMoves.add(((i, j), 100, '100 for being in column 3 or 4'))
                    if j==2 or j==3 or j==game.boardSize-3 or j==game.boardSize-4:
                        possibleMoves.add(((i, j), 100, '100 for being in row 3 or 4'))
                    if (i>=1 and i<=game.boardSize-2) and (j>=1 and j<=game.boardSize-2):
                        possibleMoves.add(((i, j), 100, '100 for not first line'))
                
                    #Shape bonuses
                    if len(game.pattern3x3([[-1, 17, 17], [17, -1, 1], [17, 1, 1]], i, j,game.move ))>0:
                        possibleMoves.add(((i, j), -10000, '-10000 for filling in eye'))
                    
                    if len(game.pattern3x3([[-1, 18, -1], [18, -1, 18], [-1, 18, -1]], i, j,game.move ))>0:
                        possibleMoves.add(((i, j), -5000, '-5000 for self-atari'))
                
                    if len(game.pattern3x3([[-1, 1, -1], [2, -1,2], [-1, 1, -1]], i, j,game.move ))>0:
                        possibleMoves.add(((i, j), 1500, '1500 for connecting through'))
                
                    if len(game.pattern3x3([[-1, 1, -1], [2, -1,2], [-3, -2, -1]], i, j,game.move ))>0:
                        possibleMoves.add(((i, j), 1000, '1000 for pushing through'))
                    
                    if len(game.pattern5x5([[-1, -1, -1, -1, -1], [-1, -1, -1, -1, -1], [-1, -1, -1, -3, -1], [-1, 1, 2, 4, 2], [-1, -1, 1, 2, -1]], i, j, game.move))>0:
                        possibleMoves.add(((i, j), 1000, '1000 for loss-free atari'))
                
                    if len(game.pattern5x5([[-1, -1, -1, -1, -1], [-1, -1, -2, -1, -1], [-1, 1, -1, -2, 16], [-1, 2, 1, -1, 16], [-1, -1, 2, -1, -1]], i, j, game.move))>0:
                        possibleMoves.add(((i, j), 3000, '3000 for edge capture'))
                    
                    if len(game.pattern5x5([[-1, -1, -1, -1, -1], [-1, 4, 4, -1, -1], [2, 1, -1, -19, -1], [-1, 2, 4, -1, -1], [-1, -1, -1, -1, -1]], i, j, game.move))>0:
                        possibleMoves.add(((i, j), 2000, '2000 for extend-from-hane'))
                    
                    if len(game.pattern3x3([[2, -2, -2], [-2, -1,-2], [-2, -2, -2]], i, j,game.move ))>0:
                        possibleMoves.add(((i, j), -4000, '-4000 for unsupported shoulder hit'))
                    
                    if len(game.pattern5x5([[-1, -1, -2, -1, -1], [2, 1, -2, -2, 16], [-2, 2, -1, -2, 16], [-1, -1, -2, -1, -1], [-1, -1, -1, -1, -1]], i, j, game.move))>0:
                        possibleMoves.add(((i, j), -7000, '-7000 for stupid 2nd line hane'))
                    
                    if len(game.pattern5x5([[-1, 4,4,4, -1], [4, 4, 4, 4, 4], [4, 4, -1, 4, 4], [4, 4, 4, 4, 4], [-1, 4,4,4, -1]], i, j, game.move))>0:
                        possibleMoves.add(((i, j), 6000, '6000 for playing in empty space'))
                    
                    if len(game.pattern5x5([[-1, -1,-1,-1, -1], [-1, -1, -2, -1, -1], [-1, -2, -1, -2, -1], [-1, -1, 2, 1, 2], [-1, -1,-1,2, -1]], i, j, game.move))>0:
                        possibleMoves.add(((i, j), -6000, '-10000 for playing next to atari stone'))
        
        #generate moves that kill teams
        
        #generate moves that play in empty space
        
        #generate moves that capture stones/save stones
        for group in range(game.noOfGroups):
            if game.groups[group].merged==False:
                if game.groups[group].colour==game.move:
                    for x in game.groups[group].toEscape:
                        if x!=(-1, -1):
                            possibleMoves.add((x, 2000*game.groups[group].length, str(2000*game.groups[group].length)+' for saving group '+str(group)))
                else: #if enemy group
                    if (-1, -1) not in game.groups[group].toCapture:
                        for x in game.groups[group].toCapture:
                            possibleMoves.add((x, 2000*game.groups[group].length,  str(2000*game.groups[group].length)+' for capturing group '+str(group)))


        #Amalgamate possible move reasons
        amalgamatedMoves=[]
        while len(possibleMoves)>0:
            x = possibleMoves.pop()
            put=False
            for y in amalgamatedMoves:
                if x[0]==y[0]:
                    y[1]+=x[1]
                    y[2]+=', '+x[2]

                    put=True
            if put==False:
                amalgamatedMoves.append(list(x))
        
        
        #Pick randomly from moves with highest value
        amalgamatedMoves.sort(key=getPMValue)
        for x in amalgamatedMoves:
            if x[1]>=1000:
                print('Move ', x[0], '=', x[1], ': ', x[2])
        
        if len(amalgamatedMoves)==0:
            print('random move!')
            (i, j)=(-10, -10)
            while (game.isLegalMove(i, j))==False:
                (i, j)=(random.randrange(game.boardSize), random.randrange(game.boardSize))
                return (i, j)
        return amalgamatedMoves[len(amalgamatedMoves)-1][0]
    
 
    def recalculateControl(self, game, team): #Determine which points are controlled exclusively by team
        #sets team.controlledPoints to be the set of points undoubtably controlled by the team
        nearbyPoints=set()
        impassablePoints=set()
        taggedImpassables=set()
        colour=team.colour
        for group in team.groups:
            for (i, j) in game.groups[group].stones:
                nearbyPoints|=game.libertiesInEuclideanRadius(i, j, 4)
                impassablePoints|=game.pointsInTaxicabRadius(i, j, 1)
                taggedImpassables.add((i, j))
        
        enemyPoints=set()
        justAddedEnemyPoints=set()
        
        for a in range(team.left-4,  team.right+4+1):
            for b in range(team.top-4,  team.bottom+4+1):
                if game.isOnBoard(a, b) and game.board[a][b]>=0 and game.groups[game.board[a][b]].colour!=colour and ((-1, -1) not in game.groups[game.board[a][b]].toCapture):
                    justAddedEnemyPoints.add((a, b)) #add living enemy stones to justAddedEnemyStones
        
        for k in range(5):
            enemyPoints|=justAddedEnemyPoints
            newEnemyPoints=set()
            for (a, b) in justAddedEnemyPoints:
                for (c, d) in game.libertiesInTaxicabRadius(a, b, 1):
                    newEnemyPoints.add((c, d))
            newEnemyPoints-=enemyPoints
            taggedImpassables|=newEnemyPoints&impassablePoints
            newEnemyPoints-=impassablePoints
            justAddedEnemyPoints=newEnemyPoints
        enemyPoints|=justAddedEnemyPoints
        
        nearbyPoints-=enemyPoints
        nearbyPoints-=taggedImpassables
    
        team.controlledPoints = nearbyPoints


    
    
    def updateConnectionsAndTeams(self,  game): #creates and recalculates all connections, then call recalculateTeams
        #move is location of last played move
        
        #Update toCapture moves of all interesting groups
        for group in game.interestingGroups:
            game.groups[group].toCapture=capturingMoves(game,  group)
            #Then update toEscape moves for all interesting groups under threat
            if len(game.groups[group].toCapture)>0 and ((-1, -1) not in game.groups[group].toCapture):
                game.groups[group].toEscape=canEscapeIn(game,  group,  searchDepth,  True)
            else:
                game.groups[group].toEscape=set()
        
        #strip out connections involving at least one interestingGroup; remake those connections
        #also remove connections between merged groups.
        toRemove=set()
        for connection in self.connections:
                
            if (connection.group1 in game.justMergedGroups) or (connection.group2 in game.justMergedGroups) or (connection.group1 in game.interestingGroups) or (connection.group2 in game.interestingGroups) or (game.groups[connection.group1].merged==True) or (game.groups[connection.group2].merged==True):
                toRemove.add(connection)
        self.connections-=toRemove
        
        for group1 in range(game.noOfGroups):  #group1<group2?
            for group2 in range(game.noOfGroups):
                if group1 >= group2 or ((group1 not in game.interestingGroups) and (group2 not in game.interestingGroups)):
                    continue
                 
                if game.groups[group1].merged==False and game.groups[group2].merged==False and game.groups[group1].colour==game.groups[group2].colour:
                    x=connectionObj(group1,  group2,  game)
                    self.connections.add(x)
                    self.recalculateConnection(game, x)
                    
        
        self.interestingTeams=set()
        self.recalculateTeams(game)#now merge connected groups into teams
        
        for team in self.setOfTeams(game): #then recalculate life/death status of teams
            self.recalculateControl(game,  team)
            self.recalculateTeamStatus(game, team)
        
  
    def recalculateConnection(self, game,  connection): #recalculates the status of single connection 
        #ignore too far away
        a = max([game.groups[connection.group1].left - game.groups[connection.group2].right,game.groups[connection.group2].left - game.groups[connection.group1].right,  0])
        b= max([game.groups[connection.group1].top - game.groups[connection.group2].bottom,game.groups[connection.group2].top - game.groups[connection.group1].bottom,  0])
        if a+b>=9: #this just rules out large knight's move and two-space jump
            connection.status=0
            return
    
        libs1=set(game.touchingLiberties(connection.group1))
        libs2=set(game.touchingLiberties(connection.group2))
        sharedLibs=libs1&libs2
        touchingGroups1=set(game.touchingGroups(connection.group1))
        touchingGroups2=set(game.touchingGroups(connection.group2))
        cuttingGroups=touchingGroups1&touchingGroups2
        connection.halfConnections=set() #contains shared liberties and one stone from each capturable cutting groups
        connection.fullConnections=set()
        connection.toCut=set()
        connection.toConnect=set()
        
        for x in sharedLibs: #add a half connection for each shared liberty, unless opponent can't play there
            if isCapturable(game,  x[0],  x[1],  otherColour(connection.colour)):
                connection.fullConnections.add(x)
            else:
                connection.halfConnections.add(x)
        if len(connection.fullConnections)==0 and len(connection.halfConnections)<=1: #if necessary...
            for x in cuttingGroups: #...add half connection for capturable group, and... IMPLEMENT: full connection for dead group as long as it has fewer liberties 
                if (-1, -1) in game.groups[x].toCapture:
                    connection.fullConnections.add(game.groups[x].stones[0]) #add full connection for dead cutting stone
                elif len(game.groups[x].toCapture)>0:
                        connection.halfConnections.add(game.groups[x].stones[0]) #add a random stone from the group to halfconnections
            
        if len(connection.fullConnections)==0 and len(connection.halfConnections)==1: #If still no connection, look deeper
            (i, j)=connection.halfConnections.pop()
            if len(game.pattern3x3([[-1, 4, -1], [1, -1, 1], [-3, 4, -3]], i, j, connection.colour, {1, -1, 2, -2}, True))>0:
                connection.fullConnections.add((i, j)) #one-point jump, no peep, counts as full connection
            a=game.pattern3x3([[-1, 2, -1], [1, -1, 1], [-1, 4, -1]], i, j, connection.colour, {1, -1, 2, -2}, True)
            if len(a)==1: #one point jump with peep counts if both cutting points are individually capturable
                orientation=a.pop()
                gamecopy=copy.deepcopy(game)
                if gamecopy.move==connection.colour:
                    gamecopy.makeMove(-1, -1)
                gamecopy.makeMove(i, j)
                (x, y)=game.patternCoordinates(i, j, 1, 0, orientation)
                if gamecopy.isLegalMove(x, y):
                    gamecopy.makeMove(x, y)
                    (x_1, y_1)=gamecopy.patternCoordinates(i, j, 1, -1, orientation)
                    (x_2, y_2)=gamecopy.patternCoordinates(i, j, 1, -1, orientation)
                    if isCapturable(gamecopy, x_1, y_1, gamecopy.move) and isCapturable(gamecopy, x_2, y_2, gamecopy.move):
                        connection.fullConnections.add((i, j))
            
        if len(connection.fullConnections)==0 and len(connection.halfConnections)==0: #look for knight's move
            for (i, j) in (set(game.touchingLiberties(connection.group1))&set(game.touchingLiberties(connection.group2)))|(set(game.touchingLiberties(connection.group2))&set(game.touchingLiberties(connection.group1))):
                if len(game.pattern3x3([[-3, -3, -3], [1, -3, -3], [-3, -3, 1]], i, j, connection.colour))>0:
                    connection.fullConnections.add((i, j))
            
            
            
            
        #set status of connection
        if len(connection.halfConnections)>=2 or len(connection.fullConnections)>=1: #at least two possible connections, or a full one, makes connected
            connection.status=1
        elif len(connection.halfConnections)==1: #exactly one possible connection move
            for y in connection.halfConnections:
                connection.toCut.add(y)
                connection.toConnect.add(y)
            #where else to look for connecting moves? IMPLEMENT once captureMoves is more useful            
            connection.status=2
        else:
            connection.status=0
    
   
    def recalculateTeams(self, game): # given connections, group into teams. Recalculate control
        self.teams=[] #list of teams: pointer to the team of group i at index i. Many duplicates
        #Only update teams involving a group from game.interestingGroups
        
        
        for group in range(game.noOfGroups):
            if game.groups[group].merged==False:
                self.teams.append(team(game, group)) 
                #make one new team for every existent group
            else:
                self.teams.append('No team here - merged')
        
        for x in self.connections: #merge teams according to connections.
            team1=self.teams[x.group1]
            team2=self.teams[x.group2]
            if x.status==1: #if connected
                mergedTeam=self.mergeTeams(team1,  team2)
                for y in range(len(self.teams)):
                    if self.teams[y]==team1 or self.teams[y]==team2:
                        self.teams[y]=mergedTeam
                        
 
    def mergeTeams(self,  team1,  team2): #returns the merged team (used in recalculateTeams
        if team1==team2:
            return team1        
        team1.groups|=team2.groups
        team1.left=min(team1.left,  team2.left)
        team1.right=max(team1.right,  team2.right)
        team1.top=min(team1.top,  team2.top)
        team1.bottom=max(team1.bottom,  team2.bottom)
        return team1

    
    
    def recalculateTeamStatus(self,  game,  team): #recalculate life/death status of team.
        if len(team.controlledPoints)>7: #only return 1 for definitely alive
            #print('Team ',  team.name,  ' alive,  controlling ', len(team.controlledPoints), ' points')
            team.status=1
            return
        
        for group in team.groups: #can't be that dead if lots of liberties (!)
            if len(game.touchingLiberties(group))>5:
                #print('Team ', team.name, ' unsettled - group ', group,  'many liberties')
                team.status=2
                return
            if (-1, -1) in game.groups[group].toCapture:
                #print('Team ', team.name, ' dead - group ', group, ' cannot be saved, so team is dead')
                team.status=0
                return
        
        #print('Team ', team.name, ' unsettled.')
        team.status=2
        return
    
    
    
    def possibleChangeInSpace(self,  game,  team): #generates moves which expand the eye space of team or shrink it
        
        oldControlledPoints=team.controlledPoints
        possibleMoves=set()
        profitableMoves=set()
        for group in team.groups:
            for (i, j) in game.groups[group].stones:
                possibleMoves|=game.libertiesInTaxicabRadius(i, j, 2)
        for (i, j) in possibleMoves:        
            if game.isLegalMove(i, j):
                gamecopy=copy.deepcopy(game)
                gamecopy.makeMove(i, j)
                team.groups.add(gamecopy.noOfGroups-1)
                self.recalculateControl(gamecopy, team) 
                newControlledPoints=len(team.controlledPoints)
                team.groups.remove(gamecopy.noOfGroups-1)
                team.controlledPoints=oldControlledPoints
                profit=newControlledPoints-len(oldControlledPoints)
                if team.colour==game.move:
                    word='extra'
                else:
                    profit=-profit
                    word = 'less'
                if profit>0:
                    profitableMoves.add(((i, j), 1000*profit,  str(profit)+' '+word+' territory for team '+team.name))
            
        return profitableMoves
    
    
    
    
    def possibleConnections(self,  game,  team1,  team2):
        pass
    
    
    
    
    
    def setOfTeams(self, game): #returns duplicate-free set of team objects from game
        setTeams=set()
        for x in range(game.noOfGroups):
            if game.groups[x].merged==False:
                setTeams.add(self.teams[x])
        return setTeams
    
    
    
    
    
    
    
    
    
    
    
    
    def debugDraw(self,  game): #Draw useful data onto board
        if game.noOfGroups<=1:
            return
       

#PRINT CAPTURABILITY OF ALL GROUPS
#        for x in range(game.noOfGroups):
#            if game.groups[x].merged==False:
#                capmoves=game.groups[x].toCapture
#                if len(capmoves)==0:
#                    print('Group ', x, ' not capturable.')
#                else:
#                    print('Group ', x, ' capturable by: ', capmoves )
#                    print('...and can be saved with ', game.groups[x].toEscape)

#DRAW ON CONTROL
        listOfTeams=self.setOfTeams(game)
        
        statuses=['D', 'A', 'U']
        for x in listOfTeams:
            if x.status!=0:
                for (i, j) in x.controlledPoints:
                    pygame.draw.circle(DISPLAYSURF,x.colour,coordinates(i, j),10)
                    makeText(x.name, otherColour(x.colour), x.colour, coordinates(i,j)[0], coordinates(i,j)[1]-1, True)
            for group in x.groups:
                for stone in game.groups[group].stones:
                    if group in game.interestingGroups:
                        c='I'
                    else:
                        c='/'
                    makeText(x.name+c+statuses[x.status], otherColour(x.colour), x.colour, coordinates(stone[0],stone[1])[0], coordinates(stone[0], stone[1])[1]+8, True)
        
       # game.pattern5x5([[-1, -1, -1, -1, -1], [-1, -1, -1, -1, -1], [-1, -1, -1, -1, -1], [-1, -1, -1, -1, -1], [-1, -1, -1, -1, -1]], 4,4, game.move, {-4, -3, -2, -1, 1, 2, 3, 4}, False, [-1, -1, -1, -1],  True)

#Pattern matching test
#        target=[[16, 16, 16], [-1, 4, -1], [3, -1, 3]]
#        for i in range(game.boardSize):
#            for j in range(game.boardSize):
#                result=game.pattern3x3(target, i, j, BLACK, {-4, -3, -2, -1, 1, 2, 3, 4}, True)
#                if len(result)>0:
#                    print('At ', (i, j), ': ',result )
        
class team(object): #set of groups connected together by connections
    def __init__(self, game, firstGroup):
        self.colour=game.groups[firstGroup].colour
        self.groups={firstGroup} #group numbers involved in the team
        self.status=2 #0=dead, 1=alive, 2=unsettled. When in doubt, return "unsettled"
        self.controlledPoints=set() #set of points controlled by this team
        self.left=min(game.groups[firstGroup].stones[i][0] for i in range(game.groups[firstGroup].length)) #leftmost coordinate in all stones in this team
        self.right=max(game.groups[firstGroup].stones[i][0] for i in range(game.groups[firstGroup].length))#rightmost coordinate
        self.top=min(game.groups[firstGroup].stones[0][1] for i in range(game.groups[firstGroup].length))#top (remember this is a low number)!
        self.bottom=max(game.groups[firstGroup].stones[0][1] for i in range(game.groups[firstGroup].length))#bottom (high number)
        self.name=random.choice([ 'b', 'c', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'v', 'w', 'x', 'y', 'z'])    
    
    def __str__(self):
        returnString='Team with groups '
        returnString+=str(self.groups)
        return returnString



class connectionObj(object): #a connection between two groups
    def __init__(self,  group1,  group2,  game): 
        self.group1=group1
        self.group2=group2
        self.colour=game.groups[group1].colour
        assert group1<group2,  'Calling connection with group1 >= group2'
        self.halfConnections={}
        self.fullConnections={}
        self.status=0 #0=not connected, 1=connected, 2=unsettled
        self.toConnect={}#if cut, threatens to connect; if unsettled, connects (not implemented)
        self.toCut={} #if connected, threaten to cut; if unsettled, cuts (not implemented)

    

    def __str__(self):
        returnString='Groups '+str(self.group1)+' and '+str(self.group2)+' are '
        if self.status==2:
            returnString+='cut at '
            for x in self.toCut:
                returnString+=str(x)
            returnString+= ' and connected at '
            for x in self.toConnect:
                returnString+=str(x)
        if self.status==1:
            returnString+='connected: half connections at '
            for x in self.halfConnections:
                returnString+=str(x)
            returnString+='; full connections at '
            for x in self.fullConnections:
                returnString+=str(x)
        if self.status==0:
            returnString+='not connected'
        return returnString
 
 
 
#other
def condenseList(list1): #returns a list with duplicates removed
    list2=[]
    for item in list1:
        if item in list2:
            pass
        else:
            list2.append(item)
    return list2
    
def otherColour(colour):
    if colour==BLACK:
        return WHITE
    else:
        return BLACK
        
def getPMValue(tuple): #Used in getMove
    return tuple[1]

#GameState and capturing subroutines for BetterBot
searchDepth=4
 
def isCapturable(game,  i,  j,  colour): #Can a hypothetical move at i,j be captured? Returns True for illegal move
    gamecopy=copy.deepcopy(game)
    if gamecopy.move!=colour:
        gamecopy.makeMove(-1, -1,  True)
    if gamecopy.isLegalMove(i, j):
        gamecopy.makeMove(i, j,  True)
        capMoves = capturingMoves(gamecopy,  gamecopy.noOfGroups-1)
        if len(capMoves)>=1:
            return True
        else:
            return False
    else:
        return True
        
def capturingMoves(game,  group,  depth=searchDepth,  returnMoves=True): #returns list of moves that capture group with group number group. Call this one! Returns pass (only!) if can't escape.
    #Ladders are read out to the end, but depth determines how deep we search if we're not just reading atari. A depth of d aims to find anything which will remove the group
    #in d stones. We always return ladders, so effectively depth >= 2
    #returnMoves determines whether a full set of moves is returned, or just whether it's possible (allowing an early return)
    #Recursive calls from this function must pass depth-1!
    
    
    #assert game.groups[group].colour!=game.move,  'Calling capturingMoves to capture a group of my own colour! Group '+str(group)+' depth '+ str(depth) +' board '+str(game.board)
    #print(game.board)

    
    if game.groups[group].colour==game.move: #if target group is same colour as to move, insert pass
        gamecopy=copy.deepcopy(game)
        gamecopy.makeMove(-1, -1, True)
        game=gamecopy

    if returnMoves==True and canEscapeIn(game,  group,  depth-1)==False:
        return {(-1, -1)}
    
    capturingMoves=set()
    libs = game.touchingLiberties(group)
    if returnMoves==False and len(libs)==1:
        return True
    if len(libs)<=2:
        ladderMoves=isLadderable(game,  group,  returnMoves)
        if returnMoves==True and ladderMoves!=False:
            capturingMoves|=set(ladderMoves) #add whatever captures in a ladder (including capturing stones in atari)
        if returnMoves==False and ladderMoves==True:
            return True
    
    if depth==len(libs) and len(libs)>1: #don't bother if in atari - just return the capturing move
        movesToTry=libs
    if depth>len(libs) and len(libs)>1:
        movesToTry=possibleCapturingMoves(game,  group)
        
        for move in movesToTry:
            if game.isLegalMove(move[0], move[1]):
                gamecopy=copy.deepcopy(game)
                gamecopy.makeMove(move[0], move[1]) #Try that move, see if w can escape.
                if (move in libs) and (len(libs)==2): #ataris don't count as extra depth, because they have less branching
                    newdepth=depth-1
                else:
                    newdepth=depth-1
                if canEscapeIn(gamecopy,  group,  newdepth)==False:
                    if returnMoves==True:
                        capturingMoves.add(move)
                    else:
                        return True
    if returnMoves==False:
        assert len(capturingMoves)==0,  'In capturingMoves,  have returnMoves==False but capturingMoves list non-empty.'
        return False #if moves in capturingmoves list with this flag, should have returned there
    return capturingMoves

def canEscapeIn(game, group,  depth,  returnMoves=False): #returns set of escaping moves if group (to move) can survive (depth) more opponent stones
    #pass is only returned if liberties <=2 (seki, eye space filling) or if it has far too many liberties. Semeai will break here :(
    #print('Calling canEscapeIn,  ',  group,  ' depth ',  depth,  'board:')
    #print(game.board)
    if game.groups[group].liberties>depth: #obviously if it has too many liberties it will survive
        if returnMoves:
            return {(-1, -1)}
        else:
            return True
    
    if game.move!=game.groups[group].colour:
        gamecopy2=copy.deepcopy(game)
        gamecopy2.makeMove(-1, -1)
        game=gamecopy2
    
    movesToTry=possibleEscapingMoves(game,  group)
    escapingMoves=set()

    for move in movesToTry:  
        if game.isLegalMove(move[0], move[1]):
            gamecopy=copy.deepcopy(game)
            if move!=(-1, -1) and len(gamecopy.adjLiberties(move[0], move[1], [group]))>0: #if this escaping move merges with target group, change target group 
                newgroup=gamecopy.noOfGroups
            else:
                newgroup=group
            gamecopy.makeMove(move[0], move[1]) #Try that move, see if escaper can escape.
            a=capturingMoves(gamecopy,  newgroup,  depth, True) 
            if len(a)==0:
                if returnMoves:
                    escapingMoves|={move}
                else:
                    return True

    if returnMoves:
        return escapingMoves
    else:
        return False
    
def isLadderable(game,  group,  returnMoves=False): #returns True if group can be captured with constant ataris. Returns False if it can get more than two liberties.
    #returnMoves determines whether the successful liberties are returned, or just True/False (for recursion)
    
    #print('Calling isLadderable ',  group, '...')
    libs=game.touchingLiberties(group)
    assert len(libs)>0,  'Group '+str(group)+  ' has no liberties!'
    if len(libs)==1: #return immediately if target in atari
        if returnMoves==True:
            return libs
        else:
            return True
    if len(libs)>2:
        return False
    
    libs0legal=game.isLegalMove(libs[0][0],  libs[0][1])
    libs1legal=game.isLegalMove(libs[1][0],  libs[1][1])
    #print('...liberties ',  libs, '...')
    
    if libs0legal==False and libs1legal==False: #return false if neither liberty can be played
        #print('...returning False because neither is legal.')
        return False
    
    #Now we have exactly two liberties, possibly one illegal move. Possibly surrounding stones are in atari.
    touchingGroups=game.touchingGroups(group)    
    atariStones=0
    canCaptureHere=(-10, -10)
    for x in touchingGroups: #return False if atari-ing a group of two stones or longer, or two single stones
        if game.groups[x].liberties==1:
            if game.touchingLiberties(x)[0]==libs[0] or game.touchingLiberties(x)[0]==libs[1]:
                pass
            else:
                atariStones+=len(game.touchingStones(group,  x))
                canCaptureHere=game.touchingLiberties(x)[0]
    if atariStones>1: 
        #print('...returning False because more than two surrounding stones in atari.')
        return False

    atariFailsAfter0 = True #must declare them here; if nothing in atari, then they just stay as true
    atariFailsAfter1 = True
    if atariStones==1: #first, if escaper answers atari by capturing the one stone

        #print('...surrounding stone at ',  canCaptureHere, ' is in atari...')
        if libs0legal==True:
            gamecopy=copy.deepcopy(game)
            gamecopy.makeMove(libs[0][0],  libs[0][1]) #play liberty 0
            if gamecopy.isLegalMove(canCaptureHere[0],  canCaptureHere[1]):
                if group in gamecopy.adjGroups(canCaptureHere[0],  canCaptureHere[1]):
                    newGroupNumber=gamecopy.noOfGroups #capturing stone will be merged, group number of target will change
                else:
                    newGroupNumber=group
                gamecopy.makeMove(canCaptureHere[0],  canCaptureHere[1]) #gamecopy has lib 0 played, stone captured.
                atariFailsAfter0= isLadderable(gamecopy,  newGroupNumber) #if false, then can escape move 0 by capturing
            #print('...atariFailsAfter0: ', atariFailsAfter0, '...')
        if libs1legal==True:
            gamecopy=copy.deepcopy(game)
            gamecopy.makeMove(libs[1][0],  libs[1][1]) #play liberty 1
            if gamecopy.isLegalMove(canCaptureHere[0],  canCaptureHere[1]):
                if group in gamecopy.adjGroups(canCaptureHere[0],  canCaptureHere[1]):
                    newGroupNumber=gamecopy.noOfGroups #capturing stone will be merged, group number of target will change
                else:
                    newGroupNumber=group
                gamecopy.makeMove(canCaptureHere[0],  canCaptureHere[1]) #gamecopy has lib 1 played, stone captured.
                atariFailsAfter1= isLadderable(gamecopy,  newGroupNumber)
                #print('...atariFailsAfter1: ', atariFailsAfter1, '...')
        if (atariFailsAfter0==False or libs0legal==False) and (atariFailsAfter1==False or libs1legal==False): #if both libs are either illegal or fail after the capture
            #print('...returning False for ',  group, ' because capturing will escape.')
            return False
    
    
    
    #At this point we have exactly two liberties. Capturer is playing one, possibly self-atari. Escaper can't escape by capturing, so must either take the other or capture
    move0captures=False
    move1captures=False
    if libs0legal==True: #SAME CODE TWICE
        gamecopy=copy.deepcopy(game)
        gamecopy.makeMove(libs[0][0],  libs[0][1]) #make move 0
        libsOfCapturer=gamecopy.touchingLiberties(gamecopy.noOfGroups-1)
        capturingEscapes=False
        otherLibEscapes=False
        if len(libsOfCapturer)==1: #if playing that liberty was self-atari...
            gamecopy2 = copy.deepcopy(gamecopy)
            if gamecopy2.isLegalMove(libsOfCapturer[0][0],  libsOfCapturer[0][1]):
                if group in gamecopy2.adjGroups(libsOfCapturer[0][0],  libsOfCapturer[0][1]):
                    newGroupNumber=gamecopy2.noOfGroups #capturing stone will be merged, group number of target will change
                else:
                    newGroupNumber=group
                gamecopy2.makeMove(libsOfCapturer[0][0],  libsOfCapturer[0][1]) #...capture it and see if the result is ladderable
                capturingEscapes=not isLadderable(gamecopy2, newGroupNumber)
        if gamecopy.isLegalMove(libs[1][0],  libs[1][1]): #otherwise, escaper must play other liberty if possible, and see if that escapes
            gamecopy.makeMove(libs[1][0],  libs[1][1])
            otherLibEscapes=not isLadderable(gamecopy,  gamecopy.noOfGroups-1)
        if capturingEscapes==False and otherLibEscapes==False:
            move0captures=True
    if libs1legal==True and (move0captures==False or returnMoves==True): #SAME CODE TWICE
        gamecopy=copy.deepcopy(game)
        gamecopy.makeMove(libs[1][0],  libs[1][1]) #make move 1
        libsOfCapturer=gamecopy.touchingLiberties(gamecopy.noOfGroups-1)
        capturingEscapes=False
        otherLibEscapes=False
        if len(libsOfCapturer)==1:
            gamecopy2 = copy.deepcopy(gamecopy)
            if gamecopy2.isLegalMove(libsOfCapturer[0][0],  libsOfCapturer[0][1]):
                if group in gamecopy2.adjGroups(libsOfCapturer[0][0],  libsOfCapturer[0][1]):
                    newGroupNumber=gamecopy2.noOfGroups #capturing stone will be merged, group number of target will change
                else:
                    newGroupNumber=group
                gamecopy2.makeMove(libsOfCapturer[0][0],  libsOfCapturer[0][1])
                capturingEscapes=not isLadderable(gamecopy2,  newGroupNumber)
        if gamecopy.isLegalMove(libs[0][0],  libs[0][1]):
            gamecopy.makeMove(libs[0][0],  libs[0][1])
            otherLibEscapes=not isLadderable(gamecopy,  gamecopy.noOfGroups-1)
        if capturingEscapes==False and otherLibEscapes==False:
            move1captures=True
    #print('... returning ',  move0captures or move1captures, ' for ',  group, ' because move0captures ',  move0captures, ' and (if false) move1captures ',  move1captures)
    if returnMoves:
        moves=[]
        if (move0captures ==True and atariFailsAfter0==True and libs0legal):
            moves.append(libs[0])
        if (move1captures ==True and atariFailsAfter1==True and libs1legal):
            moves.append(libs[1])
        if moves==[]:
            return False
        else:
            return moves
    else:
        return move0captures or move1captures

def possibleCapturingMoves(game,  group): #returns moves that might capture group, including liberties. Put most promising first
    assert game.move!=game.groups[group].colour,  'Called capturingMoves with mismatched colours'
    possibles=[]
    for surroundingGroup in game.touchingGroups(group): #append connecting own stones in atari
        if game.groups[surroundingGroup].liberties==1:
            lib=game.touchingLiberties(surroundingGroup)[0]
            if game.isLegalMove(lib[0], lib[1]):
                possibles.append(lib)
    for x in game.touchingLiberties(group): #append removing a liberty
        if game.isLegalMove(x[0], x[1]):
            possibles.append(x)
    for x in game.diagTouchingLiberties(group): #append diagonal net-like moves
        if game.isLegalMove(x[0], x[1]):
            possibles.append(x)
    
    return condenseList(possibles)

def possibleEscapingMoves(game,  group): #returns possible moves to escape, most promising first, including liberties.
    assert game.move==game.groups[group].colour,  'Called escapingMoves with mismatched colours'
    possibles=[]
    for surroundingGroup in game.touchingGroups(group): #append atari or capture of surrounding stones. Only one of these so leave it at the front
        if game.groups[surroundingGroup].liberties<=2: #IMPLEMENT add all possible capturing moves if surrounding group has fewer or equal number of liberties.
            for lib in game.touchingLiberties(surroundingGroup):
                if game.isLegalMove(lib[0], lib[1]):
                    possibles.append(lib)
    libIncreasingPossibles=[]
    for x in game.touchingLiberties(group):
        if game.isLegalMove(x[0], x[1]):
            libIncreasingPossibles.append(x)
    libIncreasingPossibles.sort(key=game.lenResultingLibertiesFromTuple,  reverse=True)
    possibles.extend(libIncreasingPossibles)
    
    if game.groups[group].liberties>1: #only return diagonal moves if more than one liberty
        for x in game.diagTouchingLiberties(group):
            if game.isLegalMove(x[0], x[1]):
                possibles.append(x)
    return condenseList(possibles)
    
    if game.groups[group].liberties<=2: #put pass in last, and only if 2 or fewer liberties
        possibles.append((-1, -1))
