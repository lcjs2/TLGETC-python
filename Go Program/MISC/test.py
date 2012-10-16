import random, pygame, sys, time, copy
from pygame.locals import *

pygame.init()

#Define classes

class group(object): #Group of solidly connected stones
    def __init__(self, stones, colour):
        self.colour=colour
        self.stones = stones #list of tuples
        self.length = len(stones)
        self.liberties = 4
        self.merged = False #should not be touched after this is set to True


    def removeLiberties(self, n):
        self.liberties-=n

 
        

class gameState(object): #New empty game state
    def __init__(self):
        #self.board = [] #Create empty board. Board contains group index numbers, -1 for empty, -2 for ko
        self.board = [[-1 for i in range(boardsize)] for j in range(boardsize)]
        #for i in range(0,boardSize):
        #    column=[]
        #    for j in range(0,boardSize):
        #        column.append(-1)
        #    self.board.append(column)
        self.groups=[] #list of connected groups, indexed by their position in this list.
        self.noOfGroups=0
        self.move=BLACK

        self.blackCaptures=0
        self.whiteCaptures=0
        self.komi=6

    def isLegalMove(self, i, j):
        if i==-10 and j==-10:
            return True
        if self.board[i][j]!=-1:
            return False
        #check for suicide        
        gotSpace=False
        for pos in self.adjacentPoints(i,j):
            if self.board[pos[0]][pos[1]]<0 or (self.groups[self.board[pos[0]][pos[1]]].colour==self.move and self.groups[self.board[pos[0]][pos[1]]].liberties>1) or (self.groups[self.board[pos[0]][pos[1]]].colour!=self.move and self.groups[self.board[pos[0]][pos[1]]].liberties==1):
                gotSpace=True
        return gotSpace

    def adjacentPoints(self,i,j):
        listOfPoints=[]
        if i>0:
            listOfPoints.append((i-1,j))
        if j>0:
            listOfPoints.append((i,j-1))
        if i<boardSize-1:
            listOfPoints.append((i+1,j))
        if j<boardSize-1:
            listOfPoints.append((i,j+1))
        return listOfPoints

    def diagonalPoints(self, i, j):
        listOfPoints=[]
        if i>0 and j>0:
            listOfPoints.append((i-1,j-1))
        if i>0 and j<boardSize-1:
            listOfPoints.append((i-1,j+1))
        if j>0 and i<boardSize-1:
            listOfPoints.append((i+1,j-1))
        if i<boardSize-1 and j<boardSize-1:
            listOfPoints.append((i+1,j+1))
        return listOfPoints

    def diagonalSameGroups(self, i, j, colour):
        neighbours=[]
        for point in self.diagonalPoints(i,j):
            if self.board[point[0]][point[1]]>=0 and self.groups[self.board[point[0]][point[1]]].colour==colour:
                neighbours.append(self.board[point[0]][point[1]])
        return condenseList(neighbours)

    def diagonalEnemyGroups(self, i, j, colour):
        neighbours=[]
        for point in self.diagonalPoints(i,j):
            if self.board[point[0]][point[1]]>=0 and self.groups[self.board[point[0]][point[1]]].colour!=colour:
                neighbours.append(self.board[point[0]][point[1]])
        
        return condenseList(neighbours)

    def neighbouringSameGroups(self, i, j, colour): #returns list of group index numbers adjacent to (i,j) of the same colour
        neighbours=[]
        for point in self.adjacentPoints(i,j):
            if self.board[point[0]][point[1]]>=0 and self.groups[self.board[point[0]][point[1]]].colour==colour:
                neighbours.append(self.board[point[0]][point[1]])
        return condenseList(neighbours)

    def neighbouringEnemyGroups(self, i, j, colour): #returns list of group index numbers adjacent to (i,j) of the opposite colour
        neighbours=[]
        for point in self.adjacentPoints(i,j):
            if self.board[point[0]][point[1]]>=0 and self.groups[self.board[point[0]][point[1]]].colour!=colour:
                neighbours.append(self.board[point[0]][point[1]])
        return condenseList(neighbours)
    
    def neighbouringLiberties(self, i, j, emptySpaces=[-2,-1]): #returns list of empty board tuples adjacent to (i,j)
        neighbours=[]
        for point in self.adjacentPoints(i,j):
            if self.board[point[0]][point[1]] in emptySpaces:
                neighbours.append(point)
        return neighbours


    def recalculateLiberties(self, a):#calculates liberties in group a
        listOfLibs=[]
        for (i,j) in self.groups[a].stones:
            if i>0 and self.board[i-1][j]<0: #NB Python has minimal evaluation so not out of range
                listOfLibs.append((i-1,j))
            if i<boardSize-1 and self.board[i+1][j]<0: 
                listOfLibs.append((i+1,j))
            if j>0 and self.board[i][j-1]<0: 
                listOfLibs.append((i,j-1))
            if j<boardSize-1 and self.board[i][j+1]<0:
                listOfLibs.append((i,j+1))
        listOfLibs=condenseList(listOfLibs)
        self.groups[a].liberties=len(listOfLibs)
        return

    def makeMove(self, i, j):#returns move made. Returns (-10,-10) for pass and (-1,-1) for error.
        if self.isLegalMove(i, j)==False:
            return (-1,-1)
        if i==-10 and j==-10: #check for pass
            self.makePass()
            return (-10,-10)
        #legal move, not suicide
        self.groups.append(group([(i,j)],self.move))
        self.board[i][j]=self.noOfGroups
        #Remove ko markers
        for a in range(0,boardSize):
            for b in range(0,boardSize):
                if self.board[a][b]==-2:
                    self.board[a][b]=-1
        
        totalCaptured=0
        

        for item in self.neighbouringEnemyGroups(i,j,self.move):
            if self.groups[item].liberties==1:
                totalCaptured+=self.groups[item].length
                self.captureGroup(item)
            else:
                self.groups[item].removeLiberties(1)

        for item in self.neighbouringSameGroups(i,j,self.move):
            totalCaptured=0
            self.mergeGroups(item, self.noOfGroups)

        if totalCaptured==1: #then have captured exactly one, and not adjacent to same-colour stones
            self.recalculateLiberties(self.noOfGroups)
            assert self.groups[self.noOfGroups].liberties!=0, 'Suicide somehow allowed.'
            if self.groups[self.noOfGroups].liberties==1: #then ko!
                for pos in self.adjacentPoints(i,j):
                    if self.board[pos[0]][pos[1]]==-1:
                        self.board[pos[0]][pos[1]]=-2 #put in ko marker

        #Recalculate number of liberties on all groups (!)
        for k in range(0,self.noOfGroups+1):
            if self.groups[k].merged==False:
                self.recalculateLiberties(k)
        self.noOfGroups+=1
        self.incrementMove()
        return (i,j)

    def captureGroup(self, target):
        for pos in self.groups[target].stones:
            self.board[pos[0]][pos[1]]=-1
            if self.groups[target].colour==WHITE:
                self.whiteCaptures+=1 #white captures in number of captured white stones
            else:
                self.blackCaptures+=1
        self.groups[target].merged=True
        return

    def mergeGroups(self,a,b): #merge groups a and b into group b
        assert self.groups[a].colour==self.groups[b].colour, 'Trying to merge two groups of different colours.'
        for (i,j) in self.groups[a].stones:
            assert self.board[i][j]==a, 'First merging group was incorrectly labelled on the board.'
            self.board[i][j]=b
        self.groups[b].stones.extend(self.groups[a].stones)
        self.groups[b].length=len(self.groups[b].stones)
        self.groups[a].merged=True

        return

    def resultingLiberties(self,i,j,colour):#returns the number of liberties a move at (i,j) would end up with.
        emptySpaces=[-2,-1]
        for group in self.neighbouringEnemyGroups(i,j,colour):
            if self.groups[group].liberties==1:
                emptySpaces.append(group)
        listOfLiberties=self.neighbouringLiberties(i,j, emptySpaces)
        for group in self.neighbouringSameGroups(i,j,colour):
            listOfLiberties.extend(self.touchingLiberties(group, emptySpaces))
        while (i,j) in listOfLiberties:
            listOfLiberties.remove((i,j))
        listOfLiberties=condenseList(listOfLiberties)
        return len(listOfLiberties)

    def touchingLiberties(self,group, emptySpaces=[-2,-1]): #returns a list of liberties (as tuples) touching group
        liberties=[]
        for stone in self.groups[group].stones:
            for pos in self.adjacentPoints(stone[0], stone[1]):
                if self.board[pos[0]][pos[1]] in emptySpaces:
                    liberties.append((pos[0], pos[1]))
        return condenseList(liberties)

    def touchingGroups(self, group):
        listOfTouchingGroups=[]
        for stone in self.groups[group].stones:
            for pos in self.adjacentPoints(stone[0],stone[1]):
                if self.board[pos[0]][pos[1]]>=0 and self.groups[self.board[pos[0]][pos[1]]].colour!=self.groups[group].colour:
                    listOfTouchingGroups.append(self.board[pos[0]][pos[1]])
        return condenseList(listOfTouchingGroups)

    def makePass(self):
        self.incrementMove()

    def incrementMove(self):
        if self.move==BLACK:
            self.move=WHITE
        else:
            self.move=BLACK
        return

    def score(self): #Only works correctly in Chinese rules with all but single eyes filled
        blackTotal=0
        whiteTotal=0

        #WRITE BETTER SCORING SYSTEM!
        
        for i in range(0,boardSize):
            for j in range(0,boardSize):
                if self.board[i][j]<0: #empty places
                    blackNeighbours=len(self.neighbouringSameGroups(i,j,BLACK))
                    whiteNeighbours=len(self.neighbouringSameGroups(i,j,WHITE))
                    if blackNeighbours==0 and whiteNeighbours==0:
                        print('Scoring cannot handle isolated spaces!')
                    if blackNeighbours>0 and whiteNeighbours==0:
                        blackTotal+=1
                    if whiteNeighbours>0 and blackNeighbours==0:
                        whiteTotal+=1
                    
                elif self.groups[self.board[i][j]].colour==BLACK:
                    blackTotal+=1
                elif self.groups[self.board[i][j]].colour==WHITE:
                    whiteTotal+=1
        #blackTotal+= self.whiteCaptures #whiteCaptures in number of captured white stones
        #whiteTotal+= self.blackCaptures
        whiteTotal+=self.komi
        return blackTotal, whiteTotal
