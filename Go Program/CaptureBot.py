import random

#This code is getting messy. Use at your own risk!

#THIS CODE IS FROZEN
#STOP FIDDLING WITH THIS CRAP
#WRITE SOMETHING BETTER INSTEAD

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
        
