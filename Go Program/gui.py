import sys
import time
import random
import cProfile
from constants import *
from bots import *
import pygame
from pygame.locals import *

pygame.init()

debug=True

stoneWidth=5
board=0

def redraw(game,  players=[0, 0],  drawDebug=False):
    global board
    global stoneWidth
    board=game.boardSize
    stoneWidth=int((boardWidth-(2*margin))/board)
    drawBoard(game,  players,  drawDebug)
    drawPanel(game,  players)
    pygame.display.update()
    return

def drawBoard(game,  players=[0, 0],  drawDebug=False):
    pygame.draw.rect(DISPLAYSURF, boardColour, (0,0,boardWidth, boardWidth))
    # Draw grid
    for i in range(0,board):
        pygame.draw.line(DISPLAYSURF, (0,0,0), coordinates(0,i), coordinates(board-1,i))
        if debug==True:
            makeText(str(i),  BLACK,  boardColour,  coordinates(0, i)[0]-int(margin/2),  coordinates(0, i)[1],  True,  True)
    for i in range(0, board):
        pygame.draw.line(DISPLAYSURF, (0,0,0), coordinates(i,0), coordinates(i,board-1))
        if debug==True:
            makeText(str(i),  BLACK,  boardColour,  coordinates(i, 0)[0],   coordinates(i, 0)[1]-int(margin/2),  True,  True)
    
    
    
    # Draw stones
    for i in range(0,board): #row
        for j in range(0,board): #column
            if game.board[i][j]==-1:
                continue
            elif game.board[i][j]==-2: #draw ko small circle
                pygame.draw.circle(DISPLAYSURF,(128,128,128),coordinates(i,j),int(stoneWidth/10))
                continue
            elif game.groups[game.board[i][j]].colour==BLACK:
                pygame.draw.circle(DISPLAYSURF,BLACK,coordinates(i,j),int(stoneWidth/2))
                if debug==True:
                    makeText(str(game.board[i][j]), WHITE, BLACK, coordinates(i,j)[0], coordinates(i,j)[1]-8, True)
            elif game.groups[game.board[i][j]].colour==WHITE:
                pygame.draw.circle(DISPLAYSURF, WHITE, coordinates(i,j),int(stoneWidth/2))
                if debug==True:
                    makeText(str(game.board[i][j]), BLACK, WHITE, coordinates(i,j)[0], coordinates(i,j)[1]-8, True)
    
    nextMoveNumber = len(game.history)+1 #Draw last move marker
    if nextMoveNumber!=1:
        if game.history[nextMoveNumber-2]==(-1, -1):
            makeText('('+getColourName(game.move,  True)+' passes)',  BLACK,  boardColour,  boardWidth-60,  boardWidth-40,  True,  True)
        elif debug==False:
            pygame.draw.circle(DISPLAYSURF,(128,128,128),coordinates(game.history[nextMoveNumber-2][0],game.history[nextMoveNumber-2][1]),int(stoneWidth/10)) #add last move marker only if not debugging
        
    if debug==True and drawDebug==True:
        players[playerNumber(game.move)].debugDraw(game) #pass to engine for drawing
    

def drawPanel(game,  players=[0, 0]): #This will fall apart when panelWidth changes
    pygame.draw.rect(DISPLAYSURF,  panelColour,  (boardWidth,  0,  boardWidth+panelWidth,boardWidth))
    pygame.draw.circle(DISPLAYSURF, BLACK,  (boardWidth+30,  70), 15)
    makeText(game.blackName,  BLACK,  panelColour,  boardWidth+55 + int((panelWidth-70)/2),  70,  True)
    pygame.draw.circle(DISPLAYSURF, WHITE,  (boardWidth+30,  70+int(boardWidth/2)), 16)
    makeText(game.whiteName,  BLACK,  panelColour,  boardWidth+55 + int((panelWidth-70)/2),  70+int(boardWidth/2),  True)
    
    makeText('Captured:',  BLACK,  panelColour,  boardWidth+70,  120,  True)
    makeText(str(game.whiteStonesCaptured),  BLACK,  panelColour,  boardWidth+140,  120,  True)
    pygame.draw.circle(DISPLAYSURF,  WHITE,  (boardWidth+170, 118), 10)
    makeText('Captured:',  BLACK,  panelColour,  boardWidth+70,  120+int(boardWidth/2),  True)
    makeText(str(game.blackStonesCaptured),  BLACK,  panelColour,  boardWidth+140,  120+int(boardWidth/2),  True)
    pygame.draw.circle(DISPLAYSURF,  BLACK,  (boardWidth+170, 118+int(boardWidth/2)), 10)
    
    makeText('To move:',  BLACK,  panelColour,  boardWidth+int(panelWidth/2)-30,  int(boardWidth/2)-50, True)
    pygame.draw.circle(DISPLAYSURF,  game.move,  (boardWidth+int(panelWidth/2)+40,  int(boardWidth/2)-50),  15)
    
    makeText('Pass',  BLACK,  panelColour,  boardWidth+int(panelWidth/2),  boardWidth-50, True)
    
def makeText(text, colour, bgcolour, left, top, centreGiven,  small=False):
    if small==False:
        textSurf = font.render(text, True, colour, bgcolour)
    else:
        textSurf = fontSmall.render(text, True, colour, bgcolour)
    textRect=textSurf.get_rect()
    if centreGiven:
        textRect.center=(left, top)
    else:
        textRect.topleft=(left, top)
    DISPLAYSURF.blit(textSurf, textRect)
    
def getColourName(colour,  other):
    if (colour==BLACK and other==False) or (colour==WHITE and other==True):
        return 'Black'
    else:
        return 'White'
    
def coordinates(i,j): #gets pixel coordinates of centre of board position i,j
    x = int(margin + ((2*i + 1)*(stoneWidth/2)))
    y = int(margin + ((2*j + 1)*(stoneWidth/2)))
    return (x,y)
    
def isOnBoard(x,y): #checks whether pixel x,y is on the board
    if (x>=margin) and (y>=margin) and (x<margin+board*stoneWidth) and (y<margin+board*stoneWidth):
        return True
    else:
        return False

def getBoardCoordinates(x,y): #gets board coordinates of pixel x,y 
    i = int((x-margin)/stoneWidth)
    j = int((y-margin)/stoneWidth)
    return i,j
    
def playerNumber(colour):
    if colour==BLACK:
        return 0
    else:
        return 1

#Useful functions
def waitForClick():
	clicked=False
	while clicked==False:
		for event in pygame.event.get():
			if event.type==MOUSEBUTTONDOWN:
				clicked=True

def waitForKey():
	clicked=False
	while clicked==False:
		for event in pygame.event.get():
			if event.type==KEYDOWN:
				clicked=True
def play(game, players):
    passCounter=0
    while passCounter<2:
        print('Thinking...')
        (i, j) = players[playerNumber(game.move)].getMove(game)
        #print('Engine selected ',  (i, j))
        if False: #player control of engine moves
            redraw(game,  players)
            print('Engine selected ',  (i, j), '. Waiting for human choice...')
            (i, j)=HumanBot().getMove(game)
        
        if (i, j)==(-1, -1):
            passCounter+=1
        else:
            passCounter=0
        
        
        redraw(game, players,  True)
        print('Engine selected: ',  (i, j),  ' based on this board')
        #waitForKey()
        game.makeMove(i, j,  False)
        redraw(game, players)
        #time.sleep(0.5)
        #waitForKey() 