#Set constants

BOARDWIDTH = 604
PANELWIDTH = 200
MARGIN = 50
BOARDCOLOUR = (230,200,130)
PANELCOLOUR = (180,180,180)

FONT1 = pygame.font.Font('freesansbold.ttf', 22)

WHITE = (255,255,255)
BLACK = (0,0,0)
EMPTY = (128,128,128,0)
KO = (255,0,0)


pygame.init()
DISPLAYSURF = pygame.display.set_mode((BOARDWIDTH + PANELWIDTH,BOARDWIDTH))
pygame.display.set_caption('The Little Go Engine That Could')


boardSize=9
stoneWidth = int((BOARDWIDTH - (2*MARGIN))/boardSize)

#~~~~~~~~~~~~~~~~~~~~~  MAIN  ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


def main():
    blackWins=0
    trials=100
    for t in range(0,trials):
        game=gameState() #New blank game
        redraw(game)
        engines=[0,2]
   
        passCounter=0
        while passCounter<2:
            toPlay=getTurn(game)
            fetchedMove=getMove(engines[toPlay], game) #get tuple from engine
            madeMove=game.makeMove(fetchedMove[0],fetchedMove[1])
            assert madeMove!=(-1,-1), 'Error making move.'
            if madeMove==(-10,-10):
                #print('PASS', game.move)
                passCounter+=1
            else:
                passCounter=0
            redraw(game)
            time.sleep(0.5)
            #waitForClick()
            #waitForButton()

        blackTotal, whiteTotal=game.score()
        if blackTotal>whiteTotal:
            blackWins+=1
        if engines[0]*engines[1]!=0:
            print('Game Over: Black ', blackTotal, ' White ', whiteTotal)
        waitForButton()
    print('Black wins ', blackWins,' out of ', trials,': ',100*blackWins/trials, '%')
    

