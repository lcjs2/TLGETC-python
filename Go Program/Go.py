import pygame,  sys,  time,  random, cProfile
if False: #error warnings...
    cProfile
    random
    time
from pygame.locals import *
from gameState import *

pygame.init()

#Global constants:
BLACK=(0, 0, 0)
WHITE=(255, 255, 255)

import drawBoard



def main():
    game=gameState()
    players=[]

    from drawBoard import HumanBot
    from RandomBot import RandomBot
    from CaptureBot import CaptureBot
    from BetterBot import BetterBot
    
    #set players
    players=[0, 0]
    players[0]=HumanBot()
    players[1]=HumanBot()

    
    #NB 14 characters is maximum name size
    game.blackName=players[0].getName()
    game.whiteName=players[1].getName()
    
    #draw game for first time
    drawBoard.redraw(game,  players)
    #waitForKey()
    
    passCounter=0
    while passCounter<2:
        print('Thinking...')
        (i, j) = players[playerNumber(game.move)].getMove(game)
        #print('Engine selected ',  (i, j))
        if False: #player control of engine moves
            drawBoard.redraw(game,  players)
            print('Engine selected ',  (i, j), '. Waiting for human choice...')
            (i, j)=HumanBot().getMove(game)
        
        if (i, j)==(-1, -1):
            passCounter+=1
        else:
            passCounter=0
        
        
        drawBoard.redraw(game, players,  True)
        print('Engine selected: ',  (i, j),  ' based on this board')
        #waitForKey()
        game.makeMove(i, j,  False)
        drawBoard.redraw(game, players)
        #time.sleep(0.5)
        #waitForKey() 
        
    drawBoard.redraw(game,  players)
    print('Game Over')    
    waitForKey()
    sys.exit()


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



#Finally, run
if __name__=='__main__':
    #cProfile.run('main()')
    main()