#~~~~~~~~~~~~~~~~~~~~  GAME ENGINES  ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#Returned move is a tuple (i,j). Return (-10,-10) for pass.
    #Engines:
    #0=Human input
    #1=Random
    #2=CaptureBot

def getMove(engine,game):
    fetchedMove=(-1,-1)
    if engine==0:
        fetchedMove=HumanBot(game)
    elif engine==1:
        fetchedMove=RandomBot(game)
    elif engine==2:
        fetchedMove=CaptureBot(game)
    assert fetchedMove!=(-1,-1), 'That engine does not exist.'
    return fetchedMove
        


def HumanBot(game):
    pygame.event.get()#clear waiting events
    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            if event.type == MOUSEBUTTONDOWN:
                mousex, mousey = event.pos
                if isOnBoard(mousex,mousey):
                    i, j = getBoardCoordinates(mousex,mousey)
                    if game.isLegalMove(i,j):
                        return (i,j)                  
 

def RandomBot(game): #Plays random moves!
    possibles=[]
    for i in range(0,boardSize):
        for j in range(0,boardSize):
            if game.isLegalMove(i,j):
                possibles.append((i,j))
    if len(possibles)==0:
        return (-10,-10) 
    
    return random.choice(possibles)


def CaptureBot(game):
    #Each square on the board gets +10 for each capture, +10 for each stone of it own it saves from atari, +2 for each
    #liberty it takes from opponent, +1 for each liberty it gains and -10 for each stone of its own it puts in atari.
    value=0
    possibles=[(-10,-10)]
    maxValue=-10
    for i in range(0,boardSize):
        for j in range(0,boardSize):
            value=0
            if game.isLegalMove(i,j)==False:
                value=-10000
                #print('Illegal Move')
                continue

            
            if len(game.neighbouringLiberties(i,j))==4:
                value+=10 #slight preference for empty space with single stones
            resultingLibs=game.resultingLiberties(i,j,game.move)
            
            stonesToSave = 0 #compute number of friendly stones in atari here
            for group in game.neighbouringSameGroups(i,j,game.move):
                if game.groups[group].liberties==1:
                    stonesToSave+=game.groups[group].length
            stonesToCapture = 0 #compute number of enemy stones in atari here
            for group in game.neighbouringEnemyGroups(i,j,game.move):
                if game.groups[group].liberties==1:
                    stonesToCapture+=game.groups[group].length
                    for friendlyGroup in game.touchingGroups(group):
                        if game.groups[friendlyGroup].liberties==1:
                            stonesToSave+=game.groups[friendlyGroup].length

            if (stonesToSave>0) or len(game.neighbouringLiberties(i,j))>1 or len(game.neighbouringEnemyGroups(i,j,game.move))>1:
                value+=100*stonesToCapture
            if (stonesToCapture>0) or resultingLibs>1:
                value+=100*stonesToSave

            if resultingLibs==1 and stonesToCapture==0:
                value-=50 #self-atari bad!

            for group in game.neighbouringEnemyGroups(i,j,game.move):
                if game.groups[group].liberties<=min(4,resultingLibs) and game.groups[group].liberties>1:
                    value+=30 #reduce liberties
                    if game.groups[group].liberties==2: #favour atari
                        value+=30
                if resultingLibs==1 and game.groups[group].liberties==2:
                    value+=10*game.groups[group].length #atari anything 6 stones or bigger, even with self-atari

            

            if len(game.neighbouringEnemyGroups(i,j,game.move))>0 and len(game.neighbouringSameGroups(i,j,game.move))>1:
                value+=20 #favour connecting

            if (i==1 or j==1 or i==boardSize-2 or j==boardSize-2) and game.noOfGroups<9:
                value-=5 # avoid second line at start
            
                     
            #Add to list is equal to max; replace list if greater
            if value>maxValue:
                possibles=[(i,j)]
                maxValue=value
            elif value==maxValue:
                possibles.append((i,j))
    if possibles==[(-10,-10)]:
        return (-10,-10)
    if (-10,-10) in possibles:
        possibles.remove((-10,-10))
    #Second pass with equal value list
    maxFineTuneValue=0
    fineTuneValue=0
    fineTunePossibles=[]
    for (i,j) in possibles:
        fineTuneValue=0
        if maxValue>20 and len(game.neighbouringSameGroups(i,j,game.move))==0:
            for pos in game.diagonalSameGroups(i,j,game.move):
                fineTuneValue+=10 #if more than random placement involved, favour the one with most diagonals

        if len(game.neighbouringSameGroups(i,j,game.move))+ len(game.diagonalSameGroups(i,j,game.move))==1 and len(game.neighbouringEnemyGroups(i,j,game.move))==1 and (i==0 or j==0 or i==boardSize-1 or j==boardSize-1):
            for nb in game.neighbouringEnemyGroups(i,j,game.move):
                if game.groups[nb].liberties>2:
                    fineTuneValue+=50 #edge move


        if maxValue<10:
            fineTuneValue+=10*len(game.neighbouringLiberties(i,j,game.move)) #three-in-a-row rule


                   
        if fineTuneValue>maxFineTuneValue:
            fineTunePossibles=[(i,j)]
            maxFineTuneValue=fineTuneValue
        elif fineTuneValue==maxFineTuneValue:
            fineTunePossibles.append((i,j))

            

    selectedMove=random.choice(fineTunePossibles)
    
    #print('Value of move ', selectedMove, ' is ', maxValue)
    return selectedMove
    

#~~~~~~~~~~~~~~~~~~~~  USEFUL NON-GAMESTATE FUNCTIONS  ~~~~~~~~~~~~~~~~~~~~~~~

def emptyArray(n):
    result=[]
    for i in range(0,boardSize):
        column=[]
        for j in range(0,boardSize):
            column.append(n)
        result.append(column)
    return result

#~~~~~~~~~~~~~~~~~~~~  NON-GAME FUNCTIONS  ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# (coordinate calculations, board drawing, panel drawing)

def waitForClick():
    clicked=False
    while clicked==False:
        for event in pygame.event.get():
            if event.type==MOUSEBUTTONDOWN:
                clicked=True

def waitForButton():
    clicked=False
    while clicked==False:
        for event in pygame.event.get():
            if event.type==KEYDOWN:
                clicked=True

def getTurn(game):
    if game.move==BLACK:
        return 0
    else:
        return 1

def redraw(game):
    drawBoard(game)
    drawPanel(game)
    pygame.display.update()
    return

def isOnBoard(x,y): #checks whether pixel x,y is on the board
    if (x>=MARGIN) and (y>=MARGIN) and (x<BOARDWIDTH-MARGIN) and (y<BOARDWIDTH-MARGIN):
        return True
    else:
        return False
            
def getBoardCoordinates(x,y): #gets board coordinates of pixel x,y
    assert x>=MARGIN and y>=MARGIN and int((x-MARGIN)/stoneWidth)<boardSize and int((y-MARGIN)/stoneWidth)<boardSize, 'Computing board coordinates for a point off the board.'
    i = int((x-MARGIN)/stoneWidth)
    j = int((y-MARGIN)/stoneWidth)
    return i,j


def coordinates(i,j): #gets pixel coordinates of centre of board position i,j
    assert i<boardSize, 'Coordinates called with row too large.'
    assert j<boardSize, 'Coordinates called with column too large.'
    x = int(MARGIN + ((2*i + 1)*(stoneWidth/2)))
    y = int(MARGIN + ((2*j + 1)*(stoneWidth/2)))
    return (x,y)

def drawBoard(game):
    pygame.draw.rect(DISPLAYSURF, BOARDCOLOUR, (0,0,BOARDWIDTH, BOARDWIDTH))
    # Draw grid
    for i in range(0, boardSize):
        pygame.draw.line(DISPLAYSURF, (0,0,0), coordinates(0,i), coordinates(boardSize-1,i))
    for i in range(0, boardSize):
        pygame.draw.line(DISPLAYSURF, (0,0,0), coordinates(i,0), coordinates(i,boardSize-1))
    # Draw stones
    for i in range(0,boardSize): #row
        for j in range(0,boardSize): #column
            if game.board[i][j]==-1:
                continue
            if game.board[i][j]==-2: #draw ko small circle
                pygame.draw.circle(DISPLAYSURF,(128,128,128),coordinates(i,j),int(stoneWidth/10))
                continue
            if game.groups[game.board[i][j]].colour==WHITE:
                pygame.draw.circle(DISPLAYSURF,(255,255,255),coordinates(i,j),int(stoneWidth/2))
                #makeText(str(game.board[i][j]), BLACK, PANELCOLOUR, coordinates(i,j)[0], coordinates(i,j)[1], True)
            if game.groups[game.board[i][j]].colour==BLACK:
                pygame.draw.circle(DISPLAYSURF, (0,0,0), coordinates(i,j),int(stoneWidth/2))
                #makeText(str(game.board[i][j]), BLACK, PANELCOLOUR, coordinates(i,j)[0], coordinates(i,j)[1], True)
        
    return

def drawPanel(game):
    halfway=BOARDWIDTH+int(PANELWIDTH/2)
    pygame.draw.rect(DISPLAYSURF, PANELCOLOUR, (BOARDWIDTH, 0, PANELWIDTH, BOARDWIDTH))
    pygame.draw.circle(DISPLAYSURF,game.move,(BOARDWIDTH+stoneWidth+120, 200), int(stoneWidth/4))
    makeText('To move:', BLACK, PANELCOLOUR, BOARDWIDTH + 75,200, True)
    makeText('How about a ', BLACK, PANELCOLOUR, halfway,25, True)
    makeText('nice game of ', BLACK, PANELCOLOUR, halfway, 75, True)
    makeText('Go? ', BLACK, PANELCOLOUR, halfway, 125, True)
    makeText('Captured', BLACK, PANELCOLOUR, halfway, 300, True)
    pygame.draw.circle(DISPLAYSURF,BLACK,(halfway, 400), int(stoneWidth/2))
    pygame.draw.circle(DISPLAYSURF,WHITE,(halfway, 475), int(stoneWidth/2))
    makeText(str(game.blackCaptures), WHITE, BLACK, halfway, 400, True) #blackCaptures is the number of captured black stones.
    makeText(str(game.whiteCaptures), BLACK, WHITE, halfway, 475, True)
def condenseList(list1):
    list2=[]
    for item in list1:
        if item in list2:
            pass
        else:
            list2.append(item)
    return list2

def makeText(text, colour, bgcolour, left, top, centreGiven):
# create the Surface and Rect objects for some text.
    textSurf = FONT1.render(text, True, colour, bgcolour)
    textRect=textSurf.get_rect()
    if centreGiven:
        textRect.center=(left, top)
    else:
        textRect.topleft=(left, top)
    DISPLAYSURF.blit(textSurf, textRect)
    return 
    
if __name__=="__main__":
    main()
